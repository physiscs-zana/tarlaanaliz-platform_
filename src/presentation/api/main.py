# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.  # noqa: RUF003
"""FastAPI application entrypoint for presentation API."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.presentation.api.middleware._shared import ensure_request_context
from src.presentation.api.middleware.anomaly_detection_middleware import AnomalyDetectionMiddleware
from src.presentation.api.middleware.cors_middleware import add_cors_middleware
from src.presentation.api.middleware.jwt_middleware import JwtMiddleware
from src.presentation.api.middleware.rate_limit_middleware import RateLimitMiddleware
from src.presentation.api.settings import settings
from src.presentation.api.v1.endpoints import (
    admin_audit_router,
    admin_pricing_router,
    auth_router,
    expert_portal_router,
    experts_router,
    fields_router,
    missions_router,
    parcels_router,
    payment_webhooks_router,
)

LOGGER = logging.getLogger("api.main")


def _safe_error(detail: str, corr_id: str, status_code: int) -> JSONResponse:
    response = JSONResponse(status_code=status_code, content={"detail": detail})
    response.headers["X-Correlation-Id"] = corr_id
    return response


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        _ = exc
        corr_id, _ = ensure_request_context(request)
        return _safe_error("Validation error", corr_id=corr_id, status_code=422)

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        corr_id, _ = ensure_request_context(request)
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return _safe_error(detail, corr_id=corr_id, status_code=exc.status_code)

    @app.exception_handler(Exception)
    async def handle_uncaught_exception(request: Request, exc: Exception) -> JSONResponse:
        corr_id, _ = ensure_request_context(request)
        LOGGER.exception("Unhandled exception", extra={"corr_id": corr_id, "event": "api_unhandled_exception"})
        _ = exc
        return _safe_error("Internal server error", corr_id=corr_id, status_code=500)


def _register_middlewares(app: FastAPI) -> None:
    add_cors_middleware(app)
    app.add_middleware(JwtMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AnomalyDetectionMiddleware)

    @app.middleware("http")
    async def correlation_middleware(request: Request, call_next: Callable[[Request], Any]) -> JSONResponse:
        corr_id, _ = ensure_request_context(request)
        response = await call_next(request)
        response.headers["X-Correlation-Id"] = corr_id
        return response


def _register_routers(app: FastAPI) -> None:
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(fields_router, prefix="/api/v1")
    app.include_router(parcels_router, prefix="/api/v1")
    app.include_router(missions_router, prefix="/api/v1")
    app.include_router(experts_router, prefix="/api/v1")
    app.include_router(expert_portal_router, prefix="/api/v1")
    app.include_router(payment_webhooks_router, prefix="/api/v1")
    app.include_router(admin_pricing_router, prefix="/api/v1")
    app.include_router(admin_audit_router, prefix="/api/v1")


def create_app() -> FastAPI:
    app = FastAPI(
        title=os.getenv("API_TITLE", "TarlaAnaliz Platform API"),
        version=os.getenv("API_VERSION", "1.0.0"),
        docs_url=os.getenv("API_DOCS_URL", "/docs"),
        redoc_url=os.getenv("API_REDOC_URL", "/redoc"),
        openapi_url=os.getenv("API_OPENAPI_URL", "/openapi.json"),
    )

    _ = settings

    @app.on_event("startup")
    async def on_startup() -> None:
        LOGGER.info("API startup completed", extra={"event": "api_startup"})

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        LOGGER.info("API shutdown completed", extra={"event": "api_shutdown"})

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    _register_exception_handlers(app)
    _register_middlewares(app)
    _register_routers(app)
    return app


app = create_app()
