"""participation-session.json + retention-policy.json + maintenance-committee.json.

Sources:
- R5 — committee structure expansion + maintenance committee as separate object
- R7 — participation process (Art. 76.2.1)
- R9 — Loi 25 retention policy (6-year floor)
"""
from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Participant(BaseModel):
    """A participant in the participation process — accredited association rep,
    designated non-union employee rep, etc. PII minimized per Loi 25.
    """

    role: Literal[
        "accredited_association_rep",
        "non_union_employee_rep",
        "employer_rep",
        "observer",
    ]
    name: str
    affiliation: Optional[str] = None  # union local, department
    designated_date: Optional[date] = None


class InformationTransmission(BaseModel):
    transmission_date: date
    recipients_summary: str  # e.g., "All accredited associations + 4 non-union reps"
    documents: list[str] = Field(default_factory=list)
    delivery_method: Literal["in_person", "email", "internal_portal", "registered_mail", "other"]


class Consultation(BaseModel):
    consultation_date: date
    format: Literal["meeting", "survey", "portal", "focus_group", "combined", "other"]
    attendee_count: int = Field(ge=0)
    summary: str  # narrative summary of dialogue


class QuestionObservation(BaseModel):
    """Question or observation raised during consultation + how the audit considered it."""

    raised_date: date
    raised_by: str
    question_or_observation: str
    consideration_notes: str  # how it was considered in the audit
    affected_classes: list[str] = Field(default_factory=list)


class ParticipationSession(BaseModel):
    """participation-session.json — Phase M1.5.

    Created when `engagement.participation_required = True`. Records participant
    inventory, methodology, transmissions, consultations, Q&A. Hard timing gate:
    `participation_completion_date + 60 days <= maintien_posting_date`.
    """

    client_slug: str
    participants: list[Participant] = Field(default_factory=list)
    methodology: Literal[
        "meetings",
        "survey",
        "portal",
        "focus_groups",
        "combined",
        "other",
    ]
    methodology_notes: Optional[str] = None
    information_transmission: list[InformationTransmission] = Field(default_factory=list)
    consultations_held: list[Consultation] = Field(default_factory=list)
    questions_and_observations: list[QuestionObservation] = Field(default_factory=list)
    participation_completion_date: Optional[date] = None
    confidentiality_acknowledged: bool = False
    last_updated: Optional[date] = None


class RetentionPolicy(BaseModel):
    """retention-policy.json — Loi 25 + Art. 14 (6-year minimum)."""

    client_slug: str
    retention_until: date  # posting_date + 6 years
    purge_action: Literal[
        "archive_encrypted",
        "delete",
        "preserve_indefinitely",
    ] = "archive_encrypted"
    purge_reason: Optional[str] = None
    last_updated: Optional[date] = None


class CommitteeMember(BaseModel):
    """Committee composition entry — PII minimized."""

    name: str
    role: Literal["employer_rep", "employee_rep", "union_rep", "observer"]
    gender: Literal["female", "male", "non_binary", "prefer_not_to_say"]
    affiliation: Optional[str] = None
    designated_date: Optional[date] = None


class MaintenanceCommittee(BaseModel):
    """Bill 10 (2019) — distinct committee for maintien at 100+. R5 expansion."""

    client_slug: str
    established_date: date
    members: list[CommitteeMember] = Field(default_factory=list)
    quorum_rule: str  # Art. 28 operating rule
    decision_method: Literal["consensus", "majority", "weighted_vote"]
    meeting_frequency: str  # "monthly", "quarterly", "ad hoc"
    union_representation_per_unit: list[dict] = Field(default_factory=list)
    is_continuation_of_initial: bool = False


__all__ = [
    "CommitteeMember",
    "Consultation",
    "InformationTransmission",
    "MaintenanceCommittee",
    "Participant",
    "ParticipationSession",
    "QuestionObservation",
    "RetentionPolicy",
]
