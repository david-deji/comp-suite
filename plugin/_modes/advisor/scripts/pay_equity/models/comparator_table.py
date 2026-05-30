"""RLRQ E-12.001 r.2 prescribed comparator table — F017.

Used by the global comparison method when an enterprise has zero male
predominant job classes. The regulation prescribes two reference categories
(Contremaître and Préposé à la maintenance) with a 60% ratio rule.

The specific tariff values for the two categories are firewalled in CNESST
publications not yet acquired (David obtains in v1.1). All compensation values
are placeholders flagged `[UNVERIFIED]` so the rendering layer surfaces the
provenance gap to operators and reviewers.
"""
from __future__ import annotations

from typing import Any


PRESCRIBED_RATIO = 0.60  # 60% rule — RLRQ E-12.001 r.2


# Placeholder values — replace when David acquires the firewalled tariff publications.
PRESCRIBED_COMPARATORS: list[dict[str, Any]] = [
    {
        "category": "Contremaître",
        "reference_compensation_hourly": None,  # [UNVERIFIED] — placeholder
        "data_status": "UNVERIFIED",
        "source_pending": "RLRQ E-12.001 r.2 firewalled tariff publication",
    },
    {
        "category": "Préposé à la maintenance",
        "reference_compensation_hourly": None,  # [UNVERIFIED]
        "data_status": "UNVERIFIED",
        "source_pending": "RLRQ E-12.001 r.2 firewalled tariff publication",
    },
]


def lookup_prescribed_comparator(category: str) -> dict[str, Any]:
    """Return the prescribed comparator entry for a given category name.

    Output always includes `data_status: "UNVERIFIED"` until v1.1 closes.
    """
    for entry in PRESCRIBED_COMPARATORS:
        if entry["category"] == category:
            return dict(entry)
    raise KeyError(f"Unknown prescribed comparator: {category}")


def all_prescribed_comparators() -> list[dict[str, Any]]:
    """Return a list copy of all prescribed comparators (UNVERIFIED placeholders)."""
    return [dict(e) for e in PRESCRIBED_COMPARATORS]


__all__ = [
    "PRESCRIBED_RATIO",
    "PRESCRIBED_COMPARATORS",
    "lookup_prescribed_comparator",
    "all_prescribed_comparators",
]
