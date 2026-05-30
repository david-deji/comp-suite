"""Job-to-job comparison via grade-band exact match (R8).

R8 founder decision: exact grade match only — NO grade_tolerance parameter.
When no male class in band → caller falls through to regression
(computation.regression) or global comparison (computation.global_comparison).
"""
from __future__ import annotations

from typing import Any, Optional


def compare_job_to_job(
    female_class: dict[str, Any],
    male_classes: list[dict[str, Any]],
) -> Optional[dict[str, Any]]:
    """Exact grade-match job-to-job comparison.

    Returns a comparison dict (female_class_id, male_comparator_id,
    female_compensation, male_compensation, gap_hourly, gap_percentage,
    requires_adjustment) when a male class shares the same grade.
    Returns None when no exact-grade comparator is available.
    """
    target_grade = female_class.get("grade")
    if target_grade is None:
        return None
    same_grade = [m for m in male_classes if m.get("grade") == target_grade]
    if not same_grade:
        return None

    # When multiple male classes share the grade, average their total
    # compensation — the audit reports it as the male comparator value.
    male_comp = sum(float(m.get("total_compensation_hourly", 0)) for m in same_grade) / len(same_grade)
    female_comp = float(female_class.get("total_compensation_hourly", 0))
    gap_hourly = male_comp - female_comp
    gap_pct = (gap_hourly / male_comp * 100.0) if male_comp else 0.0
    return {
        "female_class_id": female_class.get("id") or female_class.get("class_id"),
        "male_comparator_id": (same_grade[0].get("id") or same_grade[0].get("class_id"))
        if len(same_grade) == 1
        else None,
        "comparison_method": "job_to_job",
        "female_compensation": female_comp,
        "male_compensation": male_comp,
        "gap_hourly": gap_hourly,
        "gap_percentage": gap_pct,
        "requires_adjustment": gap_hourly > 0,
    }


def compare_with_regression(
    female_class: dict[str, Any],
    regression: dict[str, Any],
) -> dict[str, Any]:
    """Compare against the male wage line (regression intercept + slope × score)."""
    score = float(female_class.get("evaluation_score", 0.0))
    intercept = float(regression.get("intercept", 0.0))
    slope = float(regression.get("slope", 0.0))
    male_predicted = intercept + slope * score
    female_comp = float(female_class.get("total_compensation_hourly", 0))
    gap_hourly = male_predicted - female_comp
    gap_pct = (gap_hourly / male_predicted * 100.0) if male_predicted else 0.0
    return {
        "female_class_id": female_class.get("id") or female_class.get("class_id"),
        "male_comparator_id": None,
        "comparison_method": "regression",
        "female_compensation": female_comp,
        "male_compensation": male_predicted,
        "gap_hourly": gap_hourly,
        "gap_percentage": gap_pct,
        "requires_adjustment": gap_hourly > 0,
    }


__all__ = ["compare_job_to_job", "compare_with_regression"]
