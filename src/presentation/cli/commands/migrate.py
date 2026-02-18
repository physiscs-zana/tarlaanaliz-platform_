# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
"""Database migration CLI commands."""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from collections.abc import Sequence

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_VALIDATION = 2


def register_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("migrate", help="Database migration commands")
    migrate_sub = parser.add_subparsers(dest="migrate_command")

    for name in ("upgrade", "downgrade", "current", "history"):
        cmd = migrate_sub.add_parser(name, help=f"Run {name}")
        cmd.add_argument("--revision", default="head")
        cmd.set_defaults(handler=_run_migration, action=name)


def run(args: argparse.Namespace) -> int:
    handler = getattr(args, "handler", None)
    if handler is None:
        sys.stderr.write("error: missing migrate subcommand\n")
        return EXIT_VALIDATION
    return int(handler(args))


def _run_migration(args: argparse.Namespace) -> int:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        sys.stderr.write("error: DATABASE_URL is required\n")
        return EXIT_VALIDATION

    try:
        module = importlib.import_module("alembic.config")
        command_module = importlib.import_module("alembic.command")
    except Exception:
        sys.stderr.write("TODO: Alembic not installed/configured; migration adapter hook required\n")
        return EXIT_ERROR

    config_class = getattr(module, "Config", None)
    if config_class is None:
        sys.stderr.write("error: alembic Config not available\n")
        return EXIT_ERROR

    cfg = config_class("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)

    action = str(args.action)
    revision = str(args.revision)

    if action == "upgrade":
        command_module.upgrade(cfg, revision)
    elif action == "downgrade":
        command_module.downgrade(cfg, revision)
    elif action == "current":
        command_module.current(cfg)
    elif action == "history":
        command_module.history(cfg)
    else:
        sys.stderr.write("error: invalid migration action\n")
        return EXIT_VALIDATION

    return EXIT_SUCCESS


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="migrate")
    subparsers = parser.add_subparsers(dest="command")
    register_subparser(subparsers)
    parsed = parser.parse_args(argv)
    return run(parsed)
