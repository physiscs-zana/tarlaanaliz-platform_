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

from src.core.domain.services.planning_engine import MissionDemand, PilotSlot, PlanningEngine


def test_mission_assignment_load_smoke() -> None:
    engine = PlanningEngine()

    demands = [
        MissionDemand(
            demand_id=uuid.uuid4(),
            field_id=uuid.uuid4(),
            province_code="42",
            crop_type="WHEAT",
            area_m2=2_500_000,
            priority=i,
            earliest_date=date(2026, 1, 1),
            latest_date=date(2026, 1, 3),
            estimated_duration_minutes=45,
        )
        for i in range(10)
    ]
    pilot_id = uuid.uuid4()
    slots = [
        PilotSlot(
            pilot_id=pilot_id,
            date=date(2026, 1, 1),
            province_code="42",
            remaining_capacity=4,
            daily_capacity=4,
        ),
        PilotSlot(
            pilot_id=pilot_id,
            date=date(2026, 1, 2),
            province_code="42",
            remaining_capacity=4,
            daily_capacity=4,
        ),
    ]

    result = engine.optimize_schedule(demands=demands, pilot_slots=slots)

    assert len(result.scheduled) == 8
    assert len(result.unscheduled) == 2
