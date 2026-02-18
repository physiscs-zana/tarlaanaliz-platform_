# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
# KR-033: Application-level audit append service.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class AuditLogPort(Protocol):
    def append(self, *, event_type: str, correlation_id: str, payload: dict[str, Any]) -> None: ...


@dataclass(frozen=True, slots=True)
class AuditEntry:
    event_type: str
    correlation_id: str
    payload: dict[str, Any]


@dataclass(slots=True)
class AuditLogService:
    audit_port: AuditLogPort

    def append(self, entry: AuditEntry) -> None:
        # KR-033: Record auditable action with correlation.
        self.audit_port.append(
            event_type=entry.event_type,
            correlation_id=entry.correlation_id,
            payload=entry.payload,
        )
