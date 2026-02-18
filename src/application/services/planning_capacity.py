# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
# KR-015: Capacity planning utility for effort and staffing.

from __future__ import annotations

import math
from dataclasses import dataclass


class CapacityError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class CapacityPlan:
    area_donum: float
    effort_points: float
    required_pilots: int


@dataclass(slots=True)
class PlanningCapacityService:
    effort_per_donum: float = 1.0
    max_daily_effort_per_pilot: float = 200.0

    def calculate(self, *, area_donum: float) -> CapacityPlan:
        if area_donum <= 0:
            raise CapacityError("area_donum_must_be_positive")
        if self.effort_per_donum <= 0 or self.max_daily_effort_per_pilot <= 0:
            raise CapacityError("capacity_coefficients_must_be_positive")

        effort_points = area_donum * self.effort_per_donum
        required_pilots = max(1, math.ceil(effort_points / self.max_daily_effort_per_pilot))

        # KR-015: Deterministic capacity output for planning flow.
        return CapacityPlan(
            area_donum=area_donum,
            effort_points=effort_points,
            required_pilots=required_pilots,
        )
