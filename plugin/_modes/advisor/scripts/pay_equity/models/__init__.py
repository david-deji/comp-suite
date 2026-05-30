"""Pydantic v2 models for all engagement JSON files.

Canonical source of truth — every JSON file in an engagement directory
serializes from one of these models. All field names match phase4 § 4.1
(plus R3-R9 / R5 / R8 additions).
"""
from scripts.pay_equity.models.engagement import (
    Engagement,
    Establishment,
    ExerciseType,
    MaintienMode,
    OperatorMode,
    PayPeriodFrequency,
    PostingLocation,
    PriorPosting,
    SizeTier,
)
from scripts.pay_equity.models.job_class import (
    JobClass,
    JobClassesFile,
    Predominance,
    PredominanceMethod,
    PredominanceOverrideEvidence,
)
from scripts.pay_equity.models.evaluation import (
    ClassScore,
    EvaluationFile,
    EvaluationGrid,
    SubFactor,
)
from scripts.pay_equity.models.compensation import (
    ClassCompensation,
    ComparisonResult,
    CompensationComponent,
    CompensationFile,
    GlobalComparisonResult,
    HoursWorked,
    HoursWorkedPeriod,
    RegressionResult,
)
from scripts.pay_equity.models.adjustment import (
    AdjustmentFile,
    ClassAdjustment,
    InterestBreakdownPeriod,
    PaymentScheduleYear,
    RetroactiveEvent,
)
from scripts.pay_equity.models.participation import (
    MaintenanceCommittee,
    ParticipationSession,
    RetentionPolicy,
)
from scripts.pay_equity.models.observation import (
    Observation,
    ObservationCategory,
    ObservationsFile,
)
from scripts.pay_equity.models.obligations import get_obligations_matrix

__all__ = [
    # engagement
    "Engagement",
    "Establishment",
    "ExerciseType",
    "MaintienMode",
    "OperatorMode",
    "PayPeriodFrequency",
    "PostingLocation",
    "PriorPosting",
    "SizeTier",
    # job_class
    "JobClass",
    "JobClassesFile",
    "Predominance",
    "PredominanceMethod",
    "PredominanceOverrideEvidence",
    # evaluation
    "ClassScore",
    "EvaluationFile",
    "EvaluationGrid",
    "SubFactor",
    # compensation
    "ClassCompensation",
    "ComparisonResult",
    "CompensationComponent",
    "CompensationFile",
    "GlobalComparisonResult",
    "HoursWorked",
    "HoursWorkedPeriod",
    "RegressionResult",
    # adjustment
    "AdjustmentFile",
    "ClassAdjustment",
    "InterestBreakdownPeriod",
    "PaymentScheduleYear",
    "RetroactiveEvent",
    # participation
    "MaintenanceCommittee",
    "ParticipationSession",
    "RetentionPolicy",
    # observation
    "Observation",
    "ObservationCategory",
    "ObservationsFile",
    # obligations
    "get_obligations_matrix",
]
