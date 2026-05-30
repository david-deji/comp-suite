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

from scripts.pay_equity import persistence_gdrive as persistence
from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.computation.scoring import score_class as _score_class
from scripts.pay_equity.errors import MissingDataError, ValidationError
from scripts.pay_equity.models import (
    ClassScore,
    EvaluationFile,
    EvaluationGrid,
    JobClassesFile,
    SubFactor,
)
from scripts.pay_equity.validation import (
    GRADE_BAND_WIDTH_DEFAULT_POINTS,
    validate_grid_structure,
)


_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def _load_template(template_id: str) -> dict[str, Any]:
    persistence.validate_safe_identifier(template_id, field="template_id")
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
def select_grid(client_slug: str, template_id: str) -> dict[str, Any]:
    """Attach a pre-built evaluation grid template to the engagement."""
    if not persistence.engagement_exists(client_slug):
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r}."
        )
    template = _load_template(template_id)
    eng_dir = persistence.get_engagement_dir(client_slug)
    eval_path = eng_dir / "evaluation-grid.json"

    # Build the EvaluationGrid (sub-factor model omits factor_weight_pct → store it
    # alongside in evaluation file metadata for grid-validation).
    sub_factor_objs = [SubFactor(**{k: v for k, v in sf.items() if k in SubFactor.model_fields}) for sf in template.get("sub_factors", [])]
    grid = EvaluationGrid(
        client_slug=client_slug,
        template_id=template["template_id"],
        template_name=template.get("template_name"),
        is_custom=False,
        sub_factors=sub_factor_objs,
        total_max_points=int(template.get("total_max_points", 0)),
        dimension_weights={k: float(v) for k, v in template.get("dimension_weights", {}).items()},
        last_updated=date.today(),
    )
    eval_file = EvaluationFile(grid=grid, last_updated=date.today())
    persistence.write_json(eval_path, eval_file)

    # Persist factor weights as an evaluation-grid metadata sidecar (sub-factor weights).
    sidecar_path = eng_dir / "evaluation-grid-meta.json"
    sidecar = {
        "template_id": template["template_id"],
        "sub_factor_weights": {
            sf.get("id"): float(sf.get("factor_weight_pct", 0))
            for sf in template.get("sub_factors", [])
        },
    }
    sidecar_path.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False), encoding="utf-8")

    persistence.invalidate_downstream(eng_dir, "evaluation-grid.json")

    return {
        "template_id": template["template_id"],
        "template_name": template.get("template_name"),
        "sub_factors": len(sub_factor_objs),
        "total_max_points": grid.total_max_points,
        "dimension_weights": dict(grid.dimension_weights),
    }


def _build_validation_payload(grid_data: dict[str, Any]) -> dict[str, Any]:
    """Reshape grid template payload into the dict that validate_grid_structure expects."""
    return {
        "dimension_weights": grid_data.get("dimension_weights", {}),
        "sub_factors": grid_data.get("sub_factors", []),
    }


@mcp_tool
def customize_grid(
    client_slug: str,
    modifications: dict[str, Any],
    override_physical_dominance: bool = False,
    override_rationale: Optional[str] = None,
) -> dict[str, Any]:
    """Modify the evaluation grid.

    Applies the 5 hard validation rules (R6): all 4 dimensions present,
    factor weights in [10%, 40%], physical_effort_weight <= mental_effort_weight
    (overridable with rationale), working_conditions_weight > 0, sub-factor
    weights sum to factor weight. Returns is_valid=false on any failure.
    Invalidates downstream when the grid is mutated.

    `modifications` keys:
      - `dimension_weights`: full replacement dict
      - `sub_factors`: full replacement list (each entry must include id, name,
        dimension, factor_weight_pct, levels, points_per_level, max_points)
    """
    if not persistence.engagement_exists(client_slug):
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r}."
        )
    eng_dir = persistence.get_engagement_dir(client_slug)
    eval_path = eng_dir / "evaluation-grid.json"

    # Compose the proposed grid as a plain dict for validation.
    base: dict[str, Any] = {"dimension_weights": {}, "sub_factors": []}
    if eval_path.exists():
        existing = json.loads(eval_path.read_text(encoding="utf-8"))
        base["dimension_weights"] = dict(existing.get("grid", {}).get("dimension_weights", {}))
        base["sub_factors"] = list(existing.get("grid", {}).get("sub_factors", []))
        # Bring sub-factor weights from sidecar (model strips them on load).
        sidecar_path = eng_dir / "evaluation-grid-meta.json"
        if sidecar_path.exists():
            try:
                sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
                w_lookup = sidecar.get("sub_factor_weights", {})
                for sf in base["sub_factors"]:
                    sf_id = sf.get("id")
                    if sf_id in w_lookup:
                        sf["factor_weight_pct"] = float(w_lookup[sf_id])
            except Exception:
                pass

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
            "dimension_weights": base["dimension_weights"],
            "sub_factors": len(base["sub_factors"]),
            "total_max_points": sum(int(sf.get("max_points", 0)) for sf in base["sub_factors"]),
            "invalidated_files": [],
        }

    # Persist mutated grid.
    sub_factor_objs = [
        SubFactor(**{k: v for k, v in sf.items() if k in SubFactor.model_fields})
        for sf in base["sub_factors"]
    ]
    grid = EvaluationGrid(
        client_slug=client_slug,
        is_custom=True,
        sub_factors=sub_factor_objs,
        total_max_points=sum(sf.max_points for sf in sub_factor_objs),
        dimension_weights={k: float(v) for k, v in base["dimension_weights"].items()},
        last_updated=date.today(),
    )
    eval_file = EvaluationFile(grid=grid, last_updated=date.today())
    persistence.write_json(eval_path, eval_file)

    # Update sidecar with current sub-factor weights and override audit.
    sidecar = {
        "template_id": "custom",
        "sub_factor_weights": {
            sf.get("id"): float(sf.get("factor_weight_pct", 0))
            for sf in base["sub_factors"]
        },
        "override_physical_dominance": override_physical_dominance,
        "override_rationale": override_rationale or "",
    }
    (eng_dir / "evaluation-grid-meta.json").write_text(
        json.dumps(sidecar, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    invalidated = persistence.invalidate_downstream(eng_dir, "evaluation-grid.json")

    return {
        "is_valid": True,
        "errors": {},
        "warnings": result["warnings"],
        "dimension_weights": dict(grid.dimension_weights),
        "sub_factors": len(sub_factor_objs),
        "total_max_points": grid.total_max_points,
        "invalidated_files": invalidated,
    }


@mcp_tool
def score_job_classes(
    client_slug: str,
    scores: list[dict[str, Any]],
    scored_by: Optional[str] = None,
) -> dict[str, Any]:
    """Score one or more job classes on the evaluation grid.

    Each entry is `{class_id, awarded: {sub_factor_id: level_index}}`. Single
    class or batch — same tool. Persists evaluation file class_scores. Invalidates
    compensation and adjustments.
    """
    if not persistence.engagement_exists(client_slug):
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r}."
        )
    eng_dir = persistence.get_engagement_dir(client_slug)
    eval_path = eng_dir / "evaluation-grid.json"
    if not eval_path.exists():
        raise MissingDataError(
            f"evaluation-grid.json not found for {client_slug!r} — call select_grid first."
        )

    eval_file = persistence.read_json(eval_path, EvaluationFile)
    grid_dict = {
        "sub_factors": [sf.model_dump() for sf in eval_file.grid.sub_factors],
    }

    errors: list[str] = []
    new_scores: list[ClassScore] = list(eval_file.class_scores)

    # Replace scores for any class_id present in the new payload.
    incoming_ids = {entry.get("class_id") for entry in scores}
    new_scores = [s for s in new_scores if s.class_id not in incoming_ids]

    for entry in scores:
        cls_id = entry.get("class_id")
        awarded = entry.get("awarded") or entry.get("scores") or {}
        if not cls_id:
            errors.append("entry missing class_id")
            continue
        try:
            r = _score_class(grid_dict, awarded)
        except (IndexError, ValueError) as exc:
            errors.append(f"{cls_id}: {exc}")
            continue
        new_scores.append(
            ClassScore(
                class_id=cls_id,
                scores={k: int(v) for k, v in r["per_sub_factor"].items()},
                total_score=float(r["total_score"]),
                scored_by=scored_by,
                scored_date=date.today(),
            )
        )

    if errors:
        raise ValidationError("; ".join(errors))

    eval_file = eval_file.model_copy(
        update={
            "class_scores": new_scores,
            "all_classes_scored": _all_classes_scored(client_slug, new_scores),
            "last_updated": date.today(),
        }
    )
    persistence.write_json(eval_path, eval_file)
    invalidated = persistence.invalidate_downstream(eng_dir, "evaluation-grid.json")

    totals = [s.total_score for s in new_scores]
    return {
        "scored": len(scores),
        "errors": errors,
        "summary": {
            "min_score": min(totals) if totals else 0.0,
            "max_score": max(totals) if totals else 0.0,
            "score_range": (max(totals) - min(totals)) if totals else 0.0,
            "all_classes_scored": eval_file.all_classes_scored,
        },
        "invalidated_files": invalidated,
    }


def _all_classes_scored(client_slug: str, scores: list[ClassScore]) -> bool:
    eng_dir = persistence.get_engagement_dir(client_slug)
    jc_path = eng_dir / "job-classes.json"
    if not jc_path.exists():
        return False
    try:
        f = persistence.read_json(jc_path, JobClassesFile)
    except Exception:
        return False
    expected = {c.id for c in f.classes}
    scored_ids = {s.class_id for s in scores}
    return bool(expected) and expected.issubset(scored_ids)


@mcp_tool
def get_evaluation_summary(
    client_slug: str,
    grade_band_width: Optional[int] = None,
    grade_band_width_rationale: Optional[str] = None,
) -> dict[str, Any]:
    """Return all job classes ranked by total evaluation points, grouped by equal-width grade band.

    R8 G-01 founder decision: equal-width banding only. Default 25 points
    (operator override allowed with rationale stored in operator_decisions).
    Reports dimension breakdown per class and bias warnings.
    """
    if not persistence.engagement_exists(client_slug):
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r}."
        )
    eng_dir = persistence.get_engagement_dir(client_slug)
    eval_path = eng_dir / "evaluation-grid.json"
    jc_path = eng_dir / "job-classes.json"
    if not eval_path.exists():
        raise MissingDataError(
            f"evaluation-grid.json not found for {client_slug!r}."
        )

    band_width = int(grade_band_width or GRADE_BAND_WIDTH_DEFAULT_POINTS)
    if band_width <= 0:
        raise ValidationError(f"grade_band_width must be positive (got {band_width}).")

    if grade_band_width and grade_band_width != GRADE_BAND_WIDTH_DEFAULT_POINTS:
        if not grade_band_width_rationale:
            raise ValidationError(
                f"grade_band_width override ({grade_band_width}) requires "
                "grade_band_width_rationale (audit trail)."
            )
        # Persist rationale in operator decisions sidecar.
        decisions_path = eng_dir / "operator-decisions.json"
        decisions = {}
        if decisions_path.exists():
            try:
                decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
            except Exception:
                decisions = {}
        decisions["grade_band_width"] = band_width
        decisions["grade_band_width_rationale"] = grade_band_width_rationale
        decisions_path.write_text(
            json.dumps(decisions, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    eval_file = persistence.read_json(eval_path, EvaluationFile)
    scores_by_id = {s.class_id: s for s in eval_file.class_scores}

    classes_payload: list[dict[str, Any]] = []
    unscored: list[str] = []
    if jc_path.exists():
        jc_file = persistence.read_json(jc_path, JobClassesFile)
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
    }


__all__ = [
    "customize_grid",
    "get_evaluation_summary",
    "list_grid_templates",
    "score_job_classes",
    "select_grid",
]
