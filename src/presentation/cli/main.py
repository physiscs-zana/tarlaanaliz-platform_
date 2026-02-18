# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
"""Platform CLI main entrypoint."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from src.presentation.cli.commands import expert_management, migrate, run_weekly_planner, seed, subscription_management


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tarlaanaliz")
    subparsers = parser.add_subparsers(dest="top_command")
    expert_management.register_subparser(subparsers)
    migrate.register_subparser(subparsers)
    run_weekly_planner.register_subparser(subparsers)
    seed.register_subparser(subparsers)
    subscription_management.register_subparser(subparsers)
    return parser


def dispatch(args: argparse.Namespace) -> int:
    top_command = getattr(args, "top_command", None)
    if top_command == "expert":
        return expert_management.run(args)
    if top_command == "migrate":
        return migrate.run(args)
    if top_command == "weekly-planner":
        return run_weekly_planner.run(args)
    if top_command == "seed":
        return seed.run(args)
    if top_command == "subscription":
        return subscription_management.run(args)
    sys.stderr.write("error: unknown command\n")
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if getattr(args, "top_command", None) is None:
        parser.print_help()
        return 0
    return dispatch(args)


if __name__ == "__main__":
    raise SystemExit(main())
