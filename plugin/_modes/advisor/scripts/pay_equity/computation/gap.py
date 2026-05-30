"""Gap calculation: female compensation vs male comparator / regression line.

Increase-only direction (Art. 71): never reduce male compensation to close a gap.
"""
from __future__ import annotations


def compute_gap(
    female_compensation: float,
    male_compensation: float,
    annual_hours: float = 0.0,
) -> dict:
    """Return gap_hourly = male - female (positive = underpaid female class)."""
    gap_hourly = male_compensation - female_compensation
    gap_annual = gap_hourly * annual_hours
    gap_pct = (gap_hourly / male_compensation * 100.0) if male_compensation else 0.0
    return {
        "gap_hourly": gap_hourly,
        "gap_annual": gap_annual,
        "gap_percentage": gap_pct,
        "requires_adjustment": gap_hourly > 0,
    }


__all__ = ["compute_gap"]
