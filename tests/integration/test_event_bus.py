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

import asyncio
from dataclasses import dataclass

from src.core.domain.events.base import DomainEvent


@dataclass(frozen=True)
class MissionAssignedEvent(DomainEvent):
    mission_id: str = "m-1"
    pilot_id: str = "p-1"


def test_domain_event_contract_fields_are_stable() -> None:
    event = MissionAssignedEvent()

    payload = event.to_dict()

    assert payload["event_type"] == "MissionAssignedEvent"
    assert "event_id" in payload
    assert "occurred_at" in payload


def test_domain_event_is_immutable() -> None:
    event = MissionAssignedEvent(mission_id="m-2")

    try:
        event.mission_id = "m-3"  # type: ignore[misc]
    except Exception as exc:  # frozen dataclass should reject mutation
        assert type(exc).__name__ in {"FrozenInstanceError", "AttributeError"}
    else:
        raise AssertionError("DomainEvent must stay immutable for event-bus contract safety.")


def test_event_loop_can_serialize_event_without_network() -> None:
    event = MissionAssignedEvent()

    async def _serialize() -> dict[str, str]:
        await asyncio.sleep(0)
        return event.to_dict()

    payload = asyncio.run(_serialize())
    assert payload["event_type"] == "MissionAssignedEvent"
