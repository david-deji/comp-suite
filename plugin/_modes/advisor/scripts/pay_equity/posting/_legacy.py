"""Legacy posting HTML generation — preserves exact old behavior for backward compat.

This is the original monolithic generate_posting_html moved here unchanged.
"""

from datetime import date
from html import escape

from ._base import (
    _fmt, _pct, _dimension_fr, _predominance_fr, _method_fr,
    build_html_document,
)


def generate_legacy_posting_html(
    client_slug: str,
    posting_type: str = "final",
    posting_date: str | None = None,
    *,
    engagement: dict,
    job_classes: dict,
    evaluation: dict,
    compensation: dict,
    adjustments: dict,
) -> str:
    """Build the full posting HTML from engagement data dicts (legacy format)."""
    client_name = escape(engagement.get("client_name", client_slug))
    size_tier = engagement.get("size_tier", "")
    employee_count = engagement.get("employee_count", "")
    exercise_type = engagement.get("exercise_type", "initial")
    created_date = engagement.get("created_date", "")
    display_date = posting_date or date.today().isoformat()

    is_provisoire = posting_type == "provisoire"
    title = "Affichage provisoire" if is_provisoire else "Affichage des résultats"
    title_full = f"{title} de l'exercice d'équité salariale"

    classes = job_classes.get("classes", [])
    grid = evaluation.get("grid", {})
    class_scores = evaluation.get("class_scores", [])
    comparisons = compensation.get("comparison_results", [])
    class_adjustments = adjustments.get("class_adjustments", [])
    schedule = adjustments.get("payment_schedule", [])

    # Sort scores descending
    class_scores_sorted = sorted(class_scores, key=lambda x: float(x.get("total_score", 0)), reverse=True)

    # Compute grade assignments from score bands (band width ~75 points)
    _grade_map: dict[str, int] = {}
    if class_scores_sorted:
        _scores = [float(cs.get("total_score", 0)) for cs in class_scores_sorted]
        _min_score = min(_scores)
        _band_width = 75.0
        for cs in class_scores_sorted:
            _score = float(cs.get("total_score", 0))
            _grade_map[cs.get("class_id", "")] = int((_score - _min_score) / _band_width) + 1

    # Title map for class IDs
    title_map = {c["id"]: c.get("title", "") for c in classes}

    # Build HTML
    parts = []

    # --- Header ---
    parts.append(f"""
<h1>{escape(title_full)}</h1>
<p class="legal-ref">Loi sur l'équité salariale, RLRQ c E-12.001, art. 75</p>

<div class="employer-block">
  <p><strong>Employeur&nbsp;:</strong> {client_name}</p>
  <p><strong>Nombre de personnes salariées&nbsp;:</strong> {employee_count}</p>
  <p><strong>Catégorie d'entreprise&nbsp;:</strong> {escape(size_tier)} salariés</p>
  <p><strong>Type d'exercice&nbsp;:</strong> {"Initial" if exercise_type == "initial" else "Maintien"}</p>
  <p><strong>Date d'affichage&nbsp;:</strong> {escape(display_date)}</p>
</div>
""")

    # --- Section 1: Job Classes ---
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

    parts.append("""
<table>
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

    # --- Section 2: Evaluation Grid ---
    dim_weights = grid.get("dimension_weights", {})
    sub_factors = grid.get("sub_factors", [])

    parts.append("""
<h2>2. Méthode d'évaluation des catégories d'emplois</h2>

<div class="explanation">
  L'évaluation des catégories d'emplois a été effectuée à l'aide d'une méthode par
  points et facteurs, conformément à l'article 57 de la Loi. Cette méthode évalue
  chaque catégorie d'emplois selon les quatre grandes dimensions prescrites&nbsp;:
  les qualifications requises, les responsabilités assumées, les efforts requis et
  les conditions dans lesquelles le travail est effectué.
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

    # --- Section 3: Scores ---
    parts.append("""
<h2>3. Résultats de l'évaluation des catégories d'emplois</h2>

<div class="explanation">
  Le tableau suivant présente le pointage total obtenu par chaque catégorie d'emplois
  à la suite de l'évaluation. Les catégories sont classées par ordre décroissant de
  pointage. Le grade est déterminé par regroupement des pointages en bandes.
</div>
""")
    parts.append("""<table>
<tr><th>Classe</th><th>Titre</th><th>Prédominance</th><th class="right">Score total</th><th class="right">Grade</th></tr>
""")
    pred_map = {c["id"]: c.get("predominance", "") for c in classes}
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

    # --- Section 4: Compensation Comparison ---
    parts.append("""
<h2>4. Résultats de la comparaison de la rémunération</h2>

<div class="explanation">
  La rémunération de chaque catégorie d'emplois à prédominance féminine a été comparée
  à celle d'une catégorie d'emplois à prédominance masculine de même valeur ou de valeur
  comparable au sein de l'entreprise. La rémunération comparée est le taux de la structure
  salariale (maximum de l'échelle à échelons ou point milieu de l'échelle de mérites),
  et non le salaire individuel des personnes salariées. L'écart indique la différence
  entre la rémunération masculine et féminine pour des emplois de valeur équivalente.
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

    # --- Section 5: Adjustments ---
    parts.append("""
<h2>5. Ajustements salariaux requis</h2>

<div class="explanation">
  Lorsqu'un écart de rémunération est constaté au détriment d'une catégorie d'emplois
  à prédominance féminine, l'employeur doit verser des ajustements salariaux pour
  combler cet écart. Les ajustements ci-dessous indiquent le montant horaire et annuel
  à verser par catégorie d'emplois.
</div>
""")
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

    # --- Section 6: Payment Schedule ---
    max_installments = 4 if exercise_type == "initial" else 5
    parts.append(f"""
<h2>6. Modalités de versement des ajustements</h2>

<div class="explanation">
  Conformément à l'article 68 de la Loi, les ajustements salariaux peuvent être étalés
  sur un maximum de {max_installments} versements annuels égaux. Le premier versement
  est dû à compter de la date à laquelle les ajustements auraient dû être versés.
  Des intérêts au taux légal de 5&nbsp;% (C.c.Q., art. 1617) s'appliquent sur les
  versements reportés.
</div>
""")
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

    # --- Consultation notice (provisoire only) ---
    if is_provisoire:
        parts.append(f"""
<div class="consultation-notice">
  <h2>Avis de consultation</h2>
  <p>Conformément à l'article 76 de la Loi sur l'équité salariale, les personnes
  salariées de l'entreprise disposent d'un délai de <strong>60 jours</strong>
  suivant la date du présent affichage pour formuler leurs observations à l'employeur.</p>
  <p><strong>Date d'affichage&nbsp;:</strong> {escape(display_date)}</p>
  <p><strong>Fin de la période de consultation&nbsp;:</strong> ______________________</p>
</div>
""")

    # --- Signature ---
    parts.append("""
<div class="signature-block">
  <p><strong>Signature de l'employeur ou du représentant autorisé&nbsp;:</strong></p>
  <p><span class="signature-line">&nbsp;</span></p>
  <p>Nom&nbsp;: <span class="signature-line">&nbsp;</span></p>
  <p>Date&nbsp;: <span class="signature-line">&nbsp;</span></p>
</div>
""")

    # --- Disclaimer ---
    parts.append("""
<div class="disclaimer">
  <strong>Avis important&nbsp;:</strong> Ce document a été produit à l'aide d'un outil
  automatisé. Il doit être révisé par une personne qualifiée avant utilisation aux fins
  de conformité à la Loi sur l'équité salariale.
</div>
""")

    return build_html_document(parts)
