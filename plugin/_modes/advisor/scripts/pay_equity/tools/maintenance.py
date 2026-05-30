"""Maintenance + participation tools: import_prior_exercise, record_participation_session.

2 of the 19 registered MCP tools.

Spec anchors:
- phase4-final-mcp-architecture.md § 5 Tool 15 (import_prior_exercise)
- r3-r9-spec-corrections.md § R7 Process de participation (Art. 76.2.1)
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import date
from typing import Any, Optional

from scripts.pay_equity import persistence_gdrive as persistence
from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.errors import MissingDataError, ValidationError
from scripts.pay_equity.models import (
    Engagement,
    JobClassesFile,
    ParticipationSession,
)
from scripts.pay_equity.validation import (
    PARTICIPATION_LEAD_DAYS,
    validate_participation_timing,
)


def _atomic_write_json(path, payload) -> None:
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


@mcp_tool
def import_prior_exercise(
    client_slug: str,
    prior_data: dict[str, Any],
) -> dict[str, Any]:
    """Import results from a prior pay equity exercise for maintenance audit comparison.

    `prior_data` carries `exercise_date`, `job_classes`, `comparison_method`, and
    `adjustments_applied`. Persisted to prior-exercise.json. Returns import
    summary and a diff against current job_classes.json (when present).
    """
    if not persistence.engagement_exists(client_slug):
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r}."
        )

    eng_dir = persistence.get_engagement_dir(client_slug)

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

    persisted_payload = {
        "client_slug": client_slug,
        "exercise_date": exercise_date.isoformat(),
        "comparison_method": prior_method,
        "adjustments_applied": prior_adjustments,
        "job_classes": prior_classes,
        "imported_at": date.today().isoformat(),
    }
    _atomic_write_json(eng_dir / "prior-exercise.json", persisted_payload)

    # Build diff vs current job_classes.json (F053 — compare_to_prior).
    diff = _diff_classes(eng_dir, prior_classes)

    return {
        "imported_classes": len(prior_classes),
        "prior_exercise_date": exercise_date.isoformat(),
        "prior_method": prior_method,
        "prior_adjustments": prior_adjustments,
        "diff": diff,
    }


def _diff_classes(eng_dir, prior_classes: list[dict[str, Any]]) -> dict[str, Any]:
    jc_path = eng_dir / "job-classes.json"
    if not jc_path.exists():
        return {"available": False, "reason": "current job-classes.json not yet created"}

    file = persistence.read_json(jc_path, JobClassesFile)
    current_ids = {c.id: c for c in file.classes}
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
        cur_score = cur.evaluation_score
        pri_score = pri.get("evaluation_score")
        if cur_score is not None and pri_score is not None and cur_score != pri_score:
            score_changes.append(
                {"class_id": cid, "prior_score": pri_score, "current_score": cur_score}
            )
        cur_pred = cur.predominance.value if cur.predominance else None
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
    client_slug: str,
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

    Per R5 REG-H1, this is a HARD GATE — the session refuses to persist if
    timing fails, unless the operator explicitly sets force_record_with_warning=True
    AND supplies force_rationale (logged to operator-decisions.json).
    """
    from datetime import timedelta

    if not persistence.engagement_exists(client_slug):
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r}."
        )
    eng_dir = persistence.get_engagement_dir(client_slug)
    engagement = persistence.read_json(eng_dir / "engagement.json", Engagement)

    if not engagement.participation_required:
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
    elif engagement.statutory_deadline:
        posting_date = engagement.statutory_deadline

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

    # R5 REG-H1: HARD GATE — refuse to persist when timing fails, unless the
    # operator explicitly forces with a logged rationale. CNESST treats the
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
            "(logged to operator-decisions.json for audit purposes)."
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
    persistence.write_json(eng_dir / "participation-session.json", session)

    if not timing_passed and force_record_with_warning:
        # Append decision to operator-decisions.json audit log.
        decisions_path = eng_dir / "operator-decisions.json"
        existing: list[dict[str, Any]] = []
        if decisions_path.exists():
            try:
                existing = json.loads(decisions_path.read_text(encoding="utf-8"))
            except Exception:
                existing = []
        existing.append(
            {
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
        )
        _atomic_write_json(decisions_path, existing)

    return {
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
        "saved": True,
        "force_override_used": (not timing_passed) and force_record_with_warning,
    }


def has_participation_gate_satisfied(eng_dir) -> tuple[bool, str]:
    """Return (gate_satisfied, reason) for the Art. 76.2.1 participation gate.

    Used by render_document to refuse maintien deliverables when the gate
    has not been cleared. Returns (True, "") when:
      - the engagement does not require participation, OR
      - participation-session.json exists AND its last record passed timing.
    """
    engagement = persistence.read_json(eng_dir / "engagement.json", Engagement)
    if not engagement.participation_required:
        return True, ""
    session_path = eng_dir / "participation-session.json"
    if not session_path.exists():
        return False, (
            "Art. 76.2.1: participation session not recorded — call "
            "record_participation_session before rendering this document."
        )
    # If the session was force-saved with override, gate is NOT satisfied.
    decisions_path = eng_dir / "operator-decisions.json"
    if decisions_path.exists():
        try:
            decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
            if any(
                d.get("decision_type") == "art_76_2_1_timing_gate_override"
                for d in decisions
            ):
                return False, (
                    "Art. 76.2.1: participation timing gate previously overridden "
                    "with operator force flag. Restore compliant timing or escalate."
                )
        except Exception:
            pass
    return True, ""


__all__ = [
    "import_prior_exercise",
    "record_participation_session",
    "has_participation_gate_satisfied",
]
