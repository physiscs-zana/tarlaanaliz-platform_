# PATH: src/core/__init__.py
"""
Core package public API.

Domain katmanı ve port interface'lerinin tek giriş noktası.
Dış dünya erişimi (IO, veritabanı, HTTP) bu katmanda YOKTUR.

Alt paketler:
  - domain.entities: Aggregate root ve entity tanımları.
  - domain.value_objects: Immutable değer nesneleri.
  - domain.services: Domain servisleri (saf iş kuralları).
  - domain.events: Domain event tanımları.
  - ports.external: Dış servis port interface'leri.
  - ports.messaging: Event publish/subscribe port interface'leri.
  - ports.repositories: Veri erişim port interface'leri.

SSOT: KR-015, KR-018, KR-033, KR-081 ile tutarlı.
"""

# -- Domain Entities --
from src.core.domain.entities import (
    AnalysisJob,
    AnalysisResult,
    AuditLogEntry,
    CalibrationRecord,
    Expert,
    ExpertReview,
    FeedbackRecord,
    Field,
    Mission,
    PaymentIntent,
    Pilot,
    PriceSnapshot,
    QCReportRecord,
    Subscription,
    User,
    UserPII,
    WeatherBlockReport,
)

# -- Domain Events --
from src.core.domain.events import (
    AnalysisCompleted,
    AnalysisFailed,
    AnalysisRequested,
    AnalysisStarted,
    CalibrationValidated,
    DataUploaded,
    DomainEvent,
    ExpertActivated,
    ExpertDeactivated,
    ExpertRegistered,
    ExpertReviewAssigned,
    ExpertReviewCompleted,
    ExpertReviewEscalated,
    ExpertReviewRequested,
    FeedbackProvided,
    FieldCreated,
    FieldCropUpdated,
    FieldDeleted,
    FieldUpdated,
    LowConfidenceDetected,
    MissionAnalysisRequested,
    MissionAssigned,
    MissionCancelled,
    MissionCompleted,
    MissionReplanQueued,
    MissionScheduled,
    MissionStarted,
    PaymentApproved,
    PaymentIntentCreated,
    PaymentRejected,
    ReceiptUploaded,
    SubscriptionActivated,
    SubscriptionCompleted,
    SubscriptionCreated,
    SubscriptionRescheduled,
    TrainingDataExported,
    TrainingFeedbackAccepted,
    TrainingFeedbackRejected,
    TrainingFeedbackSubmitted,
)

# -- External Ports --
from src.core.ports.external import (
    AIWorkerFeedback,
    BlobMetadata,
    FeedbackPipelineStatus,
    FeedbackSubmissionResult,
    ParcelGeometry,
    ParcelGeometryProvider,
    ParcelValidationResult,
    PaymentGateway,
    PaymentSessionResponse,
    PaymentVerificationResult,
    PresignedUrl,
    RefundResult,
    SmsBatchResult,
    SmsDeliveryStatus,
    SMSGateway,
    SmsResult,
    StorageService,
    TrainingDatasetExport,
)

# -- Messaging Ports --
from src.core.ports.messaging import EventBus, EventHandler

# -- Repository Ports --
from src.core.ports.repositories import (
    AnalysisResultRepository,
    AuditLogRepository,
    CalibrationRecordRepository,
    ExpertRepository,
    ExpertReviewRepository,
    FeedbackRecordRepository,
    FieldRepository,
    MissionRepository,
    PaymentIntentRepository,
    PilotRepository,
    PriceSnapshotRepository,
    QCReportRepository,
    SubscriptionRepository,
    UserRepository,
    WeatherBlockReportRepository,
    WeatherBlockRepository,
)

__all__: list[str] = [
    # -- External Ports --
    "AIWorkerFeedback",
    "AnalysisCompleted",
    "AnalysisFailed",
    # -- Domain Entities --
    "AnalysisJob",
    "AnalysisRequested",
    "AnalysisResult",
    # -- Repository Ports --
    "AnalysisResultRepository",
    "AnalysisStarted",
    "AuditLogEntry",
    "AuditLogRepository",
    "BlobMetadata",
    "CalibrationRecord",
    "CalibrationRecordRepository",
    "CalibrationValidated",
    "DataUploaded",
    # -- Domain Events --
    "DomainEvent",
    # -- Messaging Ports --
    "EventBus",
    "EventHandler",
    "Expert",
    "ExpertActivated",
    "ExpertDeactivated",
    "ExpertRegistered",
    "ExpertRepository",
    "ExpertReview",
    "ExpertReviewAssigned",
    "ExpertReviewCompleted",
    "ExpertReviewEscalated",
    "ExpertReviewRepository",
    "ExpertReviewRequested",
    "FeedbackPipelineStatus",
    "FeedbackProvided",
    "FeedbackRecord",
    "FeedbackRecordRepository",
    "FeedbackSubmissionResult",
    "Field",
    "FieldCreated",
    "FieldCropUpdated",
    "FieldDeleted",
    "FieldRepository",
    "FieldUpdated",
    "LowConfidenceDetected",
    "Mission",
    "MissionAnalysisRequested",
    "MissionAssigned",
    "MissionCancelled",
    "MissionCompleted",
    "MissionReplanQueued",
    "MissionRepository",
    "MissionScheduled",
    "MissionStarted",
    "ParcelGeometry",
    "ParcelGeometryProvider",
    "ParcelValidationResult",
    "PaymentApproved",
    "PaymentGateway",
    "PaymentIntent",
    "PaymentIntentCreated",
    "PaymentIntentRepository",
    "PaymentRejected",
    "PaymentSessionResponse",
    "PaymentVerificationResult",
    "Pilot",
    "PilotRepository",
    "PresignedUrl",
    "PriceSnapshot",
    "PriceSnapshotRepository",
    "QCReportRecord",
    "QCReportRepository",
    "ReceiptUploaded",
    "RefundResult",
    "SMSGateway",
    "SmsBatchResult",
    "SmsDeliveryStatus",
    "SmsResult",
    "StorageService",
    "Subscription",
    "SubscriptionActivated",
    "SubscriptionCompleted",
    "SubscriptionCreated",
    "SubscriptionRepository",
    "SubscriptionRescheduled",
    "TrainingDataExported",
    "TrainingDatasetExport",
    "TrainingFeedbackAccepted",
    "TrainingFeedbackRejected",
    "TrainingFeedbackSubmitted",
    "User",
    "UserPII",
    "UserRepository",
    "WeatherBlockReport",
    "WeatherBlockReportRepository",
    "WeatherBlockRepository",
]
