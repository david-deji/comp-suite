"""Maintenance posting (art. 76.3).

Content varies based on has_participation_process and maintenance_evaluation_method.
"""

from datetime import date
from html import escape

from ._base import (
    _fmt, _pct, _predominance_fr,
    build_html_document, employer_header, signature_block, disclaimer_block,
)
from ._legal_text import (
    rights_notice_maintenance,
    recourse_art100,
    recourse_art101,
    formulaire_notice,
    nouvel_affichage_notice,
)


def generate_maintenance_html(
    engagement: dict,
    job_classes: dict,
    adjustments: dict,
) -> str:
    """Build the maintenance posting HTML (art. 76.3)."""
    display_date = date.today().isoformat()
    classes = job_classes.get("classes", [])
    class_adjustments = adjustments.get("class_adjustments", [])
    schedule = adjustments.get("payment_schedule", [])

    # Get maintenance-specific fields with defaults
    maintenance_events = engagement.get("maintenance_events", [])
    has_participation = engagement.get("has_participation_process", False)
    eval_method = engagement.get("maintenance_evaluation_method") or "employer_alone"

    female_classes = [c for c in classes if c.get("predominance") == "female"]

    parts = []

    # Header
    parts.append(employer_header(
        engagement,
        "Affichage des résultats de l'évaluation du maintien de l'équité salariale",
        "Loi sur l'équité salariale, RLRQ c E-12.001, art. 76.3",
        display_date,
    ))

    # Section 1: Summary of approach
    method_labels = {
        "employer_alone": "seul",
        "committee": "avec un comité de maintien",
        "joint_with_association": "conjointement avec l'association accréditée",
    }
    method_label = method_labels.get(eval_method, eval_method)

    parts.append(f"""
<h2>1. Sommaire de la démarche retenue</h2>
<div class="explanation">
  L'employeur a procédé à l'évaluation du maintien de l'équité salariale {method_label},
  conformément à la Loi sur l'équité salariale. Cette évaluation vise à vérifier
  que l'équité salariale est maintenue dans l'entreprise.
</div>
""")

    # Section 2 (conditional): Participation process
    if has_participation:
        parts.append("""
<h2>2. Sommaire des questions et observations</h2>
<div class="explanation">
  Dans le cadre du processus de participation, les personnes salariées ont eu
  l'occasion de formuler des questions et des observations concernant l'évaluation
  du maintien de l'équité salariale.
</div>
<p><em>Les questions et observations reçues sont résumées ci-dessous.</em></p>

<h2>3. Traitement des questions et observations</h2>
<div class="explanation">
  Les questions et observations formulées ont été considérées dans le cadre
  de l'évaluation du maintien. Le tableau ci-dessous indique comment elles
  ont été prises en compte.
</div>
""")
        next_section = 4
    else:
        next_section = 2

    # Events section
    parts.append(f"""
<h2>{next_section}. Liste des événements survenus</h2>
""")
    if maintenance_events:
        parts.append("""<table>
<tr><th>Type</th><th>Description</th><th>Date de début</th><th>Date de fin</th><th>Classes touchées</th><th>Génère ajustement</th></tr>
""")
        for ev in maintenance_events:
            affected = ", ".join(ev.get("affected_class_ids", []))
            end_date = ev.get("end_date") or "—"
            generates = "Oui" if ev.get("generates_adjustment", False) else "Non"
            parts.append(f"""<tr>
  <td>{escape(str(ev.get('event_type', '')))}</td>
  <td>{escape(ev.get('description', ''))}</td>
  <td>{ev.get('start_date', '')}</td>
  <td>{end_date}</td>
  <td>{escape(affected)}</td>
  <td>{generates}</td>
</tr>""")
        parts.append("</table>")
    else:
        parts.append("<p><strong>Aucun événement ayant généré un ajustement.</strong></p>")

    # Female classes with adjustments
    next_section += 1
    parts.append(f"""
<h2>{next_section}. Catégories d'emplois féminines avec droit aux ajustements</h2>
""")
    if class_adjustments:
        adjusted_ids = {adj.get("class_id") for adj in class_adjustments}
        adjusted_female = [c for c in female_classes if c["id"] in adjusted_ids]
        parts.append("""<table>
<tr><th>Classe</th><th>Titre</th><th class="right">Effectif</th></tr>
""")
        for c in adjusted_female:
            parts.append(f"""<tr>
  <td>{escape(c.get('id', ''))}</td>
  <td>{escape(c.get('title', ''))}</td>
  <td class="right">{c.get('total_incumbents', '')}</td>
</tr>""")
        parts.append("</table>")
    else:
        parts.append("<p><strong>Aucun ajustement requis.</strong></p>")

    # Adjustments and payment
    next_section += 1
    parts.append(f"""
<h2>{next_section}. Pourcentage ou montant des ajustements et modalités de versement</h2>
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

        if schedule:
            parts.append("<h3>Modalités de versement</h3>")
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
        parts.append("<p><strong>Aucun ajustement requis.</strong></p>")

    # Rights notice
    next_section += 1
    parts.append(f"<h2>{next_section}. Renseignements sur les droits</h2>")
    parts.append(rights_notice_maintenance())

    # Recourse based on method
    if eval_method == "employer_alone":
        parts.append(recourse_art100())
    parts.append(recourse_art101())
    parts.append(formulaire_notice())
    parts.append(nouvel_affichage_notice())

    parts.append(signature_block())
    parts.append(disclaimer_block())

    return build_html_document(parts)
