"""Legacy posting HTML generation — preserves exact old behavior for backward compat.

This is the original monolithic generate_posting_html moved here unchanged.
"""

from datetime import date
from html import escape
from pathlib import Path

from scripts.pay_equity.persistence_gdrive import ENGAGEMENTS_ROOT

from ._base import (
    _read, _fmt, _pct, _dimension_fr, _predominance_fr, _method_fr,
    build_html_document,
)


def generate_legacy_posting_html(
    client_slug: str,
    posting_type: str = "final",
    posting_date: str | None = None,
    engagements_root: Path | None = None,
) -> str:
    """Build the full posting HTML from engagement data files (legacy format)."""
    root = engagements_root or ENGAGEMENTS_ROOT
    eng_dir = root / client_slug

    engagement = _read(eng_dir, "engagement.json")
    job_classes = _read(eng_dir, "job-classes.json")
    evaluation = _read(eng_dir, "evaluation-grid.json")
    compensation = _read(eng_dir, "compensation.json")
    adjustments = _read(eng_dir, "adjustments.json")

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
<p class="legal-ref">Loi sur l'\u00e9quit\u00e9 salariale, RLRQ c E-12.001, art. 75</p>

<div class="employer-block">
  <p><strong>Employeur&nbsp;:</strong> {client_name}</p>
  <p><strong>Nombre de personnes salari\u00e9es&nbsp;:</strong> {employee_count}</p>
  <p><strong>Cat\u00e9gorie d'entreprise&nbsp;:</strong> {escape(size_tier)} salari\u00e9s</p>
  <p><strong>Type d'exercice&nbsp;:</strong> {"Initial" if exercise_type == "initial" else "Maintien"}</p>
  <p><strong>Date d'affichage&nbsp;:</strong> {escape(display_date)}</p>
</div>
""")

    # --- Section 1: Job Classes ---
    parts.append("""
<h2>1. Identification des cat\u00e9gories d'emplois \u00e0 pr\u00e9dominance f\u00e9minine et masculine</h2>

<div class="explanation">
  La Loi sur l'\u00e9quit\u00e9 salariale exige que l'employeur identifie les cat\u00e9gories d'emplois
  au sein de l'entreprise et d\u00e9termine leur pr\u00e9dominance sexuelle. Une cat\u00e9gorie d'emplois
  est \u00e0 pr\u00e9dominance f\u00e9minine ou masculine lorsqu'elle est couramment associ\u00e9e aux femmes
  ou aux hommes en raison de st\u00e9r\u00e9otypes occupationnels, ou lorsqu'au moins 60&nbsp;% des
  personnes salari\u00e9es qui occupent les emplois de cette cat\u00e9gorie sont du m\u00eame sexe.
</div>
""")

    parts.append("""
<table>
<tr>
  <th>Classe</th><th>Titre</th><th class="right">Effectif</th>
  <th class="right">% F\u00e9minin</th><th>Pr\u00e9dominance</th><th>M\u00e9thode</th>
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
<h2>2. M\u00e9thode d'\u00e9valuation des cat\u00e9gories d'emplois</h2>

<div class="explanation">
  L'\u00e9valuation des cat\u00e9gories d'emplois a \u00e9t\u00e9 effectu\u00e9e \u00e0 l'aide d'une m\u00e9thode par
  points et facteurs, conform\u00e9ment \u00e0 l'article 57 de la Loi. Cette m\u00e9thode \u00e9value
  chaque cat\u00e9gorie d'emplois selon les quatre grandes dimensions prescrites&nbsp;:
  les qualifications requises, les responsabilit\u00e9s assum\u00e9es, les efforts requis et
  les conditions dans lesquelles le travail est effectu\u00e9.
</div>
""")

    parts.append("<h3>Dimensions et pond\u00e9ration</h3>")
    parts.append("""<table>
<tr><th>Dimension</th><th class="right">Poids</th></tr>
""")
    for dim, w in sorted(dim_weights.items()):
        parts.append(f"<tr><td>{_dimension_fr(dim)}</td><td class='right'>{_pct(float(w) * 100)}</td></tr>")
    parts.append("</table>")

    parts.append("<h3>Sous-facteurs d'\u00e9valuation</h3>")
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
<h2>3. R\u00e9sultats de l'\u00e9valuation des cat\u00e9gories d'emplois</h2>

<div class="explanation">
  Le tableau suivant pr\u00e9sente le pointage total obtenu par chaque cat\u00e9gorie d'emplois
  \u00e0 la suite de l'\u00e9valuation. Les cat\u00e9gories sont class\u00e9es par ordre d\u00e9croissant de
  pointage. Le grade est d\u00e9termin\u00e9 par regroupement des pointages en bandes.
</div>
""")
    parts.append("""<table>
<tr><th>Classe</th><th>Titre</th><th>Pr\u00e9dominance</th><th class="right">Score total</th><th class="right">Grade</th></tr>
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
<h2>4. R\u00e9sultats de la comparaison de la r\u00e9mun\u00e9ration</h2>

<div class="explanation">
  La r\u00e9mun\u00e9ration de chaque cat\u00e9gorie d'emplois \u00e0 pr\u00e9dominance f\u00e9minine a \u00e9t\u00e9 compar\u00e9e
  \u00e0 celle d'une cat\u00e9gorie d'emplois \u00e0 pr\u00e9dominance masculine de m\u00eame valeur ou de valeur
  comparable au sein de l'entreprise. La r\u00e9mun\u00e9ration compar\u00e9e est le taux de la structure
  salariale (maximum de l'\u00e9chelle \u00e0 \u00e9chelons ou point milieu de l'\u00e9chelle de m\u00e9rites),
  et non le salaire individuel des personnes salari\u00e9es. L'\u00e9cart indique la diff\u00e9rence
  entre la r\u00e9mun\u00e9ration masculine et f\u00e9minine pour des emplois de valeur \u00e9quivalente.
</div>
""")
    parts.append("""<table>
<tr>
  <th>Cat\u00e9gorie f\u00e9minine</th><th>Titre</th><th>Comparateur masculin</th>
  <th>M\u00e9thode</th><th class="right">R\u00e9m. f\u00e9minine ($/h)</th>
  <th class="right">R\u00e9m. masculine ($/h)</th><th class="right">\u00c9cart ($/h)</th>
  <th class="right">\u00c9cart %</th>
</tr>
""")
    for comp in comparisons:
        fid = comp.get("female_class_id", "")
        mid = comp.get("male_comparator_id") or "\u2014"
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
  Lorsqu'un \u00e9cart de r\u00e9mun\u00e9ration est constat\u00e9 au d\u00e9triment d'une cat\u00e9gorie d'emplois
  \u00e0 pr\u00e9dominance f\u00e9minine, l'employeur doit verser des ajustements salariaux pour
  combler cet \u00e9cart. Les ajustements ci-dessous indiquent le montant horaire et annuel
  \u00e0 verser par cat\u00e9gorie d'emplois.
</div>
""")
    parts.append("""<table>
<tr>
  <th>Classe</th><th>Titre</th><th class="right">\u00c9cart ($/h)</th>
  <th class="right">Ajustement annuel par personne ($)</th>
  <th class="right">Effectif</th><th class="right">Co\u00fbt total classe ($)</th>
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
<h2>6. Modalit\u00e9s de versement des ajustements</h2>

<div class="explanation">
  Conform\u00e9ment \u00e0 l'article 68 de la Loi, les ajustements salariaux peuvent \u00eatre \u00e9tal\u00e9s
  sur un maximum de {max_installments} versements annuels \u00e9gaux. Le premier versement
  est d\u00fb \u00e0 compter de la date \u00e0 laquelle les ajustements auraient d\u00fb \u00eatre vers\u00e9s.
  Des int\u00e9r\u00eats au taux l\u00e9gal de 5&nbsp;% (C.c.Q., art. 1617) s'appliquent sur les
  versements report\u00e9s.
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
  <p>Conform\u00e9ment \u00e0 l'article 76 de la Loi sur l'\u00e9quit\u00e9 salariale, les personnes
  salari\u00e9es de l'entreprise disposent d'un d\u00e9lai de <strong>60 jours</strong>
  suivant la date du pr\u00e9sent affichage pour formuler leurs observations \u00e0 l'employeur.</p>
  <p><strong>Date d'affichage&nbsp;:</strong> {escape(display_date)}</p>
  <p><strong>Fin de la p\u00e9riode de consultation&nbsp;:</strong> ______________________</p>
</div>
""")

    # --- Signature ---
    parts.append("""
<div class="signature-block">
  <p><strong>Signature de l'employeur ou du repr\u00e9sentant autoris\u00e9&nbsp;:</strong></p>
  <p><span class="signature-line">&nbsp;</span></p>
  <p>Nom&nbsp;: <span class="signature-line">&nbsp;</span></p>
  <p>Date&nbsp;: <span class="signature-line">&nbsp;</span></p>
</div>
""")

    # --- Disclaimer ---
    parts.append("""
<div class="disclaimer">
  <strong>Avis important&nbsp;:</strong> Ce document a \u00e9t\u00e9 produit \u00e0 l'aide d'un outil
  automatis\u00e9. Il doit \u00eatre r\u00e9vis\u00e9 par une personne qualifi\u00e9e avant utilisation aux fins
  de conformit\u00e9 \u00e0 la Loi sur l'\u00e9quit\u00e9 salariale.
</div>
""")

    return build_html_document(parts)
