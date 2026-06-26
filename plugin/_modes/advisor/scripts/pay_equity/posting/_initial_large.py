"""Initial posting for 50+ employees (art. 75).

Generates 2 HTML documents:
- 1er affichage: Steps 1-2 (class identification + evaluation method/grid)
- 2e affichage: Steps 3-4 (compensation comparison + adjustments + payment schedule)
"""

from datetime import date
from html import escape

from ._base import (
    _fmt, _pct, _dimension_fr, _predominance_fr, _method_fr,
    build_html_document, employer_header, signature_block, disclaimer_block,
)
from ._legal_text import (
    rights_notice_initial,
    recourse_art101,
    formulaire_notice,
    nouvel_affichage_notice,
)


def generate_1er_affichage(
    engagement: dict,
    job_classes: dict,
    evaluation: dict,
) -> str:
    """Build the 1er affichage HTML (steps 1-2) for 50+ employees."""
    display_date = date.today().isoformat()
    classes = job_classes.get("classes", [])
    grid = evaluation.get("grid", {})
    class_scores = evaluation.get("class_scores", [])
    dim_weights = grid.get("dimension_weights", {})
    sub_factors = grid.get("sub_factors", [])

    # Sort scores descending
    class_scores_sorted = sorted(
        class_scores, key=lambda x: float(x.get("total_score", 0)), reverse=True
    )

    # Compute grade map
    _grade_map: dict[str, int] = {}
    if class_scores_sorted:
        _scores = [float(cs.get("total_score", 0)) for cs in class_scores_sorted]
        _min_score = min(_scores)
        _band_width = 75.0
        for cs in class_scores_sorted:
            _score = float(cs.get("total_score", 0))
            _grade_map[cs.get("class_id", "")] = int((_score - _min_score) / _band_width) + 1

    title_map = {c["id"]: c.get("title", "") for c in classes}
    pred_map = {c["id"]: c.get("predominance", "") for c in classes}

    parts = []

    # Header
    parts.append(employer_header(
        engagement,
        "Premier affichage — Exercice d'équité salariale",
        "Loi sur l'équité salariale, RLRQ c E-12.001, art. 75",
        display_date,
    ))

    # Step 1: Job classes
    parts.append("""
<h2>1. Identification des catégories d'emplois à prédominance féminine et masculine</h2>

<div class="explanation">
  La Loi sur l'équité salariale exige que l'employeur identifie les catégories d'emplois
  au sein de l'entreprise et détermine leur prédominance sexuelle. Une catégorie d'emplois
  est à prédominance féminine ou masculine lorsqu'elle est couramment associée aux femmes
  ou aux hommes en raison de stéréotypes occupationnels, ou lorsqu'au moins 60&nbsp;% des
  personnes salariées qui occupent les emplois de cette catégorie sont du même sexe.
</div>
""")
    parts.append("""<table>
<tr>
  <th>Classe</th><th>Titre</th><th class="right">Effectif</th>
  <th class="right">% Féminin</th><th>Prédominance</th><th>Méthode</th>
</tr>
""")
    for c in classes:
        parts.append(f"""<tr>
  <td>{escape(c.get('id', ''))}</td>
  <td>{escape(c.get('title', ''))}</td>
  <td class="right">{c.get('total_incumbents', '')}</td>
  <td class="right">{_pct(c.get('female_percentage', 0))}</td>
  <td>{_predominance_fr(c.get('predominance', ''))}</td>
  <td>{_method_fr(c.get('predominance_method', ''))}</td>
</tr>""")
    parts.append("</table>")

    # Step 2: Evaluation grid
    parts.append("""
<h2>2. Méthode d'évaluation des catégories d'emplois</h2>

<div class="explanation">
  L'évaluation des catégories d'emplois a été effectuée à l'aide d'une méthode par
  points et facteurs, conformément à l'article 57 de la Loi. Cette méthode évalue
  chaque catégorie d'emplois selon les quatre grandes dimensions prescrites.
</div>
""")

    parts.append("<h3>Dimensions et pondération</h3>")
    parts.append("""<table>
<tr><th>Dimension</th><th class="right">Poids</th></tr>
""")
    for dim, w in sorted(dim_weights.items()):
        parts.append(f"<tr><td>{_dimension_fr(dim)}</td><td class='right'>{_pct(float(w) * 100)}</td></tr>")
    parts.append("</table>")

    parts.append("<h3>Sous-facteurs d'évaluation</h3>")
    parts.append("""<table>
<tr><th>Sous-facteur</th><th>Dimension</th><th class="right">Points max</th><th class="right">Niveaux</th></tr>
""")
    for sf in sub_factors:
        parts.append(f"""<tr>
  <td>{escape(sf.get('name', sf.get('id', '')))}</td>
  <td>{_dimension_fr(sf.get('dimension', ''))}</td>
  <td class="right">{sf.get('max_points', '')}</td>
  <td class="right">{len(sf.get('levels', []))}</td>
</tr>""")
    parts.append("</table>")

    # Scores table
    parts.append("""
<h3>Résultats de l'évaluation</h3>
""")
    parts.append("""<table>
<tr><th>Classe</th><th>Titre</th><th>Prédominance</th><th class="right">Score total</th><th class="right">Grade</th></tr>
""")
    for cs in class_scores_sorted:
        cid = cs.get("class_id", "")
        parts.append(f"""<tr>
  <td>{escape(cid)}</td>
  <td>{escape(title_map.get(cid, ''))}</td>
  <td>{_predominance_fr(pred_map.get(cid, ''))}</td>
  <td class="right">{float(cs.get('total_score', 0)):.0f}</td>
  <td class="right">{_grade_map.get(cid, '')}</td>
</tr>""")
    parts.append("</table>")

    # Rights and recourse
    parts.append(rights_notice_initial())
    parts.append(nouvel_affichage_notice())

    parts.append(signature_block())
    parts.append(disclaimer_block())

    return build_html_document(parts)


def generate_2e_affichage(
    engagement: dict,
    job_classes: dict,
    compensation: dict,
    adjustments: dict,
) -> str:
    """Build the 2e affichage HTML (steps 3-4) for 50+ employees."""
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
        "Deuxième affichage — Exercice d'équité salariale",
        "Loi sur l'équité salariale, RLRQ c E-12.001, art. 75",
        display_date,
    ))

    parts.append("""
<div class="explanation">
  Le présent affichage fait suite au premier affichage qui présentait l'identification
  des catégories d'emplois et la méthode d'évaluation. Il présente les résultats de la
  comparaison de la rémunération et les ajustements salariaux requis.
</div>
""")

    # Step 3: Compensation comparison
    parts.append("""
<h2>3. Résultats de la comparaison de la rémunération</h2>

<div class="explanation">
  La rémunération de chaque catégorie d'emplois à prédominance féminine a été comparée
  à celle d'une catégorie d'emplois à prédominance masculine de même valeur ou de valeur
  comparable au sein de l'entreprise.
</div>
""")
    parts.append("""<table>
<tr>
  <th>Catégorie féminine</th><th>Titre</th><th>Comparateur masculin</th>
  <th>Méthode</th><th class="right">Rém. féminine ($/h)</th>
  <th class="right">Rém. masculine ($/h)</th><th class="right">Écart ($/h)</th>
  <th class="right">Écart %</th>
</tr>
""")
    for comp in comparisons:
        fid = comp.get("female_class_id", "")
        mid = comp.get("male_comparator_id") or "—"
        parts.append(f"""<tr>
  <td>{escape(fid)}</td>
  <td>{escape(title_map.get(fid, ''))}</td>
  <td>{escape(mid)}</td>
  <td>{_method_fr(comp.get('comparison_method', ''))}</td>
  <td class="right">{_fmt(comp.get('female_compensation', 0))}</td>
  <td class="right">{_fmt(comp.get('male_compensation', 0))}</td>
  <td class="right">{_fmt(comp.get('gap_hourly', 0))}</td>
  <td class="right">{_pct(comp.get('gap_percentage', 0))}</td>
</tr>""")
    parts.append("</table>")

    # Step 4: Adjustments
    parts.append("""
<h2>4. Ajustements salariaux requis</h2>
""")
    if class_adjustments:
        parts.append("""<table>
<tr>
  <th>Classe</th><th>Titre</th><th class="right">Écart ($/h)</th>
  <th class="right">Ajustement annuel par personne ($)</th>
  <th class="right">Effectif</th><th class="right">Coût total classe ($)</th>
</tr>
""")
        for adj in class_adjustments:
            parts.append(f"""<tr>
  <td>{escape(adj.get('class_id', ''))}</td>
  <td>{escape(adj.get('title', ''))}</td>
  <td class="right">{_fmt(adj.get('gap_hourly', 0))}</td>
  <td class="right">{_fmt(adj.get('annual_adjustment', 0))}</td>
  <td class="right">{adj.get('incumbents', '')}</td>
  <td class="right">{_fmt(adj.get('total_class_cost', 0))}</td>
</tr>""")
        parts.append("</table>")
    else:
        parts.append("<p><strong>Aucun ajustement requis.</strong></p>")

    # Payment schedule
    parts.append("""
<h2>5. Modalités de versement des ajustements</h2>
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

    # Rights, recourse, form, nouvel affichage
    parts.append(rights_notice_initial())
    parts.append(recourse_art101())
    parts.append(formulaire_notice())
    parts.append(nouvel_affichage_notice())

    parts.append(signature_block())
    parts.append(disclaimer_block())

    return build_html_document(parts)
