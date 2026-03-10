# Documentation Index

Owner: Scott Pigeon (sjpigeon)  
Last Updated (UTC): 2026-03-10  
Status: active

This folder is the long-term memory layer for the project. Use it to quickly recover context after long gaps, branch cleanup, or handoffs.

## Start Here
- [Project Memory](project-memory.md)
- [Architecture](architecture.md)
- [Traceability Matrix](traceability-matrix.md)

## Decision Records (ADR)
- [ADR Index](adr/README.md)
- [ADR Template](adr/0000-template.md)

## Runbooks
- [Runbook Index](runbooks/README.md)
- [Deploy and Rollback](runbooks/deploy-and-rollback.md)
- [Incident Response](runbooks/incident-response.md)

## Contracts
- [Contracts Index](contracts/README.md)
- [Query API Contract](contracts/query-api.md)
- [Ingest Contract](contracts/ingest-contract.md)

## Existing Reference Docs
- [Chunking Strategy](chunking_strategy.md)
- [AWS Support Case Note (AOSS 403)](aws-support-case-note-aoss-403.md)

## Documentation Standards
For all docs in this folder, include:
- **Owner**
- **Last Updated (UTC)**
- **Status** (`draft`, `active`, `deprecated`)
- **Source of truth / related code paths**

## Daily Checklist (10 minutes)
Trigger: At session start, message Copilot with **"Start daily ritual"**.

1. Open [Project Memory](project-memory.md) and confirm current mission, blockers, and active sprint intent.
2. Open [Traceability Matrix](traceability-matrix.md) and set/update status for the issue(s) you will touch today.
3. Before coding, confirm expected request/response behavior in [Query API Contract](contracts/query-api.md) and ingest expectations in [Ingest Contract](contracts/ingest-contract.md).
4. If a design or policy decision changes, create/update an ADR from [ADR Template](adr/0000-template.md) and list it in [ADR Index](adr/README.md).
5. At PR open/merge, update traceability acceptance evidence and refresh **Last Updated (UTC)** on changed docs.

## Weekly Checklist (30 minutes)
1. Reconcile [Traceability Matrix](traceability-matrix.md) against merged/open issues and PRs.
2. Refresh [Project Memory](project-memory.md) sections: done, open, blockers, and next sprint intent.
3. Review [Deploy and Rollback](runbooks/deploy-and-rollback.md) and [Incident Response](runbooks/incident-response.md) with any new operational learnings.
4. Check for contract drift in [Contracts Index](contracts/README.md) and bump contract versions when interface behavior changes.
5. Ensure at least one ADR exists for any non-trivial architectural or compliance tradeoff made during the week.
