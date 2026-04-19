# Pulumi (AWS)

This Pulumi project provisions a serverless RAG MVP:
- S3 bucket for artifacts
- OpenSearch Serverless vector collection
- Lambda ingest and query functions

## Usage

1) Configure AWS credentials and region (us-west-2).
2) From this folder, run:

pulumi stack init dev
pulumi config set aws:region us-west-2
pulumi up

## Daily Cost-Control Automation (Session Up/Down)

Use the automation script to create a repeatable start/end-of-day flow.

From repo root:

- Start session (provision resources):

	`python infra/automation.py up --stack dev --region us-west-2 --skip-preview`

- Check current stack outputs/status:

	`python infra/automation.py status --stack dev`

- End session (destroy resources):

	`python infra/automation.py down --stack dev --skip-preview`

Notes:
- `up` will auto-create the stack if missing.
- `down` requires the stack to already exist.
- Keep your Pulumi backend/state configured as normal before running these commands.

