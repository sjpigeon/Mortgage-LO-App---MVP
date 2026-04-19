from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


INFRA_DIR = Path(__file__).resolve().parent


def run_cmd(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=INFRA_DIR,
        text=True,
        capture_output=True,
        check=check,
    )


def print_result(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)


def ensure_stack(stack: str, create_if_missing: bool) -> None:
    selected = run_cmd(["pulumi", "stack", "select", stack, "--non-interactive"], check=False)
    if selected.returncode == 0:
        return

    if not create_if_missing:
        print_result(selected)
        raise RuntimeError(
            f"Unable to select stack '{stack}'. Create it first or run with create enabled."
        )

    initialized = run_cmd(["pulumi", "stack", "init", stack, "--non-interactive"], check=False)
    if initialized.returncode != 0:
        print_result(selected)
        print_result(initialized)
        raise RuntimeError(f"Unable to initialize stack '{stack}'.")


def set_region(region: str) -> None:
    updated = run_cmd(
        ["pulumi", "config", "set", "aws:region", region, "--non-interactive"],
        check=False,
    )
    if updated.returncode != 0:
        print_result(updated)
        raise RuntimeError(f"Unable to set aws:region to '{region}'.")


def cmd_up(stack: str, region: str, skip_preview: bool) -> None:
    ensure_stack(stack=stack, create_if_missing=True)
    set_region(region)

    args = ["pulumi", "up", "--yes", "--non-interactive"]
    if skip_preview:
        args.append("--skip-preview")

    result = run_cmd(args, check=False)
    print_result(result)
    if result.returncode != 0:
        raise RuntimeError("Pulumi up failed.")


def cmd_down(stack: str, skip_preview: bool) -> None:
    ensure_stack(stack=stack, create_if_missing=False)

    args = ["pulumi", "destroy", "--yes", "--non-interactive"]
    if skip_preview:
        args.append("--skip-preview")

    result = run_cmd(args, check=False)
    print_result(result)
    if result.returncode != 0:
        raise RuntimeError("Pulumi destroy failed.")


def cmd_status(stack: str) -> None:
    ensure_stack(stack=stack, create_if_missing=False)
    result = run_cmd(["pulumi", "stack", "output", "--json"], check=False)
    print_result(result)
    if result.returncode != 0:
        raise RuntimeError("Unable to retrieve Pulumi stack outputs.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Session lifecycle automation for Pulumi infrastructure (up/down/status)."
    )
    parser.add_argument("action", choices=["up", "down", "status"])
    parser.add_argument("--stack", default="dev", help="Pulumi stack name (default: dev)")
    parser.add_argument(
        "--region",
        default="us-west-2",
        help="AWS region used when running 'up' (default: us-west-2)",
    )
    parser.add_argument(
        "--skip-preview",
        action="store_true",
        help="Skip preview for up/down operations to reduce runtime.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.action == "up":
            cmd_up(stack=args.stack, region=args.region, skip_preview=args.skip_preview)
        elif args.action == "down":
            cmd_down(stack=args.stack, skip_preview=args.skip_preview)
        elif args.action == "status":
            cmd_status(stack=args.stack)
        else:
            parser.error(f"Unsupported action: {args.action}")
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
