# Content Chunking Strategy (Issue #57)

This document defines the canonical chunking contract for ingestion prior to embedding/indexing.

## Rules

- Target chunk size: `900` characters (`CHUNK_TARGET_CHARS`)
- Overlap size: `120` characters (`CHUNK_OVERLAP_CHARS`)
- Chunking method: deterministic word-window chunking per section
- Section order:
  1. `summary`
  2. `key_steps` (ordered by input)
  3. `faq_items` (ordered by input)
  4. `escalation_triggers` (ordered by input)

## Stable identity mapping

- `doc_id`: normalized from artifact source key filename (lowercase kebab-case)
- `chunk_id`: `"{doc_id}-chunk-{sha256(doc_id|section_type|section_index|chunk_text)[:12]}"`
- Chunk IDs are deterministic for unchanged content and section structure.

## Per-chunk metadata contract

Each chunk document includes:

- `id` (same as `chunk_id`)
- `doc_id`
- `chunk_id`
- `text`
- `metadata`:
  - `source_key`
  - `topic`
  - `version`
  - `section_type`
  - `section_index`
  - `chunk_index`
  - `total_chunks_in_section`
  - `prohibited_topics_detected`

## Notes

- This issue formalizes `load JSON → chunk` + mapping/metadata preservation.
- Embedding and OpenSearch upsert are subsequent steps in ingest completion.
