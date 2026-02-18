# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
"""Subscription management CLI commands."""

from __future__ import annotations

import argparse
import importlib
import sys
from collections.abc import Sequence

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_VALIDATION = 2


def register_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("subscription", help="Subscription management")
    subscription_sub = parser.add_subparsers(dest="subscription_command")

    list_cmd = subscription_sub.add_parser("list", help="List subscriptions")
    list_cmd.set_defaults(handler=_run_action, subscription_action="list")

    create_cmd = subscription_sub.add_parser("create", help="Create subscription")
    create_cmd.add_argument("--owner-id", required=True)
    create_cmd.add_argument("--plan-id", required=True)
    create_cmd.set_defaults(handler=_run_action, subscription_action="create")

    cancel_cmd = subscription_sub.add_parser("cancel", help="Cancel subscription")
    cancel_cmd.add_argument("--subscription-id", required=True)
    cancel_cmd.set_defaults(handler=_run_action, subscription_action="cancel")

    renew_cmd = subscription_sub.add_parser("renew", help="Renew subscription")
    renew_cmd.add_argument("--subscription-id", required=True)
    renew_cmd.set_defaults(handler=_run_action, subscription_action="renew")

    attach_cmd = subscription_sub.add_parser("attach-field", help="Attach field to subscription")
    attach_cmd.add_argument("--subscription-id", required=True)
    attach_cmd.add_argument("--field-id", required=True)
    attach_cmd.set_defaults(handler=_run_action, subscription_action="attach-field")


def run(args: argparse.Namespace) -> int:
    handler = getattr(args, "handler", None)
    if handler is None:
        sys.stderr.write("error: missing subscription subcommand\n")
        return EXIT_VALIDATION
    return int(handler(args))


def _run_action(args: argparse.Namespace) -> int:
    try:
        module = importlib.import_module("src.application.services.subscription_management_service")
    except Exception:
        sys.stderr.write("TODO: src.application.services.subscription_management_service missing\n")
        return EXIT_ERROR

    service = getattr(module, "service", None)
    if service is None:
        sys.stderr.write("error: subscription management service entrypoint not found\n")
        return EXIT_ERROR

    # KR-033: paid-state gating and payment verification are application-layer responsibilities.
    payload = {k: v for k, v in vars(args).items() if k not in {"handler"}}
    result = service.handle(command=payload)
    sys.stdout.write(f"{result}\n")
    return EXIT_SUCCESS


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="subscription")
    register_subparser(parser.add_subparsers(dest="command"))
    parsed = parser.parse_args(argv)
    return run(parsed)
