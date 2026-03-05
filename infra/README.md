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

