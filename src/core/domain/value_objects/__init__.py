# PATH: src/core/domain/value_objects/__init__.py
# DESC: Domain value object module: __init__.py.
"""Domain Value Objects public API."""

from src.core.domain.value_objects.money import CurrencyCode, Money
from src.core.domain.value_objects.parcel_ref import ParcelRef
from src.core.domain.value_objects.payment_status import (
    TERMINAL_PAYMENT_STATUSES,
    VALID_PAYMENT_TRANSITIONS,
    PaymentStatus,
    is_valid_payment_transition,
    requires_payment_intent,
)
from src.core.domain.value_objects.price_snapshot import PriceSnapshotRef
from src.core.domain.value_objects.province import VALID_PROVINCE_CODES, Province
from src.core.domain.value_objects.qc_flag import QCFlag, QCFlagSeverity, QCFlagType
from src.core.domain.value_objects.qc_report import QCReport
from src.core.domain.value_objects.qc_status import (
    QCRecommendedAction,
    QCStatus,
    is_qc_blocking,
    is_qc_passable,
)
from src.core.domain.value_objects.recommended_action import (
    RecommendedAction,
    RecommendedActionError,
)
from src.core.domain.value_objects.role import Role, RoleError
from src.core.domain.value_objects.sla_metrics import SLAMetrics, SLAMetricsError
from src.core.domain.value_objects.sla_threshold import SLAThreshold, SLAThresholdError
from src.core.domain.value_objects.specialization import (
    SPECIALIZATION_DISPLAY_NAMES,
    SPECIALIZATION_LAYER_MAPPINGS,
    Specialization,
    get_related_layer_codes,
    get_specialization_display_name,
    matches_finding_code,
)
from src.core.domain.value_objects.subscription_plan import (
    SubscriptionPlan,
    SubscriptionPlanError,
)
from src.core.domain.value_objects.training_grade import TrainingGrade, TrainingGradeError
from src.core.domain.value_objects.weather_block_status import (
    TERMINAL_WEATHER_BLOCK_STATUSES,
    VALID_WEATHER_BLOCK_TRANSITIONS,
    WeatherBlockStatus,
    is_blocking_mission,
    is_force_majeure,
    is_valid_weather_block_transition,
)

__all__: list[str] = [
    "SPECIALIZATION_DISPLAY_NAMES",
    "SPECIALIZATION_LAYER_MAPPINGS",
    "TERMINAL_PAYMENT_STATUSES",
    "TERMINAL_WEATHER_BLOCK_STATUSES",
    "VALID_PAYMENT_TRANSITIONS",
    "VALID_PROVINCE_CODES",
    "VALID_WEATHER_BLOCK_TRANSITIONS",
    # money
    "CurrencyCode",
    "Money",
    # parcel_ref
    "ParcelRef",
    # payment_status
    "PaymentStatus",
    # price_snapshot
    "PriceSnapshotRef",
    # province
    "Province",
    # qc_flag
    "QCFlag",
    "QCFlagSeverity",
    "QCFlagType",
    # qc_status
    "QCRecommendedAction",
    # qc_report
    "QCReport",
    "QCStatus",
    # recommended_action
    "RecommendedAction",
    "RecommendedActionError",
    # role
    "Role",
    "RoleError",
    # sla_metrics
    "SLAMetrics",
    "SLAMetricsError",
    # sla_threshold
    "SLAThreshold",
    "SLAThresholdError",
    # specialization
    "Specialization",
    # subscription_plan
    "SubscriptionPlan",
    "SubscriptionPlanError",
    # training_grade
    "TrainingGrade",
    "TrainingGradeError",
    # weather_block_status
    "WeatherBlockStatus",
    "get_related_layer_codes",
    "get_specialization_display_name",
    "is_blocking_mission",
    "is_force_majeure",
    "is_qc_blocking",
    "is_qc_passable",
    "is_valid_payment_transition",
    "is_valid_weather_block_transition",
    "matches_finding_code",
    "requires_payment_intent",
]
