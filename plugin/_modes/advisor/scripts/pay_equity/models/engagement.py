"""engagement.json — top-level engagement state.

Sources: phase4 § 4.1.1 + R5 data-model additions + R7 deadline computations + R8 100+
guided gates. Field names match the spec exactly.
"""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class SizeTier(str, Enum):
    SMALL = "10-49"
    MEDIUM = "50-99"
    LARGE = "100+"


class ExerciseType(str, Enum):
    INITIAL = "initial"
    MAINTENANCE = "maintenance"


class OperatorMode(str, Enum):
    """Operator mode set at engagement creation. 100+ guided triggers extra gates (R8)."""

    EXPERT = "expert"
    GUIDED = "guided"


class MaintienMode(str, Enum):
    """Mode for the maintien (5-year audit) — R5 + R7 participation trigger logic."""

    EMPLOYER_SOLO = "employer_solo"
    EMPLOYER_SOLO_WITH_PARTICIPATION = "employer_solo_with_participation"
    COMMITTEE = "committee"
    JOINT_WITH_UNION = "joint_with_union"


class PayPeriodFrequency(str, Enum):
    """R3 / R5 — required for per-pay-period interest engine."""

    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    SEMI_MONTHLY = "semi_monthly"
    MONTHLY = "monthly"


class Establishment(BaseModel):
    name: str
    location: str
    employee_count: int = Field(ge=1)


class PostingLocation(BaseModel):
    """R5 — list per establishment of posting medium and physical/digital location."""

    establishment_id: str
    posting_method: Literal["physical", "digital"]
    location: Optional[str] = None  # physical address or URL
    posted_date: Optional[date] = None


class PriorPosting(BaseModel):
    """R5 — record of all prior cycle postings for maintien continuity."""

    cycle: str  # e.g., "initial-2018", "maintien-2023"
    posting_date: date
    posting_type: Literal[
        "interim",
        "final",
        "maintien",
        "nouvel_affichage_initial",
        "nouvel_affichage_maintien",
    ]
    notes: Optional[str] = None


EngagementStatus = Literal[
    "created",
    "job_classes_defined",
    "evaluation_complete",
    "comparison_complete",
    "adjustments_calculated",
    "finalized",
]

ComparisonMethod = Literal["job_to_job", "regression", "hybrid", "global"]


class Engagement(BaseModel):
    """engagement.json — root engagement record.

    Per R5 / R7, deadline fields are computed at create time. Per R8 100+ guided gates
    are flagged elsewhere; this model only stores the raw flags needed for that logic.
    """

    # --- Identity ----------------------------------------------------------
    client_name: str
    client_slug: str  # URL-safe; auto-generated
    neq: Optional[str] = None  # R5 — Quebec NEQ; required at intake
    employee_count: int = Field(ge=10)
    size_tier: SizeTier
    exercise_type: ExerciseType
    operator_mode: OperatorMode = OperatorMode.EXPERT
    has_union: bool = False
    establishments: list[Establishment] = Field(default_factory=list)

    # --- Maintien-specific (R5 + R7) ---------------------------------------
    maintien_mode: Optional[MaintienMode] = None
    pay_period_frequency: Optional[PayPeriodFrequency] = None  # required 50+; R3 engine
    initial_had_committee: bool = False  # R7 participation trigger
    has_accredited_association: bool = False  # R7 participation trigger
    intended_maintien_mode: Optional[MaintienMode] = None  # operator-stated intent
    participation_required: bool = False  # computed by tool

    # --- Reference / data periods (R5) -------------------------------------
    data_period_start: Optional[date] = None
    data_period_end: Optional[date] = None

    # --- Deadlines (R5 + R7) -----------------------------------------------
    statutory_deadline: Optional[date] = None  # initial: 4y; maintien: 5y anniversary
    initial_exercise_deadline: Optional[date] = None  # Dec 31 of (threshold_reach_year + 4)
    document_retention_until: Optional[date] = None  # posting_date + 6 years (Loi 25)

    # --- Posting record (R5) -----------------------------------------------
    posting_locations: list[PostingLocation] = Field(default_factory=list)
    prior_postings_log: list[PriorPosting] = Field(default_factory=list)

    # --- Lifecycle ---------------------------------------------------------
    created_date: Optional[date] = None
    status: EngagementStatus = "created"
    comparison_method: Optional[ComparisonMethod] = None
    notes: list[str] = Field(default_factory=list)

    # --- Stale tracking (phase4 § 3.5) -------------------------------------
    stale_files: list[str] = Field(default_factory=list)
    stale_reasons: dict[str, str] = Field(default_factory=dict)


__all__ = [
    "ComparisonMethod",
    "Engagement",
    "EngagementStatus",
    "Establishment",
    "ExerciseType",
    "MaintienMode",
    "OperatorMode",
    "PayPeriodFrequency",
    "PostingLocation",
    "PriorPosting",
    "SizeTier",
]
