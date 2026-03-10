# AWS Support Case Note: Persistent OpenSearch Serverless 403 from Lambda

## Executive Summary
Production query Lambda requests to OpenSearch Serverless are consistently failing with `403 Forbidden` despite validated IAM permissions, matching runtime principal, active collection, and verified data/network/encryption policies. We executed broad and least-privilege policy tests, identity diagnostics, and propagation waits; all continued to return `403`.

## Environment
- Account: 905592002429
- Region: us-west-2
- Lambda: queryLambda-a72bcf3
- Lambda execution role: arn:aws:iam::905592002429:role/ragLambdaRole-7f504bf
- AOSS collection: mortgage-lo-rag-dev-rag (id: ew9a73rn6larukyw056c)
- AOSS endpoint: https://ew9a73rn6larukyw056c.us-west-2.aoss.amazonaws.com
- AOSS index: artifacts
- Data policy: mortgage-lo-rag-dev-access
- Network policy: mortgage-lo-rag-dev-net
- Encryption policy: mortgage-lo-rag-dev-enc

## Timeline (PT)
| Time (approx) | Action | Result |
|---|---|---|
| 12:10-12:30 | Validated/updated AOSS policies and collection state | Collection remained ACTIVE; policy updates accepted |
| 12:30 | Applied temporary broad AOSS data policy (`collection/*`, `index/*/*`, `aoss:*`) for Lambda principal | Policy update successful; no behavior change |
| 12:33+ | Waited for propagation and re-tested Lambda invoke | Still `403 Forbidden` |
| 20:44 | Added one-time runtime identity diagnostic in Lambda and invoked | Runtime principal confirmed as assumed-role/ragLambdaRole-7f504bf; still `403` |
| 21:10 | Removed diagnostic code and redeployed rollback package | Lambda restored; issue persists |
| 21:xx | Applied AWS-recommended explicit resource/permission tweaks (incl. DescribeCollectionItems, explicit index path) and retested | Still `403 Forbidden` |

## Evidence Table
| Category | Evidence | Status |
|---|---|---|
| Runtime identity | Logged from Lambda: `arn:aws:sts::905592002429:assumed-role/ragLambdaRole-7f504bf/queryLambda-a72bcf3` | Confirmed |
| Endpoint/region/index at runtime | `https://ew9a73rn6larukyw056c.us-west-2.aoss.amazonaws.com`, `us-west-2`, `artifacts` | Confirmed |
| IAM role policy attached | `arn:aws:iam::905592002429:policy/ragLambdaPolicy-844f314` attached to role | Confirmed |
| IAM permission boundary | Not set on role | Confirmed |
| IAM simulator | `aoss:APIAccessAll` evaluated Allowed for role | Confirmed |
| SCP | Only FullAWSAccess applied; no explicit deny identified | Confirmed |
| AOSS data policy (least privilege) | Principal exact match + collection/index rules configured | Confirmed |
| AOSS data policy (broad diagnostic) | `collection/*`, `index/*/*`, `aoss:*` tested | Confirmed, still 403 |
| AOSS network policy | `AllowFromPublic: true` for target collection | Confirmed |
| AOSS encryption policy | `AWSOwnedKey: true`, scoped to target collection | Confirmed |
| Collection state | `ACTIVE` (VECTORSEARCH) | Confirmed |
| Functional result | Lambda invoke consistently fails on AOSS search with 403 | Reproducible |

## Latest Correlation IDs
| Source | ID |
|---|---|
| Lambda requestId | b56a77d9-1367-411f-98d2-bcb1785806a5 |
| AOSS request-id | 6da9470e-c480-9935-b3e0-e41d42b84844 |

Additional recent pair:
- Lambda requestId: dd4f0d8f-2678-445a-a723-8c70671e2424
- AOSS request-id: 833997d4-ee60-9cb0-b5ba-fe42f8e09935

## Requested AWS Action
Please escalate to OpenSearch Serverless service engineering and provide internal authorization trace/decision details for the request IDs above, including the exact deny source in the authorization pipeline and concrete remediation steps.

## Reproduction Command Used
```powershell
Set-Content -Path payload.json -Value '{"question":"What is escrow?","top_k":3,"metadata_filter":{"approval_status":"pending"}}' -NoNewline
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" lambda invoke --function-name queryLambda-a72bcf3 --region us-west-2 --profile mort-dev --cli-binary-format raw-in-base64-out --payload fileb://payload.json out.json
Get-Content out.json
```

Observed error excerpt:
```json
{"errorMessage":"OpenSearch search failed: status=403, body={\"status\":403,...\"type\":\"Forbidden\"}"}
```