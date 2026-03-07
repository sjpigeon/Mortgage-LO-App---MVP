import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from infra.lambdas.query.handler import handler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run retrieval baseline evaluation against query Lambda handler.")
    parser.add_argument(
        "--eval-file",
        default="tests/rag/eval_questions_seed_v1.json",
        help="Path to eval questions JSON file",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Top-k retrieval depth for each eval question")
    parser.add_argument(
        "--output",
        default="artifacts/eval/retrieval_baseline.json",
        help="Path to write evaluation summary JSON",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop evaluation immediately if a handler invocation fails",
    )
    return parser.parse_args()


def load_eval_questions(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("Eval file must contain a JSON array")
    return payload


def topic_hit(results: List[Dict[str, Any]], expected_topic: str) -> Dict[str, bool]:
    normalized_expected = (expected_topic or "").strip().lower()
    observed_topics = [
        (item.get("metadata", {}).get("topic") or "").strip().lower()
        for item in results
    ]
    top1_hit = bool(observed_topics) and observed_topics[0] == normalized_expected
    topk_hit = normalized_expected in observed_topics
    return {"top1_hit": top1_hit, "topk_hit": topk_hit}


def invoke_query(question: str, top_k: int) -> Dict[str, Any]:
    response = handler({"question": question, "top_k": top_k}, None)
    status_code = response.get("statusCode", 500)
    body = response.get("body")
    parsed = json.loads(body) if isinstance(body, str) else body
    return {"status_code": status_code, "body": parsed}


def main() -> int:
    args = parse_args()
    eval_path = Path(args.eval_file)
    output_path = Path(args.output)

    questions = load_eval_questions(eval_path)

    rows: List[Dict[str, Any]] = []
    total = 0
    top1_hits = 0
    topk_hits = 0
    error_count = 0

    for item in questions:
        total += 1
        qid = item.get("id")
        question = item.get("question", "")
        expected_topic = item.get("expected_topic", "")

        try:
            result = invoke_query(question, args.top_k)
        except Exception as exc:  # noqa: BLE001
            error_count += 1
            rows.append(
                {
                    "id": qid,
                    "question": question,
                    "expected_topic": expected_topic,
                    "status": "error",
                    "error": str(exc),
                }
            )
            if args.stop_on_error:
                break
            continue

        status_code = result["status_code"]
        body = result["body"] if isinstance(result["body"], dict) else {}
        retrieval_count = body.get("retrieval_count", 0)
        results = body.get("results", []) if isinstance(body.get("results"), list) else []
        confidence = body.get("confidence", {})

        if status_code != 200:
            error_count += 1
            rows.append(
                {
                    "id": qid,
                    "question": question,
                    "expected_topic": expected_topic,
                    "status": "error",
                    "status_code": status_code,
                    "response": body,
                }
            )
            if args.stop_on_error:
                break
            continue

        hits = topic_hit(results, expected_topic)
        if hits["top1_hit"]:
            top1_hits += 1
        if hits["topk_hit"]:
            topk_hits += 1

        rows.append(
            {
                "id": qid,
                "question": question,
                "expected_topic": expected_topic,
                "status": "ok",
                "retrieval_count": retrieval_count,
                "top1_hit": hits["top1_hit"],
                "topk_hit": hits["topk_hit"],
                "confidence": confidence,
            }
        )

    evaluated = max(1, total - error_count)
    summary = {
        "eval_file": str(eval_path),
        "top_k": args.top_k,
        "total_questions": total,
        "errors": error_count,
        "top1_hits": top1_hits,
        "topk_hits": topk_hits,
        "top1_hit_rate": top1_hits / evaluated,
        "topk_hit_rate": topk_hits / evaluated,
    }

    output = {"summary": summary, "results": rows}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"Saved baseline report to: {output_path}")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
