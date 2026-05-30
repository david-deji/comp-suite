"""Point-factor scoring computation (F039).

Given a SubFactor (with `levels` and `points_per_level`) and an awarded level
index, return the awarded points. Aggregate across sub-factors for a class
total. Pure function — no I/O, no LLM.
"""
from __future__ import annotations

from typing import Any


def score_sub_factor(sub_factor: dict[str, Any], awarded_level: int) -> int:
    """Return points awarded for one sub-factor at a given level (0-indexed).

    Raises IndexError when awarded_level is out of range, ValueError when the
    sub_factor is malformed.
    """
    points = sub_factor.get("points_per_level")
    if not isinstance(points, list) or not points:
        raise ValueError(
            f"sub_factor {sub_factor.get('id')!r}: points_per_level missing or empty"
        )
    if awarded_level < 0 or awarded_level >= len(points):
        raise IndexError(
            f"sub_factor {sub_factor.get('id')!r}: level {awarded_level} "
            f"outside [0, {len(points) - 1}]"
        )
    return int(points[awarded_level])


def score_class(grid: dict[str, Any], awarded: dict[str, int]) -> dict[str, Any]:
    """Score one class against a grid.

    `awarded` maps sub_factor_id → level_index (0-based). Returns:
      - total_score: float (sum of all sub-factor points)
      - per_sub_factor: dict[sub_factor_id, points]
      - dimension_breakdown: dict[dimension, total points]
      - missing: list[sub_factor_id] (in grid but not awarded)
    """
    sub_factors = grid.get("sub_factors") or []
    per_sub: dict[str, int] = {}
    by_dim: dict[str, int] = {}
    missing: list[str] = []

    for sf in sub_factors:
        sf_id = sf.get("id")
        if sf_id is None:
            continue
        if sf_id not in awarded:
            missing.append(sf_id)
            continue
        level = awarded[sf_id]
        pts = score_sub_factor(sf, level)
        per_sub[sf_id] = pts
        dim = sf.get("dimension", "")
        by_dim[dim] = by_dim.get(dim, 0) + pts

    total = float(sum(per_sub.values()))
    return {
        "total_score": total,
        "per_sub_factor": per_sub,
        "dimension_breakdown": by_dim,
        "missing": missing,
    }


__all__ = ["score_class", "score_sub_factor"]
