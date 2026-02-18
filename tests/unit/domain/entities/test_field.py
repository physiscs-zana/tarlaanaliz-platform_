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

from datetime import date
from decimal import Decimal

import pytest

from src.core.domain.entities.field import Field, FieldStatus


def test_field_parcel_ref_and_area_donum() -> None:
    field = Field(
        field_id=__import__("uuid").uuid4(),
        user_id=__import__("uuid").uuid4(),
        province="Konya",
        district="Selcuklu",
        village="Sancak",
        ada="10",
        parsel="20",
        area_m2=Decimal("3000000"),
        status=FieldStatus.ACTIVE,
        created_at=__import__("datetime").datetime(2026, 1, 1),
        updated_at=__import__("datetime").datetime(2026, 1, 1),
    )

    assert field.parcel_ref == "Konya/Selcuklu/Sancak/10/20"
    assert field.area_donum == Decimal("3000")


def test_field_crop_type_change_outside_window_fails() -> None:
    field = Field(
        field_id=__import__("uuid").uuid4(),
        user_id=__import__("uuid").uuid4(),
        province="Konya",
        district="Selcuklu",
        village="Sancak",
        ada="10",
        parsel="20",
        area_m2=Decimal("3000000"),
        status=FieldStatus.ACTIVE,
        created_at=__import__("datetime").datetime(2026, 1, 1),
        updated_at=__import__("datetime").datetime(2026, 1, 1),
    )

    with pytest.raises(ValueError, match="KR-013"):
        field.change_crop_type("CORN", date(2026, 5, 1))
