import hashlib
import json
import os
import re
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

import boto3
import urllib3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.exceptions import ClientError


CHUNK_TARGET_CHARS = int(os.getenv("CHUNK_TARGET_CHARS", "900"))
CHUNK_OVERLAP_CHARS = int(os.getenv("CHUNK_OVERLAP_CHARS", "120"))
OPENSEARCH_INDEX = os.getenv("OPENSEARCH_INDEX", "artifacts")
OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT", "")
OPENSEARCH_REGION = os.getenv("OPENSEARCH_REGION", os.getenv("AWS_REGION", "us-west-2"))
OPENSEARCH_VECTOR_DIMENSION = int(os.getenv("OPENSEARCH_VECTOR_DIMENSION", "1024"))
DEFAULT_APPROVAL_STATUS = os.getenv("DEFAULT_APPROVAL_STATUS", "approved")
BEDROCK_EMBED_MODEL = os.getenv("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", os.getenv("AWS_REGION", "us-west-2"))
ENABLE_EMBED_UPSERT = os.getenv("ENABLE_EMBED_UPSERT", "true").lower() == "true"

HTTP = urllib3.PoolManager()


def normalize_doc_id(source_key: str) -> str:
    stem = source_key.rsplit("/", 1)[-1]
    stem = stem.rsplit(".", 1)[0]
    return re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")


def build_sections(artifact: Dict[str, Any]) -> List[Tuple[str, int, str]]:
    sections: List[Tuple[str, int, str]] = []

    summary = artifact.get("summary", "").strip()
    if summary:
        sections.append(("summary", 0, summary))

    for index, step in enumerate(artifact.get("key_steps", []), start=1):
        step_number = step.get("step_number", index)
        title = step.get("title", "")
        instruction = step.get("instruction", "")
        notes = step.get("notes", "")
        text = f"Step {step_number}: {title}\n{instruction}".strip()
        if notes:
            text = f"{text}\nNotes: {notes}".strip()
        if text:
            sections.append(("key_step", index, text))

    for index, faq in enumerate(artifact.get("faq_items", []), start=1):
        question = faq.get("question", "")
        answer = faq.get("answer", "")
        if question or answer:
            sections.append(("faq", index, f"Q: {question}\nA: {answer}".strip()))

    for index, trigger in enumerate(artifact.get("escalation_triggers", []), start=1):
        category = trigger.get("category", "")
        trigger_text = trigger.get("trigger_text", "")
        action = trigger.get("action", "")
        severity = trigger.get("severity", "")
        text = (
            f"Category: {category}\n"
            f"Trigger: {trigger_text}\n"
            f"Action: {action}\n"
            f"Severity: {severity}"
        ).strip()
        if text:
            sections.append(("escalation_trigger", index, text))

    return sections


def split_text_into_chunks(text: str, target_chars: int, overlap_chars: int) -> List[str]:
    words = text.split()
    if not words:
        return []

    avg_word_len = max(4, int(sum(len(word) for word in words) / len(words)))
    overlap_words = max(1, overlap_chars // (avg_word_len + 1))

    chunks: List[str] = []
    start = 0
    while start < len(words):
        current_words: List[str] = []
        current_len = 0
        cursor = start

        while cursor < len(words):
            word = words[cursor]
            projected_len = current_len + (1 if current_words else 0) + len(word)
            if current_words and projected_len > target_chars:
                break
            current_words.append(word)
            current_len = projected_len
            cursor += 1

        if not current_words:
            current_words.append(words[cursor])
            cursor += 1

        chunks.append(" ".join(current_words))

        if cursor >= len(words):
            break

        start = max(start + 1, cursor - overlap_words)

    return chunks


def stable_chunk_id(doc_id: str, section_type: str, section_index: int, chunk_text: str) -> str:
    digest = hashlib.sha256(
        f"{doc_id}|{section_type}|{section_index}|{chunk_text}".encode("utf-8")
    ).hexdigest()[:12]
    return f"{doc_id}-chunk-{digest}"


def artifact_to_chunks(artifact: Dict[str, Any], source_key: str) -> List[Dict[str, Any]]:
    doc_id = normalize_doc_id(source_key)
    topic = artifact.get("topic")
    version = artifact.get("version")
    approval_status = str(artifact.get("approval_status") or DEFAULT_APPROVAL_STATUS).strip().lower()
    prohibited_topics = artifact.get("prohibited_topics_detected", [])
    sections = build_sections(artifact)

    chunk_docs: List[Dict[str, Any]] = []

    for section_type, section_index, section_text in sections:
        section_chunks = split_text_into_chunks(
            section_text,
            target_chars=CHUNK_TARGET_CHARS,
            overlap_chars=CHUNK_OVERLAP_CHARS,
        )

        total_chunks = len(section_chunks)
        for chunk_index, chunk_text in enumerate(section_chunks, start=1):
            chunk_id = stable_chunk_id(doc_id, section_type, section_index, chunk_text)
            chunk_docs.append(
                {
                    "id": chunk_id,
                    "doc_id": doc_id,
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "metadata": {
                        "source_key": source_key,
                        "topic": topic,
                        "version": version,
                        "approval_status": approval_status,
                        "section_type": section_type,
                        "section_index": section_index,
                        "chunk_index": chunk_index,
                        "total_chunks_in_section": total_chunks,
                        "prohibited_topics_detected": prohibited_topics,
                    },
                }
            )

    return chunk_docs


def load_artifact_from_s3(bucket: str, key: str) -> Dict[str, Any]:
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=bucket, Key=key)
    payload = response["Body"].read().decode("utf-8")
    return json.loads(payload)


def _normalized_opensearch_endpoint() -> str:
    endpoint = OPENSEARCH_ENDPOINT.strip()
    if not endpoint:
        return ""
    if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
        endpoint = f"https://{endpoint}"
    return endpoint.rstrip("/")


def _signed_aoss_request(method: str, path: str, payload: Any = None, content_type: str = "application/json"):
    endpoint = _normalized_opensearch_endpoint()
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
        headers={"Content-Type": content_type},
    )
    SigV4Auth(credentials, "aoss", OPENSEARCH_REGION).add_auth(aws_request)
    prepared = aws_request.prepare()

    response = HTTP.request(
        method=method,
        url=url,
        body=body,
        headers=dict(prepared.headers.items()),
        retries=False,
    )
    return response


def _ensure_index_mapping(vector_dimension: int) -> str:
    head_response = _signed_aoss_request("HEAD", f"/{OPENSEARCH_INDEX}", payload=None)
    if head_response.status == 200:
        return "exists"
    if head_response.status != 404:
        raise RuntimeError(
            f"Unable to check index state for '{OPENSEARCH_INDEX}': status={head_response.status}"
        )

    mapping_payload = {
        "settings": {"index": {"knn": True}},
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "doc_id": {"type": "keyword"},
                "chunk_id": {"type": "keyword"},
                "text": {"type": "text"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": vector_dimension,
                    "method": {"name": "hnsw", "engine": "faiss", "space_type": "cosinesimil"},
                },
                "metadata": {
                    "properties": {
                        "source_key": {"type": "keyword"},
                        "topic": {"type": "keyword"},
                        "version": {"type": "keyword"},
                        "approval_status": {"type": "keyword"},
                        "section_type": {"type": "keyword"},
                        "section_index": {"type": "integer"},
                        "chunk_index": {"type": "integer"},
                        "total_chunks_in_section": {"type": "integer"},
                        "prohibited_topics_detected": {"type": "keyword"},
                    }
                },
            }
        },
    }

    create_response = _signed_aoss_request("PUT", f"/{OPENSEARCH_INDEX}", payload=mapping_payload)
    if create_response.status not in (200, 201):
        raise RuntimeError(
            f"Index create failed for '{OPENSEARCH_INDEX}': status={create_response.status}, body={create_response.data.decode('utf-8', errors='ignore')}"
        )
    return "created"


def _embed_text(text: str) -> List[float]:
    bedrock_client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
    try:
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_EMBED_MODEL,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"inputText": text}),
        )
    except ClientError as exc:
        raise RuntimeError(f"Bedrock embedding call failed: {exc}") from exc

    payload = json.loads(response["body"].read())
    return payload.get("embedding", [])


def _embed_chunk_documents(chunk_documents: List[Dict[str, Any]]) -> int:
    embedded = 0
    for chunk_doc in chunk_documents:
        embedding = _embed_text(chunk_doc["text"])
        if not embedding:
            raise RuntimeError(f"Empty embedding returned for chunk_id={chunk_doc['chunk_id']}")
        chunk_doc["embedding"] = embedding
        embedded += 1
    return embedded


def _bulk_upsert_documents(chunk_documents: List[Dict[str, Any]]) -> int:
    lines: List[str] = []
    for chunk_doc in chunk_documents:
        lines.append(json.dumps({"index": {"_index": OPENSEARCH_INDEX, "_id": chunk_doc["id"]}}))
        lines.append(json.dumps(chunk_doc))
    payload = "\n".join(lines) + "\n"

    response = _signed_aoss_request(
        "POST",
        f"/{OPENSEARCH_INDEX}/_bulk",
        payload=payload,
        content_type="application/x-ndjson",
    )
    if response.status not in (200, 201):
        raise RuntimeError(
            f"Bulk upsert failed: status={response.status}, body={response.data.decode('utf-8', errors='ignore')}"
        )

    body = json.loads(response.data.decode("utf-8"))
    if body.get("errors"):
        raise RuntimeError(f"Bulk upsert returned item errors: {json.dumps(body)[:1000]}")
    return len(chunk_documents)


def handler(event, context):
    records = event.get("Records", [])
    chunk_documents: List[Dict[str, Any]] = []
    processed_sources: List[str] = []

    if records:
        for record in records:
            s3_info = record.get("s3", {})
            bucket = s3_info.get("bucket", {}).get("name")
            key = s3_info.get("object", {}).get("key")
            if not bucket or not key:
                continue

            artifact = load_artifact_from_s3(bucket, key)
            source_key = f"s3://{bucket}/{key}"
            chunk_documents.extend(artifact_to_chunks(artifact, source_key))
            processed_sources.append(source_key)
    elif "artifact" in event:
        source_key = event.get("source_key", "inline-artifact.json")
        chunk_documents = artifact_to_chunks(event["artifact"], source_key)
        processed_sources.append(source_key)

    result = {
        "status": "ok",
        "processed_sources": processed_sources,
        "chunk_count": len(chunk_documents),
        "embedded_count": 0,
        "upserted_count": 0,
        "index_status": "not_attempted",
        "chunking_config": {
            "target_chars": CHUNK_TARGET_CHARS,
            "overlap_chars": CHUNK_OVERLAP_CHARS,
        },
        "chunks": chunk_documents,
        "next_step": "embed_and_upsert_pending",
    }

    if not chunk_documents:
        result["next_step"] = "no_chunks"
        print(json.dumps({"summary": {k: v for k, v in result.items() if k != "chunks"}}))
        return result

    if not ENABLE_EMBED_UPSERT:
        result["next_step"] = "embed_upsert_disabled"
        print(json.dumps({"summary": {k: v for k, v in result.items() if k != "chunks"}}))
        return result

    if not _normalized_opensearch_endpoint():
        result["next_step"] = "missing_opensearch_endpoint"
        print(json.dumps({"summary": {k: v for k, v in result.items() if k != "chunks"}}))
        return result

    embedded_count = _embed_chunk_documents(chunk_documents)
    vector_dimension = len(chunk_documents[0].get("embedding") or []) or OPENSEARCH_VECTOR_DIMENSION
    index_status = _ensure_index_mapping(vector_dimension)
    upserted_count = _bulk_upsert_documents(chunk_documents)

    result["embedded_count"] = embedded_count
    result["upserted_count"] = upserted_count
    result["index_status"] = index_status
    result["next_step"] = "ingest_completed"

    print(json.dumps({"summary": {k: v for k, v in result.items() if k != "chunks"}}))
    return result
