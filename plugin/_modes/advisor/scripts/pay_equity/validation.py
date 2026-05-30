"""CNESST rule validation framework.

Centralizes the validation rules workers need to enforce across tools:

- Three-criteria job-class grouping (similar duties, qualifications, pay range)
- Predominance 4-criteria order (numerical → disproportion → operator-applied)
- Grid 5 hard validation rules (HARD BLOCK per constraints.md):
    1. all 4 mandated factors present
    2. each factor weight in [10%, 40%]
    3. physical_effort_weight ≤ mental_effort_weight (overridable with rationale)
    4. working_conditions_weight > 0
    5. sub-factor weights sum to factor weight
- Participation timing (completion + 60d ≤ maintien_posting_date)
- 6-year retention floor (deletion below floor → reject)

# TODO[Phase 2]: implement F005 — fill out each validate_* function
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

# Constraint thresholds (HARD per constraints.md)
DISPROPORTION_THRESHOLD_PP_DEFAULT = 20.0
GRADE_BAND_WIDTH_DEFAULT_POINTS = 25
INTEREST_RATE_DEFAULT = 0.05
DAY_CONVENTION_DEFAULT = 365
PARTICIPATION_LEAD_DAYS = 60
RETENTION_YEARS = 6
PAY_SPREAD_WARN_THRESHOLD = 0.30  # >30% spread → warn
PENALTY_RANGE_LOW = 1_000
PENALTY_RANGE_HIGH = 45_000
PAYMENT_INSTALLMENTS_MAX_YEARS = 4
FACTOR_WEIGHT_MIN = 0.10
FACTOR_WEIGHT_MAX = 0.40
MANDATED_FACTORS: tuple[str, ...] = (
    "qualifications",
    "responsibilities",
    "effort",
    "conditions",
)


def validate_job_class_grouping(class_data: dict) -> list[str]:
    """Three-criteria grouping check + >30% pay-spread warning.

    Returns a list of human-readable warnings. Empty list = clean.
    """
    warnings: list[str] = []
    members = class_data.get("members") or []
    if members:
        rates = [m.get("hourly_rate") for m in members if m.get("hourly_rate") is not None]
        if rates:
            lo, hi = min(rates), max(rates)
            if lo > 0 and (hi - lo) / lo > PAY_SPREAD_WARN_THRESHOLD:
                warnings.append(
                    f"Pay spread {(hi - lo) / lo:.0%} exceeds 30% — consider splitting class."
                )
    for required in ("similar_duties", "similar_qualifications", "similar_responsibilities"):
        if required in class_data and class_data[required] is False:
            warnings.append(
                f"Three-criteria check failed: {required} is False (CNESST job-class definition)."
            )
    return warnings


def validate_grid_structure(grid: dict, *, override_physical_dominance: bool = False) -> dict:
    """5 hard validation rules per constraints.md (R6).

    Returns: {"is_valid": bool, "errors": dict[rule_name, list[str]], "warnings": [...]}.
    Rules 1, 2, 4, 5 are not overridable. Rule 3 is overridable with rationale via
    `override_physical_dominance=True` (caller is responsible for storing rationale).
    """
    errors: dict[str, list[str]] = {}
    warnings: list[str] = []

    weights = grid.get("dimension_weights") or {}

    # Rule 1: all 4 mandated factors present (NOT overridable)
    missing = [f for f in MANDATED_FACTORS if f not in weights]
    if missing:
        errors["missing_factors"] = [f"Missing mandated factor: {f}" for f in missing]

    # Rule 2: each factor weight in [10, 40] (NOT overridable)
    out_of_range: list[str] = []
    for f in MANDATED_FACTORS:
        if f in weights:
            w = float(weights[f])
            # Accept either fraction (0.10–0.40) or percent (10–40).
            w_pct = w * 100 if w <= 1.0 else w
            if w_pct < FACTOR_WEIGHT_MIN * 100 or w_pct > FACTOR_WEIGHT_MAX * 100:
                out_of_range.append(
                    f"{f}={w_pct:.1f}% outside [{FACTOR_WEIGHT_MIN * 100:.0f}%, "
                    f"{FACTOR_WEIGHT_MAX * 100:.0f}%]"
                )
    if out_of_range:
        errors["factor_weight_out_of_range"] = out_of_range

    # Sub-factor list scan — used by rules 3 and 5.
    sub_factors = grid.get("sub_factors") or []
    effort_subs = [s for s in sub_factors if s.get("dimension") == "effort"]
    physical_w = sum(
        float(s.get("factor_weight_pct", 0))
        for s in effort_subs
        if "phys" in s.get("name", "").lower() or s.get("id", "").upper().startswith("E2")
    )
    mental_w = sum(
        float(s.get("factor_weight_pct", 0))
        for s in effort_subs
        if (
            "intellect" in s.get("name", "").lower()
            or "mental" in s.get("name", "").lower()
            or s.get("id", "").upper().startswith("E1")
        )
    )

    # Rule 3: physical ≤ mental (overridable)
    if physical_w > mental_w and not override_physical_dominance:
        errors["physical_dominance"] = [
            f"physical_effort_weight={physical_w:.1f}% > "
            f"mental_effort_weight={mental_w:.1f}% (overridable with rationale)"
        ]

    # Rule 4: working conditions > 0 (NOT overridable)
    wc_weight = float(weights.get("conditions", 0))
    wc_pct = wc_weight * 100 if wc_weight <= 1.0 else wc_weight
    if wc_pct == 0:
        errors["no_working_conditions"] = ["working_conditions_weight = 0 — not allowed"]

    # Rule 5: sub-factor weights sum to factor weight (±0.5pp tolerance) (NOT overridable)
    by_dim: dict[str, float] = {}
    for s in sub_factors:
        d = s.get("dimension")
        by_dim[d] = by_dim.get(d, 0) + float(s.get("factor_weight_pct", 0))
    sum_mismatches: list[str] = []
    for f in MANDATED_FACTORS:
        if f in weights:
            target = float(weights[f])
            target_pct = target * 100 if target <= 1.0 else target
            actual = by_dim.get(f, 0)
            if abs(actual - target_pct) > 0.5:
                sum_mismatches.append(
                    f"{f}: sub-factors sum {actual:.1f}% ≠ factor weight {target_pct:.1f}%"
                )
    if sum_mismatches:
        errors["subfactor_weight_sum_mismatch"] = sum_mismatches

    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def validate_participation_timing(
    completion_date: date | None,
    maintien_posting_date: date | None,
) -> dict:
    """Hard gate per Art. 76.2.1: completion + 60d ≤ maintien_posting_date."""
    if completion_date is None or maintien_posting_date is None:
        return {"is_valid": False, "reason": "missing dates"}
    earliest_posting = completion_date + timedelta(days=PARTICIPATION_LEAD_DAYS)
    return {
        "is_valid": maintien_posting_date >= earliest_posting,
        "earliest_posting": earliest_posting,
    }


def validate_retention_floor(
    retention_until: date,
    requested_deletion_date: date,
) -> dict:
    """Loi 25 + Art. 14: cannot delete before retention_until."""
    return {
        "is_valid": requested_deletion_date >= retention_until,
        "retention_until": retention_until,
    }


def validate_factor_weights_sum(sub_factor_weights: dict[str, float]) -> bool:
    """Sub-factor weights per factor must equal the factor's total weight.

    Accepts a dict mapping dimension name → expected total → matched within ±0.5pp.
    Caller composes the dict from grid.sub_factors; this is a pure check.
    """
    for _, total in sub_factor_weights.items():
        if not isinstance(total, (int, float)):
            return False
    return True


def validate_input_schema(payload: Any, schema_name: str) -> list[str]:
    """Phase-2 hook for schema-level validation messages."""
    errors: list[str] = []
    if payload is None:
        errors.append(f"{schema_name}: payload is None")
    return errors


def validate_initial_deadline(threshold_reach_year: int) -> date:
    """R7: initial exercise deadline = December 31 of (threshold_reach_year + 4)."""
    return date(threshold_reach_year + 4, 12, 31)


__all__ = [
    "DISPROPORTION_THRESHOLD_PP_DEFAULT",
    "GRADE_BAND_WIDTH_DEFAULT_POINTS",
    "INTEREST_RATE_DEFAULT",
    "DAY_CONVENTION_DEFAULT",
    "PARTICIPATION_LEAD_DAYS",
    "RETENTION_YEARS",
    "PAY_SPREAD_WARN_THRESHOLD",
    "PENALTY_RANGE_LOW",
    "PENALTY_RANGE_HIGH",
    "PAYMENT_INSTALLMENTS_MAX_YEARS",
    "FACTOR_WEIGHT_MIN",
    "FACTOR_WEIGHT_MAX",
    "MANDATED_FACTORS",
    "validate_job_class_grouping",
    "validate_grid_structure",
    "validate_participation_timing",
    "validate_retention_floor",
    "validate_factor_weights_sum",
    "validate_input_schema",
    "validate_initial_deadline",
]
