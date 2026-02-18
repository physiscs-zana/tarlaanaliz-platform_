# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
"""Expert management CLI commands."""

from __future__ import annotations

import argparse
import importlib
import sys
from collections.abc import Sequence

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_VALIDATION = 2
EXIT_NOT_FOUND = 3
EXIT_FORBIDDEN = 4


def register_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("expert", help="Expert management commands")
    expert_sub = parser.add_subparsers(dest="expert_command")

    list_cmd = expert_sub.add_parser("list-experts", help="List experts")
    list_cmd.set_defaults(handler=_list_experts)

    add_cmd = expert_sub.add_parser("add-expert", help="Add a new expert")
    add_cmd.add_argument("--display-name", required=True)
    add_cmd.add_argument("--phone", required=True)
    add_cmd.add_argument("--corr-id", default=None)
    add_cmd.set_defaults(handler=_add_expert)

    deactivate_cmd = expert_sub.add_parser("deactivate-expert", help="Deactivate an expert")
    deactivate_cmd.add_argument("--expert-id", required=True)
    deactivate_cmd.add_argument("--corr-id", default=None)
    deactivate_cmd.set_defaults(handler=_deactivate_expert)

    assign_cmd = expert_sub.add_parser("assign-expert-to-job", help="Assign expert to job")
    assign_cmd.add_argument("--expert-id", required=True)
    assign_cmd.add_argument("--analysis-job-id", required=True)
    assign_cmd.add_argument("--corr-id", default=None)
    assign_cmd.set_defaults(handler=_assign_expert_to_job)


def run(args: argparse.Namespace) -> int:
    handler = getattr(args, "handler", None)
    if handler is None:
        sys.stderr.write("error: missing expert subcommand\n")
        return EXIT_VALIDATION
    return int(handler(args))


def _load_service_module():
    try:
        return importlib.import_module("src.application.services.expert_management_service")
    except Exception:
        sys.stderr.write("TODO: src.application.services.expert_management_service missing\n")
        return None


def _list_experts(args: argparse.Namespace) -> int:
    _ = args
    module = _load_service_module()
    if module is None:
        return EXIT_ERROR
    service = getattr(module, "service", None)
    if service is None:
        sys.stderr.write("error: expert management service entrypoint not found\n")
        return EXIT_ERROR
    result = service.list_experts()
    sys.stdout.write(f"{result}\n")
    return EXIT_SUCCESS


def _add_expert(args: argparse.Namespace) -> int:
    module = _load_service_module()
    if module is None:
        return EXIT_ERROR
    service = getattr(module, "service", None)
    if service is None:
        sys.stderr.write("error: expert management service entrypoint not found\n")
        return EXIT_ERROR
    result = service.add_expert(display_name=args.display_name, phone=args.phone, corr_id=args.corr_id)
    sys.stdout.write(f"{result}\n")
    return EXIT_SUCCESS


def _deactivate_expert(args: argparse.Namespace) -> int:
    module = _load_service_module()
    if module is None:
        return EXIT_ERROR
    service = getattr(module, "service", None)
    if service is None:
        sys.stderr.write("error: expert management service entrypoint not found\n")
        return EXIT_ERROR
    result = service.deactivate_expert(expert_id=args.expert_id, corr_id=args.corr_id)
    sys.stdout.write(f"{result}\n")
    return EXIT_SUCCESS


def _assign_expert_to_job(args: argparse.Namespace) -> int:
    module = _load_service_module()
    if module is None:
        return EXIT_ERROR
    service = getattr(module, "service", None)
    if service is None:
        sys.stderr.write("error: expert management service entrypoint not found\n")
        return EXIT_ERROR
    result = service.assign_expert_to_job(
        expert_id=args.expert_id,
        analysis_job_id=args.analysis_job_id,
        corr_id=args.corr_id,
    )
    sys.stdout.write(f"{result}\n")
    return EXIT_SUCCESS


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="expert")
    subparsers = parser.add_subparsers(dest="command")
    register_subparser(subparsers)
    parsed = parser.parse_args(argv)
    return run(parsed)
