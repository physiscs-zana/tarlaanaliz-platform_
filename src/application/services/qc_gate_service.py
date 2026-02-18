# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
# KR-018: QC fail must block analysis start.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class QcStatus(str, Enum):
    PASS = "pass"  # noqa: S105
    WARN = "warn"
    FAIL = "fail"


class QcGateError(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class QcGateDecision:
    status: QcStatus
    reason: str | None = None


@dataclass(slots=True)
class QcGateService:
    def assert_analysis_allowed(self, decision: QcGateDecision) -> None:
        # KR-018: Fail state is a hard-gate.
        if decision.status is QcStatus.FAIL:
            raise QcGateError(decision.reason or "qc_hard_gate_failed")
