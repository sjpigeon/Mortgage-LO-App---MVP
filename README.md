# Mortgage-Loan-Officer-Knowledge-Delivery---MVP
MVP of system that provides mortgage info to new clients, stopping short of loan origination activities. 

## Build-time embeddings

Generate embeddings for seed artifacts during environment bring-up:

```bash
python scripts/build_seed_embeddings.py
```

Config via env vars:
- `BEDROCK_REGION` (default: us-west-2)
- `BEDROCK_MODEL_ID` (default: amazon.titan-embed-text-v2:0)
