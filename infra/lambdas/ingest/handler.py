import hashlib
import json
import os
import re
from typing import Any, Dict, List, Tuple

import boto3


CHUNK_TARGET_CHARS = int(os.getenv("CHUNK_TARGET_CHARS", "900"))
CHUNK_OVERLAP_CHARS = int(os.getenv("CHUNK_OVERLAP_CHARS", "120"))


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
        "chunking_config": {
            "target_chars": CHUNK_TARGET_CHARS,
            "overlap_chars": CHUNK_OVERLAP_CHARS,
        },
        "chunks": chunk_documents,
        "next_step": "embed_and_upsert_pending",
    }

    print(json.dumps({"summary": {k: v for k, v in result.items() if k != "chunks"}}))
    return result
