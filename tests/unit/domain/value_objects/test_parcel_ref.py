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

import pytest

from src.core.domain.value_objects.parcel_ref import ParcelRef


def test_parcel_ref_composite_and_hash_are_deterministic() -> None:
    ref = ParcelRef("Konya", "Selcuklu", "Sancak", "10", "20")

    assert ref.composite_key == "Konya/Selcuklu/Sancak/10/20"
    assert len(ref.unique_hash) == 64


def test_parcel_ref_rejects_blank_fields() -> None:
    with pytest.raises(ValueError, match="province"):
        ParcelRef("", "Selcuklu", "Sancak", "10", "20")
