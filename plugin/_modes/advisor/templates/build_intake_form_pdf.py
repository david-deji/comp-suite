"""
Fillable Strategic Intake Form — PDF
Audience: VP HR, VP Operations
Brand: active brand kit (defaults to `_default` — Acme Inc.)

Reads palette + logo from `template_assets/branding/<active-kit>/theme/` at runtime.
When `<active-kit>` differs from `_default`, palette + typography are deep-merged
over the `_default` kit (so per-org kits only ship the keys they override).
Logo is read from `<active-kit>/theme/logo.svg`, falling back to `_default/theme/logo.svg`.

Per-org kit override mechanics: see `references/brand-kit-protocol.md`.
Default kit seed content: see `brand-guidelines.md`.

DEPENDENCIES (install once):
    pip install reportlab svglib

USAGE:
    python3 build_intake_form_pdf.py
    python3 build_intake_form_pdf.py --kit acme-pharmacy --cycle "Pharmacy FY26"
    python3 build_intake_form_pdf.py --kit acme-grocery --output /tmp/acme-intake.pdf

CLI ARGS:
    --kit          Active brand kit slug (default: _default). Reads from
                   template_assets/branding/<kit>/theme/.
    --cycle        Cycle name shown in header (default: "FY26 Annual Wage Review").
    --output       Output PDF path (default: ./strategic-intake-form.pdf).

NOTE: Question 8 peer-set ("Loblaw, Metro, ...") and Question 10 org reference
("Acme") are still hardcoded for the `_default` kit. Per-org rendering of
those questions is owned by intake-mode-protocol.md (Stage 3 — One-At-A-Time
Approval Loop), which generates kit-aware question variants from
engagement-config.benchmark.peer_companies and engagement-config.org.name
before invoking this script. A future refactor will accept questions as a
JSON payload; until then, single-tenant question text reflects the `_default`
kit's seed content.
"""

import argparse
import json
import sys
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

SCRIPT_DIR = Path(__file__).resolve().parent
BRANDING_ROOT = SCRIPT_DIR / "branding"

# ── Brand-kit loader ─────────────────────────────────────────────────────


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge `override` into `base`, returning a new dict."""
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_brand_kit(slug: str) -> dict:
    """Load the active brand kit's palette, typography, and logo path.

    Always loads `_default` first; when `slug != "_default"`, deep-merges the
    per-org kit's palette.json + typography.json over `_default`. Logo path
    is the per-org file when present, otherwise the `_default` file.

    Returns: {"palette": dict, "typography": dict, "logo_path": Path, "slug": str}
    Raises: FileNotFoundError if `_default` kit is missing (bundle is broken).
    """
    default_dir = BRANDING_ROOT / "_default" / "theme"
    if not default_dir.is_dir():
        raise FileNotFoundError(
            f"Default brand kit not found at {default_dir}. "
            "Bundle is broken — `_default` kit must always be present."
        )

    palette = _read_json(default_dir / "palette.json")
    typography = _read_json(default_dir / "typography.json")
    logo_path = _resolve_logo(default_dir)

    if slug != "_default":
        org_dir = BRANDING_ROOT / slug / "theme"
        if not org_dir.is_dir():
            print(
                f"⚠ brand kit '{slug}' not found at {org_dir} — falling back to _default",
                file=sys.stderr,
            )
        else:
            org_palette_file = org_dir / "palette.json"
            if org_palette_file.exists():
                palette = _deep_merge(palette, _read_json(org_palette_file))
            org_typography_file = org_dir / "typography.json"
            if org_typography_file.exists():
                typography = _deep_merge(typography, _read_json(org_typography_file))
            org_logo = _resolve_logo(org_dir)
            if org_logo is not None:
                logo_path = org_logo

    return {
        "palette": palette,
        "typography": typography,
        "logo_path": logo_path,
        "slug": slug,
    }


def _resolve_logo(theme_dir: Path):
    """Prefer logo.svg (vector), fall back to logo-large.png. Return None if neither."""
    for candidate in ("logo.svg", "logo-large.png", "logo_large.png"):
        p = theme_dir / candidate
        if p.exists():
            return p
    return None


def _hex(palette: dict, key: str, fallback: str) -> "HexColor":
    """Read a hex string from palette by key; tolerate `#` prefix or its absence."""
    raw = palette.get(key, fallback)
    if not raw.startswith("#"):
        raw = "#" + raw
    return HexColor(raw)


# ── Build context (palette + tokens resolved at runtime) ─────────────────


class BrandTokens:
    """Hex tokens derived from the active brand kit's palette.json.

    Brand-essential keys (`green`, `offwhite`, `deepPurple`, `teal`, `primaryDark`,
    `accentTeal`, `borderGray`, `textGray`) come from palette.json so per-org kits
    override them via `branding/<org>/theme/palette.json`. Form-UI colors (input
    background, input border) are kit-overridable via the `_form_ui` block but
    default to PDF-safe greys when absent.

    Key names are palette tokens, not client-specific: `primaryDark` / `accentTeal`
    are the brand's primary + accent colours (body text uses `primaryDark`). Fallback
    hexes below are neutral placeholders; the active palette.json supplies real values.
    """

    def __init__(self, kit: dict):
        p = kit["palette"]
        ui = p.get("_form_ui", {})

        self.primary_dark = _hex(p, "primaryDark", "4B2E83")
        self.accent_teal = _hex(p, "accentTeal", "2A8C82")
        self.green = _hex(p, "green", "4AA447")
        self.offwhite = _hex(p, "offwhite", "FAF8F7")
        self.deep_purple = _hex(p, "deepPurple", "3C1E54")  # available; not yet used (see NOTE)

        self.line_grey = _hex(p, "borderGray", "D9D9D9")
        self.soft_grey = _hex(p, "textGray", "555555")  # was #8A8A8A pre-refactor

        # Form-UI colours — overridable via palette["_form_ui"], defaults preserve pre-refactor look
        self.input_bg = HexColor("#" + ui.get("inputBg", "FAFAFA").lstrip("#"))
        self.input_border = HexColor("#" + ui.get("inputBorder", "C0C0C0").lstrip("#"))


# Font registration — reportlab built-ins (Times/Helvetica) used as PDF-safe stand-ins
# for the active kit's typography.json (typically Noto Serif + Lexend Deca). Embedding
# the actual fonts requires registering TTFs via pdfmetrics.registerFont; deferred to
# a future refactor when the bundle ships TTF files.
HEADING_FONT = "Times-Bold"
HEADING_FONT_REG = "Times-Roman"
BODY_FONT = "Helvetica"
BODY_FONT_BOLD = "Helvetica-Bold"
BODY_FONT_ITALIC = "Helvetica-Oblique"

PAGE_WIDTH, PAGE_HEIGHT = LETTER
MARGIN_LEFT = 0.85 * inch
MARGIN_RIGHT = 0.85 * inch
MARGIN_TOP = 0.85 * inch
MARGIN_BOTTOM = 0.7 * inch
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

LOGO_RENDER_WIDTH = 100  # points


class Layout:
    def __init__(self, c, kit: dict, tokens: BrandTokens):
        self.c = c
        self.kit = kit
        self.t = tokens
        self.y = PAGE_HEIGHT - MARGIN_TOP
        self.page = 1
        self.total_pages = 4
        self.logo = None
        if kit["logo_path"] is not None and str(kit["logo_path"]).endswith(".svg"):
            self.logo = svg2rlg(str(kit["logo_path"]))
            if self.logo is not None:
                scale = LOGO_RENDER_WIDTH / self.logo.width
                self.logo.width *= scale
                self.logo.height *= scale
                self.logo.scale(scale, scale)
                self.logo_height = self.logo.height
            else:
                self.logo_height = 0
        else:
            self.logo_height = 0

    def new_page(self):
        self.draw_footer()
        self.c.showPage()
        self.page += 1
        self.y = PAGE_HEIGHT - MARGIN_TOP
        self.draw_header()

    def ensure_space(self, needed):
        if self.y - needed < MARGIN_BOTTOM + 30:
            self.new_page()

    def draw_header(self):
        c = self.c
        if self.logo is not None:
            logo_y = PAGE_HEIGHT - MARGIN_TOP + 14
            renderPDF.draw(self.logo, c, MARGIN_LEFT, logo_y)
        c.setStrokeColor(self.t.green)
        c.setLineWidth(1.5)
        c.line(MARGIN_LEFT, PAGE_HEIGHT - MARGIN_TOP + 8,
               PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - MARGIN_TOP + 8)

    def draw_footer(self):
        c = self.c
        c.setStrokeColor(self.t.line_grey)
        c.setLineWidth(0.5)
        c.line(MARGIN_LEFT, MARGIN_BOTTOM - 5,
               PAGE_WIDTH - MARGIN_RIGHT, MARGIN_BOTTOM - 5)
        c.setFont(BODY_FONT, 8)
        c.setFillColor(self.t.soft_grey)
        text = f"Confidential — Compensation Strategic Intake   |   Page {self.page} of {self.total_pages}"
        c.drawCentredString(PAGE_WIDTH / 2, MARGIN_BOTTOM - 18, text)


def draw_eyebrow(L, text, color=None):
    if color is None:
        color = L.t.green
    L.ensure_space(20)
    L.c.setFont(BODY_FONT_BOLD, 9)
    L.c.setFillColor(color)
    L.c.drawString(MARGIN_LEFT, L.y, text)
    L.y -= 18


def draw_title(L, text, size=24, color=None, font=HEADING_FONT_REG):
    if color is None:
        color = L.t.primary_dark
    L.ensure_space(size + 6)
    L.c.setFont(font, size)
    L.c.setFillColor(color)
    L.c.drawString(MARGIN_LEFT, L.y - size, text)
    L.y -= size + 4


def draw_subtitle(L, text, size=12, color=None, font=BODY_FONT_ITALIC):
    if color is None:
        color = L.t.soft_grey
    L.ensure_space(size + 12)
    L.c.setFont(font, size)
    L.c.setFillColor(color)
    L.c.drawString(MARGIN_LEFT, L.y - size, text)
    L.y -= size + 16


def draw_paragraph(L, text, size=10, color=None, font=BODY_FONT,
                   leading=14, max_width=None):
    if color is None:
        color = L.t.primary_dark
    if max_width is None:
        max_width = CONTENT_WIDTH
    L.c.setFont(font, size)
    L.c.setFillColor(color)
    words = text.split(' ')
    line = ''
    for word in words:
        test = (line + ' ' + word).strip()
        if pdfmetrics.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            L.ensure_space(leading)
            L.c.drawString(MARGIN_LEFT, L.y - size, line)
            L.y -= leading
            line = word
    if line:
        L.ensure_space(leading)
        L.c.drawString(MARGIN_LEFT, L.y - size, line)
        L.y -= leading


def draw_section_header(L, text):
    L.ensure_space(40)
    L.y -= 16
    L.c.setFont(BODY_FONT_BOLD, 10)
    L.c.setFillColor(L.t.primary_dark)
    L.c.drawString(MARGIN_LEFT, L.y, text)
    L.c.setStrokeColor(L.t.green)
    L.c.setLineWidth(1.5)
    L.c.line(MARGIN_LEFT, L.y - 6, PAGE_WIDTH - MARGIN_RIGHT, L.y - 6)
    L.y -= 24


def wrap_text(text, font, size, max_width):
    words = text.split(' ')
    lines = []
    line = ''
    for word in words:
        test = (line + ' ' + word).strip()
        if pdfmetrics.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_metadata_table(L, cycle_name: str):
    """
    Top row:    Recipient (fillable) | Please return by (fillable)
    Bottom row: Cycle (full width, static, runtime-set)
    """
    cell_h_top = 38
    cell_h_bottom = 38
    L.ensure_space(cell_h_top + cell_h_bottom + 12)
    half_w = CONTENT_WIDTH / 2
    full_w = CONTENT_WIDTH

    # Top row: 2 fillable cells
    for col_idx, (label, field_name) in enumerate([
        ("Recipient", "meta_recipient"),
        ("Please return by", "meta_return_by")
    ]):
        x = MARGIN_LEFT + col_idx * half_w
        y = L.y - cell_h_top
        L.c.setFillColor(L.t.offwhite)
        L.c.rect(x, y, half_w - 4, cell_h_top, stroke=0, fill=1)
        L.c.setStrokeColor(L.t.line_grey)
        L.c.setLineWidth(0.5)
        L.c.line(x, y, x + half_w - 4, y)
        L.c.setFont(BODY_FONT_BOLD, 7)
        L.c.setFillColor(L.t.soft_grey)
        L.c.drawString(x + 8, y + cell_h_top - 12, label.upper())
        L.c.acroForm.textfield(
            name=field_name, tooltip=label,
            x=x + 6, y=y + 4, width=half_w - 18, height=20,
            borderStyle='inset', borderColor=L.t.input_border,
            fillColor=white, textColor=L.t.primary_dark,
            forceBorder=True, fontSize=10, fontName=BODY_FONT
        )
    L.y -= cell_h_top + 4

    # Bottom row: full-width static cycle
    x = MARGIN_LEFT
    y = L.y - cell_h_bottom
    L.c.setFillColor(L.t.offwhite)
    L.c.rect(x, y, full_w, cell_h_bottom, stroke=0, fill=1)
    L.c.setStrokeColor(L.t.line_grey)
    L.c.setLineWidth(0.5)
    L.c.line(x, y, x + full_w, y)
    L.c.setFont(BODY_FONT_BOLD, 7)
    L.c.setFillColor(L.t.soft_grey)
    L.c.drawString(x + 8, y + cell_h_bottom - 12, "CYCLE")
    L.c.setFont(BODY_FONT, 12)
    L.c.setFillColor(L.t.primary_dark)
    L.c.drawString(x + 8, y + 10, cycle_name)
    L.y -= cell_h_bottom + 12


def draw_question(L, num, title, why, lines=4, bullets=None, field_name=None):
    title_lines = wrap_text(title, HEADING_FONT, 13, CONTENT_WIDTH - 22)
    why_lines = wrap_text("Why we ask: " + why, BODY_FONT_ITALIC, 8.5, CONTENT_WIDTH)
    bullet_count = len(bullets) if bullets else 0
    box_height = lines * 16 + 10
    needed = (
        18 + len(title_lines) * 17 + len(why_lines) * 12 + 6 +
        bullet_count * 13 + box_height + 12
    )
    L.ensure_space(needed)
    L.y -= 8

    L.c.setFont(HEADING_FONT, 13)
    num_text = f"{num}. "
    num_width = pdfmetrics.stringWidth(num_text, HEADING_FONT, 13)
    L.c.setFillColor(L.t.green)
    L.c.drawString(MARGIN_LEFT, L.y - 13, num_text)
    L.c.setFillColor(L.t.primary_dark)
    title_x = MARGIN_LEFT + num_width
    title_max_width = CONTENT_WIDTH - num_width
    title_wrapped = wrap_text(title, HEADING_FONT, 13, title_max_width)
    for i, line in enumerate(title_wrapped):
        if i == 0:
            L.c.drawString(title_x, L.y - 13, line)
        else:
            L.y -= 17
            L.c.drawString(MARGIN_LEFT, L.y - 13, line)
    L.y -= 17 + 4

    L.c.setFont(BODY_FONT_ITALIC, 8.5)
    L.c.setFillColor(L.t.soft_grey)
    why_wrapped = wrap_text("Why we ask: " + why, BODY_FONT_ITALIC, 8.5, CONTENT_WIDTH)
    for line in why_wrapped:
        L.c.drawString(MARGIN_LEFT, L.y - 8.5, line)
        L.y -= 11.5
    L.y -= 4

    if bullets:
        for b in bullets:
            L.c.setFont(BODY_FONT_BOLD, 9)
            L.c.setFillColor(L.t.green)
            L.c.drawString(MARGIN_LEFT + 8, L.y - 9, "•")
            L.c.setFont(BODY_FONT, 9)
            L.c.setFillColor(L.t.primary_dark)
            L.c.drawString(MARGIN_LEFT + 18, L.y - 9, b)
            L.y -= 12
        L.y -= 2

    field_h = lines * 16 + 4
    field_y = L.y - field_h
    L.c.acroForm.textfield(
        name=field_name or f"q{num}", tooltip=title,
        x=MARGIN_LEFT, y=field_y, width=CONTENT_WIDTH, height=field_h,
        borderStyle='solid', borderColor=L.t.input_border, borderWidth=0.75,
        fillColor=L.t.input_bg, textColor=L.t.primary_dark,
        forceBorder=True, fontSize=10, fontName=BODY_FONT,
        fieldFlags='multiline'
    )
    L.y = field_y - 14


def build(output_path: Path, kit_slug: str, cycle_name: str, total_pages_hint: int = 4):
    kit = load_brand_kit(kit_slug)
    tokens = BrandTokens(kit)

    c = canvas.Canvas(str(output_path), pagesize=LETTER)
    c.setTitle(f"Strategic Intake — {cycle_name}")
    # Author metadata: still hardcoded for the _default kit. Per-org kits should ship
    # a `_meta.publisher` field in palette.json (or a separate kit-info.yaml) that this
    # script reads. Deferred to the question-content refactor (see module docstring NOTE).
    c.setAuthor("Acme Inc. Compensation")
    c.setSubject("Strategic Intake Form for Wage Review")

    L = Layout(c, kit, tokens)
    L.total_pages = total_pages_hint
    L.draw_header()

    draw_eyebrow(L, "WAGE REVIEW   |   STRATEGIC INTAKE", color=tokens.green)
    L.y -= 4
    draw_title(L, "Your insight, before we run the numbers.", size=24)
    draw_subtitle(L, "Ten questions. Roughly 15–20 minutes. Shapes the analysis we bring back.", size=12)

    draw_metadata_table(L, cycle_name)

    draw_eyebrow(L, "WHY THIS FORM EXISTS", color=tokens.green)
    L.c.setStrokeColor(tokens.line_grey)
    L.c.setLineWidth(0.5)
    L.c.line(MARGIN_LEFT, L.y + 14, PAGE_WIDTH - MARGIN_RIGHT, L.y + 14)
    L.y -= 2

    draw_paragraph(L,
        "Market data tells us what the labour market is paying. It does not tell us what is keeping you up at night, "
        "which roles you cannot afford to lose, or what you have heard about competitors that has not yet shown up in postings.",
        size=10, leading=13)
    L.y -= 4
    draw_paragraph(L,
        "These ten questions capture the strategic context behind the numbers. Your answers shape the scenarios we model, "
        "the trade-offs we surface, and the recommendation we bring back for sign-off.",
        size=10, leading=13)
    L.y -= 4
    draw_paragraph(L,
        "Answer in whatever format works — bullets, full sentences, voice notes you transcribe later. "
        "Skip questions that don't apply. The goal is your honest read, not a polished memo.",
        size=10, leading=13)
    L.y -= 6

    L.c.setFont(BODY_FONT_BOLD, 10)
    L.c.setFillColor(tokens.accent_teal)
    L.c.drawString(MARGIN_LEFT, L.y - 10, "Estimated time:")
    w = pdfmetrics.stringWidth("Estimated time:", BODY_FONT_BOLD, 10)
    L.c.setFont(BODY_FONT, 10)
    L.c.setFillColor(tokens.primary_dark)
    L.c.drawString(MARGIN_LEFT + w + 4, L.y - 10, "15–20 minutes.")
    w2 = pdfmetrics.stringWidth("15–20 minutes.", BODY_FONT, 10) + w + 4 + 16
    L.c.setFont(BODY_FONT_BOLD, 10)
    L.c.setFillColor(tokens.accent_teal)
    L.c.drawString(MARGIN_LEFT + w2, L.y - 10, "Format:")
    w3 = pdfmetrics.stringWidth("Format:", BODY_FONT_BOLD, 10) + w2 + 4
    L.c.setFont(BODY_FONT, 10)
    L.c.setFillColor(tokens.primary_dark)
    L.c.drawString(MARGIN_LEFT + w3, L.y - 10, "click any field below and type, or print and write in.")
    L.y -= 18

    draw_section_header(L, "SECTION 1   |   BUSINESS PRIORITIES & HEADWINDS")
    draw_question(L, 1,
        "What are the two or three operational priorities that will define the next 12 months for your business line?",
        "Compensation has to support the business, not run parallel to it. Knowing your top priorities tells us which roles to weight the analysis toward.",
        lines=4, field_name="q1_priorities")
    draw_question(L, 2,
        "What is the single biggest headwind that could derail those priorities — and is it a labour issue, a cost issue, or both?",
        "Lets us position the wage recommendation as a lever for your real problem, not a stand-alone HR ask.",
        lines=4, field_name="q2_headwind")
    draw_question(L, 3,
        "If we had to hold the wage envelope flat this cycle, what would break first?",
        "Tests the do-nothing scenario from your perspective. The honest answer becomes the risk-first frame in the SVP/CHRO deck.",
        lines=4, field_name="q3_do_nothing")

    draw_section_header(L, "SECTION 2   |   TALENT RISK — TURNOVER, RECRUITMENT, RETENTION")
    draw_question(L, 4,
        "Which two or three roles are you most worried about losing right now? Name the role and the reason.",
        "Turnover data is backward-looking. Your worry list is forward-looking — and usually more accurate.",
        lines=4,
        bullets=[
            "Examples of reasons: pay below market, manager issues, schedule, career path, location-specific",
            "Be specific (e.g., 'meat cutters in BC stores' rather than 'meat department')"
        ],
        field_name="q4_worry_roles")
    draw_question(L, 5,
        "Where are you having the hardest time recruiting — by role, by province, or by store format?",
        "Recruitment difficulty is the leading indicator of where wages are off. Where postings sit unfilled, the market has already moved.",
        lines=4, field_name="q5_recruiting")
    draw_question(L, 6,
        "What have you heard in the last 90 days from store managers, HR business partners, or exit interviews about pay?",
        "Anecdotal signal that doesn't make it into HRIS. Soft intel often surfaces issues 6–12 months before turnover does.",
        lines=4, field_name="q6_soft_intel")
    draw_question(L, 7,
        "Are there any roles where you suspect we are over-paying relative to what the work demands — even if it is uncomfortable to flag?",
        "Wage reviews almost always recommend increases. This question opens the door to the harder conversation about right-sizing.",
        lines=3, field_name="q7_overpay")

    draw_section_header(L, "SECTION 3   |   COMPETITOR INTEL & MARKET SIGNALS")
    draw_question(L, 8,
        "What have you heard, formally or through the grapevine, about what Loblaw, Metro, Walmart, Costco, or Save-On have done on pay in the last six months?",
        "Public market data lags real moves by 3–9 months. Industry chatter is faster.",
        lines=4,
        bullets=[
            "Specific banners welcome (Maxi vs Loblaws, Super C vs Metro, etc.)",
            "Include rumour with a confidence flag (e.g., 'recruiter said, low confidence')"
        ],
        field_name="q8_competitor_moves")
    draw_question(L, 9,
        "Is any competitor actively poaching from us — which one, in which roles, and what are they offering?",
        "Targeted poaching reveals which roles competitors think are most valuable. Helps us prioritize where to lead the market vs match it.",
        lines=4, field_name="q9_poaching")
    draw_question(L, 10,
        "If you could change one thing about how Acme positions on pay relative to competitors, what would it be — and why has it not happened yet?",
        "Surfaces strategic tensions you've been carrying. Often the most useful answer in the form.",
        lines=4, field_name="q10_one_thing")

    L.ensure_space(155)
    L.y -= 8
    L.c.setStrokeColor(tokens.green)
    L.c.setLineWidth(2)
    L.c.line(MARGIN_LEFT, L.y, PAGE_WIDTH - MARGIN_RIGHT, L.y)
    L.y -= 10
    L.c.setFont(BODY_FONT_BOLD, 9)
    L.c.setFillColor(tokens.green)
    L.c.drawString(MARGIN_LEFT, L.y, "ANYTHING ELSE")
    L.y -= 12

    L.c.setFont(HEADING_FONT_REG, 11)
    L.c.setFillColor(tokens.primary_dark)
    L.c.drawString(MARGIN_LEFT, L.y, "Anything we haven't asked that you think we should know before running the analysis?")
    L.y -= 14

    field_h = 3 * 16 + 4
    L.c.acroForm.textfield(
        name="q_anything_else", tooltip="Anything else",
        x=MARGIN_LEFT, y=L.y - field_h, width=CONTENT_WIDTH, height=field_h,
        borderStyle='solid', borderColor=tokens.input_border, borderWidth=0.75,
        fillColor=tokens.input_bg, textColor=tokens.primary_dark,
        forceBorder=True, fontSize=10, fontName=BODY_FONT,
        fieldFlags='multiline'
    )
    L.y -= field_h + 14

    L.c.setFont(BODY_FONT_BOLD, 11)
    L.c.setFillColor(tokens.primary_dark)
    L.c.drawString(MARGIN_LEFT, L.y, "Completed by:")
    L.y -= 16

    name_w = CONTENT_WIDTH * 0.62
    date_w = CONTENT_WIDTH * 0.30
    L.c.acroForm.textfield(
        name="sign_name", tooltip="Your name",
        x=MARGIN_LEFT, y=L.y - 20, width=name_w, height=18,
        borderStyle='solid', borderColor=tokens.input_border, borderWidth=0.75,
        fillColor=tokens.input_bg, textColor=tokens.primary_dark,
        forceBorder=True, fontSize=10, fontName=BODY_FONT
    )
    L.c.acroForm.textfield(
        name="sign_date", tooltip="Date",
        x=MARGIN_LEFT + CONTENT_WIDTH - date_w, y=L.y - 20, width=date_w, height=18,
        borderStyle='solid', borderColor=tokens.input_border, borderWidth=0.75,
        fillColor=tokens.input_bg, textColor=tokens.primary_dark,
        forceBorder=True, fontSize=10, fontName=BODY_FONT
    )
    L.y -= 26
    L.c.setFont(BODY_FONT_ITALIC, 8)
    L.c.setFillColor(tokens.soft_grey)
    L.c.drawString(MARGIN_LEFT, L.y, "Name")
    L.c.drawString(MARGIN_LEFT + CONTENT_WIDTH - date_w, L.y, "Date")
    L.y -= 22

    L.c.setFont(HEADING_FONT_REG, 11)
    L.c.setFillColor(tokens.green)
    text = "Thank you. Your answers shape what we bring back."
    text_w = pdfmetrics.stringWidth(text, HEADING_FONT_REG, 11)
    L.c.drawString((PAGE_WIDTH - text_w) / 2, L.y - 10, text)

    L.draw_footer()
    c.save()
    return output_path, L.page


def main():
    parser = argparse.ArgumentParser(
        description="Build the strategic intake PDF using the active brand kit."
    )
    parser.add_argument(
        "--kit", default="_default",
        help="Active brand kit slug (default: _default). Reads from "
             "template_assets/branding/<kit>/theme/.",
    )
    parser.add_argument(
        "--cycle", default="FY26 Annual Wage Review",
        help='Cycle name shown in the header (default: "FY26 Annual Wage Review").',
    )
    parser.add_argument(
        "--output", default=None,
        help="Output PDF path (default: ./strategic-intake-form.pdf next to script).",
    )
    args = parser.parse_args()

    output = Path(args.output) if args.output else SCRIPT_DIR / "strategic-intake-form.pdf"

    # Two-pass build: first pass counts pages, second pass renders with correct total
    _, page_count = build(output, args.kit, args.cycle, total_pages_hint=4)
    if page_count != 4:
        path, page_count = build(output, args.kit, args.cycle, total_pages_hint=page_count)
    else:
        path = output
    print(f"✓ PDF written ({page_count} pages, kit: '{args.kit}', cycle: '{args.cycle}'): {path}")


if __name__ == "__main__":
    main()
