import argparse
import json
import sys

import boto3
from botocore.exceptions import ClientError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Invoke Titan Embeddings v2 via Bedrock.")
    parser.add_argument("text", help="Text to embed")
    parser.add_argument("--region", default="us-west-2", help="AWS region")
    parser.add_argument(
        "--model-id",
        default="amazon.titan-embed-text-v2:0",
        help="Bedrock model id",
    )
    parser.add_argument("--output", default="response.json", help="Output JSON file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client = boto3.client("bedrock-runtime", region_name=args.region)

    payload = {"inputText": args.text}
    try:
        response = client.invoke_model(
            modelId=args.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload),
        )
    except ClientError as exc:
        print(f"Bedrock invoke failed: {exc}", file=sys.stderr)
        return 1

    data = json.loads(response["body"].read())
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)

    embedding = data.get("embedding", [])
    print(f"Embedding length: {len(embedding)}")
    print(f"Saved response to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
