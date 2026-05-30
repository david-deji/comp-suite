"""4-criteria predominance algorithm (R4).

Auto-applied tests in order:
  1. Numerical: female_pct >= 60 → female; female_pct <= 40 → male.
  2. Disproportion vs enterprise ratio: |class_pct - enterprise_pct| >= threshold (default 20pp).
  3-4. Operator-applied historical/stereotype overrides — handled via tools.job_classes.override_predominance.
First positive test wins. Source: r3-r9-spec-corrections.md § R4.
"""
from __future__ import annotations

from typing import Optional


DISPROPORTION_THRESHOLD_DEFAULT_PP = 20.0  # percentage points
NUMERICAL_THRESHOLD_PCT = 60.0


def determine_predominance(
    female_pct: float,
    enterprise_female_pct: Optional[float] = None,
    threshold_pp: float = DISPROPORTION_THRESHOLD_DEFAULT_PP,
) -> dict:
    """Return the predominance result for a single class.

    Result dict keys:
      - predominance: "female" | "male" | "neutral"
      - method: "quantitative" | "disproportion" | "requires_operator_test"
      - female_pct (input echoed)
      - delta_pp (only when method == disproportion)
      - threshold_pp (only when method == disproportion)
    """
    if female_pct >= NUMERICAL_THRESHOLD_PCT:
        return {
            "predominance": "female",
            "method": "quantitative",
            "female_pct": female_pct,
        }
    if female_pct <= (100.0 - NUMERICAL_THRESHOLD_PCT):
        return {
            "predominance": "male",
            "method": "quantitative",
            "female_pct": female_pct,
        }

    if enterprise_female_pct is None:
        return {
            "predominance": "neutral",
            "method": "requires_operator_test",
            "female_pct": female_pct,
        }

    delta = female_pct - enterprise_female_pct
    if abs(delta) >= threshold_pp:
        return {
            "predominance": "female" if delta > 0 else "male",
            "method": "disproportion",
            "female_pct": female_pct,
            "delta_pp": delta,
            "threshold_pp": threshold_pp,
        }

    return {
        "predominance": "neutral",
        "method": "requires_operator_test",
        "female_pct": female_pct,
    }


__all__ = [
    "DISPROPORTION_THRESHOLD_DEFAULT_PP",
    "NUMERICAL_THRESHOLD_PCT",
    "determine_predominance",
]
