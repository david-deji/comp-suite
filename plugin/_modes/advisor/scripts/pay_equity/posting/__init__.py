"""Pay equity posting (affichage) generation — multi-variant system.

Generates the correct posting variant based on employer size and exercise type,
per the Loi sur l'equite salariale (RLRQ c E-12.001).

Public API:
    generate_posting_pdf   — backward-compatible single-PDF generator (deprecated)
    generate_posting_html  — backward-compatible single-HTML generator (deprecated)
    generate_postings      — auto-detect variant, generate all applicable PDFs
"""

import warnings
from typing import Optional

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
    *,
    engagement: dict,
    job_classes: dict,
    evaluation: dict,
    compensation: dict,
    adjustments: dict,
) -> str:
    """Backward-compatible HTML generator. Delegates to the old monolithic logic.

    Deprecated: use generate_postings() for variant-aware generation.
    """
    from ._legacy import generate_legacy_posting_html

    return generate_legacy_posting_html(
        client_slug=client_slug,
        posting_type=posting_type,
        posting_date=posting_date,
        engagement=engagement,
        job_classes=job_classes,
        evaluation=evaluation,
        compensation=compensation,
        adjustments=adjustments,
    )


def generate_posting_pdf(
    client_slug: str,
    posting_type: str = "final",
    posting_date: str | None = None,
    *,
    engagement: dict,
    job_classes: dict,
    evaluation: dict,
    compensation: dict,
    adjustments: dict,
) -> tuple[bytes, str]:
    """Backward-compatible single-PDF generator. Returns (pdf_bytes, filename).

    Deprecated: use generate_postings() for variant-aware generation.
    """
    warnings.warn(
        "generate_posting_pdf is deprecated. Use generate_postings() for "
        "variant-aware posting generation.",
        DeprecationWarning,
        stacklevel=2,
    )
    from weasyprint import HTML

    html_content = generate_posting_html(
        client_slug=client_slug,
        posting_type=posting_type,
        posting_date=posting_date,
        engagement=engagement,
        job_classes=job_classes,
        evaluation=evaluation,
        compensation=compensation,
        adjustments=adjustments,
    )

    filename = "affichage-provisoire.pdf" if posting_type == "provisoire" else "affichage-final.pdf"
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes, filename


def generate_postings(
    engagement: dict,
    job_classes: Optional[dict] = None,
    evaluation: Optional[dict] = None,
    compensation: Optional[dict] = None,
    adjustments: Optional[dict] = None,
) -> list[tuple[bytes, str]]:
    """Auto-detect the correct posting variant and generate all applicable PDFs.

    Returns a list of (pdf_bytes, intended_filename) tuples — deliverables for
    the caller to route; does not write to any filesystem path.
    """
    from weasyprint import HTML

    job_classes = job_classes or {}
    evaluation = evaluation or {}
    compensation = compensation or {}
    adjustments = adjustments or {}

    size_tier = engagement.get("size_tier", "10-49")
    exercise_type = engagement.get("exercise_type", "initial")

    results: list[tuple[bytes, str]] = []

    if exercise_type == "maintenance":
        # Maintenance posting (art. 76.3)
        html = generate_maintenance_html(engagement, job_classes, adjustments)
        results.append((HTML(string=html).write_pdf(), "affichage-maintien-art76-3.pdf"))

        # Nouvel affichage for maintenance (art. 76.4)
        nouvel_html = generate_nouvel_maintenance(engagement)
        results.append((HTML(string=nouvel_html).write_pdf(), "nouvel-affichage-maintien-art76-4.pdf"))

    elif size_tier == "10-49":
        # Initial 10-49 (art. 35)
        html = generate_initial_small_html(engagement, job_classes, compensation, adjustments)
        results.append((HTML(string=html).write_pdf(), "affichage-initial-art35.pdf"))

        # Nouvel affichage for 10-49
        nouvel_html = generate_nouvel_initial(engagement)
        results.append((HTML(string=nouvel_html).write_pdf(), "nouvel-affichage-initial-art35.pdf"))

    else:
        # Initial 50+ (art. 75): two postings
        html_1er = generate_1er_affichage(engagement, job_classes, evaluation)
        results.append((HTML(string=html_1er).write_pdf(), "affichage-1er-art75.pdf"))

        nouvel_1er_html = generate_nouvel_1er(engagement)
        results.append((HTML(string=nouvel_1er_html).write_pdf(), "nouvel-affichage-1er-art75.pdf"))

        html_2e = generate_2e_affichage(engagement, job_classes, compensation, adjustments)
        results.append((HTML(string=html_2e).write_pdf(), "affichage-2e-art75.pdf"))

        nouvel_2e_html = generate_nouvel_2e(engagement)
        results.append((HTML(string=nouvel_2e_html).write_pdf(), "nouvel-affichage-2e-art75.pdf"))

    return results


__all__ = [
    "generate_posting_html",
    "generate_posting_pdf",
    "generate_postings",
]
