# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
"""
Amaç: Test modülü; davranış doğrulama ve regresyon engeli.
Sorumluluk: Mission entity; KR-028 (yasam dongusu), KR-033 (odeme hard gate), KR-015-2/3 (atama).
Girdi/Çıktı (Contract/DTO/Event): N/A
Güvenlik (RBAC/PII/Audit): N/A
Hata Modları (idempotency/retry/rate limit): N/A
Observability (log fields/metrics/traces): N/A
Testler: N/A
Bağımlılıklar: N/A
Notlar/SSOT: Tek referans: SSOT v1.0.0. Aynı kavram başka yerde tekrar edilmez. KR-015.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from src.core.domain.entities.mission import (
    AssignmentReason,
    AssignmentSource,
    Mission,
    MissionStatus,
)


def _mission() -> Mission:
    return Mission(
        mission_id=uuid.uuid4(),
        field_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        crop_type="WHEAT",
        analysis_type="MULTISPECTRAL",
        status=MissionStatus.PLANNED,
        price_snapshot_id=uuid.uuid4(),
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def test_mission_happy_path_transitions() -> None:
    mission = _mission()

    mission.assign_pilot(uuid.uuid4())
    mission.acknowledge()
    mission.mark_flown()
    mission.mark_uploaded()
    mission.start_analysis()
    mission.complete()

    assert mission.status == MissionStatus.DONE


def test_mission_invalid_transition_raises() -> None:
    mission = _mission()

    with pytest.raises(ValueError, match="Invalid status transition"):
        mission.start_analysis()


def test_mission_schedule_window_fields_optional() -> None:
    """schedule_window_start/end None ile oluşturulabilmeli (KR-015-5)."""
    mission = _mission()
    assert mission.schedule_window_start is None
    assert mission.schedule_window_end is None


def test_mission_assignment_source_and_reason() -> None:
    """SYSTEM_SEED + AUTO_DISPATCH değerleri atanabilmeli (KR-015-2/3)."""
    mission = _mission()
    mission.assignment_source = AssignmentSource.SYSTEM_SEED
    mission.assignment_reason = AssignmentReason.AUTO_DISPATCH

    assert mission.assignment_source == AssignmentSource.SYSTEM_SEED
    assert mission.assignment_reason == AssignmentReason.AUTO_DISPATCH
