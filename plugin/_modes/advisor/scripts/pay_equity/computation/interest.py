"""Per-pay-period interest engine (R3 — F055).

For each pay period i in the retroactivity window:
    principal_i  = gap_per_hour × hours_worked_in_period_i
    days_i       = (calc_date - period_end_i).days
    interest_i   = principal_i × rate × (days_i / day_convention)
total_principal = Σ principal_i; total_interest = Σ interest_i.

Single-principal midpoint approximation is FORBIDDEN — CNESST disavows it.
Output is flagged [UNVERIFIED] by callers until the CNESST Excel
spreadsheet is matched against this engine.
"""
from __future__ import annotations

from datetime import date
from typing import Any


SIMPLE_INTEREST_RATE_ANNUAL = 0.05  # 5% per C.C.Q. art. 1617
DAY_CONVENTION_DEFAULT = 365  # Quebec legal default; configurable to 360 if Excel says so


def compute_period_interest(
    principal: float,
    days_elapsed: int,
    rate: float = SIMPLE_INTEREST_RATE_ANNUAL,
    day_convention: int = DAY_CONVENTION_DEFAULT,
) -> float:
    """Simple interest: principal × rate × (days_elapsed / day_convention)."""
    if days_elapsed < 0:
        return 0.0
    return principal * rate * (days_elapsed / day_convention)


def compute_per_pay_period_interest(
    gap_per_hour: float,
    pay_periods: list[dict[str, Any]],
    calc_date: date,
    rate: float = SIMPLE_INTEREST_RATE_ANNUAL,
    day_convention: int = DAY_CONVENTION_DEFAULT,
) -> dict[str, Any]:
    """Compute the per-pay-period interest for one gap.

    Each pay_period is `{period_start, period_end, hours}`. Returns:
      - total_principal (Σ gap × hours)
      - total_interest  (Σ interest_i)
      - day_convention, rate (for audit)
      - breakdown: list of dicts mirroring InterestBreakdownPeriod
    """
    breakdown: list[dict[str, Any]] = []
    total_principal = 0.0
    total_interest = 0.0
    for p in pay_periods:
        start = p["period_start"]
        end = p["period_end"]
        hours = float(p.get("hours", 0))
        if isinstance(start, str):
            start = date.fromisoformat(start)
        if isinstance(end, str):
            end = date.fromisoformat(end)

        principal = gap_per_hour * hours
        days = max((calc_date - end).days, 0)
        interest = compute_period_interest(principal, days, rate, day_convention)
        total_principal += principal
        total_interest += interest
        breakdown.append(
            {
                "period_start": start,
                "period_end": end,
                "hours_worked": hours,
                "gap_per_hour": gap_per_hour,
                "principal_period": principal,
                "days_elapsed": days,
                "interest_period": interest,
            }
        )

    return {
        "total_principal": total_principal,
        "total_interest": total_interest,
        "rate": rate,
        "day_convention": day_convention,
        "breakdown": breakdown,
    }


__all__ = [
    "DAY_CONVENTION_DEFAULT",
    "SIMPLE_INTEREST_RATE_ANNUAL",
    "compute_per_pay_period_interest",
    "compute_period_interest",
]
