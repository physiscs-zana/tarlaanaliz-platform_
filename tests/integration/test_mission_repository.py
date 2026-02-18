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

import pytest

from src.core.domain.entities.mission import Mission


class InMemoryMissionRepository:
    def __init__(self) -> None:
        self._missions: dict[str, Mission] = {}

    def save(self, mission: Mission) -> None:
        self._missions[str(mission.mission_id)] = mission

    def get(self, mission_id: str) -> Mission | None:
        return self._missions.get(mission_id)


def test_mission_repository_persists_status_transitions(mission_entity: Mission) -> None:
    repo = InMemoryMissionRepository()

    mission_entity.assign_pilot(uuid.uuid4())
    mission_entity.acknowledge()
    repo.save(mission_entity)

    loaded = repo.get(str(mission_entity.mission_id))
    assert loaded is not None
    assert loaded.status.value == "ACKED"


def test_mission_repository_prevents_invalid_transition(mission_entity: Mission) -> None:
    with pytest.raises(ValueError, match="Invalid status transition"):
        mission_entity.complete()
