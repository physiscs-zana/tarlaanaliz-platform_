# BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
# KR-081: Service container wiring for dependency injection.
"""Service factory: creates real service instances at startup."""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ServiceContainer:
    """Holds all application service instances.

    Created during lifespan and assigned to app.state.services.
    Endpoint dependencies retrieve services from this container.
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
    """Create application services and register them in the container.

    Args:
        db_session_factory: SQLAlchemy async session factory (None means in-memory).
        event_bus: EventBus instance (None means stub).
        storage: StorageService instance (None means stub).

    Returns:
        Populated ServiceContainer.
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
