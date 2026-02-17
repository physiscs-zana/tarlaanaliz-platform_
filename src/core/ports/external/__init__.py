# PATH: src/core/ports/external/__init__.py
# DESC: External ports module: dış servis entegrasyonları.
"""External service ports public API."""

from src.core.ports.external.ai_worker_feedback import (
    AIWorkerFeedback,
    FeedbackPipelineStatus,
    FeedbackSubmissionResult,
    TrainingDatasetExport,
)
from src.core.ports.external.ddos_protection import (
    DDoSProtection,
    IPAccessAction,
    IPAccessRule,
    IPAccessRuleResult,
    ProtectionStatus,
    SecurityEvent,
    SecurityEventAction,
    SecurityEventsPage,
    SecurityLevel,
    ZoneAnalytics,
)
from src.core.ports.external.parcel_geometry_provider import (
    ParcelGeometry,
    ParcelGeometryProvider,
    ParcelValidationResult,
)
from src.core.ports.external.payment_gateway import (
    PaymentGateway,
    PaymentSessionResponse,
    PaymentVerificationResult,
    RefundResult,
)
from src.core.ports.external.sms_gateway import (
    SmsBatchResult,
    SmsDeliveryStatus,
    SMSGateway,
    SmsResult,
)
from src.core.ports.external.storage_service import (
    BlobMetadata,
    PresignedUrl,
    StorageService,
)

__all__: list[str] = [
    # AI Worker Feedback (KR-019, KR-029)
    "AIWorkerFeedback",
    "BlobMetadata",
    # DDoS Protection
    "DDoSProtection",
    "FeedbackPipelineStatus",
    "FeedbackSubmissionResult",
    "IPAccessAction",
    "IPAccessRule",
    "IPAccessRuleResult",
    "ParcelGeometry",
    # Parcel Geometry (KR-013, KR-016)
    "ParcelGeometryProvider",
    "ParcelValidationResult",
    # Payment Gateway (KR-033)
    "PaymentGateway",
    "PaymentSessionResponse",
    "PaymentVerificationResult",
    "PresignedUrl",
    "ProtectionStatus",
    "RefundResult",
    # SMS Gateway
    "SMSGateway",
    "SecurityEvent",
    "SecurityEventAction",
    "SecurityEventsPage",
    "SecurityLevel",
    "SmsBatchResult",
    "SmsDeliveryStatus",
    "SmsResult",
    # Storage Service
    "StorageService",
    "TrainingDatasetExport",
    "ZoneAnalytics",
]
