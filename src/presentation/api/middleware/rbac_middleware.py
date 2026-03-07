# BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.
# KR-063: Merkezi RBAC middleware — her request'te rol kontrolu yapilir.
"""RBAC (Role-Based Access Control) middleware.

KR-063: Gercek yetki kontrolu backend'de yapilir.
Frontend RBAC'i gorsellestirme icindir.

Route prefix'lerine gore izin verilen rolleri kontrol eder.
Bypass route'lar (auth, health, docs) atlanir.
"""

from __future__ import annotations

from typing import Any

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = structlog.get_logger(__name__)


# Route prefix → izin verilen roller mapping'i
_ROUTE_ROLES: list[tuple[str, frozenset[str]]] = [
    # Admin endpoint'leri
    ("/api/v1/admin/", frozenset({"CENTRAL_ADMIN", "BILLING_ADMIN"})),
    # Expert portal
    ("/api/v1/expert/", frozenset({"EXPERT", "CENTRAL_ADMIN"})),
    # Ingest (edge kiosk) — mTLS ile de korumali
    ("/api/v1/ingest/", frozenset({"STATION_OPERATOR", "CENTRAL_ADMIN"})),
    # Pilot
    ("/api/v1/pilots", frozenset({"PILOT", "CENTRAL_ADMIN"})),
    # Weather block
    ("/api/v1/weather-block", frozenset({"PILOT", "CENTRAL_ADMIN"})),
    # QC + Calibration
    ("/api/v1/qc/", frozenset({"STATION_OPERATOR", "CENTRAL_ADMIN"})),
    ("/api/v1/calibration/", frozenset({"STATION_OPERATOR", "CENTRAL_ADMIN"})),
    # Training feedback
    ("/api/v1/training-feedback/", frozenset({"AI_SERVICE", "EXPERT", "CENTRAL_ADMIN"})),
    # Fields
    ("/api/v1/fields", frozenset({
        "FARMER_SINGLE", "FARMER_MEMBER", "COOP_OWNER", "COOP_ADMIN",
        "COOP_AGRONOMIST", "CENTRAL_ADMIN",
    })),
    # Missions
    ("/api/v1/missions", frozenset({
        "FARMER_SINGLE", "FARMER_MEMBER", "COOP_OWNER", "COOP_ADMIN",
        "PILOT", "CENTRAL_ADMIN",
    })),
    # Payments
    ("/api/v1/payments", frozenset({
        "FARMER_SINGLE", "FARMER_MEMBER", "COOP_OWNER",
        "BILLING_ADMIN", "CENTRAL_ADMIN",
    })),
    # Subscriptions
    ("/api/v1/subscriptions", frozenset({
        "FARMER_SINGLE", "FARMER_MEMBER", "COOP_OWNER", "COOP_ADMIN", "CENTRAL_ADMIN",
    })),
    # Results
    ("/api/v1/results", frozenset({
        "FARMER_SINGLE", "FARMER_MEMBER", "COOP_OWNER", "COOP_ADMIN",
        "COOP_AGRONOMIST", "EXPERT", "CENTRAL_ADMIN",
    })),
    # Parcels
    ("/api/v1/parcels", frozenset({
        "FARMER_SINGLE", "FARMER_MEMBER", "COOP_OWNER", "COOP_ADMIN",
        "COOP_AGRONOMIST", "CENTRAL_ADMIN",
    })),
]

_BYPASS_PREFIXES = (
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/",
    "/api/v1/pricing",  # public read-only
    "/api/v1/sla-metrics",  # monitoring
)


class RBACMiddleware(BaseHTTPMiddleware):
    """Merkezi rol tabanli erisim kontrolu (KR-063).

    JWT middleware'den sonra calisir.
    request.state.roles listesini _ROUTE_ROLES ile karsilastirir.
    Eslesme yoksa 403 Forbidden doner.
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        path = request.url.path

        # Bypass kontrol
        for prefix in _BYPASS_PREFIXES:
            if path.startswith(prefix):
                return await call_next(request)

        # OPTIONS preflight bypass
        if request.method == "OPTIONS":
            return await call_next(request)

        # JWT bypass ise (user yok) → bir sonraki middleware'e birak
        user = getattr(request.state, "user", None)
        if user is None:
            return await call_next(request)

        # Kullanici rolleri
        user_roles = set(getattr(request.state, "roles", []))

        # Route eslesmesi bul
        for route_prefix, allowed_roles in _ROUTE_ROLES:
            if path.startswith(route_prefix):
                if not user_roles.intersection(allowed_roles):
                    corr_id = getattr(request.state, "corr_id", "")
                    logger.warning(
                        "rbac_denied",
                        path=path,
                        user_roles=sorted(user_roles),
                        required_roles=sorted(allowed_roles),
                        corr_id=corr_id,
                    )
                    return JSONResponse(
                        status_code=403,
                        content={
                            "detail": "Forbidden — insufficient role",
                            "corr_id": corr_id,
                        },
                    )
                break  # Eslesme bulundu, izin verildi

        return await call_next(request)
