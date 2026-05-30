"""Global comparison method — RLRQ E-12.001 r.2 prescribed comparators (F057).

For enterprises with no male job classes, the regulation prescribes two
reference categories (Contremaître + Préposé à la maintenance) and a 60%
ratio of female compensation to the reference compensation.

Tariff values for the prescribed categories live in `models.comparator_table`
and are flagged [UNVERIFIED] until David obtains the firewalled regulation.
"""
from __future__ import annotations

from typing import Any, Optional


PRESCRIBED_CATEGORIES = ("Contremaître", "Préposé à la maintenance")
PRESCRIBED_RATIO = 0.60  # 60% per Reg. E-12.001 r.2


def lookup_prescribed_comparators() -> list[dict[str, Any]]:
    """Return the prescribed comparator entries (with [UNVERIFIED] flag)."""
    from scripts.pay_equity.models.comparator_table import all_prescribed_comparators
    return list(all_prescribed_comparators())


def apply_global_comparison(
    female_classes: list[dict[str, Any]],
    reference_compensation: Optional[float] = None,
) -> dict[str, Any]:
    """Compare female classes against the prescribed reference at the 60% ratio.

    `reference_compensation` is the operator-supplied compensation for the
    prescribed reference category (Contremaître / Préposé à la maintenance).
    When None, the comparator placeholder values are used and the result is
    flagged data_status="UNVERIFIED".
    """
    placeholders = lookup_prescribed_comparators()
    target = (
        float(reference_compensation) * PRESCRIBED_RATIO
        if reference_compensation is not None
        else None
    )

    comparisons: list[dict[str, Any]] = []
    is_unverified = target is None
    for f in female_classes:
        fc = float(f.get("total_compensation_hourly", 0))
        male_target = target if target is not None else 0.0
        gap_hourly = (male_target - fc) if target is not None else 0.0
        # When data_status=UNVERIFIED, do not assert requires_adjustment=False
        # (would be a phantom-compliance signal). None signals "unknown".
        requires_adjustment = None if is_unverified else gap_hourly > 0
        comparisons.append(
            {
                "female_class_id": f.get("id") or f.get("class_id"),
                "female_compensation": fc,
                "prescribed_target": male_target,
                "gap_hourly": gap_hourly,
                "requires_adjustment": requires_adjustment,
            }
        )

    return {
        "method": "global",
        "reference_category_1": placeholders[0]["category"]
        if placeholders
        else PRESCRIBED_CATEGORIES[0],
        "reference_category_2": placeholders[1]["category"]
        if len(placeholders) > 1
        else PRESCRIBED_CATEGORIES[1],
        "prescribed_ratio": PRESCRIBED_RATIO,
        "reference_compensation": reference_compensation,
        "data_status": "VERIFIED" if reference_compensation is not None else "UNVERIFIED",
        "note": (
            "Operator-supplied reference compensation."
            if reference_compensation is not None
            else "Reference compensation pending — RLRQ E-12.001 r.2 tariff firewalled."
        ),
        "comparisons": comparisons,
    }


__all__ = [
    "PRESCRIBED_CATEGORIES",
    "PRESCRIBED_RATIO",
    "apply_global_comparison",
    "lookup_prescribed_comparators",
]
