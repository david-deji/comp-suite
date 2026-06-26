"""Evaluation tools: list_grid_templates, select_grid, customize_grid,
score_job_classes, get_evaluation_summary.

5 of the 19 registered MCP tools.

Spec anchors:
- phase4-final-mcp-architecture.md § 5 Tools 8-12
- r3-r9-spec-corrections.md § R6 (5 hard grid validation rules)
- constraints.md § Grade banding (equal-width only, default 25-pt)
"""
from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path
from typing import Any, Optional

from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.errors import ValidationError
from scripts.pay_equity.models import (
    EvaluationFile,
    EvaluationGrid,
    JobClassesFile,
    SubFactor,
)
from scripts.pay_equity.validation import (
    GRADE_BAND_WIDTH_DEFAULT_POINTS,
    validate_grid_structure,
    validate_safe_identifier,
)


_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def _load_template(template_id: str) -> dict[str, Any]:
    validate_safe_identifier(template_id, field="template_id")
    p = (_TEMPLATES_DIR / f"{template_id}.json").resolve()
    if not p.is_relative_to(_TEMPLATES_DIR.resolve()):
        raise ValidationError(
            "template_id resolves outside templates directory",
            data={"field": "template_id"},
        )
    if not p.exists():
        raise ValidationError(
            f"template_id={template_id!r} not found in {_TEMPLATES_DIR}."
        )
    return json.loads(p.read_text(encoding="utf-8"))


def _grid_to_dict_for_validation(grid: EvaluationGrid) -> dict[str, Any]:
    return {
        "dimension_weights": dict(grid.dimension_weights),
        "sub_factors": [
            {
                "id": sf.id,
                "name": sf.name,
                "dimension": sf.dimension,
                "factor_weight_pct": _factor_weight_for_subfactor(sf, grid),
            }
            for sf in grid.sub_factors
        ],
    }


def _factor_weight_for_subfactor(sf: SubFactor, grid: EvaluationGrid) -> float:
    """Pull factor_weight_pct stored on the sub-factor (extra fields are ignored by Pydantic by default,
    so when constructing SubFactor we lose factor_weight_pct — we attach it via grid metadata).

    For templates loaded directly from JSON, factor_weight_pct is on the dict — convert before validation.
    """
    return float(getattr(sf, "factor_weight_pct", 0))


@mcp_tool
def list_grid_templates() -> dict[str, Any]:
    """List available pre-built evaluation grid templates."""
    templates: list[dict[str, Any]] = []
    if not _TEMPLATES_DIR.exists():
        return {"templates": templates}
    for p in sorted(_TEMPLATES_DIR.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        templates.append(
            {
                "template_id": data.get("template_id"),
                "template_name": data.get("template_name"),
                "description": data.get("description", ""),
                "total_max_points": data.get("total_max_points", 0),
                "dimension_weights": data.get("dimension_weights", {}),
                "sub_factor_count": len(data.get("sub_factors", [])),
            }
        )
    return {"templates": templates}


@mcp_tool
def select_grid(template_id: str) -> dict[str, Any]:
    """Build an evaluation grid from a pre-built template (pure).

    Reads the packaged template (a skill asset, not engagement data), builds the
    EvaluationGrid + sub-factor objects + the sub-factor weights, and returns all
    three for the orchestrator to persist. The grid carries `sub_factor_weights`
    (the SubFactor model omits `factor_weight_pct`), so the orchestrator persists
    the weights on the grid entity via `payequity_put_evaluation_grid`.
    """
    template = _load_template(template_id)

    sub_factor_objs = [SubFactor(**{k: v for k, v in sf.items() if k in SubFactor.model_fields}) for sf in template.get("sub_factors", [])]
    grid = EvaluationGrid(
        client_slug="",  # engagement identity is set server-side on payequity_put_evaluation_grid
        template_id=template["template_id"],
        template_name=template.get("template_name"),
        is_custom=False,
        sub_factors=sub_factor_objs,
        total_max_points=int(template.get("total_max_points", 0)),
        dimension_weights={k: float(v) for k, v in template.get("dimension_weights", {}).items()},
        last_updated=date.today(),
    )

    sub_factor_weights = {
        sf.get("id"): float(sf.get("factor_weight_pct", 0))
        for sf in template.get("sub_factors", [])
    }

    return {
        "evaluation_grid": grid.model_dump(mode="json"),
        "sub_factors": [sf.model_dump(mode="json") for sf in sub_factor_objs],
        "sub_factor_weights": sub_factor_weights,
        "summary": {
            "template_id": template["template_id"],
            "template_name": template.get("template_name"),
            "sub_factors": len(sub_factor_objs),
            "total_max_points": grid.total_max_points,
            "dimension_weights": dict(grid.dimension_weights),
        },
    }


def _build_validation_payload(grid_data: dict[str, Any]) -> dict[str, Any]:
    """Reshape grid template payload into the dict that validate_grid_structure expects."""
    return {
        "dimension_weights": grid_data.get("dimension_weights", {}),
        "sub_factors": grid_data.get("sub_factors", []),
    }


@mcp_tool
def customize_grid(
    current_grid: Optional[dict[str, Any]],
    current_sub_factor_weights: Optional[dict[str, Any]],
    modifications: dict[str, Any],
    override_physical_dominance: bool = False,
    override_rationale: Optional[str] = None,
) -> dict[str, Any]:
    """Modify the evaluation grid (pure).

    Applies the 5 hard validation rules (R6): all 4 dimensions present,
    factor weights in [10%, 40%], physical_effort_weight <= mental_effort_weight
    (overridable with rationale), working_conditions_weight > 0, sub-factor
    weights sum to factor weight. Returns is_valid=false (no rebuilt grid) on any
    failure; on success returns the rebuilt grid + sub-factor weights for the
    orchestrator to persist.

    Receives the current grid (the `grid` block of the evaluation file) and the
    current sub-factor weights (the SubFactor model strips `factor_weight_pct`, so
    the weights round-trip on the grid entity).

    `modifications` keys:
      - `dimension_weights`: full replacement dict
      - `sub_factors`: full replacement list (each entry must include id, name,
        dimension, factor_weight_pct, levels, points_per_level, max_points)
    """
    # Compose the proposed grid as a plain dict for validation.
    base: dict[str, Any] = {"dimension_weights": {}, "sub_factors": []}
    if current_grid:
        base["dimension_weights"] = dict(current_grid.get("dimension_weights", {}))
        base["sub_factors"] = list(current_grid.get("sub_factors", []))
        # Bring sub-factor weights from the passed-in weights (model strips them).
        w_lookup = current_sub_factor_weights or {}
        for sf in base["sub_factors"]:
            sf_id = sf.get("id")
            if sf_id in w_lookup:
                sf["factor_weight_pct"] = float(w_lookup[sf_id])

    if "dimension_weights" in modifications:
        base["dimension_weights"] = {
            k: float(v) for k, v in modifications["dimension_weights"].items()
        }
    if "sub_factors" in modifications:
        base["sub_factors"] = list(modifications["sub_factors"])

    if override_physical_dominance and not override_rationale:
        raise ValidationError(
            "override_physical_dominance=True requires override_rationale (audit trail)."
        )

    result = validate_grid_structure(
        _build_validation_payload(base),
        override_physical_dominance=override_physical_dominance,
    )

    if not result["is_valid"]:
        return {
            "is_valid": False,
            "errors": result["errors"],
            "warnings": result["warnings"],
            "summary": {
                "dimension_weights": base["dimension_weights"],
                "sub_factors": len(base["sub_factors"]),
                "total_max_points": sum(int(sf.get("max_points", 0)) for sf in base["sub_factors"]),
            },
        }

    # Build the mutated grid for the orchestrator to persist.
    sub_factor_objs = [
        SubFactor(**{k: v for k, v in sf.items() if k in SubFactor.model_fields})
        for sf in base["sub_factors"]
    ]
    grid = EvaluationGrid(
        client_slug="",  # engagement identity is set server-side on payequity_put_evaluation_grid
        is_custom=True,
        sub_factors=sub_factor_objs,
        total_max_points=sum(sf.max_points for sf in sub_factor_objs),
        dimension_weights={k: float(v) for k, v in base["dimension_weights"].items()},
        last_updated=date.today(),
    )

    sub_factor_weights = {
        sf.get("id"): float(sf.get("factor_weight_pct", 0))
        for sf in base["sub_factors"]
    }

    return {
        "is_valid": True,
        "errors": {},
        "warnings": result["warnings"],
        "evaluation_grid": grid.model_dump(mode="json"),
        "sub_factor_weights": sub_factor_weights,
        "override_physical_dominance": override_physical_dominance,
        "override_rationale": override_rationale or "",
        "summary": {
            "dimension_weights": dict(grid.dimension_weights),
            "sub_factors": len(sub_factor_objs),
            "total_max_points": grid.total_max_points,
        },
    }


@mcp_tool
def all_classes_scored(class_ids: list[str], scored_ids: list[str]) -> bool:
    """Completeness gate before comparison (pure).

    The per-class weighted scoring math runs server-side
    (`payequity_compute_scoring`, looped per class). This residual keeps the
    cross-class completeness check in tested Python: true iff every job class has a
    score. Empty class set is not complete.
    """
    expected = set(class_ids)
    return bool(expected) and expected.issubset(set(scored_ids))


@mcp_tool
def get_evaluation_summary(
    evaluation: dict[str, Any],
    job_classes: Optional[dict[str, Any]] = None,
    grade_band_width: Optional[int] = None,
    grade_band_width_rationale: Optional[str] = None,
) -> dict[str, Any]:
    """Return all job classes ranked by total evaluation points, grouped by equal-width grade band (pure).

    R8 G-01 founder decision: equal-width banding only. Default 25 points
    (operator override allowed with rationale). Reports dimension breakdown per
    class and bias warnings. Receives the evaluation file + job classes (fetched
    by the orchestrator); when a band-width override is supplied, returns an
    `operator_decision` audit entry for the orchestrator to append.
    """
    eval_file = EvaluationFile(**evaluation)
    jc_file = JobClassesFile(**job_classes) if job_classes else None

    band_width = int(grade_band_width or GRADE_BAND_WIDTH_DEFAULT_POINTS)
    if band_width <= 0:
        raise ValidationError(f"grade_band_width must be positive (got {band_width}).")

    operator_decision: Optional[dict[str, Any]] = None
    if grade_band_width and grade_band_width != GRADE_BAND_WIDTH_DEFAULT_POINTS:
        if not grade_band_width_rationale:
            raise ValidationError(
                f"grade_band_width override ({grade_band_width}) requires "
                "grade_band_width_rationale (audit trail)."
            )
        operator_decision = {
            "grade_band_width": band_width,
            "grade_band_width_rationale": grade_band_width_rationale,
        }

    scores_by_id = {s.class_id: s for s in eval_file.class_scores}

    classes_payload: list[dict[str, Any]] = []
    unscored: list[str] = []
    if jc_file is not None:
        for cls in jc_file.classes:
            if cls.id not in scores_by_id:
                unscored.append(cls.id)
                continue
            score = scores_by_id[cls.id]
            # Build dimension breakdown from grid metadata.
            by_dim: dict[str, int] = {}
            for sf in eval_file.grid.sub_factors:
                if sf.id in score.scores:
                    by_dim[sf.dimension] = by_dim.get(sf.dimension, 0) + score.scores[sf.id]
            classes_payload.append(
                {
                    "class_id": cls.id,
                    "title": cls.title,
                    "predominance": cls.predominance.value if cls.predominance else None,
                    "total_score": score.total_score,
                    "dimension_breakdown": by_dim,
                }
            )
    else:
        for sid, score in scores_by_id.items():
            classes_payload.append(
                {
                    "class_id": sid,
                    "title": "",
                    "predominance": None,
                    "total_score": score.total_score,
                    "dimension_breakdown": {},
                }
            )

    classes_payload.sort(key=lambda x: x["total_score"], reverse=True)

    # Equal-width banding: starting from band 1 at the lowest score.
    grades: list[dict[str, Any]] = []
    if classes_payload:
        scores_only = [c["total_score"] for c in classes_payload]
        lo = math.floor(min(scores_only))
        hi = math.ceil(max(scores_only))
        n_bands = max(1, math.ceil((hi - lo + 1) / band_width))
        # Highest scores get the lowest grade number (Grade 1 = best paid / most demanding).
        for c in classes_payload:
            offset = hi - c["total_score"]
            grade = int(offset // band_width) + 1
            c["grade"] = grade
        grade_set = sorted({c["grade"] for c in classes_payload})
        for g in grade_set:
            members = [c for c in classes_payload if c["grade"] == g]
            band_top = hi - (g - 1) * band_width
            band_bottom = band_top - band_width + 1
            grades.append(
                {
                    "grade": g,
                    "band_min": max(band_bottom, lo),
                    "band_max": band_top,
                    "class_ids": [c["class_id"] for c in members],
                    "count": len(members),
                }
            )

    bias_warnings: list[str] = []
    # Bias check: female-predominant classes systematically lower than males in the same grade.
    for grade_entry in grades:
        members = [c for c in classes_payload if c["class_id"] in grade_entry["class_ids"]]
        female_scores = [c["total_score"] for c in members if c["predominance"] == "female"]
        male_scores = [c["total_score"] for c in members if c["predominance"] == "male"]
        if female_scores and male_scores:
            avg_f = sum(female_scores) / len(female_scores)
            avg_m = sum(male_scores) / len(male_scores)
            if avg_m - avg_f > band_width / 2:
                bias_warnings.append(
                    f"Grade {grade_entry['grade']}: avg male score ({avg_m:.0f}) "
                    f"exceeds avg female score ({avg_f:.0f}) by more than half a band."
                )

    return {
        "classes_ranked": classes_payload,
        "grades": grades,
        "grade_band_width": band_width,
        "bias_warnings": bias_warnings,
        "unscored_classes": unscored,
        "operator_decision": operator_decision,
    }


__all__ = [
    "all_classes_scored",
    "customize_grid",
    "get_evaluation_summary",
    "list_grid_templates",
    "select_grid",
]
