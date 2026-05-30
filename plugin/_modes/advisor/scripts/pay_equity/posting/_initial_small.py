"""Initial posting for 10-49 employees (art. 35).

Generates a single HTML document with 9 sections. Does NOT include
evaluation grid details or sub-factor tables (those are 50+ only).
"""

from datetime import date
from html import escape
from pathlib import Path

from ._base import (
    _read, _fmt, _pct, _predominance_fr, _method_fr,
    build_html_document, employer_header, signature_block, disclaimer_block,
)
from ._legal_text import (
    rights_notice_initial,
    recourse_art101,
    formulaire_notice,
    nouvel_affichage_notice,
)


def generate_initial_small_html(eng_dir: Path) -> str:
    """Build the art. 35 posting HTML for enterprises with 10-49 employees."""
    engagement = _read(eng_dir, "engagement.json")
    job_classes = _read(eng_dir, "job-classes.json")
    compensation = _read(eng_dir, "compensation.json")
    adjustments = _read(eng_dir, "adjustments.json")

    display_date = date.today().isoformat()
    classes = job_classes.get("classes", [])
    comparisons = compensation.get("comparison_results", [])
    class_adjustments = adjustments.get("class_adjustments", [])
    schedule = adjustments.get("payment_schedule", [])

    title_map = {c["id"]: c.get("title", "") for c in classes}

    parts = []

    # Header
    parts.append(employer_header(
        engagement,
        "Affichage des résultats de l'exercice d'équité salariale",
        "Loi sur l'équité salariale, RLRQ c E-12.001, art. 35",
        display_date,
    ))

    # Section 1: Sommaire de la démarche
    parts.append("""
<h2>1. Sommaire de la démarche suivie</h2>
<div class="explanation">
  L'employeur a réalisé un exercice d'équité salariale conformément à la section III
  de la Loi sur l'équité salariale applicable aux entreprises de 10 à 49 personnes
  salariées. Cet exercice vise à identifier et corriger les écarts salariaux entre
  les catégories d'emplois à prédominance féminine et masculine.
</div>
""")

    # Section 2: Female job classes
    female_classes = [c for c in classes if c.get("predominance") == "female"]
    parts.append("""
<h2>2. Liste des catégories d'emplois à prédominance féminine</h2>
""")
    parts.append("""<table>
<tr><th>Classe</th><th>Titre</th><th class="right">Effectif</th><th class="right">% Féminin</th><th>Méthode</th></tr>
""")
    for c in female_classes:
        parts.append(f"""<tr>
  <td>{escape(c.get('id', ''))}</td>
  <td>{escape(c.get('title', ''))}</td>
  <td class="right">{c.get('total_incumbents', '')}</td>
  <td class="right">{_pct(c.get('female_percentage', 0))}</td>
  <td>{_method_fr(c.get('predominance_method', ''))}</td>
</tr>""")
    parts.append("</table>")

    # Section 3: Male comparator classes
    male_classes = [c for c in classes if c.get("predominance") == "male"]
    parts.append("""
<h2>3. Liste des catégories d'emplois à prédominance masculine ayant servi de comparateurs</h2>
""")
    parts.append("""<table>
<tr><th>Classe</th><th>Titre</th><th class="right">Effectif</th><th class="right">% Féminin</th><th>Méthode</th></tr>
""")
    for c in male_classes:
        parts.append(f"""<tr>
  <td>{escape(c.get('id', ''))}</td>
  <td>{escape(c.get('title', ''))}</td>
  <td class="right">{c.get('total_incumbents', '')}</td>
  <td class="right">{_pct(c.get('female_percentage', 0))}</td>
  <td>{_method_fr(c.get('predominance_method', ''))}</td>
</tr>""")
    parts.append("</table>")

    # Section 4: Adjustments
    parts.append("""
<h2>4. Pourcentage ou montant des ajustements</h2>
""")
    if class_adjustments:
        parts.append("""<table>
<tr>
  <th>Classe</th><th>Titre</th><th class="right">Écart ($/h)</th>
  <th class="right">Ajustement annuel ($)</th>
</tr>
""")
        for adj in class_adjustments:
            parts.append(f"""<tr>
  <td>{escape(adj.get('class_id', ''))}</td>
  <td>{escape(adj.get('title', ''))}</td>
  <td class="right">{_fmt(adj.get('gap_hourly', 0))}</td>
  <td class="right">{_fmt(adj.get('annual_adjustment', 0))}</td>
</tr>""")
        parts.append("</table>")
    else:
        parts.append("<p><strong>Aucun ajustement requis.</strong></p>")

    # Section 5: Payment schedule
    parts.append("""
<h2>5. Modalités de versement</h2>
""")
    if schedule:
        parts.append("""<table>
<tr>
  <th class="right">Versement</th><th>Date</th><th class="right">%</th>
  <th class="right">Montant ($)</th><th class="right">Cumul %</th>
</tr>
""")
        for inst in schedule:
            parts.append(f"""<tr>
  <td class="right">{inst.get('installment', '')}</td>
  <td>{inst.get('date', '')}</td>
  <td class="right">{_pct(inst.get('percentage', 0))}</td>
  <td class="right">{_fmt(inst.get('amount_per_installment', inst.get('amount_per_employee', 0)))}</td>
  <td class="right">{_pct(inst.get('cumulative_percentage', 0))}</td>
</tr>""")
        parts.append("</table>")
    else:
        parts.append("<p>Sans objet (aucun ajustement requis).</p>")

    # Section 6: Rights notice
    parts.append("<h2>6. Renseignements sur les droits</h2>")
    parts.append(rights_notice_initial())

    # Section 7: Recourse
    parts.append("<h2>7. Renseignements sur les recours et délais</h2>")
    parts.append(recourse_art101())

    # Section 8: CNESST form
    parts.append("<h2>8. Formulaire prescrit</h2>")
    parts.append(formulaire_notice())

    # Section 9: Nouvel affichage mention
    parts.append("<h2>9. Nouvel affichage</h2>")
    parts.append(nouvel_affichage_notice())

    parts.append(signature_block())
    parts.append(disclaimer_block())

    return build_html_document(parts)
