# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
"""Weekly planner CLI command."""

from __future__ import annotations

import argparse
import importlib
import re
import sys
import uuid
from collections.abc import Sequence

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_VALIDATION = 2

_WEEK_PATTERN = re.compile(r"^\d{4}-\d{2}$")


def register_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("weekly-planner", help="Run weekly planner")
    parser.add_argument("--week", required=True, help="ISO week in YYYY-WW format")
    parser.add_argument("--dry-run", action="store_true", help="Do not persist outputs")
    parser.add_argument("--corr-id", default=None, help="Correlation id")
    parser.add_argument("--max-work-days", type=int, default=6)
    parser.add_argument("--daily-capacity", type=int, default=2500)
    parser.set_defaults(handler=_run_weekly_planner)


def run(args: argparse.Namespace) -> int:
    handler = getattr(args, "handler", None)
    if handler is None:
        sys.stderr.write("error: missing weekly-planner command\n")
        return EXIT_VALIDATION
    return int(handler(args))


def _validate_args(args: argparse.Namespace) -> str | None:
    if not _WEEK_PATTERN.match(args.week):
        return "error: --week must be YYYY-WW"
    if not (1 <= int(args.max_work_days) <= 6):
        return "error: --max-work-days must be between 1 and 6"
    if not (2500 <= int(args.daily_capacity) <= 3000):
        return "error: --daily-capacity must be between 2500 and 3000"
    return None


def _run_weekly_planner(args: argparse.Namespace) -> int:
    error = _validate_args(args)
    if error:
        sys.stderr.write(f"{error}\n")
        return EXIT_VALIDATION

    corr_id = args.corr_id or str(uuid.uuid4())
    try:
        module = importlib.import_module("src.application.services.weekly_planner_service")
    except Exception:
        sys.stderr.write("TODO: src.application.services.weekly_planner_service missing\n")
        if args.dry_run:
            sys.stderr.write(f"graceful error: planner service unavailable for dry-run (corr_id={corr_id})\n")
        return EXIT_ERROR

    service = getattr(module, "service", None)
    if service is None:
        sys.stderr.write("error: weekly planner service entrypoint not found\n")
        return EXIT_ERROR

    result = service.run(
        week=args.week,
        dry_run=bool(args.dry_run),
        corr_id=corr_id,
        max_work_days=int(args.max_work_days),
        daily_capacity_donum=int(args.daily_capacity),
    )
    sys.stdout.write(f"{result}\n")
    return EXIT_SUCCESS


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="weekly-planner")
    register_subparser(parser.add_subparsers(dest="command"))
    parsed = parser.parse_args(argv)
    return run(parsed)
