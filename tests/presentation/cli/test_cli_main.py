from src.presentation.cli.main import main


def test_help_works() -> None:
    exit_code = main(["--help"])
    assert exit_code == 0


def test_unknown_command_returns_non_zero() -> None:
    exit_code = main(["unknown-cmd"])
    assert exit_code != 0


def test_weekly_planner_dry_run_graceful_without_service() -> None:
    exit_code = main(["weekly-planner", "--week", "2026-10", "--dry-run"])
    assert exit_code == 1
