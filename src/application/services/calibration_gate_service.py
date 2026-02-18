# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
# KR-018: Calibration hard-gate is enforced in application layer.

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class CalibrationEvidencePort(Protocol):
    def is_calibration_verified(self, *, mission_id: str) -> bool: ...


class CalibrationGateError(PermissionError):
    pass


@dataclass(slots=True)
class CalibrationGateService:
    evidence_port: CalibrationEvidencePort

    def assert_ready(self, *, mission_id: str) -> None:
        # KR-018: Uncalibrated input must not start analysis.
        if not self.evidence_port.is_calibration_verified(mission_id=mission_id):
            raise CalibrationGateError("calibration_hard_gate_failed")
