# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
# KR-081: Contract-first validation is mandatory before orchestration.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class JsonSchemaPort(Protocol):
    def validate(self, *, schema_name: str, payload: dict[str, Any]) -> None: ...


@dataclass(slots=True)
class ContractValidatorService:
    schema_port: JsonSchemaPort

    def validate_payload(self, *, schema_name: str, payload: dict[str, Any]) -> None:
        # KR-081: Validate schema contract before state transition.
        self.schema_port.validate(schema_name=schema_name, payload=payload)
