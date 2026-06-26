"""Maintenance + participation tools: import_prior_exercise, record_participation_session.

2 of the registered MCP tools, refactored pure (no persistence). MCP fetch/persist
lives in the orchestration markdown; these functions receive their former reads as
arguments and return models for the orchestrator to persist.

Spec anchors:
- phase4-final-mcp-architecture.md § 5 Tool 15 (import_prior_exercise)
- r3-r9-spec-corrections.md § R7 Process de participation (Art. 76.2.1)
- p4b-cutover-contract.md § OR-7 (participation gate recomputes timing from passed-in data)
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.errors import ValidationError
from scripts.pay_equity.models import ParticipationSession
from scripts.pay_equity.validation import (
    PARTICIPATION_LEAD_DAYS,
    validate_participation_timing,
)


@mcp_tool
def import_prior_exercise(
    prior_data: dict[str, Any],
    current_classes: dict[str, Any],
) -> dict[str, Any]:
    """Import results from a prior pay equity exercise for maintenance audit comparison.

    `prior_data` carries `exercise_date`, `job_classes`, `comparison_method`, and
    `adjustments_applied`. `current_classes` is the current job-classes file blob
    (a JobClassesFile dump) used for the diff. The prior-exercise snapshot is
    transient import provenance — NOT persisted as a backend entity (RD-P4-1).
    Returns the import summary and a diff against the current classes.
    """
    # Loose validation — allow prior_data to be any well-formed dict but require key fields.
    required = ("exercise_date", "job_classes", "comparison_method")
    missing = [k for k in required if k not in prior_data]
    if missing:
        raise ValidationError(
            f"prior_data missing required keys: {missing}"
        )
    try:
        exercise_date = date.fromisoformat(prior_data["exercise_date"])
    except (TypeError, ValueError):
        raise ValidationError(
            f"prior_data.exercise_date={prior_data.get('exercise_date')!r} not ISO format"
        )

    prior_classes = list(prior_data.get("job_classes", []))
    prior_method = str(prior_data.get("comparison_method", ""))
    prior_adjustments = int(prior_data.get("adjustments_applied", 0))

    # Build diff vs current job classes (F053 — compare_to_prior).
    diff = _diff_classes(current_classes, prior_classes)

    return {
        "imported_classes": len(prior_classes),
        "prior_exercise_date": exercise_date.isoformat(),
        "prior_method": prior_method,
        "prior_adjustments": prior_adjustments,
        "diff": diff,
    }


def _diff_classes(
    current_classes: Optional[dict[str, Any]],
    prior_classes: list[dict[str, Any]],
) -> dict[str, Any]:
    if not current_classes:
        return {"available": False, "reason": "current job-classes not provided"}

    current_list = current_classes.get("classes", []) or []
    current_ids = {c.get("id"): c for c in current_list if c.get("id")}
    prior_ids = {pc.get("id"): pc for pc in prior_classes if pc.get("id")}

    added = [cid for cid in current_ids if cid not in prior_ids]
    removed = [cid for cid in prior_ids if cid not in current_ids]

    score_changes: list[dict[str, Any]] = []
    predominance_changes: list[dict[str, Any]] = []
    for cid in current_ids:
        if cid not in prior_ids:
            continue
        cur = current_ids[cid]
        pri = prior_ids[cid]
        cur_score = cur.get("evaluation_score")
        pri_score = pri.get("evaluation_score")
        if cur_score is not None and pri_score is not None and cur_score != pri_score:
            score_changes.append(
                {"class_id": cid, "prior_score": pri_score, "current_score": cur_score}
            )
        cur_pred = cur.get("predominance")
        pri_pred = pri.get("predominance")
        if cur_pred and pri_pred and cur_pred != pri_pred:
            predominance_changes.append(
                {"class_id": cid, "prior_predominance": pri_pred, "current_predominance": cur_pred}
            )

    return {
        "available": True,
        "added_classes": added,
        "removed_classes": removed,
        "score_changes": score_changes,
        "predominance_changes": predominance_changes,
    }


@mcp_tool
def record_participation_session(
    engagement: dict[str, Any],
    participants: list[dict[str, Any]],
    methodology: str,
    information_transmission: list[dict[str, Any]],
    consultations_held: list[dict[str, Any]],
    questions_and_observations: list[dict[str, Any]],
    participation_completion_date: str,
    methodology_notes: Optional[str] = None,
    maintien_posting_date: Optional[str] = None,
    force_record_with_warning: bool = False,
    force_rationale: Optional[str] = None,
) -> dict[str, Any]:
    """Record the Art. 76.2.1 participation process session (Phase M1.5).

    Required when engagement.participation_required = True (solo-employer maintien
    AND (initial had committee OR accredited association exists)). Enforces the
    hard timing gate: participation_completion_date + 60 days <= maintien posting.

    Per R5 REG-H1, this is a HARD GATE — the session refuses to return if timing
    fails, unless the operator explicitly sets force_record_with_warning=True AND
    supplies force_rationale. On force, returns the session model PLUS an
    `audit_entry` dict for the orchestrator to append to the audit log.

    `engagement` is the fetched engagement blob (for `participation_required` and
    `statutory_deadline`). No persistence here — the orchestrator persists the
    returned session and audit_entry.
    """
    from datetime import timedelta

    client_slug = engagement.get("client_slug")

    if not engagement.get("participation_required"):
        raise ValidationError(
            f"client {client_slug!r}: participation_required=False — Art. 76.2.1 "
            "only triggers under solo employer maintien with committee or association."
        )

    try:
        completion_date = date.fromisoformat(participation_completion_date)
    except ValueError:
        raise ValidationError(
            f"participation_completion_date={participation_completion_date!r} not ISO format"
        )

    posting_date: Optional[date] = None
    if maintien_posting_date:
        try:
            posting_date = date.fromisoformat(maintien_posting_date)
        except ValueError:
            raise ValidationError(
                f"maintien_posting_date={maintien_posting_date!r} not ISO format"
            )
    elif engagement.get("statutory_deadline"):
        statutory_deadline = engagement["statutory_deadline"]
        posting_date = (
            statutory_deadline
            if isinstance(statutory_deadline, date)
            else date.fromisoformat(str(statutory_deadline))
        )

    timing = validate_participation_timing(completion_date, posting_date)
    timing_passed = bool(timing.get("is_valid"))
    earliest = completion_date + timedelta(days=PARTICIPATION_LEAD_DAYS)
    timing_message = ""
    if not timing_passed:
        if posting_date is None:
            timing_message = (
                "Art. 76.2.1: maintien_posting_date is unknown. Either supply "
                "it as an argument or call record_posting_date first. Earliest "
                f"valid posting date is {earliest.isoformat()} (60 days after "
                "participation completion)."
            )
        else:
            timing_message = (
                f"Hard gate Art. 76.2.1: maintien_posting_date={posting_date.isoformat()} "
                f"is too soon. Must be >= {earliest.isoformat()} (60 days after "
                "participation completion)."
            )

    # R5 REG-H1: HARD GATE — refuse to return a session when timing fails, unless
    # the operator explicitly forces with a logged rationale. CNESST treats the
    # 60-day gate as a structural defect of the maintien exercise.
    if not timing_passed and not force_record_with_warning:
        raise ValidationError(
            "Art. 76.2.1 participation timing gate failed: " + timing_message
            + " To override (with audit trail), set force_record_with_warning=True"
            " and supply force_rationale.",
            data={
                "earliest_valid_posting_date": earliest.isoformat(),
                "supplied_posting_date": posting_date.isoformat() if posting_date else None,
            },
        )
    if not timing_passed and force_record_with_warning and not (force_rationale or "").strip():
        raise ValidationError(
            "force_record_with_warning=True requires a non-empty force_rationale "
            "(appended to the audit log for audit purposes)."
        )

    session = ParticipationSession(
        client_slug=client_slug,
        participants=participants,
        methodology=methodology,  # type: ignore[arg-type]
        methodology_notes=methodology_notes,
        information_transmission=information_transmission,
        consultations_held=consultations_held,
        questions_and_observations=questions_and_observations,
        participation_completion_date=completion_date,
        confidentiality_acknowledged=True,
        last_updated=date.today(),
    )

    force_override_used = (not timing_passed) and force_record_with_warning
    audit_entry: Optional[dict[str, Any]] = None
    if force_override_used:
        audit_entry = {
            "decision_type": "art_76_2_1_timing_gate_override",
            "decision_date": date.today().isoformat(),
            "client_slug": client_slug,
            "rationale": force_rationale,
            "timing_message": timing_message,
            "earliest_valid_posting_date": earliest.isoformat(),
            "supplied_posting_date": (
                posting_date.isoformat() if posting_date else None
            ),
        }

    result: dict[str, Any] = {
        "session": session.model_dump(mode="json"),
        "client_slug": client_slug,
        "participation_completion_date": completion_date.isoformat(),
        "participants_recorded": len(participants),
        "consultations_recorded": len(consultations_held),
        "questions_recorded": len(questions_and_observations),
        "timing_validation_passed": timing_passed,
        "timing_validation_message": timing_message,
        "earliest_maintien_posting_date": (
            posting_date.isoformat() if (timing_passed and posting_date) else earliest.isoformat()
        ),
        "force_override_used": force_override_used,
    }
    if audit_entry is not None:
        result["audit_entry"] = audit_entry
    return result


def has_participation_gate_satisfied(
    engagement: dict[str, Any],
    participation_session: Optional[dict[str, Any]],
    maintien_posting_date: Any,
) -> tuple[bool, str]:
    """Return (gate_satisfied, reason) for the Art. 76.2.1 participation gate.

    Used by render_document to refuse maintien deliverables when the gate has not
    been cleared. Recomputes the 60-day timing from passed-in data (no audit-log
    read — OR-7). Returns (True, "") when:
      - the engagement does not require participation, OR
      - a participation session exists AND completion + 60 days <= the maintien
        posting date.

    `participation_session` is the fetched session blob (or None). `maintien_posting_date`
    is the maintien posting date (date, ISO string, or None) — from posting metadata
    or the engagement's statutory_deadline.
    """
    from datetime import timedelta

    if not engagement.get("participation_required"):
        return True, ""

    if not participation_session:
        return False, (
            "Art. 76.2.1: participation session not recorded — call "
            "record_participation_session before rendering this document."
        )

    completion_raw = participation_session.get("participation_completion_date")
    if not completion_raw:
        return False, (
            "Art. 76.2.1: participation session has no completion date — cannot "
            "verify the 60-day timing gate."
        )
    completion_date = (
        completion_raw
        if isinstance(completion_raw, date)
        else date.fromisoformat(str(completion_raw))
    )

    posting_date: Optional[date] = None
    if maintien_posting_date:
        posting_date = (
            maintien_posting_date
            if isinstance(maintien_posting_date, date)
            else date.fromisoformat(str(maintien_posting_date))
        )
    if posting_date is None:
        return False, (
            "Art. 76.2.1: maintien posting date is unknown — cannot verify the "
            "60-day participation timing gate."
        )

    earliest = completion_date + timedelta(days=PARTICIPATION_LEAD_DAYS)
    if posting_date < earliest:
        return False, (
            f"Art. 76.2.1: maintien_posting_date={posting_date.isoformat()} is too "
            f"soon. Must be >= {earliest.isoformat()} (60 days after participation "
            "completion). Restore compliant timing or escalate."
        )
    return True, ""


__all__ = [
    "import_prior_exercise",
    "record_participation_session",
    "has_participation_gate_satisfied",
]
