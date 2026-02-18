# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
"""Seed data CLI commands."""

from __future__ import annotations

import argparse
import importlib
import sys
from collections.abc import Sequence

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_VALIDATION = 2


_CONFIRM_TOKEN = "I_UNDERSTAND"  # noqa: S105


def register_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("seed", help="Seed data commands")
    seed_sub = parser.add_subparsers(dest="seed_command")

    for name in ("seed-all", "seed-minimal"):
        cmd = seed_sub.add_parser(name, help=f"Run {name}")
        cmd.set_defaults(handler=_run_seed, seed_action=name)

    admin_cmd = seed_sub.add_parser("seed-admin", help="Run privileged admin seed")
    admin_cmd.add_argument("--force", action="store_true")
    admin_cmd.add_argument("--confirm", default="")
    admin_cmd.set_defaults(handler=_run_seed, seed_action="seed-admin")


def run(args: argparse.Namespace) -> int:
    handler = getattr(args, "handler", None)
    if handler is None:
        sys.stderr.write("error: missing seed subcommand\n")
        return EXIT_VALIDATION
    return int(handler(args))


def _run_seed(args: argparse.Namespace) -> int:
    action = str(args.seed_action)
    force = bool(getattr(args, "force", False))
    confirm = str(getattr(args, "confirm", ""))
    if action == "seed-admin" and not (force or confirm == _CONFIRM_TOKEN):
        sys.stderr.write("error: seed-admin requires --force or --confirm I_UNDERSTAND\n")
        return EXIT_VALIDATION

    try:
        module = importlib.import_module("src.application.services.seed_service")
    except Exception:
        sys.stderr.write("TODO: src.application.services.seed_service missing\n")
        return EXIT_ERROR

    service = getattr(module, "service", None)
    if service is None:
        sys.stderr.write("error: seed service entrypoint not found\n")
        return EXIT_ERROR

    result = service.run(action=action)
    sys.stdout.write(f"{result}\n")
    return EXIT_SUCCESS


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="seed")
    register_subparser(parser.add_subparsers(dest="command"))
    parsed = parser.parse_args(argv)
    return run(parsed)
