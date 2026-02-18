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

from src.core.domain.services.capacity_manager import (
    CapacityError,
    CapacityManager,
    PilotAssignment,
    PilotCapacity,
)


def test_capacity_manager_blocks_non_work_day() -> None:
    manager = CapacityManager()
    pilot = PilotCapacity(
        pilot_id=uuid.uuid4(),
        work_days=frozenset({0, 1, 2, 3, 4, 5}),
        daily_capacity=2,
        province_code="42",
    )

    result = manager.check_availability(pilot, date(2026, 1, 4), [])  # Sunday

    assert result.is_available is False
    assert "çalışma günü" in result.reason


def test_capacity_manager_detects_full_daily_capacity() -> None:
    manager = CapacityManager()
    pid = uuid.uuid4()
    day = date(2026, 1, 5)
    pilot = PilotCapacity(pilot_id=pid, work_days=frozenset({0, 1, 2, 3, 4}), daily_capacity=2, province_code="42")
    assignments = [
        PilotAssignment(pilot_id=pid, mission_id=uuid.uuid4(), scheduled_date=day),
        PilotAssignment(pilot_id=pid, mission_id=uuid.uuid4(), scheduled_date=day),
    ]

    result = manager.check_availability(pilot, day, assignments)

    assert result.is_available is False
    assert result.remaining == 0


def test_capacity_manager_rejects_invalid_date_range() -> None:
    manager = CapacityManager()
    pilot = PilotCapacity(pilot_id=uuid.uuid4(), work_days=frozenset({0}), daily_capacity=1, province_code="42")

    with pytest.raises(CapacityError, match="start_date"):
        manager.find_available_slots(pilot, date(2026, 1, 2), date(2026, 1, 1), [])
