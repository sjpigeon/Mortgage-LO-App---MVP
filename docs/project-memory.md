# Project Memory

Owner: Scott Pigeon (sjpigeon)  
Last Updated (UTC): 2026-03-10  
Status: active

How to Trigger Ritual: At session start, message Copilot with **"Start daily ritual"** to run the daily checklist in `docs/README.md`.

## 1) Current Mission
- Build a compliance-first mortgage education assistant.
- Strictly avoid loan-origination behavior (rates, eligibility, underwriting decisions).

## 2) Current Phase
- Parent epic/feature: #21 (Constrained LLM Orchestration)
- Active branch expectation: `scott-dev`
- Environment: `us-west-2`

## 3) What Is Done
- Retrieval baseline and metadata-filter controls implemented.
- Mandatory approval/topic-boundary retrieval controls implemented.
- Retrieval audit envelope fields implemented.

## 4) What Is Open
- Prompt template/versioning
- Prompt injection-safe assembly
- Output post-processing validator
- Escalation integration
- Full inference trace completion

## 5) External Dependencies / Blockers
- AWS Support case for AOSS 403 (live verification blocker for issue #60 evidence collection).
- Case link and latest request IDs should be maintained here.

## 6) Invariants (Must Not Break)
- Retrieval must be deterministic and policy-constrained.
- User metadata filters cannot override mandatory guardrail filters.
- Every response path should be auditable.

## 7) Restart Checklist (After Long Gap)
1. Read [README](README.md), [architecture](architecture.md), and [traceability matrix](traceability-matrix.md).
2. Confirm open issues and PR status.
3. Validate local branch and environment.
4. Run targeted validations before edits.

## 8) Next 1-2 Sprint Intent
- Complete #63–#67 in small, mergeable PR slices.
- Keep #60 open until live verification evidence is attached.
