"""Job-class tools: add_job_classes, determine_predominance, override_predominance.

3 of the 19 registered MCP tools.

Spec anchors:
- phase4-final-mcp-architecture.md § 5 Tools 5-7
- r3-r9-spec-corrections.md § R4 (4-criteria predominance + disproportion)
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

from pydantic import ValidationError as PydanticValidationError

from scripts.pay_equity import persistence_gdrive as persistence
from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.computation.predominance import determine_predominance as _compute_predominance
from scripts.pay_equity.errors import MissingDataError, ValidationError
from scripts.pay_equity.models import (
    JobClass,
    JobClassesFile,
    Predominance,
    PredominanceMethod,
    PredominanceOverrideEvidence,
)
from scripts.pay_equity.validation import (
    DISPROPORTION_THRESHOLD_PP_DEFAULT,
    PAY_SPREAD_WARN_THRESHOLD,
)


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
    client_slug: str,
    classes: list[dict[str, Any]],
    enterprise_female_percentage: Optional[float] = None,
) -> dict[str, Any]:
    """Add job classes to the engagement.

    Validates three-criteria grouping (similar duties / similar qualifications /
    same compensation range). Warns on >30% pay spread within a class. Warns on
    >70% description token overlap between classes (likely-duplicate). Persists
    JobClassesFile and invalidates downstream files (evaluation/compensation/
    adjustments) when the file already exists.
    """
    if not persistence.engagement_exists(client_slug):
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r} — call create_engagement first."
        )

    eng_dir = persistence.get_engagement_dir(client_slug)
    jc_path = eng_dir / "job-classes.json"

    existing: list[JobClass] = []
    pre_existing_file = jc_path.exists()
    if pre_existing_file:
        try:
            f = persistence.read_json(jc_path, JobClassesFile)
            existing = list(f.classes)
        except Exception:
            existing = []

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

    file_payload = JobClassesFile(
        client_slug=client_slug,
        classes=all_classes,
        enterprise_female_percentage=enterprise_pct,
        last_updated=date.today(),
    )
    persistence.write_json(jc_path, file_payload)

    invalidated = []
    if pre_existing_file:
        invalidated = persistence.invalidate_downstream(eng_dir, "job-classes.json")

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
        "invalidated_files": invalidated,
    }


@mcp_tool
def determine_predominance(
    client_slug: str,
    disproportion_threshold_pp: float = DISPROPORTION_THRESHOLD_PP_DEFAULT,
) -> dict[str, Any]:
    """Run the 4-criteria CNESST predominance test on all job classes.

    Order applied: numerical (>=60%) → disproportion vs enterprise ratio
    (default >=20pp) → operator-applied historical/stereotype path for remaining
    neutrals. Sets `global_comparison_eligible=true` when no male classes exist
    (signals RLRQ E-12.001 r.2 path).
    """
    if not persistence.engagement_exists(client_slug):
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r}."
        )
    eng_dir = persistence.get_engagement_dir(client_slug)
    jc_path = eng_dir / "job-classes.json"
    if not jc_path.exists():
        raise MissingDataError(
            f"job-classes.json not found for {client_slug!r} — call add_job_classes first."
        )

    file = persistence.read_json(jc_path, JobClassesFile)
    enterprise_pct = file.enterprise_female_percentage

    results: list[dict[str, Any]] = []
    warnings: list[str] = []
    counts = {"female": 0, "male": 0, "neutral": 0}

    updated_classes: list[JobClass] = []
    for cls in file.classes:
        # Skip classes with operator overrides — preserve them.
        if cls.is_override and cls.predominance:
            counts[cls.predominance.value] += 1
            results.append(
                {
                    "class_id": cls.id,
                    "predominance": cls.predominance.value,
                    "method": cls.predominance_method.value if cls.predominance_method else "operator_override",
                    "female_pct": cls.female_percentage,
                    "preserved_override": True,
                }
            )
            updated_classes.append(cls)
            continue

        outcome = _compute_predominance(
            female_pct=cls.female_percentage,
            enterprise_female_pct=enterprise_pct,
            threshold_pp=disproportion_threshold_pp,
        )
        method_map = {
            "quantitative": PredominanceMethod.QUANTITATIVE,
            "disproportion": PredominanceMethod.DISPROPORTION,
        }
        new_pred = Predominance(outcome["predominance"])
        new_method = method_map.get(outcome["method"])
        cls = cls.model_copy(
            update={
                "predominance": new_pred,
                "predominance_method": new_method,
            }
        )
        counts[new_pred.value] += 1
        if new_pred == Predominance.NEUTRAL:
            warnings.append(
                f"class {cls.id}: neutral — apply historical/stereotype override or accept as neutral."
            )
        results.append(
            {
                "class_id": cls.id,
                **{k: v for k, v in outcome.items()},
            }
        )
        updated_classes.append(cls)

    male_classes = counts["male"]
    no_male = male_classes == 0

    file = file.model_copy(
        update={
            "classes": updated_classes,
            "all_predominance_determined": all(
                c.predominance is not None for c in updated_classes
            ),
            "last_updated": date.today(),
        }
    )
    persistence.write_json(jc_path, file)
    persistence.invalidate_downstream(eng_dir, "job-classes.json")

    return {
        "results": results,
        "summary": {
            "female_classes": counts["female"],
            "male_classes": counts["male"],
            "neutral_classes": counts["neutral"],
            "no_male_classes": no_male,
        },
        "warnings": warnings,
        "global_comparison_eligible": no_male,
        "disproportion_threshold_pp": disproportion_threshold_pp,
        "enterprise_female_percentage": enterprise_pct,
    }


@mcp_tool
def override_predominance(
    client_slug: str,
    class_id: str,
    predominance: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Override the quantitative predominance result using stereotype or historical test.

    Requires structured PredominanceOverrideEvidence. The evidence is persisted
    into the JobClass record and downstream files invalidated.
    """
    if not persistence.engagement_exists(client_slug):
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r}."
        )
    eng_dir = persistence.get_engagement_dir(client_slug)
    jc_path = eng_dir / "job-classes.json"
    if not jc_path.exists():
        raise MissingDataError(
            f"job-classes.json not found for {client_slug!r}."
        )

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

    file = persistence.read_json(jc_path, JobClassesFile)
    found = False
    previous_pred: Optional[Predominance] = None
    new_classes: list[JobClass] = []
    for c in file.classes:
        if c.id == class_id:
            previous_pred = c.predominance
            method = (
                PredominanceMethod.HISTORICAL
                if ev.evidence_type == "historical"
                else PredominanceMethod.STEREOTYPE
            )
            c = c.model_copy(
                update={
                    "predominance": new_pred,
                    "predominance_method": method,
                    "predominance_override_evidence": ev,
                    "is_override": True,
                }
            )
            found = True
        new_classes.append(c)
    if not found:
        raise ValidationError(f"class_id {class_id!r} not found")

    file = file.model_copy(update={"classes": new_classes, "last_updated": date.today()})
    persistence.write_json(jc_path, file)
    invalidated = persistence.invalidate_downstream(eng_dir, "job-classes.json")

    return {
        "class_id": class_id,
        "previous_predominance": previous_pred.value if previous_pred else None,
        "new_predominance": new_pred.value,
        "evidence_recorded": True,
        "method": ev.evidence_type,
        "invalidated_files": invalidated,
    }


__all__ = [
    "add_job_classes",
    "determine_predominance",
    "override_predominance",
]
