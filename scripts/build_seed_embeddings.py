import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError


DEFAULT_MODEL_ID = "amazon.titan-embed-text-v2:0"
DEFAULT_REGION = "us-west-2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build embeddings for seed artifacts via Bedrock."
    )
    parser.add_argument(
        "--input-dir",
        default="artifacts/seed_v1",
        help="Directory of seed artifacts",
    )
    parser.add_argument(
        "--output-dir",
        default="artifacts/seed_v1_embeddings",
        help="Directory to write embedded artifacts",
    )
    parser.add_argument(
        "--region",
        default=os.getenv("BEDROCK_REGION", DEFAULT_REGION),
        help="AWS region (or BEDROCK_REGION)",
    )
    parser.add_argument(
        "--model-id",
        default=os.getenv("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID),
        help="Bedrock model id (or BEDROCK_MODEL_ID)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild embeddings even if source version/content/model is unchanged",
    )
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def build_embedding_text(artifact: Dict[str, Any]) -> str:
    parts: List[str] = []
    topic = artifact.get("topic", "")
    summary = artifact.get("summary", "")
    if topic:
        parts.append(f"Topic: {topic}")
    if summary:
        parts.append(f"Summary: {summary}")

    key_steps = artifact.get("key_steps", [])
    if key_steps:
        parts.append("Key steps:")
        for step in sorted(key_steps, key=lambda item: item.get("step_number", 0)):
            title = step.get("title", "")
            instruction = step.get("instruction", "")
            if title or instruction:
                parts.append(f"- {title}: {instruction}".strip())

    faq_items = artifact.get("faq_items", [])
    if faq_items:
        parts.append("FAQ:")
        for item in faq_items:
            question = item.get("question", "")
            answer = item.get("answer", "")
            if question or answer:
                parts.append(f"Q: {question}")
                parts.append(f"A: {answer}")

    escalation = artifact.get("escalation_triggers", [])
    if escalation:
        parts.append("Escalation triggers:")
        for item in escalation:
            category = item.get("category", "")
            trigger = item.get("trigger_text", "")
            action = item.get("action", "")
            if category or trigger or action:
                parts.append(
                    f"- {category} | {trigger} | action: {action}".strip()
                )

    return "\n".join([p for p in parts if p])


def embed_text(client, model_id: str, text: str) -> List[float]:
    payload = {"inputText": text}
    response = client.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload),
    )
    data = json.loads(response["body"].read())
    return data.get("embedding", [])


def compute_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def is_embedding_current(
    existing_output: Dict[str, Any],
    *,
    content_hash: str,
    source_version: Any,
    model_id: str,
) -> bool:
    embedding = existing_output.get("embedding")
    return (
        isinstance(embedding, list)
        and len(embedding) > 0
        and existing_output.get("embedding_content_hash") == content_hash
        and existing_output.get("embedding_source_version") == source_version
        and existing_output.get("embedding_model_id") == model_id
    )


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not input_dir.exists():
        print(f"Input directory not found: {input_dir}", file=sys.stderr)
        return 1

    client = boto3.client("bedrock-runtime", region_name=args.region)

    artifacts = sorted(input_dir.glob("*.json"))
    if not artifacts:
        print(f"No artifacts found in: {input_dir}")
        return 1

    embedded_count = 0
    skipped_count = 0
    failed_count = 0

    for artifact_path in artifacts:
        artifact = load_json(artifact_path)
        text = build_embedding_text(artifact)
        if not text:
            print(f"Skipping empty artifact: {artifact_path.name}")
            skipped_count += 1
            continue

        content_hash = compute_content_hash(text)
        source_version = artifact.get("version")
        output_path = output_dir / artifact_path.name

        if not args.force and output_path.exists():
            existing_output = load_json(output_path)
            if is_embedding_current(
                existing_output,
                content_hash=content_hash,
                source_version=source_version,
                model_id=args.model_id,
            ):
                print(f"Skipping unchanged artifact: {artifact_path.name}")
                skipped_count += 1
                continue

        try:
            embedding = embed_text(client, args.model_id, text)
        except ClientError as exc:
            print(f"Embedding failed for {artifact_path.name}: {exc}", file=sys.stderr)
            failed_count += 1
            print(
                f"Summary: embedded={embedded_count}, skipped={skipped_count}, failed={failed_count}",
                file=sys.stderr,
            )
            return 1

        embedded = dict(artifact)
        embedded["embedding"] = embedding
        embedded["embedding_model_id"] = args.model_id
        embedded["embedding_content_hash"] = content_hash
        embedded["embedding_generated_at"] = utc_timestamp()
        embedded["embedding_source_version"] = source_version

        write_json(output_path, embedded)
        print(f"Embedded {artifact_path.name} -> {output_path}")
        embedded_count += 1

    print(f"Summary: embedded={embedded_count}, skipped={skipped_count}, failed={failed_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
