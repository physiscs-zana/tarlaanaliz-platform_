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

from dataclasses import dataclass

from src.core.domain.services.reschedule_service import RescheduleService


class _PilotAvailability:
    def __init__(self, available: bool) -> None:
        self.available = available

    def is_available(self, pilot_id: str, date_iso: str) -> bool:
        return self.available


@dataclass
class _Subscription:
    id: str = "sub-1"
    reschedule_tokens_remaining: int = 1


@dataclass
class _Mission:
    id: str = "m-1"
    scheduled_date: str = "2026-01-10"
    schedule_window_start: str = "2026-01-01"
    schedule_window_end: str = "2026-01-31"
    assigned_pilot_id: str | None = "pilot-1"


def test_weather_block_replan_success_when_token_and_availability_ok() -> None:
    service = RescheduleService(_PilotAvailability(True))

    result = service.reschedule(_Subscription(), _Mission(), "2026-01-20")

    assert result.ok is True
    assert result.reason == "OK"
    assert result.token_remaining == 0


def test_weather_block_replan_fails_without_token() -> None:
    service = RescheduleService(_PilotAvailability(True))

    result = service.reschedule(_Subscription(reschedule_tokens_remaining=0), _Mission(), "2026-01-20")

    assert result.ok is False
    assert result.reason == "NO_TOKENS"
