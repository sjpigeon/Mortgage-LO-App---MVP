# Deploy and Rollback Runbook

Owner: Scott Pigeon (sjpigeon)  
Last Updated (UTC): 2026-03-10  
Status: active

## Preconditions
- Correct AWS profile and region
- Clean git state on expected branch
- Required approvals/checks complete

## Deploy Steps
1. Pull latest from `main`.
2. Build/package deployment artifacts.
3. Apply infrastructure changes (if any).
4. Deploy Lambda updates.
5. Run post-deploy smoke checks.

## Verify
- Query path returns expected schema.
- Logs include expected trace fields.
- No policy bypass in metadata filters.

## Rollback
1. Re-deploy prior artifact/package.
2. Revert infra changes if required.
3. Re-run smoke checks.

## Escalation
- If deploy blocks production verification, open/update incident thread and issue references.
