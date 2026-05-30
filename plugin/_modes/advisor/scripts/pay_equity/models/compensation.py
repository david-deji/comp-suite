"""compensation.json — per-class compensation + comparison results.

Source: phase4 § 4.1.4 + R5 hours-by-period granularity.
"""
from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

from scripts.pay_equity.models.job_class import Predominance


ComparisonMethodLiteral = Literal[
    "job_to_job", "regression", "hybrid", "global", "global_unverified"
]
DataStatusLiteral = Literal["VERIFIED", "UNVERIFIED"]


class CompensationComponent(BaseModel):
    """All hourly. `total_compensation_hourly` is the computed sum."""

    base_salary_hourly: float
    bonuses_commissions: float = 0.0
    shift_differentials: float = 0.0
    group_insurance_employer: float = 0.0
    pension_employer: float = 0.0
    paid_leave_above_statutory: float = 0.0
    other_monetary: float = 0.0
    total_compensation_hourly: float = 0.0  # computed sum of components


class HoursWorkedPeriod(BaseModel):
    """R5 — granular hours per pay period for the per-pay-period interest engine."""

    period_start: date
    period_end: date
    hours: float = Field(ge=0)
    includes_overtime: bool = False
    includes_paid_leave: bool = False


class HoursWorked(BaseModel):
    """R5 — replaces the single annual_hours field with per-period detail."""

    annual_baseline: float = Field(ge=0)
    by_period: list[HoursWorkedPeriod] = Field(default_factory=list)
    overtime_total: float = 0.0
    paid_absences_total: float = 0.0


class ClassCompensation(BaseModel):
    class_id: str
    predominance: Predominance
    evaluation_score: float
    grade: int
    components: CompensationComponent
    hours_worked: Optional[HoursWorked] = None  # required for late or maintien retro
    is_comparator: bool = False


class ComparisonResult(BaseModel):
    female_class_id: str
    male_comparator_id: Optional[str] = None  # null if regression / global used
    comparison_method: ComparisonMethodLiteral
    female_compensation: float
    male_compensation: float  # actual or regression-predicted
    gap_hourly: float  # male - female (positive = underpaid)
    gap_percentage: float  # gap / male * 100
    requires_adjustment: Optional[bool]  # None when data_status=UNVERIFIED
    data_status: DataStatusLiteral = "VERIFIED"


class RegressionResult(BaseModel):
    intercept: float
    slope: float
    r_squared: float
    data_points: int
    male_classes_used: list[str] = Field(default_factory=list)
    outlier_class_ids: list[str] = Field(default_factory=list)  # residuals > 2 SD
    quality_assessment: Literal["good", "acceptable", "poor"]
    quality_notes: str = ""


class GlobalComparisonResult(BaseModel):
    """RLRQ E-12.001 r.2 — used when no male job classes exist."""

    reference_category_1: str = "Contremaître"
    reference_category_2: str = "Préposé à la maintenance"
    prescribed_ratio: float = 0.60
    reference_compensation: float = 0.0
    note: str = (
        "Prescribed comparison per RLRQ E-12.001 r.2 — enterprise has no male job classes"
    )
    data_status: DataStatusLiteral = "VERIFIED"
    note_unverified: Optional[str] = None  # populated when data_status=UNVERIFIED


class CompensationFile(BaseModel):
    client_slug: str
    method: ComparisonMethodLiteral = "hybrid"
    class_compensations: list[ClassCompensation] = Field(default_factory=list)
    comparison_results: list[ComparisonResult] = Field(default_factory=list)
    regression: Optional[RegressionResult] = None
    global_comparison: Optional[GlobalComparisonResult] = None
    total_gap_annual: Optional[float] = None
    last_updated: Optional[date] = None
    stale: bool = False
    stale_reason: Optional[str] = None


__all__ = [
    "ClassCompensation",
    "ComparisonMethodLiteral",
    "ComparisonResult",
    "CompensationComponent",
    "CompensationFile",
    "DataStatusLiteral",
    "GlobalComparisonResult",
    "HoursWorked",
    "HoursWorkedPeriod",
    "RegressionResult",
]
