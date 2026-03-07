# Mortgage-Loan-Officer-Knowledge-Delivery---MVP
MVP of system that provides mortgage info to new clients, stopping short of loan origination activities. 

## Build-time embeddings

Generate embeddings for seed artifacts during environment bring-up:

```bash
python scripts/build_seed_embeddings.py
```

Behavior:
- Re-embeds only artifacts whose source version/content hash/model id changed.
- Skips unchanged artifacts and prints an embedded/skipped/failed summary.
- Use `--force` to rebuild all embeddings.

Config via env vars:
- `BEDROCK_REGION` (default: us-west-2)
- `BEDROCK_MODEL_ID` (default: amazon.titan-embed-text-v2:0)

## Retrieval baseline eval

Run retrieval baseline scoring against the query handler using the seed eval set:

```bash
python scripts/eval_retrieval_baseline.py --top-k 5
```

Output report is written to `artifacts/eval/retrieval_baseline.json`.

Query API (Lambda handler) supports:
- `metadata_filter` (allowlisted metadata keys only)
- confidence summary in response (`score_max`, `score_min`, `score_avg`, `confidence_band`)
