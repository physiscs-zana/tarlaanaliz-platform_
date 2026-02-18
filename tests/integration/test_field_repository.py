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

from decimal import Decimal

import pytest

from src.core.domain.entities.field import Field, FieldStatus


class InMemoryFieldRepository:
    def __init__(self) -> None:
        self._by_id: dict[str, Field] = {}
        self._parcel_refs: set[str] = set()

    def create(self, field: Field) -> None:
        if field.parcel_ref in self._parcel_refs:
            raise ValueError("duplicate_parcel_ref")
        self._by_id[str(field.field_id)] = field
        self._parcel_refs.add(field.parcel_ref)

    def get(self, field_id: str) -> Field | None:
        return self._by_id.get(field_id)


def test_field_repository_create_and_get(field_entity: Field) -> None:
    repo = InMemoryFieldRepository()

    repo.create(field_entity)
    loaded = repo.get(str(field_entity.field_id))

    assert loaded is not None
    assert loaded.parcel_ref == field_entity.parcel_ref
    assert loaded.area_donum == Decimal("2500")


def test_field_repository_rejects_duplicate_parcel(field_entity: Field) -> None:
    repo = InMemoryFieldRepository()
    repo.create(field_entity)

    duplicate = Field(
        field_id=field_entity.field_id,
        user_id=field_entity.user_id,
        province=field_entity.province,
        district=field_entity.district,
        village=field_entity.village,
        ada=field_entity.ada,
        parsel=field_entity.parsel,
        area_m2=field_entity.area_m2,
        status=FieldStatus.ACTIVE,
        crop_type=field_entity.crop_type,
        created_at=field_entity.created_at,
        updated_at=field_entity.updated_at,
        geometry=field_entity.geometry,
    )

    with pytest.raises(ValueError, match="duplicate_parcel_ref"):
        repo.create(duplicate)
