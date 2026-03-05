import json
import re
import pulumi
import pulumi_aws as aws

config = pulumi.Config()
project = pulumi.get_project()
stack = pulumi.get_stack()

raw_prefix = config.get("name") or f"{project}-{stack}"
safe_prefix = re.sub(r"[^a-z0-9-]", "-", raw_prefix.lower())

bucket_name = f"{safe_prefix}-artifacts"[:63].strip("-")
collection_name = f"{safe_prefix[:20]}-rag".strip("-")
index_name = "artifacts"

artifacts_bucket = aws.s3.Bucket(
    "artifactsBucket",
    bucket=bucket_name,
    force_destroy=True,
)

collection = aws.opensearchserverless.Collection(
    "ragCollection",
    name=collection_name,
    type="VECTORSEARCH",
)

encryption_policy = aws.opensearchserverless.SecurityPolicy(
    "ragEncryptionPolicy",
    type="encryption",
    policy=json.dumps(
        {
            "Rules": [
                {
                    "ResourceType": "collection",
                    "Resource": [f"collection/{collection_name}"],
                }
            ],
            "AWSOwnedKey": True,
        }
    ),
)

network_policy = aws.opensearchserverless.SecurityPolicy(
    "ragNetworkPolicy",
    type="network",
    policy=json.dumps(
        [
            {
                "Rules": [
                    {
                        "ResourceType": "collection",
                        "Resource": [f"collection/{collection_name}"],
                    },
                    {
                        "ResourceType": "dashboard",
                        "Resource": [f"collection/{collection_name}"],
                    },
                ],
                "AllowFromPublic": True,
            }
        ]
    ),
)

lambda_role = aws.iam.Role(
    "ragLambdaRole",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Effect": "Allow",
                }
            ],
        }
    ),
)

lambda_policy = aws.iam.Policy(
    "ragLambdaPolicy",
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    "Resource": "*",
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:GetObject", "s3:ListBucket"],
                    "Resource": [
                        artifacts_bucket.arn,
                        pulumi.Output.concat(artifacts_bucket.arn, "/*"),
                    ],
                },
                {
                    "Effect": "Allow",
                    "Action": ["bedrock:InvokeModel"],
                    "Resource": "*",
                },
                {
                    "Effect": "Allow",
                    "Action": ["aoss:APIAccessAll"],
                    "Resource": "*",
                },
            ],
        }
    ),
)

aws.iam.RolePolicyAttachment(
    "ragLambdaPolicyAttachment",
    role=lambda_role.name,
    policy_arn=lambda_policy.arn,
)

access_policy = aws.opensearchserverless.AccessPolicy(
    "ragAccessPolicy",
    type="data",
    policy=pulumi.Output.all(lambda_role.arn).apply(
        lambda args: json.dumps(
            [
                {
                    "Rules": [
                        {
                            "ResourceType": "collection",
                            "Resource": [f"collection/{collection_name}"],
                        },
                        {
                            "ResourceType": "index",
                            "Resource": [f"index/{collection_name}/*"],
                        },
                    ],
                    "Principal": [args[0]],
                }
            ]
        )
    ),
)

lambda_env = {
    "ARTIFACTS_BUCKET": artifacts_bucket.bucket,
    "OPENSEARCH_COLLECTION": collection.name,
    "OPENSEARCH_INDEX": index_name,
    "BEDROCK_EMBED_MODEL": "amazon.titan-embed-text-v2:0",
}

ingest_lambda = aws.lambda_.Function(
    "ingestLambda",
    role=lambda_role.arn,
    runtime="python3.11",
    handler="handler.handler",
    code=pulumi.FileArchive("./lambdas/ingest"),
    environment=aws.lambda_.FunctionEnvironmentArgs(variables=lambda_env),
    timeout=60,
)

query_lambda = aws.lambda_.Function(
    "queryLambda",
    role=lambda_role.arn,
    runtime="python3.11",
    handler="handler.handler",
    code=pulumi.FileArchive("./lambdas/query"),
    environment=aws.lambda_.FunctionEnvironmentArgs(variables=lambda_env),
    timeout=30,
)

aws.lambda_.Permission(
    "ingestBucketPermission",
    action="lambda:InvokeFunction",
    function=ingest_lambda.name,
    principal="s3.amazonaws.com",
    source_arn=artifacts_bucket.arn,
)

aws.s3.BucketNotification(
    "artifactsBucketNotification",
    bucket=artifacts_bucket.id,
    lambda_functions=[
        aws.s3.BucketNotificationLambdaFunctionArgs(
            lambda_function_arn=ingest_lambda.arn,
            events=["s3:ObjectCreated:*"],
        )
    ],
)

pulumi.export("artifacts_bucket", artifacts_bucket.bucket)
pulumi.export("opensearch_collection", collection.name)
pulumi.export("query_lambda_name", query_lambda.name)
