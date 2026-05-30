"""Engagement-lifecycle tools: list, create, load, get_obligations,
process_deletion_request (Loi 25), set_maintenance_committee (Bill 10).

6 of the 19 registered MCP tools live here.

Spec anchors:
- phase4-final-mcp-architecture.md § 5 Tools 1-4
- r3-r9-spec-corrections.md § R5 (data model), § R7 (deadlines + participation),
  § R9 (Loi 25 retention + deletion)
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import date, timedelta
from typing import Any, Optional

from scripts.pay_equity import persistence_gdrive as persistence
from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.errors import MissingDataError, ValidationError
from scripts.pay_equity.models import (
    AdjustmentFile,
    CompensationFile,
    Engagement,
    Establishment,
    EvaluationFile,
    ExerciseType,
    JobClassesFile,
    MaintenanceCommittee,
    MaintienMode,
    OperatorMode,
    PayPeriodFrequency,
    PostingLocation,
    RetentionPolicy,
    SizeTier,
)
from scripts.pay_equity.models.obligations import get_obligations_matrix
from scripts.pay_equity.validation import (
    PARTICIPATION_LEAD_DAYS,
    RETENTION_YEARS,
    validate_initial_deadline,
    validate_retention_floor,
)


# --- Helpers ----------------------------------------------------------------

_SLUG_RX = re.compile(r"[^a-z0-9]+")


def slugify(name: str) -> str:
    s = _SLUG_RX.sub("-", name.lower()).strip("-")
    if not s:
        raise ValidationError("client_name produces empty slug after normalization")
    return s


def determine_size_tier(employee_count: int) -> SizeTier:
    """Tier auto: 10-49 SMALL, 50-99 MEDIUM, 100+ LARGE; <10 → ValidationError (Art. 4)."""
    if employee_count < 10:
        raise ValidationError(
            f"employee_count={employee_count} below 10 — Loi sur l'équité salariale "
            "applies only to enterprises with 10 or more employees (Art. 4)."
        )
    if employee_count <= 49:
        return SizeTier.SMALL
    if employee_count <= 99:
        return SizeTier.MEDIUM
    return SizeTier.LARGE


def compute_participation_required(
    intended_maintien_mode: Optional[MaintienMode],
    initial_had_committee: bool,
    has_accredited_association: bool,
) -> bool:
    """Art. 76.2.1 (Bill 10): required iff employer_solo AND (initial_had_committee OR has_accredited_association)."""
    if intended_maintien_mode != MaintienMode.EMPLOYER_SOLO:
        return False
    return bool(initial_had_committee or has_accredited_association)


def compute_review_juridique_required(
    employee_count: int, operator_mode: OperatorMode
) -> bool:
    """R8 founder decision: 100+ guided gets the AVIS DE RÉVISION JURIDIQUE flag on every render."""
    return employee_count >= 100 and operator_mode == OperatorMode.GUIDED


def compute_retention_until(
    posting_date: Optional[date], created_date: date
) -> date:
    """Loi 25 / Art. 14: posting_date + 6y, or created_date + 6y if no posting yet."""
    base = posting_date or created_date
    try:
        return date(base.year + RETENTION_YEARS, base.month, base.day)
    except ValueError:
        # Feb 29 on a non-leap landing year — fall back to Feb 28.
        return date(base.year + RETENTION_YEARS, base.month, 28)


def compute_plainte_windows_maintien(maintien_posting_date: date) -> dict[str, date]:
    """Plainte window for maintien: posting+90d → posting+150d (Art. 99-101)."""
    return {
        "plainte_window_start": maintien_posting_date + timedelta(days=90),
        "plainte_window_end": maintien_posting_date + timedelta(days=150),
    }


def compute_participation_earliest_posting(completion_date: date) -> date:
    """Art. 76.2.1: maintien_posting_date >= completion_date + 60d."""
    return completion_date + timedelta(days=PARTICIPATION_LEAD_DAYS)


def _atomic_write_json(path, payload) -> None:
    """Atomic JSON write of arbitrary dict/list payload."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


# --- Tools ------------------------------------------------------------------

@mcp_tool
def list_engagements(status_filter: Optional[str] = None) -> dict[str, Any]:
    """List all known engagements in the engagements directory.

    Returns slug, client name, status, exercise type, and size tier for each.
    Filters by status when status_filter is provided.
    """
    root = persistence.ENGAGEMENTS_ROOT
    if not root.exists():
        return {"engagements": [], "total": 0}
    out: list[dict[str, Any]] = []
    for p in sorted(root.iterdir()):
        if not p.is_dir():
            continue
        eng_path = p / "engagement.json"
        if not eng_path.exists():
            continue
        try:
            eng = persistence.read_json(eng_path, Engagement)
        except Exception:
            continue
        if status_filter and eng.status != status_filter:
            continue
        out.append(
            {
                "client_slug": eng.client_slug,
                "client_name": eng.client_name,
                "status": eng.status,
                "exercise_type": eng.exercise_type.value,
                "size_tier": eng.size_tier.value,
                "employee_count": eng.employee_count,
            }
        )
    return {"engagements": out, "total": len(out)}


@mcp_tool
def create_engagement(
    client_name: str,
    employee_count: int,
    exercise_type: str,
    neq: Optional[str] = None,
    operator_mode: str = "expert",
    has_union: bool = False,
    reference_period_start: Optional[str] = None,
    reference_period_end: Optional[str] = None,
    pay_period_frequency: Optional[str] = None,
    initial_had_committee: bool = False,
    has_accredited_association: bool = False,
    intended_maintien_mode: Optional[str] = None,
    establishments: Optional[list[dict[str, Any]]] = None,
    threshold_reach_year: Optional[int] = None,
) -> dict[str, Any]:
    """Create a new pay equity engagement.

    Auto-determines size tier and legal obligations from employee count.
    Computes participation_required (Art. 76.2.1 Bill 10), statutory_deadline,
    initial_exercise_deadline (Dec 31 of threshold+4y), document_retention_until
    (Loi 25 6y floor), and the 100+ guided AVIS DE RÉVISION JURIDIQUE flag.
    """
    if not client_name or not client_name.strip():
        raise ValidationError("client_name is required")
    try:
        ex_type = ExerciseType(exercise_type)
    except ValueError:
        raise ValidationError(
            f"exercise_type={exercise_type!r} not in {[e.value for e in ExerciseType]}"
        )
    try:
        op_mode = OperatorMode(operator_mode)
    except ValueError:
        raise ValidationError(
            f"operator_mode={operator_mode!r} not in {[o.value for o in OperatorMode]}"
        )
    intended_mode: Optional[MaintienMode] = None
    if intended_maintien_mode is not None:
        try:
            intended_mode = MaintienMode(intended_maintien_mode)
        except ValueError:
            raise ValidationError(
                f"intended_maintien_mode={intended_maintien_mode!r} invalid"
            )

    size_tier = determine_size_tier(employee_count)
    slug = slugify(client_name)
    if persistence.engagement_exists(slug):
        raise ValidationError(
            f"Engagement with slug {slug!r} already exists — load_engagement to resume."
        )

    today = date.today()
    threshold_year = threshold_reach_year if threshold_reach_year else today.year
    initial_deadline = validate_initial_deadline(threshold_year)

    participation_required = compute_participation_required(
        intended_mode, initial_had_committee, has_accredited_association
    )
    review_juridique_required = compute_review_juridique_required(employee_count, op_mode)
    retention_until = compute_retention_until(None, today)

    obligations = get_obligations_matrix(size_tier, ex_type)

    eng_kwargs: dict[str, Any] = dict(
        client_name=client_name.strip(),
        client_slug=slug,
        neq=neq,
        employee_count=employee_count,
        size_tier=size_tier,
        exercise_type=ex_type,
        operator_mode=op_mode,
        has_union=has_union,
        initial_had_committee=initial_had_committee,
        has_accredited_association=has_accredited_association,
        intended_maintien_mode=intended_mode,
        participation_required=participation_required,
        statutory_deadline=initial_deadline if ex_type == ExerciseType.INITIAL else None,
        initial_exercise_deadline=initial_deadline,
        document_retention_until=retention_until,
        created_date=today,
        status="created",
    )
    if establishments:
        eng_kwargs["establishments"] = [Establishment(**e) for e in establishments]
    if pay_period_frequency:
        try:
            eng_kwargs["pay_period_frequency"] = PayPeriodFrequency(pay_period_frequency)
        except ValueError:
            raise ValidationError(
                f"pay_period_frequency={pay_period_frequency!r} invalid"
            )
    if reference_period_start:
        try:
            eng_kwargs["data_period_start"] = date.fromisoformat(reference_period_start)
        except ValueError:
            raise ValidationError(
                f"reference_period_start={reference_period_start!r} not ISO date"
            )
    if reference_period_end:
        try:
            eng_kwargs["data_period_end"] = date.fromisoformat(reference_period_end)
        except ValueError:
            raise ValidationError(
                f"reference_period_end={reference_period_end!r} not ISO date"
            )

    engagement = Engagement(**eng_kwargs)

    eng_dir = persistence.get_engagement_dir(slug)
    eng_dir.mkdir(parents=True, exist_ok=True)
    persistence.write_json(eng_dir / "engagement.json", engagement)

    retention_policy = RetentionPolicy(
        client_slug=slug,
        retention_until=retention_until,
        purge_action="archive_encrypted",
        last_updated=today,
    )
    persistence.write_json(eng_dir / "retention-policy.json", retention_policy)

    return {
        "client_slug": slug,
        "size_tier": size_tier.value,
        "exercise_type": ex_type.value,
        "employee_count": employee_count,
        "operator_mode": op_mode.value,
        "obligations": {
            "committee_required": obligations["committee_required"],
            "maintenance_committee_required": obligations["maintenance_committee_required"],
            "posting_consultation_required": obligations["posting_required"],
            "consultation_period_days": obligations["consultation_period_days"],
            "interim_posting_required": obligations["interim_posting_required"],
        },
        "engagement_path": str(eng_dir),
        "initial_exercise_deadline": initial_deadline.isoformat(),
        "statutory_deadline": initial_deadline.isoformat()
        if ex_type == ExerciseType.INITIAL
        else None,
        "document_retention_until": retention_until.isoformat(),
        "participation_required": participation_required,
        "review_juridique_required": review_juridique_required,
        "intended_maintien_mode": intended_mode.value if intended_mode else None,
        "status": "created",
    }


@mcp_tool
def load_engagement(client_slug: str) -> dict[str, Any]:
    """Load an existing engagement and return all current data, including stale-file warnings."""
    eng_dir = persistence.get_engagement_dir(client_slug)
    eng_path = eng_dir / "engagement.json"
    if not eng_path.exists():
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r} — call create_engagement first."
        )
    engagement = persistence.read_json(eng_path, Engagement)

    def _load(name: str, model_cls):
        p = eng_dir / name
        if not p.exists():
            return None
        try:
            return persistence.read_json(p, model_cls).model_dump(mode="json")
        except Exception:
            return None

    stale_warnings = [
        {
            "file": f,
            "reason": engagement.stale_reasons.get(f, "upstream modified"),
        }
        for f in engagement.stale_files
    ]

    return {
        "engagement": engagement.model_dump(mode="json"),
        "job_classes": _load("job-classes.json", JobClassesFile),
        "evaluation": _load("evaluation-grid.json", EvaluationFile),
        "compensation": _load("compensation.json", CompensationFile),
        "adjustments": _load("adjustments.json", AdjustmentFile),
        "status": engagement.status,
        "stale_warnings": stale_warnings,
    }


@mcp_tool
def get_obligations(client_slug: str) -> dict[str, Any]:
    """Return the full obligation matrix for an engagement based on size tier and exercise type."""
    eng_dir = persistence.get_engagement_dir(client_slug)
    eng_path = eng_dir / "engagement.json"
    if not eng_path.exists():
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r} — call create_engagement first."
        )
    engagement = persistence.read_json(eng_path, Engagement)
    matrix = get_obligations_matrix(engagement.size_tier, engagement.exercise_type)
    return {
        "size_tier": engagement.size_tier.value,
        "exercise_type": engagement.exercise_type.value,
        **matrix,
    }


@mcp_tool
def record_posting_date(
    client_slug: str,
    posting_date: str,
    establishment_id: str = "primary",
    posting_method: str = "physical",
    location: Optional[str] = None,
) -> dict[str, Any]:
    """Record an affichage and re-anchor the Loi 25 retention floor + maintien deadline.

    Per Loi 25 / Art. 14, document_retention_until = posting_date + 6 years.
    Per Art. 76.1, the next maintien deadline = posting_date + 5 years (set on
    statutory_deadline for maintien exercises only).

    Multiple postings (multi-establishment) anchor retention to the EARLIEST
    posting date; statutory_deadline is anchored to the LATEST posting date
    (next maintien window starts after the last establishment posted).
    """
    if posting_method not in {"physical", "digital"}:
        raise ValidationError(
            f"posting_method={posting_method!r} must be 'physical' or 'digital'"
        )
    try:
        post_date = date.fromisoformat(posting_date)
    except ValueError:
        raise ValidationError(
            f"posting_date={posting_date!r} not ISO format"
        )

    eng_dir = persistence.get_engagement_dir(client_slug)
    eng_path = eng_dir / "engagement.json"
    if not eng_path.exists():
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r}."
        )
    engagement = persistence.read_json(eng_path, Engagement)

    new_posting = PostingLocation(
        establishment_id=establishment_id,
        posting_method=posting_method,  # type: ignore[arg-type]
        location=location,
        posted_date=post_date,
    )
    postings = list(engagement.posting_locations) + [new_posting]
    earliest = min(p.posted_date for p in postings if p.posted_date)
    latest = max(p.posted_date for p in postings if p.posted_date)

    # Re-anchor retention to earliest posting + 6y (Loi 25 / Art. 14).
    new_retention = compute_retention_until(earliest, engagement.created_date or date.today())
    # Maintien statutory_deadline = posting + 5y (Art. 76.1).
    new_statutory_deadline = engagement.statutory_deadline
    if engagement.exercise_type == ExerciseType.MAINTENANCE:
        try:
            new_statutory_deadline = date(latest.year + 5, latest.month, latest.day)
        except ValueError:
            new_statutory_deadline = date(latest.year + 5, latest.month, 28)

    updated = engagement.model_copy(
        update={
            "posting_locations": postings,
            "document_retention_until": new_retention,
            "statutory_deadline": new_statutory_deadline,
        }
    )
    persistence.write_json(eng_path, updated)

    pol_path = eng_dir / "retention-policy.json"
    if pol_path.exists():
        policy = persistence.read_json(pol_path, RetentionPolicy)
        new_policy = policy.model_copy(
            update={"retention_until": new_retention, "last_updated": date.today()}
        )
        persistence.write_json(pol_path, new_policy)
    else:
        new_policy = RetentionPolicy(
            client_slug=client_slug,
            retention_until=new_retention,
            purge_action="archive_encrypted",
            last_updated=date.today(),
        )
        persistence.write_json(pol_path, new_policy)

    return {
        "client_slug": client_slug,
        "posting_date": posting_date,
        "establishment_id": establishment_id,
        "posting_method": posting_method,
        "earliest_posting_date": earliest.isoformat(),
        "latest_posting_date": latest.isoformat(),
        "document_retention_until": new_retention.isoformat(),
        "statutory_deadline": (
            new_statutory_deadline.isoformat() if new_statutory_deadline else None
        ),
        "retention_anchored_to_posting": True,
    }


@mcp_tool
def process_deletion_request(
    client_slug: str,
    requested_deletion_date: str,
    requestor: str,
    reason: Optional[str] = None,
) -> dict[str, Any]:
    """Process a deletion request against the Loi 25 6-year retention floor.

    Rejects when requested_deletion_date < document_retention_until. Every decision
    is appended to retention-policy-decisions.json as an audit trail.

    R1 H-2 / R2 S-H3: retention floor must be anchored to posting_date + 6y, not
    creation_date + 6y. If no posting has been recorded, refuse approval — we
    cannot prove the legal floor has elapsed.
    """
    eng_dir = persistence.get_engagement_dir(client_slug)
    eng_path = eng_dir / "engagement.json"
    if not eng_path.exists():
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r}."
        )
    engagement = persistence.read_json(eng_path, Engagement)
    pol_path = eng_dir / "retention-policy.json"
    if not pol_path.exists():
        raise MissingDataError(
            f"retention-policy.json not found for {client_slug!r}."
        )
    policy = persistence.read_json(pol_path, RetentionPolicy)

    try:
        req_date = date.fromisoformat(requested_deletion_date)
    except ValueError:
        raise ValidationError(
            f"requested_deletion_date={requested_deletion_date!r} not ISO format"
        )

    no_posting_recorded = not engagement.posting_locations
    if no_posting_recorded:
        approved = False
        rejection_reason = (
            "Loi 25 / Art. 14: posting date not recorded — retention floor "
            "(posting + 6 years) cannot be verified. Use record_posting_date "
            "before requesting deletion."
        )
    else:
        check = validate_retention_floor(policy.retention_until, req_date)
        approved = bool(check["is_valid"])
        rejection_reason = ""
        if not approved:
            rejection_reason = (
                f"Loi 25 / Art. 14: retention runs until {policy.retention_until.isoformat()}; "
                "deletion before that date rejected."
            )

    retention_remaining = (policy.retention_until - date.today()).days
    log_entry = {
        "decision_date": date.today().isoformat(),
        "requestor": requestor,
        "requested_deletion_date": requested_deletion_date,
        "approved": approved,
        "reason": reason or "",
        "rejection_reason": rejection_reason,
        "retention_until_at_decision": policy.retention_until.isoformat(),
        "retention_remaining_days": retention_remaining,
        "posting_recorded": not no_posting_recorded,
    }
    log_path = eng_dir / "retention-policy-decisions.json"
    existing: list[dict[str, Any]] = []
    if log_path.exists():
        try:
            existing = json.loads(log_path.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    existing.append(log_entry)
    _atomic_write_json(log_path, existing)

    return {
        "approved": approved,
        "retention_until": policy.retention_until.isoformat(),
        "requested_deletion_date": requested_deletion_date,
        "rejection_reason": rejection_reason,
        "decision_logged": True,
        "retention_remaining_days": retention_remaining,
        "posting_recorded": not no_posting_recorded,
    }


@mcp_tool
def set_maintenance_committee(
    client_slug: str,
    established_date: str,
    members: list[dict[str, Any]],
    quorum_rule: str,
    decision_method: str,
    meeting_frequency: str,
    union_representation_per_unit: Optional[list[dict[str, Any]]] = None,
    is_continuation_of_initial: bool = False,
) -> dict[str, Any]:
    """Set the maintenance committee for a 100+ engagement (Bill 10, 2019).

    The maintenance committee is distinct from the initial committee — it
    governs the maintien (5-year audit) and must be established separately.
    Persists to maintenance-committee.json without disturbing the initial
    committee record (when present).
    """
    eng_dir = persistence.get_engagement_dir(client_slug)
    if not persistence.engagement_exists(client_slug):
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r} — call create_engagement first."
        )
    try:
        est_date = date.fromisoformat(established_date)
    except ValueError:
        raise ValidationError(
            f"established_date={established_date!r} not ISO format"
        )

    committee = MaintenanceCommittee(
        client_slug=client_slug,
        established_date=est_date,
        members=members,
        quorum_rule=quorum_rule,
        decision_method=decision_method,
        meeting_frequency=meeting_frequency,
        union_representation_per_unit=union_representation_per_unit or [],
        is_continuation_of_initial=is_continuation_of_initial,
    )
    persistence.write_json(eng_dir / "maintenance-committee.json", committee)

    return {
        "client_slug": client_slug,
        "established_date": est_date.isoformat(),
        "member_count": len(members),
        "is_continuation_of_initial": is_continuation_of_initial,
        "saved": True,
        "committee_path": str(eng_dir / "maintenance-committee.json"),
    }


__all__ = [
    "compute_participation_earliest_posting",
    "compute_participation_required",
    "compute_plainte_windows_maintien",
    "compute_retention_until",
    "compute_review_juridique_required",
    "create_engagement",
    "determine_size_tier",
    "get_obligations",
    "list_engagements",
    "load_engagement",
    "process_deletion_request",
    "set_maintenance_committee",
    "slugify",
]
