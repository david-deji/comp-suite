"""Observations recorded during the 60-day consultation period after a posting.

Per Loi sur l'équité salariale art. 75 / 76 / 76.4 — employees may submit
observations during the consultation window; employer must record + respond.

Ported from the standalone repo's earlier implementation; adapted to v1.0
persistence pattern (Pydantic-model serialization via persistence.{read,write}_json).
"""
from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


ObservationCategory = Literal["question", "comment", "objection", "correction_request"]


class Observation(BaseModel):
    id: str  # OBS-NNN
    posting_type: str  # interim, final, maintien, nouvel_affichage_initial, nouvel_affichage_maintien
    observer_description: str
    observation_text: str
    received_date: date
    category: Optional[ObservationCategory] = None
    response: Optional[str] = None
    response_date: Optional[date] = None


class ObservationsFile(BaseModel):
    client_slug: str
    observations: list[Observation] = Field(default_factory=list)
    last_updated: Optional[date] = None


__all__ = [
    "Observation",
    "ObservationCategory",
    "ObservationsFile",
]
