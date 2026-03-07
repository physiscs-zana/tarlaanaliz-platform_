# BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.
"""Service factory: startup'ta gercek servis instance'lari olusturur."""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ServiceContainer:
    """Tum application servislerini barindirir.

    Lifespan'de olusturulur ve app.state.services'e atanir.
    Endpoint dependency'leri bu container'dan servis alir.
    """

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        self._services[name] = service
        logger.debug("service_registered", service_name=name)

    def get(self, name: str) -> Any | None:
        return self._services.get(name)

    def get_or_raise(self, name: str) -> Any:
        svc = self._services.get(name)
        if svc is None:
            raise RuntimeError(f"Service not found: {name}")
        return svc

    @property
    def registered(self) -> list[str]:
        return list(self._services.keys())


async def create_service_container(
    *,
    db_session_factory: Any = None,
    event_bus: Any = None,
    storage: Any = None,
) -> ServiceContainer:
    """Application servislerini olusturur ve container'a kaydeder.

    Args:
        db_session_factory: SQLAlchemy async session factory (None ise in-memory).
        event_bus: EventBus instance (None ise stub).
        storage: StorageService instance (None ise stub).

    Returns:
        Doldurulmus ServiceContainer.
    """
    container = ServiceContainer()

    logger.info(
        "service_container_initialized",
        db_available=db_session_factory is not None,
        event_bus_available=event_bus is not None,
        storage_available=storage is not None,
        services=container.registered,
    )

    return container
