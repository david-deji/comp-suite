"""Engagement-lifecycle tools: create, get_obligations,
record_posting_date, process_deletion_request (Loi 25),
set_maintenance_committee (Bill 10).

Pure compute. Each tool receives the engagement-data it used to read as
function arguments and returns built/validated models (model dumps) for the
orchestrator to persist via payequity_put_*. No persistence, no network, no
MCP client lives here.

Spec anchors:
- phase4-final-mcp-architecture.md § 5 Tools 1-4
- r3-r9-spec-corrections.md § R5 (data model), § R7 (deadlines + participation),
  § R9 (Loi 25 retention + deletion)
- p4b-cutover-contract.md (this cutover)
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any, Optional

from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.errors import MissingDataError, ValidationError
from scripts.pay_equity.models import (
    Engagement,
    Establishment,
    ExerciseType,
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


# --- Tools ------------------------------------------------------------------

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
    """Create a new pay equity engagement (pure: builds the models, does not persist).

    Auto-determines size tier and legal obligations from employee count.
    Computes participation_required (Art. 76.2.1 Bill 10), statutory_deadline,
    initial_exercise_deadline (Dec 31 of threshold+4y), document_retention_until
    (Loi 25 6y floor), and the 100+ guided AVIS DE RÉVISION JURIDIQUE flag.

    The orchestrator must call payequity_get_engagement(engagement_id=slug) first;
    if it already exists, refuse before calling this. Returns both built models
    (engagement, retention_policy) for the orchestrator to persist via
    payequity_put_engagement / payequity_put_retention_policy.
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

    retention_policy = RetentionPolicy(
        client_slug=slug,
        retention_until=retention_until,
        purge_action="archive_encrypted",
        last_updated=today,
    )

    return {
        "engagement": engagement.model_dump(mode="json"),
        "retention_policy": retention_policy.model_dump(mode="json"),
        "summary": {
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
            "initial_exercise_deadline": initial_deadline.isoformat(),
            "statutory_deadline": initial_deadline.isoformat()
            if ex_type == ExerciseType.INITIAL
            else None,
            "document_retention_until": retention_until.isoformat(),
            "participation_required": participation_required,
            "review_juridique_required": review_juridique_required,
            "intended_maintien_mode": intended_mode.value if intended_mode else None,
            "status": "created",
        },
    }


@mcp_tool
def get_obligations(size_tier: str, exercise_type: str) -> dict[str, Any]:
    """Return the full obligation matrix for an engagement (pure: derived from passed-in fields).

    The orchestrator fetches the engagement via payequity_get_engagement and passes
    its size_tier + exercise_type in. Read-only / derived — nothing to persist.
    """
    try:
        tier = SizeTier(size_tier)
    except ValueError:
        raise ValidationError(
            f"size_tier={size_tier!r} not in {[t.value for t in SizeTier]}"
        )
    try:
        ex_type = ExerciseType(exercise_type)
    except ValueError:
        raise ValidationError(
            f"exercise_type={exercise_type!r} not in {[e.value for e in ExerciseType]}"
        )
    matrix = get_obligations_matrix(tier, ex_type)
    return {
        "size_tier": tier.value,
        "exercise_type": ex_type.value,
        **matrix,
    }


@mcp_tool
def record_posting_date(
    engagement: dict[str, Any],
    retention_policy: Optional[dict[str, Any]],
    posting_date: str,
    establishment_id: str = "primary",
    posting_method: str = "physical",
    location: Optional[str] = None,
) -> dict[str, Any]:
    """Record an affichage and re-anchor the Loi 25 retention floor + maintien deadline (pure).

    Per Loi 25 / Art. 14, document_retention_until = posting_date + 6 years.
    Per Art. 76.1, the next maintien deadline = posting_date + 5 years (set on
    statutory_deadline for maintien exercises only).

    Multiple postings (multi-establishment) anchor retention to the EARLIEST
    posting date; statutory_deadline is anchored to the LATEST posting date
    (next maintien window starts after the last establishment posted).

    The orchestrator passes the current engagement + retention-policy blobs in
    (payequity_get_engagement / payequity_get_retention_policy) and persists the
    updated models returned here via payequity_put_engagement /
    payequity_put_retention_policy.
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

    engagement_model = Engagement.model_validate(engagement)

    new_posting = PostingLocation(
        establishment_id=establishment_id,
        posting_method=posting_method,  # type: ignore[arg-type]
        location=location,
        posted_date=post_date,
    )
    postings = list(engagement_model.posting_locations) + [new_posting]
    earliest = min(p.posted_date for p in postings if p.posted_date)
    latest = max(p.posted_date for p in postings if p.posted_date)

    # Re-anchor retention to earliest posting + 6y (Loi 25 / Art. 14).
    new_retention = compute_retention_until(
        earliest, engagement_model.created_date or date.today()
    )
    # Maintien statutory_deadline = posting + 5y (Art. 76.1).
    new_statutory_deadline = engagement_model.statutory_deadline
    if engagement_model.exercise_type == ExerciseType.MAINTENANCE:
        try:
            new_statutory_deadline = date(latest.year + 5, latest.month, latest.day)
        except ValueError:
            new_statutory_deadline = date(latest.year + 5, latest.month, 28)

    updated = engagement_model.model_copy(
        update={
            "posting_locations": postings,
            "document_retention_until": new_retention,
            "statutory_deadline": new_statutory_deadline,
        }
    )

    if retention_policy is not None:
        policy = RetentionPolicy.model_validate(retention_policy)
        new_policy = policy.model_copy(
            update={"retention_until": new_retention, "last_updated": date.today()}
        )
    else:
        new_policy = RetentionPolicy(
            client_slug=engagement_model.client_slug,
            retention_until=new_retention,
            purge_action="archive_encrypted",
            last_updated=date.today(),
        )

    return {
        "engagement": updated.model_dump(mode="json"),
        "retention_policy": new_policy.model_dump(mode="json"),
        "summary": {
            "client_slug": engagement_model.client_slug,
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
        },
    }


@mcp_tool
def process_deletion_request(
    engagement: dict[str, Any],
    retention_policy: dict[str, Any],
    requested_deletion_date: str,
    requestor: str,
    reason: Optional[str] = None,
) -> dict[str, Any]:
    """Process a deletion request against the Loi 25 6-year retention floor (pure).

    Rejects when requested_deletion_date < document_retention_until. Returns the
    decision PLUS a discrete audit_entry for the orchestrator to append via
    payequity_append_audit_log (the Loi 25 deletion-decision trail).

    R1 H-2 / R2 S-H3: retention floor must be anchored to posting_date + 6y, not
    creation_date + 6y. If no posting has been recorded, refuse approval — we
    cannot prove the legal floor has elapsed.

    This is the *advisory* Loi 25 retention-floor check (approved/rejected +
    audit). It is NOT the W-A backend purge tool payequity_process_deletion_request
    (a separate Tier-4 data_delete op). Keep both distinct.
    """
    if engagement is None:
        raise MissingDataError("engagement is required")
    if retention_policy is None:
        raise MissingDataError("retention_policy is required")
    engagement_model = Engagement.model_validate(engagement)
    policy = RetentionPolicy.model_validate(retention_policy)

    try:
        req_date = date.fromisoformat(requested_deletion_date)
    except ValueError:
        raise ValidationError(
            f"requested_deletion_date={requested_deletion_date!r} not ISO format"
        )

    no_posting_recorded = not engagement_model.posting_locations
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
    audit_entry = {
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

    return {
        "decision": {
            "approved": approved,
            "retention_until": policy.retention_until.isoformat(),
            "requested_deletion_date": requested_deletion_date,
            "rejection_reason": rejection_reason,
            "retention_remaining_days": retention_remaining,
            "posting_recorded": not no_posting_recorded,
        },
        "audit_entry": audit_entry,
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
    """Set the maintenance committee for a 100+ engagement (Bill 10, 2019) (pure).

    The maintenance committee is distinct from the initial committee — it
    governs the maintien (5-year audit) and must be established separately.
    Builds + validates the model and returns it for the orchestrator to persist
    via payequity_put_maintenance_committee (without disturbing the initial
    committee record). The orchestrator confirms the engagement exists first via
    payequity_get_engagement.
    """
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

    return {
        "committee": committee.model_dump(mode="json"),
        "summary": {
            "client_slug": client_slug,
            "established_date": est_date.isoformat(),
            "member_count": len(members),
            "is_continuation_of_initial": is_continuation_of_initial,
        },
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
    "process_deletion_request",
    "record_posting_date",
    "set_maintenance_committee",
    "slugify",
]
