"""Pay equity posting (affichage) generation — multi-variant system.

Generates the correct posting variant based on employer size and exercise type,
per the Loi sur l'equite salariale (RLRQ c E-12.001).

Public API:
    generate_posting_pdf   — backward-compatible single-PDF generator (deprecated)
    generate_posting_html  — backward-compatible single-HTML generator (deprecated)
    generate_postings      — auto-detect variant, generate all applicable PDFs
"""

import warnings
from pathlib import Path
from typing import Optional

from scripts.pay_equity.persistence_gdrive import ENGAGEMENTS_ROOT

from ._base import build_html_document, _read
from ._initial_small import generate_initial_small_html
from ._initial_large import generate_1er_affichage, generate_2e_affichage
from ._maintenance import generate_maintenance_html
from ._nouvel import (
    generate_nouvel_initial,
    generate_nouvel_1er,
    generate_nouvel_2e,
    generate_nouvel_maintenance,
)


def generate_posting_html(
    client_slug: str,
    posting_type: str = "final",
    posting_date: str | None = None,
    engagements_root: Path | None = None,
) -> str:
    """Backward-compatible HTML generator. Delegates to the old monolithic logic.

    Deprecated: use generate_postings() for variant-aware generation.
    """
    # Import the shared helpers to reconstruct the old behavior
    from ._legacy import generate_legacy_posting_html

    return generate_legacy_posting_html(
        client_slug=client_slug,
        posting_type=posting_type,
        posting_date=posting_date,
        engagements_root=engagements_root,
    )


def generate_posting_pdf(
    client_slug: str,
    posting_type: str = "final",
    posting_date: str | None = None,
    engagements_root: Path | None = None,
) -> Path:
    """Backward-compatible single-PDF generator.

    Deprecated: use generate_postings() for variant-aware generation.
    """
    warnings.warn(
        "generate_posting_pdf is deprecated. Use generate_postings() for "
        "variant-aware posting generation.",
        DeprecationWarning,
        stacklevel=2,
    )
    from weasyprint import HTML

    root = engagements_root or ENGAGEMENTS_ROOT
    eng_dir = root / client_slug

    html_content = generate_posting_html(
        client_slug=client_slug,
        posting_type=posting_type,
        posting_date=posting_date,
        engagements_root=engagements_root,
    )

    filename = "affichage-provisoire.pdf" if posting_type == "provisoire" else "affichage-final.pdf"
    pdf_path = eng_dir / filename
    HTML(string=html_content).write_pdf(str(pdf_path))
    return pdf_path


def generate_postings(
    client_slug: str,
    engagements_root: Optional[Path] = None,
) -> list[Path]:
    """Auto-detect the correct posting variant and generate all applicable PDFs.

    Returns a list of generated PDF paths.
    """
    from weasyprint import HTML

    root = engagements_root or ENGAGEMENTS_ROOT
    eng_dir = root / client_slug

    engagement = _read(eng_dir, "engagement.json")
    size_tier = engagement.get("size_tier", "10-49")
    exercise_type = engagement.get("exercise_type", "initial")

    results: list[Path] = []

    if exercise_type == "maintenance":
        # Maintenance posting (art. 76.3)
        html = generate_maintenance_html(eng_dir, engagement)
        pdf_path = eng_dir / "affichage-maintien-art76-3.pdf"
        HTML(string=html).write_pdf(str(pdf_path))
        results.append(pdf_path)

        # Nouvel affichage for maintenance (art. 76.4)
        nouvel_html = generate_nouvel_maintenance(eng_dir, engagement)
        nouvel_path = eng_dir / "nouvel-affichage-maintien-art76-4.pdf"
        HTML(string=nouvel_html).write_pdf(str(nouvel_path))
        results.append(nouvel_path)

    elif size_tier == "10-49":
        # Initial 10-49 (art. 35)
        html = generate_initial_small_html(eng_dir)
        pdf_path = eng_dir / "affichage-initial-art35.pdf"
        HTML(string=html).write_pdf(str(pdf_path))
        results.append(pdf_path)

        # Nouvel affichage for 10-49
        nouvel_html = generate_nouvel_initial(eng_dir)
        nouvel_path = eng_dir / "nouvel-affichage-initial-art35.pdf"
        HTML(string=nouvel_html).write_pdf(str(nouvel_path))
        results.append(nouvel_path)

    else:
        # Initial 50+ (art. 75): two postings
        html_1er = generate_1er_affichage(eng_dir)
        pdf_1er = eng_dir / "affichage-1er-art75.pdf"
        HTML(string=html_1er).write_pdf(str(pdf_1er))
        results.append(pdf_1er)

        nouvel_1er_html = generate_nouvel_1er(eng_dir)
        nouvel_1er_path = eng_dir / "nouvel-affichage-1er-art75.pdf"
        HTML(string=nouvel_1er_html).write_pdf(str(nouvel_1er_path))
        results.append(nouvel_1er_path)

        html_2e = generate_2e_affichage(eng_dir)
        pdf_2e = eng_dir / "affichage-2e-art75.pdf"
        HTML(string=html_2e).write_pdf(str(pdf_2e))
        results.append(pdf_2e)

        nouvel_2e_html = generate_nouvel_2e(eng_dir)
        nouvel_2e_path = eng_dir / "nouvel-affichage-2e-art75.pdf"
        HTML(string=nouvel_2e_html).write_pdf(str(nouvel_2e_path))
        results.append(nouvel_2e_path)

    return results


__all__ = [
    "generate_posting_html",
    "generate_posting_pdf",
    "generate_postings",
]
