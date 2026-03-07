# BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.
# KR-081: Contract-first schema validation is enforced before orchestration.
"""
Contract-first (KR-081) JSON Schema doğrulama servisi.

SchemaRegistry (infrastructure) ile ContractValidatorPort (command layer)
arasında köprü görevi görür. Her iki arayüzü de destekler.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import structlog

logger = structlog.get_logger(__name__)


class SchemaRegistryProtocol(Protocol):
    """Infrastructure SchemaRegistry ile uyumlu protocol."""

    def get_by_key(self, schema_key: str) -> dict[str, Any]: ...


class ContractValidationError(ValueError):
    def __init__(self, message: str, *, schema_id: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.schema_id = schema_id
        self.details = details or {}


@dataclass(frozen=True, slots=True)
class ValidationResult:
    ok: bool
    schema_id: str
    error: ContractValidationError | None = None


class ContractValidatorService:
    """KR-081 contract-first doğrulama.

    İki kullanım modu:
      1. validate() — ValidationResult döner (application service katmanı)
      2. validate_or_raise() — Hata fırlatır (ContractValidatorPort uyumu)
    """

    def __init__(self, registry: SchemaRegistryProtocol) -> None:
        self._registry = registry

    def validate(self, *, schema_key: str, payload: Any, correlation_id: str = "") -> ValidationResult:
        """Payload'ı schema'ya karşı doğrular, sonuç döner."""
        schema = self._registry.get_by_key(schema_key)
        try:
            import jsonschema
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("jsonschema dependency is required for KR-081 validation") from exc

        try:
            jsonschema.validate(instance=payload, schema=schema)
            logger.debug("contract_validation_ok", schema_key=schema_key, correlation_id=correlation_id)
            return ValidationResult(ok=True, schema_id=schema_key)
        except jsonschema.ValidationError as exc:
            error = ContractValidationError(
                "Contract validation failed",
                schema_id=schema_key,
                details={"message": str(exc.message), "path": list(exc.path), "schema_path": list(exc.schema_path)},
            )
            logger.warning(
                "contract_validation_failed",
                schema_key=schema_key,
                correlation_id=correlation_id,
                error=str(exc.message),
            )
            return ValidationResult(ok=False, schema_id=schema_key, error=error)

    def validate_or_raise(self, *, schema_key: str, payload: dict[str, Any]) -> None:
        """ContractValidatorPort uyumlu metot — başarısızsa fırlatır.

        Command handler'lar bu metodu çağırır:
          deps.contract_validator.validate(schema_key=..., payload=...)
        """
        result = self.validate(schema_key=schema_key, payload=payload)
        if not result.ok:
            raise result.error  # type: ignore[misc]
