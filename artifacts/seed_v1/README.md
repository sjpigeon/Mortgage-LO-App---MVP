# Seed Artifacts (v1)

Add seed JSON artifacts in this folder.

Notes:
- Each file should validate against `schemas/extraction_artifact.schema.json`.
- Use consistent naming (e.g., `artifact-001.json`).
- Document any assumptions or edge cases per artifact.

Build-time embeddings:
- Run `python scripts/build_seed_embeddings.py` from repo root.
- Outputs embedded artifacts to `artifacts/seed_v1_embeddings`.
- Re-embeds only artifacts with changed source version/content hash/model id.
- Use `python scripts/build_seed_embeddings.py --force` to rebuild all embeddings.
