# Traceability Matrix

Owner: Scott Pigeon (sjpigeon)  
Last Updated (UTC): 2026-03-10  
Status: active

Use this table to preserve decision and delivery context over time.

| Issue | Scope Summary | PR(s) | Key Files | Acceptance Evidence | Status |
|---|---|---|---|---|---|
| #60 | Approval-only retrieval filtering | #114 | `infra/lambdas/query/handler.py`, `infra/lambdas/ingest/handler.py` | compile pass, runtime trace, AWS blocker notes | partial (env blocker) |
| #61 | Topic-boundary enforcement | #115 | `infra/lambdas/query/handler.py`, `infra/lambdas/ingest/handler.py`, `tests/rag/topic_boundary_eval_seed_v1.json` | compile pass, fixture added | merged |
| #62 | Retrieval audit enrichment | #115 | `infra/lambdas/query/handler.py`, `tests/rag/retrieval_audit_eval_seed_v1.json` | compile pass, fixture added | merged |
| #63 | Versioned system prompt template | TBD | TBD | TBD | open |
| #64 | Prompt injection pipeline | TBD | TBD | TBD | open |
| #65 | Output validator | TBD | TBD | TBD | open |
| #66 | Escalation integration | TBD | TBD | TBD | open |
| #67 | LLM model/version logging | TBD | TBD | TBD | open |

## Notes
- Keep this file current at PR merge time.
- Prefer links to concrete files and acceptance artifacts.
