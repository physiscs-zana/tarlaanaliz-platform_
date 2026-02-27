# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
"""API v1 router exports — all routers consolidated under endpoints/."""

from src.presentation.api.v1.endpoints import (
    admin_payments_router,
    calibration_router,
    payments_router,
    qc_router,
    sla_metrics_router,
)

__all__ = [
    "admin_payments_router",
    "calibration_router",
    "payments_router",
    "qc_router",
    "sla_metrics_router",
]
