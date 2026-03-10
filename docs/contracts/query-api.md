# Query API Contract

Owner: Scott Pigeon (sjpigeon)  
Last Updated (UTC): 2026-03-10  
Status: active  
Version: v1

## Request
```json
{
  "question": "What is escrow?",
  "top_k": 5,
  "session_id": "optional-session-id",
  "metadata_filter": {
    "topic_slug": "understanding-escrow-accounts"
  }
}
```

## Response (success)
```json
{
  "status": "ok",
  "query_id": "...",
  "session_id": "...",
  "audit_version": "1.0",
  "metadata_filter": {},
  "mandatory_metadata_filter": {},
  "retrieval_count": 0,
  "result_ids": [],
  "result_versions": [],
  "result_audit_items": [],
  "confidence": {
    "score_max": null,
    "score_min": null,
    "score_avg": null,
    "confidence_band": "none"
  },
  "results": []
}
```

## Behavioral Guarantees
- Mandatory policy filters are always applied.
- Caller metadata filters are sanitized and cannot override guardrails.
- Response includes traceable retrieval audit fields.

## Error Contract
- `statusCode: 400` for malformed/invalid request input.
- Runtime dependency failures surface explicit error reason in logs.
