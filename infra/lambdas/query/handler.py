import json
import os
from typing import Any, Dict, List, Tuple

import boto3
import urllib3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.exceptions import ClientError


HTTP = urllib3.PoolManager()

OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT", "")
OPENSEARCH_REGION = os.getenv("OPENSEARCH_REGION", os.getenv("AWS_REGION", "us-west-2"))
OPENSEARCH_INDEX = os.getenv("OPENSEARCH_INDEX", "artifacts")
BEDROCK_EMBED_MODEL = os.getenv("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", os.getenv("AWS_REGION", "us-west-2"))
DEFAULT_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
MAX_TOP_K = int(os.getenv("RETRIEVAL_TOP_K_MAX", "20"))


def _normalized_endpoint() -> str:
    endpoint = OPENSEARCH_ENDPOINT.strip()
    if not endpoint:
        return ""
    if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
        endpoint = f"https://{endpoint}"
    return endpoint.rstrip("/")


def _signed_aoss_request(method: str, path: str, payload: Any = None):
    endpoint = _normalized_endpoint()
    if not endpoint:
        raise RuntimeError("OPENSEARCH_ENDPOINT is not configured")

    url = f"{endpoint}{path}"
    body = None
    if payload is not None:
        if isinstance(payload, str):
            body = payload.encode("utf-8")
        elif isinstance(payload, bytes):
            body = payload
        else:
            body = json.dumps(payload).encode("utf-8")

    session = boto3.Session()
    credentials = session.get_credentials()
    if credentials is None:
        raise RuntimeError("AWS credentials unavailable for OpenSearch request signing")

    aws_request = AWSRequest(
        method=method,
        url=url,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    SigV4Auth(credentials, "aoss", OPENSEARCH_REGION).add_auth(aws_request)
    prepared = aws_request.prepare()

    return HTTP.request(
        method=method,
        url=url,
        body=body,
        headers=dict(prepared.headers.items()),
        retries=False,
    )


def _embed_question(question: str) -> List[float]:
    client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
    try:
        response = client.invoke_model(
            modelId=BEDROCK_EMBED_MODEL,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"inputText": question}),
        )
    except ClientError as exc:
        raise RuntimeError(f"Bedrock embedding call failed: {exc}") from exc

    payload = json.loads(response["body"].read())
    vector = payload.get("embedding", [])
    if not vector:
        raise RuntimeError("Bedrock embedding response did not include a non-empty embedding")
    return vector


def _parse_event(event: Dict[str, Any]) -> Tuple[str, int, Dict[str, Any]]:
    payload = event
    if "body" in event and isinstance(event["body"], str):
        try:
            payload = json.loads(event["body"])
        except json.JSONDecodeError:
            payload = {}

    question = (payload.get("question") or "").strip()
    if not question:
        raise ValueError("'question' is required")

    requested_top_k = payload.get("top_k", DEFAULT_TOP_K)
    try:
        top_k = int(requested_top_k)
    except (TypeError, ValueError):
        top_k = DEFAULT_TOP_K
    top_k = max(1, min(top_k, MAX_TOP_K))

    metadata_filter = payload.get("metadata_filter")
    if not isinstance(metadata_filter, dict):
        metadata_filter = {}

    return question, top_k, metadata_filter


def _build_filter_clause(metadata_filter: Dict[str, Any]) -> List[Dict[str, Any]]:
    clauses: List[Dict[str, Any]] = []
    for field, value in metadata_filter.items():
        if value is None:
            continue
        if isinstance(value, list):
            values = [item for item in value if item is not None]
            if values:
                clauses.append({"terms": {f"metadata.{field}": values}})
        else:
            clauses.append({"term": {f"metadata.{field}": value}})
    return clauses


def _vector_search(question_embedding: List[float], top_k: int, metadata_filter: Dict[str, Any]) -> List[Dict[str, Any]]:
    filter_clauses = _build_filter_clause(metadata_filter)

    query_block: Dict[str, Any] = {
        "knn": {
            "embedding": {
                "vector": question_embedding,
                "k": top_k,
            }
        }
    }
    if filter_clauses:
        query_block["knn"]["embedding"]["filter"] = {"bool": {"must": filter_clauses}}

    search_payload = {
        "size": top_k,
        "query": query_block,
        "_source": ["id", "doc_id", "chunk_id", "text", "metadata"],
    }

    response = _signed_aoss_request("POST", f"/{OPENSEARCH_INDEX}/_search", payload=search_payload)
    if response.status != 200:
        raise RuntimeError(
            f"OpenSearch search failed: status={response.status}, body={response.data.decode('utf-8', errors='ignore')}"
        )

    body = json.loads(response.data.decode("utf-8"))
    return body.get("hits", {}).get("hits", [])


def _normalize_results(hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for hit in hits:
        source = hit.get("_source", {})
        results.append(
            {
                "id": source.get("id") or hit.get("_id"),
                "doc_id": source.get("doc_id"),
                "chunk_id": source.get("chunk_id"),
                "text": source.get("text"),
                "metadata": source.get("metadata", {}),
                "score": hit.get("_score"),
            }
        )
    return results


def handler(event, context):
    try:
        question, top_k, metadata_filter = _parse_event(event or {})
    except ValueError as exc:
        return {"statusCode": 400, "body": json.dumps({"status": "error", "message": str(exc)})}

    endpoint = _normalized_endpoint()
    if not endpoint:
        body = {
            "status": "ok",
            "question": question,
            "top_k": top_k,
            "metadata_filter": metadata_filter,
            "retrieval_count": 0,
            "results": [],
            "next_step": "missing_opensearch_endpoint",
        }
        return {"statusCode": 200, "body": json.dumps(body)}

    question_embedding = _embed_question(question)
    hits = _vector_search(question_embedding, top_k, metadata_filter)
    results = _normalize_results(hits)

    body = {
        "status": "ok",
        "question": question,
        "top_k": top_k,
        "metadata_filter": metadata_filter,
        "retrieval_count": len(results),
        "results": results,
        "next_step": "llm_answer_generation_pending",
    }
    return {"statusCode": 200, "body": json.dumps(body)}
