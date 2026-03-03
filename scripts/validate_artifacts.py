import argparse
import glob
import json
import sys
from pathlib import Path

import jsonschema


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=True)
    parser.add_argument("--glob", required=True)
    args = parser.parse_args()

    schema = load_json(Path(args.schema))
    validator = jsonschema.Draft202012Validator(schema)

    matches = sorted(glob.glob(args.glob, recursive=True))
    if not matches:
        print(f"No files matched: {args.glob}")
        return 1

    failed = 0
    for file_path in matches:
        data = load_json(Path(file_path))
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errors:
            failed += 1
            print(f"\nFAIL: {file_path}")
            for err in errors:
                path = ".".join([str(p) for p in err.path]) or "<root>"
                print(f"  - {path}: {err.message}")

    if failed:
        print(f"\nValidation failed for {failed} file(s).")
        return 1

    print(f"Validated {len(matches)} file(s) successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
