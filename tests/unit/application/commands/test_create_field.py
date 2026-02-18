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

import pytest

import importlib


@dataclass
class _FieldService:
    calls: int = 0

    def create_field(
        self,
        *,
        owner_id: str,
        name: str,
        parcel_ref: str,
        geometry: dict[str, object],
        correlation_id: str,
    ) -> dict[str, str]:
        self.calls += 1
        return {"field_id": "field-1", "owner_id": owner_id, "name": name}


@dataclass
class _Audit:
    calls: int = 0

    def log(self, *, action: str, correlation_id: str, actor_id: str, payload: dict[str, str]) -> None:
        self.calls += 1


class _Idempotency:
    def __init__(self) -> None:
        self.store: dict[str, dict[str, str]] = {}

    def get(self, *, key: str) -> dict[str, str] | None:
        return self.store.get(key)

    def set(self, *, key: str, value: dict[str, str]) -> None:
        self.store[key] = value


@dataclass
class _Deps:
    field_service: _FieldService
    audit_log: _Audit
    idempotency: _Idempotency | None


def _load_create_field_module():
    try:
        return importlib.import_module("src.application.commands.create_field")
    except SyntaxError as exc:
        pytest.skip(f"application package import edilemiyor: {exc}")


def _ctx(create_field, *roles: str):
    return create_field.RequestContext(actor_id="farmer-1", roles=roles, correlation_id="corr-f-1")


def test_create_field_requires_allowed_role() -> None:
    create_field = _load_create_field_module()
    deps = _Deps(_FieldService(), _Audit(), _Idempotency())
    cmd = create_field.CreateFieldCommand(
        owner_id="u1",
        name="Field A",
        parcel_ref="42/1/2/3/4",
        geometry={"type": "Polygon", "coordinates": []},
    )

    with pytest.raises(PermissionError, match="forbidden"):
        create_field.handle(cmd, ctx=_ctx(create_field, "guest"), deps=deps)


def test_create_field_validates_name() -> None:
    create_field = _load_create_field_module()
    deps = _Deps(_FieldService(), _Audit(), _Idempotency())
    cmd = create_field.CreateFieldCommand(
        owner_id="u1",
        name=" ",
        parcel_ref="42/1/2/3/4",
        geometry={"type": "Polygon", "coordinates": []},
    )

    with pytest.raises(ValueError, match="field_name_required"):
        create_field.handle(cmd, ctx=_ctx(create_field, "farmer"), deps=deps)


def test_create_field_idempotent_cache_hit() -> None:
    create_field = _load_create_field_module()
    idem = _Idempotency()
    idem.set(key="idem-field", value={"field_id": "f1", "owner_id": "u1", "name": "Field A"})
    deps = _Deps(_FieldService(), _Audit(), idem)
    cmd = create_field.CreateFieldCommand(
        owner_id="u1",
        name="Field A",
        parcel_ref="42/1/2/3/4",
        geometry={"type": "Polygon", "coordinates": []},
        idempotency_key="idem-field",
    )

    result = create_field.handle(cmd, ctx=_ctx(create_field, "admin"), deps=deps)

    assert result.field_id == "f1"
    assert deps.field_service.calls == 0
