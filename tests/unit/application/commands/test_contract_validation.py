# BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
# KR-081: Contract validation tests - validate is called in every command handler.
"""Command handler contract validation tests."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Mock Protocol implementations
# ---------------------------------------------------------------------------


@dataclass
class _MockContractValidator:
    """ContractValidatorPort mock - records calls."""

    calls: list[dict[str, Any]] = field(default_factory=list)
    should_raise: bool = False

    def validate(self, *, schema_key: str, payload: dict[str, Any]) -> None:
        self.calls.append({"schema_key": schema_key, "payload": payload})
        if self.should_raise:
            raise ValueError(f"Contract validation failed for {schema_key}")


@dataclass
class _MockAuditLog:
    entries: list[dict[str, Any]] = field(default_factory=list)

    def log(self, *, action: str, correlation_id: str, actor_id: str, payload: dict[str, Any]) -> None:
        self.entries.append(
            {"action": action, "correlation_id": correlation_id, "actor_id": actor_id, "payload": payload}
        )


class _MockIdempotency:
    def __init__(self) -> None:
        self.store: dict[str, dict[str, Any]] = {}

    def get(self, *, key: str) -> dict[str, Any] | None:
        return self.store.get(key)

    def set(self, *, key: str, value: dict[str, Any]) -> None:
        self.store[key] = value


# --- Domain service mocks ---


@dataclass
class _MockFieldService:
    calls: int = 0

    def create_field(
        self,
        *,
        owner_id: str,
        name: str,
        parcel_ref: str,
        geometry: dict[str, Any],
        correlation_id: str,
    ) -> dict[str, Any]:
        self.calls += 1
        return {"field_id": "fld-test-1", "owner_id": owner_id, "name": name}


@dataclass
class _MockMissionService:
    calls: int = 0

    def assign_mission(self, *, mission_id: str, pilot_id: str, correlation_id: str) -> dict[str, Any]:
        self.calls += 1
        return {"mission_id": mission_id, "pilot_id": pilot_id, "status": "assigned"}


@dataclass
class _MockPlanningCapacity:
    calls: int = 0

    def ensure_assignment_allowed(self, *, pilot_id: str, mission_id: str) -> None:
        self.calls += 1

    def ensure_slot_available(self, *, subscription_id: str, scheduled_for: str) -> None:
        self.calls += 1


@dataclass
class _MockPaymentService:
    _intent: dict[str, Any] | None = field(default_factory=lambda: {"payment_intent_id": "pi-1", "status": "pending"})

    def get_payment_intent(self, *, payment_intent_id: str) -> dict[str, Any] | None:
        return self._intent

    def approve_payment(
        self,
        *,
        payment_intent_id: str,
        payment_ref: str,
        receipt_ref: str,
        approved_by: str,
        correlation_id: str,
    ) -> dict[str, Any]:
        return {"payment_intent_id": payment_intent_id, "status": "paid"}


@dataclass
class _MockPayrollService:
    def calculate_payroll(self, *, period_start: str, period_end: str, actor_type: str) -> dict[str, object]:
        return {"gross_total": "1000.00", "item_count": 5}


@dataclass
class _MockSubscriptionService:
    def create_subscription(self, *, field_id: str, plan_id: str, status: str, correlation_id: str) -> dict[str, Any]:
        return {"subscription_id": "sub-1", "field_id": field_id}


@dataclass
class _MockMissionLifecycleManager:
    def schedule_mission(self, *, subscription_id: str, scheduled_for: str, correlation_id: str) -> dict[str, Any]:
        return {"mission_id": "msn-1", "scheduled_for": scheduled_for, "status": "scheduled"}


# ---------------------------------------------------------------------------
# Deps containers - field names match each handler's Protocol
# ---------------------------------------------------------------------------


@dataclass
class _CreateFieldDeps:
    field_service: Any
    contract_validator: Any
    audit_log: Any
    idempotency: Any = None


@dataclass
class _AssignMissionDeps:
    mission_service: Any
    planning_capacity: Any
    contract_validator: Any
    audit_log: Any
    idempotency: Any = None


@dataclass
class _ApprovePaymentDeps:
    payment_service: Any
    contract_validator: Any
    audit_log: Any
    idempotency: Any = None


@dataclass
class _CalculatePayrollDeps:
    payroll_service: Any
    contract_validator: Any
    audit_log: Any


@dataclass
class _CreateSubscriptionDeps:
    subscription_service: Any
    payment_service: Any
    contract_validator: Any
    audit_log: Any


@dataclass
class _ScheduleMissionDeps:
    mission_lifecycle_manager: Any
    planning_capacity: Any
    contract_validator: Any
    audit_log: Any
    idempotency: Any = None


# ---------------------------------------------------------------------------
# Module loaders
# ---------------------------------------------------------------------------


def _load(module_name: str):
    try:
        return importlib.import_module(f"src.application.commands.{module_name}")
    except (SyntaxError, ModuleNotFoundError) as exc:
        pytest.skip(f"application package cannot be imported: {exc}")


# ============================================================
# TESTS — CreateField
# ============================================================


class TestCreateFieldContractValidation:
    """create_field command handler contract validation tests."""

    @staticmethod
    def _ctx(mod):
        return mod.RequestContext(actor_id="farmer-1", roles=("farmer",), correlation_id="corr-cf-1")

    @staticmethod
    def _cmd(mod):
        return mod.CreateFieldCommand(
            owner_id="owner-1",
            name="Test Tarla",
            parcel_ref="P-001",
            geometry={"type": "Polygon", "coordinates": [[[36.0, 37.0]]]},
        )

    def test_validate_called_with_correct_schema_key(self) -> None:
        mod = _load("create_field")
        validator = _MockContractValidator()
        deps = _CreateFieldDeps(
            field_service=_MockFieldService(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)
        assert len(validator.calls) == 1
        assert validator.calls[0]["schema_key"] == "field"

    def test_validate_payload_contains_name_and_geometry(self) -> None:
        mod = _load("create_field")
        validator = _MockContractValidator()
        deps = _CreateFieldDeps(
            field_service=_MockFieldService(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        cmd = self._cmd(mod)
        mod.handle(cmd, ctx=self._ctx(mod), deps=deps)
        payload = validator.calls[0]["payload"]
        assert payload["name"] == cmd.name
        assert payload["geometry"] == cmd.geometry

    def test_validation_failure_raises_error(self) -> None:
        mod = _load("create_field")
        validator = _MockContractValidator(should_raise=True)
        deps = _CreateFieldDeps(
            field_service=_MockFieldService(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        with pytest.raises(ValueError, match="Contract validation failed"):
            mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)

    def test_service_not_called_when_validation_fails(self) -> None:
        mod = _load("create_field")
        validator = _MockContractValidator(should_raise=True)
        field_svc = _MockFieldService()
        deps = _CreateFieldDeps(
            field_service=field_svc,
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        with pytest.raises(ValueError):
            mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)
        assert field_svc.calls == 0


# ============================================================
# TESTS — AssignMission
# ============================================================


class TestAssignMissionContractValidation:
    """assign_mission command handler contract validation tests."""

    @staticmethod
    def _ctx(mod):
        return mod.RequestContext(actor_id="admin-1", roles=("admin",), correlation_id="corr-am-1")

    @staticmethod
    def _cmd(mod):
        return mod.AssignMissionCommand(mission_id="msn-1", pilot_id="plt-1")

    def test_validate_called_with_mission_key(self) -> None:
        mod = _load("assign_mission")
        validator = _MockContractValidator()
        deps = _AssignMissionDeps(
            mission_service=_MockMissionService(),
            planning_capacity=_MockPlanningCapacity(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)
        assert len(validator.calls) == 1
        assert validator.calls[0]["schema_key"] == "mission"

    def test_validate_payload_contains_mission_and_pilot(self) -> None:
        mod = _load("assign_mission")
        validator = _MockContractValidator()
        deps = _AssignMissionDeps(
            mission_service=_MockMissionService(),
            planning_capacity=_MockPlanningCapacity(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        cmd = self._cmd(mod)
        mod.handle(cmd, ctx=self._ctx(mod), deps=deps)
        payload = validator.calls[0]["payload"]
        assert payload["mission_id"] == cmd.mission_id
        assert payload["pilot_id"] == cmd.pilot_id

    def test_validation_failure_blocks_assignment(self) -> None:
        mod = _load("assign_mission")
        validator = _MockContractValidator(should_raise=True)
        mission_svc = _MockMissionService()
        deps = _AssignMissionDeps(
            mission_service=mission_svc,
            planning_capacity=_MockPlanningCapacity(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        with pytest.raises(ValueError, match="Contract validation failed"):
            mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)
        assert mission_svc.calls == 0


# ============================================================
# TESTS — ApprovePayment
# ============================================================


class TestApprovePaymentContractValidation:
    """approve_payment contract validation tests."""

    @staticmethod
    def _ctx(mod):
        return mod.RequestContext(actor_id="admin-1", roles=("admin",), correlation_id="corr-ap-1")

    @staticmethod
    def _cmd(mod):
        return mod.ApprovePaymentCommand(
            payment_intent_id="pi-1",
            payment_ref="ref-1",
            receipt_ref="rcpt-1",
        )

    def test_validate_called_with_payment_intent_key(self) -> None:
        mod = _load("approve_payment")
        validator = _MockContractValidator()
        deps = _ApprovePaymentDeps(
            payment_service=_MockPaymentService(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)
        assert len(validator.calls) == 1
        assert validator.calls[0]["schema_key"] == "payment_intent"

    def test_validate_payload_contains_payment_fields(self) -> None:
        mod = _load("approve_payment")
        validator = _MockContractValidator()
        deps = _ApprovePaymentDeps(
            payment_service=_MockPaymentService(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        cmd = self._cmd(mod)
        mod.handle(cmd, ctx=self._ctx(mod), deps=deps)
        payload = validator.calls[0]["payload"]
        assert payload["payment_intent_id"] == cmd.payment_intent_id
        assert payload["payment_ref"] == cmd.payment_ref
        assert payload["receipt_ref"] == cmd.receipt_ref

    def test_validation_failure_blocks_payment(self) -> None:
        mod = _load("approve_payment")
        validator = _MockContractValidator(should_raise=True)
        payment_svc = _MockPaymentService()
        payment_svc.approve_payment = MagicMock()
        deps = _ApprovePaymentDeps(
            payment_service=payment_svc,
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        with pytest.raises(ValueError, match="Contract validation failed"):
            mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)
        payment_svc.approve_payment.assert_not_called()


# ============================================================
# TESTS — CalculatePayroll
# ============================================================


class TestCalculatePayrollContractValidation:
    """calculate_payroll contract validation tests."""

    @staticmethod
    def _ctx(mod):
        return mod.RequestContext(actor_id="admin-1", roles=("admin",), correlation_id="corr-cp-1")

    @staticmethod
    def _cmd(mod):
        return mod.CalculatePayrollCommand(
            period_start="2026-01-01",
            period_end="2026-01-31",
            actor_type="pilot",
        )

    def test_validate_called_with_payroll_key(self) -> None:
        mod = _load("calculate_payroll")
        validator = _MockContractValidator()
        deps = _CalculatePayrollDeps(
            payroll_service=_MockPayrollService(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)
        assert len(validator.calls) == 1
        assert validator.calls[0]["schema_key"] == "payroll"

    def test_validate_payload_contains_period_and_actor_type(self) -> None:
        mod = _load("calculate_payroll")
        validator = _MockContractValidator()
        deps = _CalculatePayrollDeps(
            payroll_service=_MockPayrollService(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        cmd = self._cmd(mod)
        mod.handle(cmd, ctx=self._ctx(mod), deps=deps)
        payload = validator.calls[0]["payload"]
        assert payload["period_start"] == cmd.period_start
        assert payload["period_end"] == cmd.period_end
        assert payload["actor_type"] == cmd.actor_type

    def test_validation_failure_blocks_payroll(self) -> None:
        mod = _load("calculate_payroll")
        validator = _MockContractValidator(should_raise=True)
        payroll_svc = _MockPayrollService()
        payroll_svc.calculate_payroll = MagicMock()
        deps = _CalculatePayrollDeps(
            payroll_service=payroll_svc,
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        with pytest.raises(ValueError, match="Contract validation failed"):
            mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)
        payroll_svc.calculate_payroll.assert_not_called()


# ============================================================
# TESTS — CreateSubscription
# ============================================================


class TestCreateSubscriptionContractValidation:
    """create_subscription contract validation tests."""

    @staticmethod
    def _ctx(mod):
        return mod.RequestContext(actor_id="farmer-1", roles=("farmer",), correlation_id="corr-cs-1")

    @staticmethod
    def _cmd(mod):
        return mod.CreateSubscriptionCommand(field_id="fld-1", plan_id="plan-basic")

    def test_validate_called_with_subscription_key(self) -> None:
        mod = _load("create_subscription")
        validator = _MockContractValidator()
        deps = _CreateSubscriptionDeps(
            subscription_service=_MockSubscriptionService(),
            payment_service=None,
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)
        assert len(validator.calls) == 1
        assert validator.calls[0]["schema_key"] == "subscription"

    def test_validate_payload_contains_field_and_plan(self) -> None:
        mod = _load("create_subscription")
        validator = _MockContractValidator()
        deps = _CreateSubscriptionDeps(
            subscription_service=_MockSubscriptionService(),
            payment_service=None,
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        cmd = self._cmd(mod)
        mod.handle(cmd, ctx=self._ctx(mod), deps=deps)
        payload = validator.calls[0]["payload"]
        assert payload["field_id"] == cmd.field_id
        assert payload["plan_id"] == cmd.plan_id

    def test_validation_failure_blocks_subscription(self) -> None:
        mod = _load("create_subscription")
        validator = _MockContractValidator(should_raise=True)
        sub_svc = _MockSubscriptionService()
        sub_svc.create_subscription = MagicMock()
        deps = _CreateSubscriptionDeps(
            subscription_service=sub_svc,
            payment_service=None,
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        with pytest.raises(ValueError, match="Contract validation failed"):
            mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)
        sub_svc.create_subscription.assert_not_called()


# ============================================================
# TESTS — ScheduleMission
# ============================================================


class TestScheduleMissionContractValidation:
    """schedule_mission contract validation tests."""

    @staticmethod
    def _ctx(mod):
        return mod.RequestContext(actor_id="admin-1", roles=("admin",), correlation_id="corr-sm-1")

    @staticmethod
    def _cmd(mod):
        return mod.ScheduleMissionCommand(subscription_id="sub-1", scheduled_for="2026-04-01")

    def test_validate_called_with_mission_key(self) -> None:
        mod = _load("schedule_mission")
        validator = _MockContractValidator()
        deps = _ScheduleMissionDeps(
            mission_lifecycle_manager=_MockMissionLifecycleManager(),
            planning_capacity=_MockPlanningCapacity(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)
        assert len(validator.calls) == 1
        assert validator.calls[0]["schema_key"] == "mission"

    def test_validate_payload_contains_subscription_and_schedule(self) -> None:
        mod = _load("schedule_mission")
        validator = _MockContractValidator()
        deps = _ScheduleMissionDeps(
            mission_lifecycle_manager=_MockMissionLifecycleManager(),
            planning_capacity=_MockPlanningCapacity(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        cmd = self._cmd(mod)
        mod.handle(cmd, ctx=self._ctx(mod), deps=deps)
        payload = validator.calls[0]["payload"]
        assert payload["subscription_id"] == cmd.subscription_id
        assert payload["scheduled_for"] == cmd.scheduled_for

    def test_validation_failure_blocks_scheduling(self) -> None:
        mod = _load("schedule_mission")
        validator = _MockContractValidator(should_raise=True)
        lifecycle = _MockMissionLifecycleManager()
        lifecycle.schedule_mission = MagicMock()
        deps = _ScheduleMissionDeps(
            mission_lifecycle_manager=lifecycle,
            planning_capacity=_MockPlanningCapacity(),
            contract_validator=validator,
            audit_log=_MockAuditLog(),
        )
        with pytest.raises(ValueError, match="Contract validation failed"):
            mod.handle(self._cmd(mod), ctx=self._ctx(mod), deps=deps)
        lifecycle.schedule_mission.assert_not_called()
