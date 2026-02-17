# PATH: src/core/domain/events/__init__.py
# DESC: Domain events module: __init__.py.

from src.core.domain.events.analysis_events import (
    AnalysisCompleted,
    AnalysisFailed,
    AnalysisRequested,
    AnalysisStarted,
    CalibrationValidated,
    LowConfidenceDetected,
)
from src.core.domain.events.base import DomainEvent
from src.core.domain.events.expert_events import (
    ExpertActivated,
    ExpertDeactivated,
    ExpertRegistered,
    FeedbackProvided,
)
from src.core.domain.events.expert_review_events import (
    ExpertReviewAssigned,
    ExpertReviewCompleted,
    ExpertReviewEscalated,
    ExpertReviewRequested,
)
from src.core.domain.events.field_events import (
    FieldCreated,
    FieldCropUpdated,
    FieldDeleted,
    FieldUpdated,
)
from src.core.domain.events.mission_events import (
    DataUploaded,
    MissionAnalysisRequested,
    MissionAssigned,
    MissionCancelled,
    MissionCompleted,
    MissionReplanQueued,
    MissionStarted,
)
from src.core.domain.events.payment_events import (
    PaymentApproved,
    PaymentIntentCreated,
    PaymentRejected,
    ReceiptUploaded,
)
from src.core.domain.events.subscription_events import (
    MissionScheduled,
    SubscriptionActivated,
    SubscriptionCompleted,
    SubscriptionCreated,
    SubscriptionRescheduled,
)
from src.core.domain.events.training_feedback_events import (
    TrainingDataExported,
    TrainingFeedbackAccepted,
    TrainingFeedbackRejected,
    TrainingFeedbackSubmitted,
)

__all__: list[str] = [
    "AnalysisCompleted",
    "AnalysisFailed",
    # Analysis (KR-017, KR-018)
    "AnalysisRequested",
    "AnalysisStarted",
    "CalibrationValidated",
    "DataUploaded",
    # Base
    "DomainEvent",
    "ExpertActivated",
    "ExpertDeactivated",
    # Expert (KR-019)
    "ExpertRegistered",
    "ExpertReviewAssigned",
    "ExpertReviewCompleted",
    "ExpertReviewEscalated",
    # Expert Review (KR-019)
    "ExpertReviewRequested",
    "FeedbackProvided",
    # Field
    "FieldCreated",
    "FieldCropUpdated",
    "FieldDeleted",
    "FieldUpdated",
    "LowConfidenceDetected",
    "MissionAnalysisRequested",
    # Mission (KR-015)
    "MissionAssigned",
    "MissionCancelled",
    "MissionCompleted",
    "MissionReplanQueued",
    "MissionScheduled",
    "MissionStarted",
    "PaymentApproved",
    # Payment (KR-033)
    "PaymentIntentCreated",
    "PaymentRejected",
    "ReceiptUploaded",
    "SubscriptionActivated",
    "SubscriptionCompleted",
    # Subscription (KR-015-5)
    "SubscriptionCreated",
    "SubscriptionRescheduled",
    "TrainingDataExported",
    "TrainingFeedbackAccepted",
    "TrainingFeedbackRejected",
    # Training Feedback (KR-019)
    "TrainingFeedbackSubmitted",
]
