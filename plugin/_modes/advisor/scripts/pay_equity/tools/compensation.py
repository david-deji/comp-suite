"""Compensation input-shaping: build_class_compensation.

Pure compensation-input shaping for the pay-equity orchestrator. The comparison
decision flow (job-to-job -> regression -> global) is server-side
(`payequity_compute_comparison`, W-A A1 verbatim port). This module keeps only the
per-class ClassCompensation assembly that feeds `payequity_put_class_compensation`.

Spec anchors:
- phase4-final-mcp-architecture.md § 5 Tool 13
- p4b-cutover-contract.md § OR-5 (compensation input shaping only; decision flow server-side)
"""
from __future__ import annotations

from typing import Any, Optional

from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.errors import ValidationError
from scripts.pay_equity.models import (
    ClassCompensation,
    CompensationComponent,
    HoursWorked,
    Predominance,
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


@mcp_tool
def build_class_compensation(
    payload: dict[str, Any],
    *,
    job_class: Optional[dict[str, Any]] = None,
    evaluation_score: Optional[float] = None,
) -> dict[str, Any]:
    """Assemble a single ClassCompensation from an operator-entered payload.

    Pure input shaping for `payequity_put_class_compensation`. The score/grade
    fallbacks mirror the former tool: explicit payload value wins, then the passed
    evaluation_score, then the job_class's own evaluation_score/grade, then 0.

    `payload` carries the raw compensation `components` (or the component fields at
    top level) and optionally `hours_worked`, `evaluation_score`, `grade`, `class_id`.
    `job_class` (when supplied) is the backend job-class dict — used for the
    class_id, predominance, score and grade fallbacks.
    """
    job_class = job_class or {}
    cid = payload.get("class_id") or payload.get("id") or job_class.get("id")
    if not cid:
        raise ValidationError(
            "build_class_compensation: class_id is required "
            "(supply payload.class_id or job_class.id)."
        )

    comp = _build_component(payload.get("components", payload))

    hours_payload = payload.get("hours_worked")
    hours = HoursWorked(**hours_payload) if hours_payload else None

    if payload.get("evaluation_score") is not None:
        score = float(payload["evaluation_score"])
    elif evaluation_score is not None:
        score = float(evaluation_score)
    else:
        score = float(job_class.get("evaluation_score") or 0)

    grade = payload.get("grade")
    if grade is None:
        grade = job_class.get("grade")
    if grade is None:
        grade = 0

    predominance_value = (
        payload.get("predominance")
        or job_class.get("predominance")
        or Predominance.NEUTRAL.value
    )

    class_comp = ClassCompensation(
        class_id=cid,
        predominance=Predominance(predominance_value),
        evaluation_score=score,
        grade=int(grade),
        components=comp,
        hours_worked=hours,
    )
    return class_comp.model_dump(mode="json")


__all__ = ["build_class_compensation"]
