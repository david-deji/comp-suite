"""Nouvel affichage generators.

These produce template PDFs with placeholder sections (blank lines for
consultant to fill) and pre-filled legal/recourse sections.
"""

from datetime import date
from html import escape

from ._base import (
    build_html_document, employer_header, signature_block, disclaimer_block,
)
from ._legal_text import (
    recourse_art100,
    recourse_art101,
    formulaire_notice,
)


def _placeholder_section(label: str) -> str:
    """Generate a placeholder section with blank lines for consultant to fill."""
    return f"""
<div class="placeholder-section">
  <p><strong>{escape(label)}&nbsp;:</strong></p>
  <p class="placeholder-line">_______________________________________________</p>
  <p class="placeholder-line">_______________________________________________</p>
  <p class="placeholder-line">_______________________________________________</p>
</div>
"""


def generate_nouvel_initial(engagement: dict) -> str:
    """Nouvel affichage for 10-49 initial (art. 35)."""
    display_date = date.today().isoformat()

    parts = []

    parts.append(employer_header(
        engagement,
        "Nouvel affichage — Exercice d'équité salariale",
        "Loi sur l'équité salariale, RLRQ c E-12.001, art. 35",
        display_date,
    ))

    parts.append("""
<div class="explanation">
  Le présent nouvel affichage fait suite à l'affichage des résultats de l'exercice
  d'équité salariale et à la période de consultation de 60 jours.
</div>
""")

    parts.append("<h2>1. Modifications apportées</h2>")
    parts.append(_placeholder_section("Modifications apportées"))

    parts.append("<h2>2. Observations reçues</h2>")
    parts.append(_placeholder_section("Observations reçues"))

    parts.append("<h2>3. Renseignements sur les recours</h2>")
    parts.append(recourse_art101())
    parts.append(formulaire_notice())

    parts.append(signature_block())
    parts.append(disclaimer_block())

    return build_html_document(parts)


def generate_nouvel_1er(engagement: dict) -> str:
    """Nouvel affichage for 50+ initial, 1er affichage (art. 75)."""
    display_date = date.today().isoformat()

    parts = []

    parts.append(employer_header(
        engagement,
        "Nouvel affichage — Premier affichage (équité salariale)",
        "Loi sur l'équité salariale, RLRQ c E-12.001, art. 75",
        display_date,
    ))

    parts.append("""
<div class="explanation">
  Le présent nouvel affichage fait suite au premier affichage de l'exercice
  d'équité salariale et à la période de consultation de 60 jours.
</div>
""")

    parts.append("<h2>1. Modifications apportées</h2>")
    parts.append(_placeholder_section("Modifications apportées"))

    parts.append("<h2>2. Observations reçues</h2>")
    parts.append(_placeholder_section("Observations reçues"))

    parts.append("<h2>3. Renseignements sur les recours</h2>")
    parts.append(recourse_art101())
    parts.append(formulaire_notice())

    parts.append(signature_block())
    parts.append(disclaimer_block())

    return build_html_document(parts)


def generate_nouvel_2e(engagement: dict) -> str:
    """Nouvel affichage for 50+ initial, 2e affichage (art. 75)."""
    display_date = date.today().isoformat()

    parts = []

    parts.append(employer_header(
        engagement,
        "Nouvel affichage — Deuxième affichage (équité salariale)",
        "Loi sur l'équité salariale, RLRQ c E-12.001, art. 75",
        display_date,
    ))

    parts.append("""
<div class="explanation">
  Le présent nouvel affichage fait suite au deuxième affichage de l'exercice
  d'équité salariale et à la période de consultation de 60 jours.
</div>
""")

    parts.append("<h2>1. Modifications apportées</h2>")
    parts.append(_placeholder_section("Modifications apportées"))

    parts.append("<h2>2. Observations reçues</h2>")
    parts.append(_placeholder_section("Observations reçues"))

    parts.append("<h2>3. Renseignements sur les recours</h2>")
    parts.append(recourse_art101())
    parts.append(formulaire_notice())

    parts.append(signature_block())
    parts.append(disclaimer_block())

    return build_html_document(parts)


def generate_nouvel_maintenance(engagement: dict) -> str:
    """Nouvel affichage for maintenance (art. 76.4).

    Conditional recourse sections based on maintenance_evaluation_method.
    """
    display_date = date.today().isoformat()
    eval_method = engagement.get("maintenance_evaluation_method") or "employer_alone"

    parts = []

    parts.append(employer_header(
        engagement,
        "Nouvel affichage — Évaluation du maintien de l'équité salariale",
        "Loi sur l'équité salariale, RLRQ c E-12.001, art. 76.4",
        display_date,
    ))

    parts.append("""
<div class="explanation">
  Le présent nouvel affichage fait suite à l'affichage des résultats de l'évaluation
  du maintien de l'équité salariale et à la période de consultation de 60 jours.
</div>
""")

    parts.append("<h2>1. Modifications apportées</h2>")
    parts.append(_placeholder_section("Modifications apportées"))

    parts.append("<h2>2. Observations reçues</h2>")
    parts.append(_placeholder_section("Observations reçues"))

    parts.append("<h2>3. Renseignements sur les recours</h2>")
    if eval_method == "employer_alone":
        parts.append(recourse_art100())
    parts.append(recourse_art101())
    parts.append(formulaire_notice())

    parts.append(signature_block())
    parts.append(disclaimer_block())

    return build_html_document(parts)
