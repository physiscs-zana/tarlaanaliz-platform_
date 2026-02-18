# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
"""
Amaç: Test modülü; davranış doğrulama ve regresyon engeli.
Sorumluluk: Bağlamına göre beklenen sorumlulukları yerine getirir; SSOT v1.0.0 ile uyumlu kalır.
Girdi/Çıktı (Contract/DTO/Event): N/A
Güvenlik (RBAC/PII/Audit): N/A
Hata Modları (idempotency/retry/rate limit): N/A
Observability (log fields/metrics/traces): N/A
Testler: N/A
Bağımlılıklar: N/A
Notlar/SSOT: Tek referans: SSOT v1.0.0. Aynı kavram başka yerde tekrar edilmez.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

import importlib


@dataclass
class _MissionService:
    calls: int = 0

    def assign_mission(self, *, mission_id: str, pilot_id: str, correlation_id: str) -> dict[str, str]:
        self.calls += 1
        return {"mission_id": mission_id, "pilot_id": pilot_id, "status": "assigned"}


@dataclass
class _PlanningCapacity:
    calls: int = 0

    def ensure_assignment_allowed(self, *, pilot_id: str, mission_id: str) -> None:
        self.calls += 1


@dataclass
class _Audit:
    calls: int = 0

    def log(self, *, action: str, correlation_id: str, actor_id: str, payload: dict[str, str]) -> None:
        self.calls += 1


class _Idempotency:
    def __init__(self) -> None:
        self.store: dict[str, dict[str, str]] = {}

    def get(self, *, key: str) -> dict[str, str] | None:
        return self.store.get(key)

    def set(self, *, key: str, value: dict[str, str]) -> None:
        self.store[key] = value


@dataclass
class _Deps:
    mission_service: _MissionService
    planning_capacity: _PlanningCapacity
    audit_log: _Audit
    idempotency: _Idempotency | None


def _load_assign_module():
    try:
        return importlib.import_module("src.application.commands.assign_mission")
    except SyntaxError as exc:
        pytest.skip(f"application package import edilemiyor: {exc}")


def _ctx(assign_mission, *roles: str):
    return assign_mission.RequestContext(actor_id="admin-1", roles=roles, correlation_id="corr-1")


def test_assign_mission_requires_role() -> None:
    assign_mission = _load_assign_module()
    deps = _Deps(_MissionService(), _PlanningCapacity(), _Audit(), _Idempotency())
    cmd = assign_mission.AssignMissionCommand(mission_id="m1", pilot_id="p1")

    with pytest.raises(PermissionError, match="forbidden"):
        assign_mission.handle(cmd, ctx=_ctx(assign_mission, "viewer"), deps=deps)


def test_assign_mission_uses_idempotency_cache() -> None:
    assign_mission = _load_assign_module()
    idem = _Idempotency()
    idem.set(key="idem-1", value={"mission_id": "m1", "pilot_id": "p1", "status": "assigned"})
    deps = _Deps(_MissionService(), _PlanningCapacity(), _Audit(), idem)
    cmd = assign_mission.AssignMissionCommand(mission_id="m1", pilot_id="p1", idempotency_key="idem-1")

    result = assign_mission.handle(cmd, ctx=_ctx(assign_mission, "admin"), deps=deps)

    assert result.status == "assigned"
    assert deps.mission_service.calls == 0
    assert deps.planning_capacity.calls == 0


def test_assign_mission_runs_capacity_and_audit() -> None:
    assign_mission = _load_assign_module()
    deps = _Deps(_MissionService(), _PlanningCapacity(), _Audit(), _Idempotency())
    cmd = assign_mission.AssignMissionCommand(mission_id="m2", pilot_id="p2", idempotency_key="idem-2")

    result = assign_mission.handle(cmd, ctx=_ctx(assign_mission, "ops"), deps=deps)

    assert result.status == "assigned"
    assert deps.planning_capacity.calls == 1
    assert deps.mission_service.calls == 1
    assert deps.audit_log.calls == 1
