# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
# KR-015: Replan queue worker delegates planning-safe reassignment.

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ReplanQueuePort(Protocol):
    def dequeue(self) -> dict[str, str] | None: ...


class ReplanServicePort(Protocol):
    def replan(self, *, mission_id: str, correlation_id: str) -> None: ...


@dataclass(slots=True)
class ReplanQueueWorker:
    queue_port: ReplanQueuePort
    replan_service: ReplanServicePort

    def run_once(self) -> bool:
        message = self.queue_port.dequeue()
        if message is None:
            return False

        mission_id = message.get("mission_id")
        if not mission_id:
            return False

        correlation_id = message.get("correlation_id", "")
        self.replan_service.replan(mission_id=mission_id, correlation_id=correlation_id)
        return True
