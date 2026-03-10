# Incident Response Runbook

Owner: Scott Pigeon (sjpigeon)  
Last Updated (UTC): 2026-03-10  
Status: active

## Trigger Conditions
- Persistent 4xx/5xx from critical dependencies
- Retrieval returns empty or policy-invalid outputs unexpectedly
- Guardrail or audit regressions

## Immediate Actions
1. Capture correlation IDs and exact timestamps.
2. Preserve request/response payloads (redact sensitive data).
3. Confirm recent deploys/changes.
4. Identify blast radius.

## Triage Checklist
- IAM/policy/network checks
- Endpoint/index/region checks
- Lambda runtime identity checks
- Recent code/config drift

## Communication
- Update related issue with executive summary and evidence.
- Document external support case links and ownership.

## Exit Criteria
- Root cause identified or external dependency ownership established.
- Mitigation/rollback executed.
- Follow-up action items logged.
