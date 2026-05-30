"""Shared helpers for posting generation."""

import json
from html import escape
from pathlib import Path

_CSS_PATH = Path(__file__).resolve().parent.parent.parent / "templates" / "posting" / "affichage.css"


def _read(eng_dir: Path, filename: str) -> dict:
    with open(eng_dir / filename, encoding="utf-8") as f:
        return json.load(f)


def _fmt(v, prefix="$") -> str:
    try:
        return f"{prefix}{float(v):,.2f}"
    except (TypeError, ValueError):
        return str(v)


def _pct(v) -> str:
    try:
        return f"{float(v):.1f}\u00a0%"
    except (TypeError, ValueError):
        return str(v)


def _dimension_fr(val: str) -> str:
    return {
        "qualifications": "Qualifications requises",
        "responsibilities": "Responsabilit\u00e9s assum\u00e9es",
        "effort": "Efforts requis",
        "conditions": "Conditions de travail",
    }.get(str(val).lower(), str(val))


def _predominance_fr(val: str) -> str:
    return {"female": "F\u00e9minine", "male": "Masculine", "neutral": "Neutre"}.get(
        str(val).lower(), str(val)
    )


def _method_fr(val: str) -> str:
    return {
        "quantitative": "Quantitative",
        "stereotype": "St\u00e9r\u00e9otype",
        "historical": "Historique",
        "job_to_job": "Poste \u00e0 poste",
        "regression": "R\u00e9gression",
        "hybrid": "Hybride",
        "global": "Global",
    }.get(str(val).lower(), str(val))


def build_html_document(parts: list[str]) -> str:
    """Wrap a list of HTML part strings into a full HTML document with CSS."""
    css_content = _CSS_PATH.read_text(encoding="utf-8")
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<style>{css_content}</style>
</head>
<body>
{"".join(parts)}
</body>
</html>"""


def employer_header(engagement: dict, title_full: str, legal_ref: str, display_date: str) -> str:
    """Generate the standard employer header block."""
    client_name = escape(engagement.get("client_name", ""))
    employee_count = engagement.get("employee_count", "")
    size_tier = engagement.get("size_tier", "")
    exercise_type = engagement.get("exercise_type", "initial")

    return f"""
<h1>{escape(title_full)}</h1>
<p class="legal-ref">{escape(legal_ref)}</p>

<div class="employer-block">
  <p><strong>Employeur&nbsp;:</strong> {client_name}</p>
  <p><strong>Nombre de personnes salari\u00e9es&nbsp;:</strong> {employee_count}</p>
  <p><strong>Cat\u00e9gorie d'entreprise&nbsp;:</strong> {escape(str(size_tier))} salari\u00e9s</p>
  <p><strong>Type d'exercice&nbsp;:</strong> {"Initial" if exercise_type == "initial" else "Maintien"}</p>
  <p><strong>Date d'affichage&nbsp;:</strong> {escape(display_date)}</p>
</div>
"""


def signature_block() -> str:
    """Standard signature block for all postings."""
    return """
<div class="signature-block">
  <p><strong>Signature de l'employeur ou du repr\u00e9sentant autoris\u00e9&nbsp;:</strong></p>
  <p><span class="signature-line">&nbsp;</span></p>
  <p>Nom&nbsp;: <span class="signature-line">&nbsp;</span></p>
  <p>Date&nbsp;: <span class="signature-line">&nbsp;</span></p>
</div>
"""


def disclaimer_block() -> str:
    """Standard automated-tool disclaimer."""
    return """
<div class="disclaimer">
  <strong>Avis important&nbsp;:</strong> Ce document a \u00e9t\u00e9 produit \u00e0 l'aide d'un outil
  automatis\u00e9. Il doit \u00eatre r\u00e9vis\u00e9 par une personne qualifi\u00e9e avant utilisation aux fins
  de conformit\u00e9 \u00e0 la Loi sur l'\u00e9quit\u00e9 salariale.
</div>
"""
