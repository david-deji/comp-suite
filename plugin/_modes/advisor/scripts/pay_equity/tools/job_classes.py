"""Job-class tools: add_job_classes, determine_predominance, override_predominance.

3 of the 19 registered MCP tools.

Spec anchors:
- phase4-final-mcp-architecture.md § 5 Tools 5-7
- r3-r9-spec-corrections.md § R4 (4-criteria predominance + disproportion)
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import ValidationError as PydanticValidationError

from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.errors import ValidationError
from scripts.pay_equity.models import (
    JobClass,
    Predominance,
    PredominanceMethod,
    PredominanceOverrideEvidence,
)
from scripts.pay_equity.validation import PAY_SPREAD_WARN_THRESHOLD


PAY_SPREAD_PCT = PAY_SPREAD_WARN_THRESHOLD * 100  # 30


def _token_overlap(a: str, b: str) -> float:
    """Jaccard similarity of word tokens, case-folded, alpha-only."""
    def _toks(s: str) -> set[str]:
        return {t for t in "".join(c.lower() if c.isalpha() else " " for c in s).split() if len(t) > 2}
    ta, tb = _toks(a), _toks(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _normalize_class(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize incoming class payload — compute female_percentage, fill defaults."""
    out = dict(payload)
    total = int(out.get("total_incumbents", 0))
    female = int(out.get("female_incumbents", 0))
    male = int(out.get("male_incumbents", total - female))
    out["female_incumbents"] = female
    out["male_incumbents"] = male
    if total:
        out["female_percentage"] = round(female / total * 100, 2)
    else:
        out["female_percentage"] = 0.0
    return out


@mcp_tool
def add_job_classes(
    existing_classes: list[dict[str, Any]],
    classes: list[dict[str, Any]],
    enterprise_female_percentage: Optional[float] = None,
) -> dict[str, Any]:
    """Add job classes to the engagement (pure).

    Validates three-criteria grouping (similar duties / similar qualifications /
    same compensation range). Warns on >30% pay spread within a class. Warns on
    >70% description token overlap between classes (likely-duplicate). Receives the
    current classes (fetched by the orchestrator) and returns the full validated
    class set for the orchestrator to persist; downstream staleness is server-side.
    """
    existing: list[JobClass] = [
        JobClass(**{k: v for k, v in c.items() if k in JobClass.model_fields})
        for c in existing_classes
    ]

    warnings: list[str] = []
    pay_spread_warnings: list[dict[str, Any]] = []
    similar_description_warnings: list[dict[str, Any]] = []
    errors: list[str] = []

    new_models: list[JobClass] = []
    for raw in classes:
        normalized = _normalize_class(raw)

        # Three-criteria validation: any explicit `similar_*` flag set to False is a hard failure.
        for flag in ("similar_duties", "similar_qualifications", "similar_responsibilities"):
            if flag in raw and raw[flag] is False:
                errors.append(
                    f"class {raw.get('id', '?')!r}: three-criteria check failed — "
                    f"{flag} is False (CNESST job-class definition Art. 54)."
                )

        # Pay-spread warning: > 30% spread between min and max → flag.
        pay_min = normalized.get("pay_range_min")
        pay_max = normalized.get("pay_range_max")
        if pay_min and pay_max and pay_min > 0:
            spread_pct = (pay_max - pay_min) / pay_min * 100
            if spread_pct > PAY_SPREAD_PCT:
                pay_spread_warnings.append(
                    {
                        "class_id": normalized.get("id"),
                        "spread_pct": round(spread_pct, 1),
                        "message": f"Pay spread {spread_pct:.1f}% exceeds {PAY_SPREAD_PCT:.0f}% — consider splitting class.",
                    }
                )

        # Build the JobClass model — validation errors surface here.
        # R2 S-M1: drop raw input_value from Pydantic error text — free-text
        # fields like description may contain incumbent-identifying info.
        try:
            jc = JobClass(**{k: v for k, v in normalized.items() if k in JobClass.model_fields})
        except PydanticValidationError as exc:
            fields = sorted({str(e["loc"][0]) for e in exc.errors() if e.get("loc")})
            errors.append(
                f"class {raw.get('id', '?')!r}: validation failed on field(s): "
                + ", ".join(fields)
            )
            continue
        except Exception as exc:
            errors.append(f"class {raw.get('id', '?')!r}: {type(exc).__name__}")
            continue
        new_models.append(jc)

    # Similar-description warnings within the new batch.
    for i, a in enumerate(new_models):
        if not a.description:
            continue
        for b in new_models[i + 1 :]:
            if not b.description:
                continue
            sim = _token_overlap(a.description, b.description)
            if sim > 0.70:
                similar_description_warnings.append(
                    {
                        "class_a": a.id,
                        "class_b": b.id,
                        "similarity": round(sim, 2),
                        "message": f"{a.id} and {b.id} share {sim:.0%} description tokens — possible duplicate.",
                    }
                )

    if errors:
        raise ValidationError("; ".join(errors))

    all_classes = existing + new_models

    # Compute enterprise female percentage if not supplied
    enterprise_pct = enterprise_female_percentage
    if enterprise_pct is None:
        total = sum(c.total_incumbents for c in all_classes)
        female = sum(c.female_incumbents for c in all_classes)
        enterprise_pct = round(female / total * 100, 2) if total else 0.0

    warnings.extend(w["message"] for w in pay_spread_warnings)
    warnings.extend(w["message"] for w in similar_description_warnings)

    return {
        "added": len(new_models),
        "total_classes": len(all_classes),
        "classes": [c.model_dump(mode="json") for c in new_models],
        "warnings": warnings,
        "pay_spread_warnings": pay_spread_warnings,
        "similar_description_warnings": similar_description_warnings,
        "enterprise_female_percentage": enterprise_pct,
    }


@mcp_tool
def summarize_predominance(classes: list[dict[str, Any]]) -> dict[str, Any]:
    """Cross-class predominance summary (pure).

    The per-class 4-criteria predominance math runs server-side
    (`payequity_compute_predominance`). This residual keeps the cross-class
    signals that must stay in tested Python: the no-male `global_comparison_eligible`
    route (RLRQ E-12.001 r.2) and the override-skip tally (overridden classes are
    excluded from the server recompute). Receives the classes with their
    determined predominance and returns the bucketed counts.
    """
    female_classes: list[str] = []
    male_classes: list[str] = []
    neutral_classes: list[str] = []
    override_classes: list[str] = []

    for cls in classes:
        cls_id = cls.get("id")
        if cls.get("is_override"):
            override_classes.append(cls_id)
        pred = cls.get("predominance")
        if pred == Predominance.FEMALE.value:
            female_classes.append(cls_id)
        elif pred == Predominance.MALE.value:
            male_classes.append(cls_id)
        elif pred == Predominance.NEUTRAL.value:
            neutral_classes.append(cls_id)

    return {
        "global_comparison_eligible": len(male_classes) == 0,
        "female_classes": female_classes,
        "male_classes": male_classes,
        "neutral_classes": neutral_classes,
        "override_classes": override_classes,
    }


@mcp_tool
def override_predominance(
    job_class: dict[str, Any],
    predominance: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Override the quantitative predominance result using stereotype or historical test (pure).

    Requires structured PredominanceOverrideEvidence. Receives the single target
    job class (fetched by the orchestrator) and returns the one updated class for
    the orchestrator to persist with `is_override=True`.
    """
    try:
        new_pred = Predominance(predominance)
    except ValueError:
        raise ValidationError(
            f"predominance={predominance!r} not in {[p.value for p in Predominance]}"
        )
    try:
        ev = PredominanceOverrideEvidence(**evidence)
    except PydanticValidationError as exc:
        fields = sorted({str(e["loc"][0]) for e in exc.errors() if e.get("loc")})
        raise ValidationError(
            "evidence invalid: validation failed on field(s): " + ", ".join(fields)
        )
    except Exception as exc:
        raise ValidationError(f"evidence invalid: {type(exc).__name__}")

    cls = JobClass(**{k: v for k, v in job_class.items() if k in JobClass.model_fields})
    previous_pred: Optional[Predominance] = cls.predominance
    method = (
        PredominanceMethod.HISTORICAL
        if ev.evidence_type == "historical"
        else PredominanceMethod.STEREOTYPE
    )
    updated = cls.model_copy(
        update={
            "predominance": new_pred,
            "predominance_method": method,
            "predominance_override_evidence": ev,
            "is_override": True,
        }
    )

    return {
        "job_class": updated.model_dump(mode="json"),
        "class_id": updated.id,
        "previous_predominance": previous_pred.value if previous_pred else None,
        "new_predominance": new_pred.value,
        "evidence_recorded": True,
        "method": ev.evidence_type,
    }


__all__ = [
    "add_job_classes",
    "summarize_predominance",
    "override_predominance",
]
