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

import uuid
from datetime import date

import pytest

from src.core.domain.services.planning_engine import MissionDemand, PilotSlot, PlanningEngine, PlanningEngineError


def test_planning_engine_schedules_by_priority_and_capacity() -> None:
    engine = PlanningEngine()
    d1 = MissionDemand(
        demand_id=uuid.uuid4(),
        field_id=uuid.uuid4(),
        province_code="42",
        crop_type="WHEAT",
        area_m2=1000,
        priority=0,
        earliest_date=date(2026, 1, 1),
        latest_date=date(2026, 1, 1),
        estimated_duration_minutes=30,
    )
    d2 = MissionDemand(
        demand_id=uuid.uuid4(),
        field_id=uuid.uuid4(),
        province_code="42",
        crop_type="WHEAT",
        area_m2=1000,
        priority=1,
        earliest_date=date(2026, 1, 1),
        latest_date=date(2026, 1, 1),
        estimated_duration_minutes=30,
    )
    slots = [
        PilotSlot(
            pilot_id=uuid.uuid4(),
            date=date(2026, 1, 1),
            province_code="42",
            remaining_capacity=1,
            daily_capacity=1,
        )
    ]

    result = engine.optimize_schedule([d2, d1], slots)

    assert len(result.scheduled) == 1
    assert result.scheduled[0].demand_id == d1.demand_id
    assert len(result.unscheduled) == 1


def test_planning_engine_generate_date_range_validates_order() -> None:
    with pytest.raises(PlanningEngineError, match="start"):
        PlanningEngine.generate_date_range(date(2026, 1, 2), date(2026, 1, 1))
