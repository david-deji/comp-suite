"""Compensation comparison tool: compare_compensation.

1 of the 19 registered MCP tools.

Spec anchors:
- phase4-final-mcp-architecture.md § 5 Tool 13
- constraints.md § Pairing tolerance (exact grade match only — no tolerance param)
- r3-r9-spec-corrections.md § R5 (hours-by-period for retroactive interest)
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

from scripts.pay_equity import persistence_gdrive as persistence
from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.computation.comparison import (
    compare_job_to_job,
    compare_with_regression,
)
from scripts.pay_equity.computation.global_comparison import apply_global_comparison
from scripts.pay_equity.computation.regression import MIN_MALE_CLASSES, fit_male_wage_line
from scripts.pay_equity.errors import MissingDataError, ValidationError
from scripts.pay_equity.models import (
    ClassCompensation,
    CompensationComponent,
    CompensationFile,
    ComparisonResult,
    EvaluationFile,
    GlobalComparisonResult,
    HoursWorked,
    JobClassesFile,
    Predominance,
    RegressionResult,
)


_COMPONENT_FIELDS: tuple[str, ...] = (
    "base_salary_hourly",
    "bonuses_commissions",
    "shift_differentials",
    "group_insurance_employer",
    "pension_employer",
    "paid_leave_above_statutory",
    "other_monetary",
)


def _build_component(payload: dict[str, Any]) -> CompensationComponent:
    base_kwargs = {k: float(payload.get(k, 0)) for k in _COMPONENT_FIELDS}
    total = sum(base_kwargs[k] for k in _COMPONENT_FIELDS)
    return CompensationComponent(**base_kwargs, total_compensation_hourly=total)


def _to_payload(cc: ClassCompensation) -> dict[str, Any]:
    return {
        "id": cc.class_id,
        "class_id": cc.class_id,
        "evaluation_score": cc.evaluation_score,
        "grade": cc.grade,
        "predominance": cc.predominance.value,
        "total_compensation_hourly": cc.components.total_compensation_hourly,
    }


@mcp_tool
def compare_compensation(
    client_slug: str,
    method: str = "hybrid",
    class_compensations: Optional[list[dict[str, Any]]] = None,
    reference_compensation: Optional[float] = None,
) -> dict[str, Any]:
    """Run compensation comparison between female and male job classes.

    Job-to-job by exact grade match is default (R8: NO grade_tolerance).
    When method=='hybrid', regression is used as fallback for female classes
    without a same-grade male comparator. Global comparison route triggered
    automatically when no male classes exist (RLRQ E-12.001 r.2). Persists
    CompensationFile and invalidates adjustments.
    """
    if not persistence.engagement_exists(client_slug):
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r}."
        )
    eng_dir = persistence.get_engagement_dir(client_slug)

    jc_path = eng_dir / "job-classes.json"
    eval_path = eng_dir / "evaluation-grid.json"
    if not jc_path.exists():
        raise MissingDataError(
            f"job-classes.json not found — call add_job_classes first."
        )

    jc_file = persistence.read_json(jc_path, JobClassesFile)
    score_lookup: dict[str, Any] = {}
    if eval_path.exists():
        try:
            eval_file = persistence.read_json(eval_path, EvaluationFile)
            score_lookup = {s.class_id: s for s in eval_file.class_scores}
        except Exception:
            score_lookup = {}

    # Load existing compensation file (if any) to preserve operator-entered components.
    comp_path = eng_dir / "compensation.json"
    existing_components: dict[str, CompensationComponent] = {}
    existing_hours: dict[str, Optional[HoursWorked]] = {}
    if comp_path.exists():
        try:
            existing = persistence.read_json(comp_path, CompensationFile)
            for cc in existing.class_compensations:
                existing_components[cc.class_id] = cc.components
                existing_hours[cc.class_id] = cc.hours_worked
        except Exception:
            pass

    # Apply incoming class_compensations payloads.
    incoming_comp: dict[str, dict[str, Any]] = {}
    if class_compensations:
        for entry in class_compensations:
            cid = entry.get("class_id") or entry.get("id")
            if cid:
                incoming_comp[cid] = entry

    class_comps: list[ClassCompensation] = []
    for cls in jc_file.classes:
        if cls.id in incoming_comp:
            payload = incoming_comp[cls.id]
            comp = _build_component(payload.get("components", payload))
            hours_payload = payload.get("hours_worked")
            hours = HoursWorked(**hours_payload) if hours_payload else existing_hours.get(cls.id)
        else:
            comp = existing_components.get(cls.id)
            hours = existing_hours.get(cls.id)
        if comp is None:
            # No compensation supplied yet — skip but keep going for partial input.
            continue

        score_obj = score_lookup.get(cls.id)
        if score_obj:
            score = float(score_obj.total_score)
        elif incoming_comp.get(cls.id, {}).get("evaluation_score") is not None:
            score = float(incoming_comp[cls.id]["evaluation_score"])
        else:
            score = float(cls.evaluation_score or 0)
        grade = cls.grade
        if grade is None and incoming_comp.get(cls.id, {}).get("grade") is not None:
            grade = incoming_comp[cls.id]["grade"]
        if grade is None:
            grade = 0
        class_comps.append(
            ClassCompensation(
                class_id=cls.id,
                predominance=cls.predominance or Predominance.NEUTRAL,
                evaluation_score=score,
                grade=int(grade),
                components=comp,
                hours_worked=hours,
            )
        )

    if not class_comps:
        raise ValidationError(
            "No class compensations available — supply class_compensations or pre-load compensation.json."
        )

    female_payloads = [_to_payload(c) for c in class_comps if c.predominance == Predominance.FEMALE]
    male_payloads = [_to_payload(c) for c in class_comps if c.predominance == Predominance.MALE]

    method_used = method
    comparisons: list[ComparisonResult] = []
    regression: Optional[dict[str, Any]] = None
    global_comparison: Optional[dict[str, Any]] = None
    warnings: list[str] = []

    if not male_payloads:
        # Global comparison route — RLRQ E-12.001 r.2.
        global_comparison = apply_global_comparison(
            female_payloads, reference_compensation=reference_compensation
        )
        is_unverified = global_comparison["data_status"] == "UNVERIFIED"
        method_used = "global_unverified" if is_unverified else "global"
        for c in global_comparison["comparisons"]:
            comparisons.append(
                ComparisonResult(
                    female_class_id=c["female_class_id"],
                    male_comparator_id=None,
                    comparison_method=method_used,  # type: ignore[arg-type]
                    female_compensation=c["female_compensation"],
                    male_compensation=c["prescribed_target"],
                    gap_hourly=c["gap_hourly"],
                    gap_percentage=(
                        c["gap_hourly"] / c["prescribed_target"] * 100.0
                        if c["prescribed_target"]
                        else 0.0
                    ),
                    requires_adjustment=c["requires_adjustment"],
                    data_status=global_comparison["data_status"],
                )
            )
        if is_unverified:
            warnings.append(
                "Global comparison: reference_compensation not supplied — output flagged [UNVERIFIED]. "
                "RLRQ E-12.001 r.2 prescribed comparator tariff required to compute gap."
            )
    else:
        # Job-to-job exact-grade pass first.
        unmatched_female: list[dict[str, Any]] = []
        for fp in female_payloads:
            j2j = compare_job_to_job(fp, male_payloads)
            if j2j is not None:
                comparisons.append(
                    ComparisonResult(
                        female_class_id=j2j["female_class_id"],
                        male_comparator_id=j2j["male_comparator_id"],
                        comparison_method="job_to_job",
                        female_compensation=j2j["female_compensation"],
                        male_compensation=j2j["male_compensation"],
                        gap_hourly=j2j["gap_hourly"],
                        gap_percentage=j2j["gap_percentage"],
                        requires_adjustment=j2j["requires_adjustment"],
                    )
                )
            else:
                unmatched_female.append(fp)

        if unmatched_female:
            if method == "job_to_job":
                # No fallback in pure job-to-job mode — record as warnings.
                for fp in unmatched_female:
                    warnings.append(
                        f"class {fp['id']}: no male class at grade {fp['grade']} "
                        f"and method=job_to_job — needs hybrid or regression."
                    )
            elif len(male_payloads) >= MIN_MALE_CLASSES:
                regression = fit_male_wage_line(male_payloads)
                method_used = "hybrid" if comparisons else "regression"
                for fp in unmatched_female:
                    r = compare_with_regression(fp, regression)
                    comparisons.append(
                        ComparisonResult(
                            female_class_id=r["female_class_id"],
                            male_comparator_id=None,
                            comparison_method="regression",
                            female_compensation=r["female_compensation"],
                            male_compensation=r["male_compensation"],
                            gap_hourly=r["gap_hourly"],
                            gap_percentage=r["gap_percentage"],
                            requires_adjustment=r["requires_adjustment"],
                        )
                    )
                if regression["quality_assessment"] != "good":
                    warnings.append(
                        f"Regression quality: {regression['quality_assessment']} "
                        f"(R²={regression['r_squared']:.2f}). {regression['quality_notes']}"
                    )
            else:
                for fp in unmatched_female:
                    warnings.append(
                        f"class {fp['id']}: insufficient male classes "
                        f"({len(male_payloads)}) for regression fallback."
                    )

    # Build a hours-by-class lookup for total_gap_annual; fall back to 1950 if absent.
    hours_lookup = {
        cc.class_id: (cc.hours_worked.annual_baseline if cc.hours_worked else None)
        for cc in class_comps
    }
    total_gap_annual = 0.0
    for c in comparisons:
        if c.gap_hourly > 0 and c.data_status == "VERIFIED":
            annual = hours_lookup.get(c.female_class_id) or 1950.0
            total_gap_annual += c.gap_hourly * annual
    classes_with_gaps = sum(1 for c in comparisons if c.requires_adjustment is True)
    classes_without_gaps = sum(1 for c in comparisons if c.requires_adjustment is False)
    classes_unverified = sum(1 for c in comparisons if c.data_status == "UNVERIFIED")

    file_payload = CompensationFile(
        client_slug=client_slug,
        method=method_used,  # type: ignore[arg-type]
        class_compensations=class_comps,
        comparison_results=comparisons,
        regression=RegressionResult(**{
            k: v for k, v in regression.items()
            if k in RegressionResult.model_fields
        }) if regression else None,
        global_comparison=GlobalComparisonResult(
            reference_category_1=global_comparison["reference_category_1"],
            reference_category_2=global_comparison["reference_category_2"],
            prescribed_ratio=global_comparison["prescribed_ratio"],
            reference_compensation=global_comparison.get("reference_compensation") or 0.0,
            note=global_comparison["note"],
            data_status=global_comparison["data_status"],
            note_unverified=(
                global_comparison["note"]
                if global_comparison["data_status"] == "UNVERIFIED"
                else None
            ),
        ) if global_comparison else None,
        total_gap_annual=total_gap_annual,
        last_updated=date.today(),
    )
    persistence.write_json(comp_path, file_payload)
    invalidated = persistence.invalidate_downstream(eng_dir, "compensation.json")

    return {
        "method_used": method_used,
        "comparisons": [c.model_dump(mode="json") for c in comparisons],
        "regression": regression,
        "global_comparison": global_comparison,
        "total_gap_annual": total_gap_annual,
        "classes_with_gaps": classes_with_gaps,
        "classes_without_gaps": classes_without_gaps,
        "classes_unverified": classes_unverified,
        "warnings": warnings,
        "invalidated_files": invalidated,
    }


__all__ = ["compare_compensation"]
