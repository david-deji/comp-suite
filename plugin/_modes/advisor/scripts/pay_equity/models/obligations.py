"""Obligations matrix lookup — tier × exercise type → obligation flags.

Source: phase4 § 4.1.1 (size-tier auto) + R7 deadlines + interim posting requirement
note (phase4 Tool 4 — `interim_posting_required` true for 50-99 and 100+).
"""
from __future__ import annotations

from typing import Any

from scripts.pay_equity.models.engagement import ExerciseType, SizeTier


# Each cell describes obligations for one (tier, exercise_type) combination.
# Posting content + deliverables sourced from r3-r9-spec-corrections.md article map
# and r2-affichage-reconciliation.md (CNESST template requirements).
_INITIAL_POSTING_CONTENT = [
    "Liste complète des catégories d'emplois identifiées",
    "Détermination de la prédominance sexuelle (méthode appliquée)",
    "Description de la méthode et des outils d'évaluation utilisés",
    "Résultats de l'évaluation par catégorie",
    "Identification des écarts salariaux et catégories à ajustement",
    "Modalités de versement (forfaitaire ou étalement, max 4 ans — Art. 76.5.1)",
    "Date du premier ajustement",
    "Coordonnées pour soumettre des observations (60 jours)",
    "Mention du droit de plainte à la CNESST",
]

_MAINTENANCE_POSTING_CONTENT = [
    "Date de l'évaluation du maintien et période de référence",
    "Liste des événements ayant affecté l'équité depuis le dernier exercice",
    "Catégories réévaluées avec rationale",
    "Résultats de la nouvelle comparaison",
    "Ajustements rétroactifs (s'il y a lieu) — calculés période-par-période",
    "Modalités de versement",
    "Coordonnées pour observations (60 jours) + droit de plainte",
]

_INITIAL_DELIVERABLES_BASIC = [
    "Affichage initial",
    "Affichage final",
    "Tableau d'évaluation des catégories",
    "Tableau de comparaison des rémunérations",
    "Échéancier de versement des ajustements",
]

_INITIAL_DELIVERABLES_COMMITTEE = _INITIAL_DELIVERABLES_BASIC + [
    "Procès-verbaux du comité d'équité salariale",
    "Documentation de la composition du comité (Art. 21)",
]

_MAINTENANCE_DELIVERABLES_BASIC = [
    "Affichage du maintien",
    "Tableau de réévaluation",
    "Calcul des ajustements rétroactifs (avec ventilation des intérêts par période)",
    "Échéancier de versement",
]

_MAINTENANCE_DELIVERABLES_COMMITTEE = _MAINTENANCE_DELIVERABLES_BASIC + [
    "Procès-verbaux du comité de maintien (Bill 10, distinct du comité initial)",
]

_OBLIGATIONS: dict[tuple[SizeTier, ExerciseType], dict[str, Any]] = {
    (SizeTier.SMALL, ExerciseType.INITIAL): {
        "committee_required": False,
        "committee_composition": None,
        "maintenance_committee_required": False,
        "posting_required": True,
        "interim_posting_required": False,
        "consultation_period_days": 60,
        "posting_content_requirements": list(_INITIAL_POSTING_CONTENT),
        "deliverables_required": list(_INITIAL_DELIVERABLES_BASIC),
        "article_refs": ["Art. 31", "Art. 35", "Art. 99", "Art. 115"],
    },
    (SizeTier.SMALL, ExerciseType.MAINTENANCE): {
        "committee_required": False,
        "committee_composition": None,
        "maintenance_committee_required": False,
        "posting_required": True,
        "interim_posting_required": False,
        "consultation_period_days": 60,
        "posting_content_requirements": list(_MAINTENANCE_POSTING_CONTENT),
        "deliverables_required": list(_MAINTENANCE_DELIVERABLES_BASIC),
        "article_refs": ["Art. 76.1", "Art. 76.3", "Art. 100", "Art. 115"],
    },
    (SizeTier.MEDIUM, ExerciseType.INITIAL): {
        "committee_required": False,
        "committee_composition": None,
        "maintenance_committee_required": False,
        "posting_required": True,
        "interim_posting_required": True,
        "consultation_period_days": 60,
        "posting_content_requirements": list(_INITIAL_POSTING_CONTENT),
        "deliverables_required": list(_INITIAL_DELIVERABLES_BASIC) + [
            "Affichage intermédiaire (étape 2/4)",
        ],
        "article_refs": ["Art. 31", "Art. 75", "Art. 76", "Art. 97", "Art. 115"],
    },
    (SizeTier.MEDIUM, ExerciseType.MAINTENANCE): {
        "committee_required": False,
        "committee_composition": None,
        "maintenance_committee_required": False,
        "posting_required": True,
        "interim_posting_required": True,
        "consultation_period_days": 60,
        "posting_content_requirements": list(_MAINTENANCE_POSTING_CONTENT),
        "deliverables_required": list(_MAINTENANCE_DELIVERABLES_BASIC) + [
            "Affichage intermédiaire de maintien",
        ],
        "article_refs": ["Art. 76.1", "Art. 76.3", "Art. 76.4", "Art. 100", "Art. 115"],
    },
    (SizeTier.LARGE, ExerciseType.INITIAL): {
        "committee_required": True,
        "committee_composition": {
            "min_employee_reps": 2,
            "min_employer_reps": 1,
            "female_majority_employee_reps": True,
        },
        "maintenance_committee_required": True,
        "posting_required": True,
        "interim_posting_required": True,
        "consultation_period_days": 60,
        "posting_content_requirements": list(_INITIAL_POSTING_CONTENT) + [
            "Identité des membres du comité d'équité salariale",
        ],
        "deliverables_required": list(_INITIAL_DELIVERABLES_COMMITTEE),
        "article_refs": ["Art. 21", "Art. 31", "Art. 32", "Art. 75", "Art. 76", "Art. 96.1", "Art. 115"],
    },
    (SizeTier.LARGE, ExerciseType.MAINTENANCE): {
        "committee_required": False,
        "committee_composition": None,
        "maintenance_committee_required": True,
        "posting_required": True,
        "interim_posting_required": True,
        "consultation_period_days": 60,
        "posting_content_requirements": list(_MAINTENANCE_POSTING_CONTENT) + [
            "Composition du comité de maintien (Bill 10) — distinct du comité initial",
        ],
        "deliverables_required": list(_MAINTENANCE_DELIVERABLES_COMMITTEE),
        "article_refs": ["Art. 76.1", "Art. 76.3", "Art. 76.4", "Art. 100", "Art. 100.1", "Art. 115"],
    },
}


def get_obligations_matrix(tier: SizeTier, exercise: ExerciseType) -> dict[str, Any]:
    """Return the obligation dict for a given size tier × exercise type.

    Returned dict matches the `get_obligations` tool output schema (phase4 Tool 4).
    """
    return dict(_OBLIGATIONS[(tier, exercise)])


__all__ = ["get_obligations_matrix"]
