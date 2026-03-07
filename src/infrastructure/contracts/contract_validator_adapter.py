# BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.
# KR-081: Adapter bridging ContractValidatorService to ContractValidatorPort protocol.
"""
ContractValidatorPort uyumlu adaptör.

Command handler'lar ContractValidatorPort protocol'ünü kullanır:
    validate(*, schema_key: str, payload: dict) -> None

Bu adaptör, infrastructure SchemaRegistry + application ContractValidatorService
kullanarak bu protocol'ü karşılar.
"""

from __future__ import annotations

from typing import Any

from src.application.services.contract_validator_service import ContractValidatorService


class ContractValidatorAdapter:
    """ContractValidatorPort protocol implementasyonu.

    Command Deps'lerine enjekte edilir.
    """

    def __init__(self, service: ContractValidatorService) -> None:
        self._service = service

    def validate(self, *, schema_key: str, payload: dict[str, Any]) -> None:
        """ContractValidatorPort.validate uyumu — hata fırlatır."""
        self._service.validate_or_raise(schema_key=schema_key, payload=payload)
