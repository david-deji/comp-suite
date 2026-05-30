"""Multi-year payment schedule builder (F058).

Lump sum: single year at 100% on first_payment_date.
Installments: equal-split across num_years (anniversary of first_payment_date),
or operator-defined percentages summing to 100%. Capped at 4 years per Art. 76.5.1.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional


MAX_INSTALLMENT_YEARS = 4  # Art. 76.5.1


def _add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        # Feb 29 → Feb 28 fallback.
        return d.replace(year=d.year + years, day=28)


def build_payment_schedule(
    annual_adjustment_per_employee: float,
    schedule_type: str,
    num_years: int,
    first_payment_date: date,
    custom_percentages: Optional[list[float]] = None,
) -> list[dict[str, Any]]:
    """Build the per-year payment schedule.

    Returns a list of dicts shaped like PaymentScheduleYear:
      {year, date, percentage, amount_per_employee, cumulative_percentage}.
    The total of all `amount_per_employee` equals the cumulative annual_adjustment
    over num_years.
    """
    if schedule_type == "lump_sum":
        total = annual_adjustment_per_employee * 1
        return [
            {
                "year": 1,
                "date": first_payment_date,
                "percentage": 100.0,
                "amount_per_employee": total,
                "cumulative_percentage": 100.0,
            }
        ]
    if schedule_type != "installments":
        raise ValueError(
            f"schedule_type={schedule_type!r} not in ('lump_sum', 'installments')"
        )
    if num_years < 1 or num_years > MAX_INSTALLMENT_YEARS:
        raise ValueError(
            f"num_years={num_years} outside [1, {MAX_INSTALLMENT_YEARS}] (Art. 76.5.1)"
        )

    # Total per-employee cost over the installment period equals annual_adjustment
    # × num_years (each year carries an additional year's worth of adjustment).
    total_per_employee = annual_adjustment_per_employee * num_years

    if custom_percentages:
        if len(custom_percentages) != num_years:
            raise ValueError(
                f"custom_percentages length {len(custom_percentages)} != num_years {num_years}"
            )
        if abs(sum(custom_percentages) - 100.0) > 0.5:
            raise ValueError(
                f"custom_percentages sum {sum(custom_percentages):.1f}% != 100%"
            )
        pcts = list(custom_percentages)
    else:
        pcts = [100.0 / num_years] * num_years

    schedule: list[dict[str, Any]] = []
    cumulative = 0.0
    for i, pct in enumerate(pcts):
        cumulative += pct
        schedule.append(
            {
                "year": i + 1,
                "date": _add_years(first_payment_date, i),
                "percentage": pct,
                "amount_per_employee": total_per_employee * (pct / 100.0),
                "cumulative_percentage": cumulative,
            }
        )
    return schedule


__all__ = ["MAX_INSTALLMENT_YEARS", "build_payment_schedule"]
