"""adjustments.json — dollar gaps + payment schedule + per-period interest breakdown.

Source: phase4 § 4.1.5 + R3 per-pay-period interest engine.
"""
from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

from scripts.pay_equity.models.compensation import ComparisonMethodLiteral  # noqa: F401


class InterestBreakdownPeriod(BaseModel):
    """R3 — one row per pay period in the retroactivity window.

    Attached to RetroactiveEvent or to ClassAdjustment when `is_retroactive=True`.
    """

    period_start: date
    period_end: date
    hours_worked: float = Field(ge=0)
    gap_per_hour: float
    principal_period: float  # gap_per_hour × hours_worked
    days_elapsed: int = Field(ge=0)  # period_end → calc_date (or first_payment_date)
    interest_period: float  # principal × rate × (days/365)


class RetroactiveEvent(BaseModel):
    """Per-event retroactive record for maintenance audits — Bill 10."""

    event_type: str  # e.g., "new_class", "compensation_change", "restructuring"
    event_date: date
    affected_class_ids: list[str] = Field(default_factory=list)
    gap_hourly_at_event: float
    simple_interest_rate: float = 0.05  # 5% per C.C.Q. art. 1617
    interest_breakdown: list[InterestBreakdownPeriod] = Field(default_factory=list)  # R3
    interest_accrued: float = 0.0  # Σ interest_breakdown[].interest_period
    total_retroactive_amount: float = 0.0  # Σ principal_period + interest_accrued


class ClassAdjustment(BaseModel):
    class_id: str
    title: str
    gap_hourly: float
    gap_annual: float  # gap_hourly × annual_hours (per class actual hours)
    annual_adjustment: float  # per-employee annual cost
    total_class_cost: float  # annual_adjustment × incumbents
    incumbents: int = Field(ge=0)
    annual_hours: float = Field(ge=0)  # actual; not assumed 1950
    interest_breakdown: list[InterestBreakdownPeriod] = Field(default_factory=list)


class PaymentScheduleYear(BaseModel):
    year: int = Field(ge=1, le=4)  # Art. 76.5.1: max 4 years (5 installments)
    date: date
    percentage: float
    amount_per_employee: float
    cumulative_percentage: float


class AdjustmentFile(BaseModel):
    client_slug: str
    schedule_type: Literal["lump_sum", "installments"]
    num_years: int = Field(ge=1, le=4)
    first_payment_date: date
    class_adjustments: list[ClassAdjustment] = Field(default_factory=list)
    payment_schedule: list[PaymentScheduleYear] = Field(default_factory=list)
    total_annual_cost: float = 0.0
    total_multi_year_cost: float = 0.0
    interest_rate: float = 0.05  # simple interest, C.C.Q. art. 1617
    day_convention: int = 365  # default per R3; configurable
    is_retroactive: bool = False
    retroactive_events: list[RetroactiveEvent] = Field(default_factory=list)
    retroactivity_start_date: Optional[date] = None  # R3 — required for late/maintien
    last_updated: Optional[date] = None
    stale: bool = False
    stale_reason: Optional[str] = None


__all__ = [
    "AdjustmentFile",
    "ClassAdjustment",
    "InterestBreakdownPeriod",
    "PaymentScheduleYear",
    "RetroactiveEvent",
]
