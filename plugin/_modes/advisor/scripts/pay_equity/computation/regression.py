"""OLS regression for the male wage line + outlier detection (F056).

Fit y = intercept + slope × x using numpy on (evaluation_score,
total_compensation_hourly) pairs from male job classes only. Outliers are
classes with residuals > 2 standard deviations. Quality bands:
    R² >= 0.7  → "good"
    0.4-0.7    → "acceptable" (warn)
    < 0.4      → "poor" (strong warn)

Min 2 male classes required to fit; warn if < 4 (small sample).
"""
from __future__ import annotations

from typing import Any


MIN_MALE_CLASSES = 2
SMALL_SAMPLE_WARN_THRESHOLD = 4


def fit_male_wage_line(male_classes: list[dict[str, Any]]) -> dict[str, Any]:
    """Fit OLS regression and tag outliers.

    `male_classes` entries: {class_id, evaluation_score, total_compensation_hourly}.
    Returns a dict with intercept, slope, r_squared, data_points,
    male_classes_used, outlier_class_ids, residuals, quality_assessment,
    quality_notes.

    R3 P-M1: numpy is imported lazily so the MCP cold-start (`python -m
    pay_equity_mcp`) doesn't pay numpy's 80–200 ms import cost on every fresh
    Claude session. Hybrid/regression flows still pay it once on first call.
    """
    import numpy as np

    if len(male_classes) < MIN_MALE_CLASSES:
        raise ValueError(
            f"OLS regression requires at least {MIN_MALE_CLASSES} male classes; "
            f"got {len(male_classes)}."
        )

    ids = [c.get("class_id") or c.get("id") for c in male_classes]
    x = np.asarray([float(c["evaluation_score"]) for c in male_classes], dtype=float)
    y = np.asarray([float(c["total_compensation_hourly"]) for c in male_classes], dtype=float)

    slope, intercept = np.polyfit(x, y, 1)
    y_pred = intercept + slope * x
    residuals = y - y_pred
    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 1.0

    # Outliers: residuals > 2 standard deviations.
    std = float(np.std(residuals)) if len(residuals) > 1 else 0.0
    outlier_ids = [
        ids[i] for i, r in enumerate(residuals) if std > 0 and abs(r) > 2 * std
    ]

    if r_squared >= 0.7:
        quality = "good"
        quality_notes = "Strong fit. Regression suitable for primary comparison."
    elif r_squared >= 0.4:
        quality = "acceptable"
        quality_notes = (
            "Moderate fit — consider whether male compensation truly tracks evaluation "
            "score, or whether an unobserved factor is at play."
        )
    else:
        quality = "poor"
        quality_notes = (
            "Weak fit — regression may not capture male pay structure. Recommend "
            "reviewing male class compensations or using job-to-job exclusively."
        )

    if len(male_classes) < SMALL_SAMPLE_WARN_THRESHOLD:
        quality_notes += (
            f" Small sample ({len(male_classes)} male classes < {SMALL_SAMPLE_WARN_THRESHOLD})."
        )

    return {
        "intercept": float(intercept),
        "slope": float(slope),
        "r_squared": float(r_squared),
        "data_points": len(male_classes),
        "male_classes_used": ids,
        "outlier_class_ids": outlier_ids,
        "residuals": [float(r) for r in residuals],
        "quality_assessment": quality,
        "quality_notes": quality_notes,
    }


__all__ = ["MIN_MALE_CLASSES", "fit_male_wage_line"]
