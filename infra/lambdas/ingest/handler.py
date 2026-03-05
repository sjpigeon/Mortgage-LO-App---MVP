def handler(event, context):
    # TODO: Parse S3 event, chunk content, embed with Bedrock, index into OpenSearch.
    return {"status": "ok", "event": event}
