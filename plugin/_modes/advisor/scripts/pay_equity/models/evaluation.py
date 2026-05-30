"""evaluation-grid.json — point-factor grid + per-class scores.

Source: phase4 § 4.1.3.
"""
from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


GridDimension = Literal["qualifications", "responsibilities", "effort", "conditions"]


class SubFactor(BaseModel):
    id: str  # e.g., "Q1"
    name: str
    dimension: GridDimension
    description: str
    levels: list[str]
    points_per_level: list[int]
    max_points: int


class EvaluationGrid(BaseModel):
    client_slug: str
    template_id: Optional[str] = None
    template_name: Optional[str] = None
    is_custom: bool = False
    sub_factors: list[SubFactor] = Field(default_factory=list)
    total_max_points: int = 0
    dimension_weights: dict[str, float] = Field(default_factory=dict)
    last_updated: Optional[date] = None
    stale: bool = False
    stale_reason: Optional[str] = None


class ClassScore(BaseModel):
    class_id: str
    scores: dict[str, int] = Field(default_factory=dict)  # sub_factor_id → awarded points
    total_score: float = 0.0
    scored_by: Optional[str] = None
    scored_date: Optional[date] = None


class EvaluationFile(BaseModel):
    grid: EvaluationGrid
    class_scores: list[ClassScore] = Field(default_factory=list)
    all_classes_scored: bool = False
    last_updated: Optional[date] = None


__all__ = [
    "ClassScore",
    "EvaluationFile",
    "EvaluationGrid",
    "GridDimension",
    "SubFactor",
]
