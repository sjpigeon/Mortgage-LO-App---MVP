# Ingest Contract

Owner: Scott Pigeon (sjpigeon)  
Last Updated (UTC): 2026-03-10  
Status: active  
Version: v1

## Source Artifact Expectations
- JSON object with topic/summary/key_steps/faq_items/escalation_triggers/version.
- Optional approval/topic-boundary metadata fields.

## Chunk Document Shape
```json
{
  "id": "...",
  "doc_id": "...",
  "chunk_id": "...",
  "text": "...",
  "embedding": [],
  "metadata": {
    "source_key": "...",
    "topic": "...",
    "topic_slug": "...",
    "topic_boundary_scope": "education_only",
    "version": "...",
    "approval_status": "approved",
    "section_type": "...",
    "section_index": 1,
    "chunk_index": 1,
    "total_chunks_in_section": 3,
    "prohibited_topics_detected": [],
    "prohibited_topics_detected_count": 0
  }
}
```

## Behavioral Guarantees
- Deterministic chunk IDs for stable source/section/chunk text.
- Metadata normalization for `topic_slug` and boundary fields.
- Index mapping includes vector and metadata fields required by query filters.

## Failure Handling
- Invalid artifacts are counted and surfaced in run output.
- Embedding/upsert errors should fail fast with diagnostic context.
