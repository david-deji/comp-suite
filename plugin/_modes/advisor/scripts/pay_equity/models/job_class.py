"""job-classes.json — job classes + predominance.

Sources: phase4 § 4.1.2 + R4 (4-criteria predominance with disproportion test).
"""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Predominance(str, Enum):
    FEMALE = "female"
    MALE = "male"
    NEUTRAL = "neutral"


class PredominanceMethod(str, Enum):
    """Four CNESST criteria — R4 added `disproportion`."""

    QUANTITATIVE = "quantitative"  # ≥60% one gender
    DISPROPORTION = "disproportion"  # |class_pct - enterprise_pct| ≥ 20pp default
    STEREOTYPE = "stereotype"  # societal association
    HISTORICAL = "historical"  # ≥10y history


class PredominanceOverrideEvidence(BaseModel):
    """Structured evidence for stereotype/historical overrides.

    Replaces the bare-string `rationale` from earlier drafts. `committee_decision`
    documents whether a committee voted; `cnesst_reference` cites a CNESST guide
    or jurisprudence excerpt.
    """

    evidence_type: Literal["stereotype", "historical"]
    description: str = Field(min_length=10)
    historical_period_years: Optional[int] = None
    historical_period_start: Optional[date] = None
    committee_decision: bool = False
    cnesst_reference: Optional[str] = None
    decided_by: Optional[str] = None  # operator name or "committee"
    decided_date: Optional[date] = None


class JobClass(BaseModel):
    id: str  # e.g., "JC-001"
    title: str
    description: Optional[str] = None
    total_incumbents: int = Field(ge=1)
    female_incumbents: int = Field(ge=0)
    male_incumbents: int = Field(ge=0)
    female_percentage: float  # computed: female / total × 100

    # --- Predominance ------------------------------------------------------
    predominance: Optional[Predominance] = None
    predominance_method: Optional[PredominanceMethod] = None
    predominance_override_evidence: Optional[PredominanceOverrideEvidence] = None
    is_override: bool = False

    # --- Evaluation linkage (filled by score_job_classes) ------------------
    evaluation_score: Optional[float] = None  # float per phase4 standardization
    grade: Optional[int] = None

    # --- Pay range (three-criteria validation) -----------------------------
    pay_range_min: Optional[float] = None
    pay_range_max: Optional[float] = None


class JobClassesFile(BaseModel):
    """job-classes.json contents."""

    client_slug: str
    classes: list[JobClass] = Field(default_factory=list)
    all_predominance_determined: bool = False
    enterprise_female_percentage: Optional[float] = None  # R4 — denominator for disproportion test
    last_updated: Optional[date] = None
    stale: bool = False
    stale_reason: Optional[str] = None


__all__ = [
    "JobClass",
    "JobClassesFile",
    "Predominance",
    "PredominanceMethod",
    "PredominanceOverrideEvidence",
]
