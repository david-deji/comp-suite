<!--
MIRRORED from: compensation-advisor/references/template-master.md
Canonical owner: compensation-advisor
Sync rule: when canonical changes, copy here. NEVER edit this file in comp-comms-builder.
Last synced: 2026-05-03
-->

# Compensation Deck Template — Reference

This skill regenerates the brand template fresh at Phase 6a from `template_assets/branding/_default/build_template.js` (or per-org override at `template_assets/branding/<org>/build_template.js`). No bundled `.pptx` ships with the skill; the template is rebuilt from the modular masters at runtime. See `references/brand-kit-protocol.md` § Regeneration discipline for the full regen contract.

Every deck this skill produces is generated from this regenerated template's layout system, not from scratch. The modular master files at `template_assets/branding/_default/masters/<NN>-*.js` are the canonical source.

## Why a master template

The earlier template was 10 standalone slides. That meant every deck started by copying slides and overwriting content, and brand drift was easy. The current template instead defines **18 reusable slide masters** via `pres.defineSlideMaster()`, so:

- A colleague opening the `.pptx` in PowerPoint can do **Insert → New Slide → [layout name]** and get a properly-branded blank canvas every time.
- Background, logo placement, footer, layout tag, and chrome live in the master — no per-slide duplication.
- Updating the brand (e.g., the parent company changes) means editing the master block in `build_template.js` once, not eighteen times.
- Visual QA defects from slide-by-slide hand-tuning effectively disappear.

## The 18 layouts

Layouts 1–12 are the core deck spine; layouts 13–18 cover specialist/long-form needs (charts, methodology, multi-province, risks, expanded TOC, ≥8-role positioning).

| # | Master name | Use for | Key elements |
|---|---|---|---|
| 1 | `01_TITLE` | Deck cover | branded left column with the active-kit logo (white variant), deck title, business unit, geo+date, prepared-by line, confidential ribbon. Right column lists 4 scales-in-scope with CODE + role title + Market P50 reference per row. |
| 2 | `02_TOC` | Table of contents — 4 to 6 sections | 3×2 grid of vertically-centered cards, each with green accent bar + deep-purple number badge + title + sub-line + page reference (`→ slide N`). |
| 3 | `03_STAT_CALLOUT` | Headline numbers (e.g., min wage, CPI, unemployment, budget envelope) | 4 large stat columns (56pt), each in a different palette colour with bold label, YoY delta tag, and source/context note. |
| 4 | `04_SECTION_DIVIDER` | Between major sections | Full-bleed primary brand colour; SECTION 0X label, white horizontal rule, large title, one-line description, "0X / 06" pagination indicator bottom-right. |
| 5 | `05_TWO_COLUMN` | Competitor watch / option A vs B / before vs after | Side-by-side panels with bullets and a coloured flag callout (red ⚠ / teal ✓). |
| 6 | `06_MARKET_POSITIONING` | Roll-up market positioning — **≤7 roles** | Multi-row table with internal pay vs market reference vs compa-ratio. Compa cells colour-coded by threshold. Legend and source footnote. For ≥8 roles use Layout 17. |
| 7 | `07_MARKET_ANALYSIS` | Per-role analysis | Left-side narrative with 4 finding sub-headers. Right-side reference market range banner + competitiveness ratio band + per-source percentile table. |
| 8 | `08_WAGE_SCALE_PROPOSAL` | Step grid proposals | Left: experience-range step grid with Current vs Option #1 vs Option #2. Right: reference market range banner + 3-stat market context strip (StatCan P50 / CBA Median / Postings P50) + proposal notes. |
| 9 | `09_COST_ANALYSIS` | Cost rollup | "By the numbers" 3-stat strip (Total cost / % of payroll / Teammates affected) + summary bullets + annual increase budget callout. Cost table by employee group with subtotal. Full-width green TOTAL ANNUAL COST band. |
| 10 | `10_NEXT_STEPS` | Implementation timeline | Action / Owner / Target Date table; full-width green decision-ask band at bottom. |
| 11 | `11_CLOSING_DECISION` | Final decision ask slide | Centred active-kit logo, large decision-ask headline, three next-action bullets, contact info. Tightened vertical rhythm. |
| 12 | `12_BLANK_FLEX` | Anything ad hoc | Branded chrome only; body left wide open for custom content. |
| 13 | `13_CHART` | Chart-driven slides | Large left-side chart frame + right-side **KEY TAKEAWAY** callout box (deep purple) with headline finding + supporting bullets. Source footnote at bottom-left. The chart itself is added per-deck via `pptxgenjs` `addChart()` or as drawn shapes. |
| 14 | `14_METHODOLOGY` | Methodology / appendix | 3 columns with deep-purple header bands: SOURCES / INCLUSIONS / EXCLUSIONS. "Last updated · Author" audit line bottom-right. |
| 15 | `15_MULTI_PROVINCE` | Multi-province compare | Compa-ratio heatmap with roles on rows × provinces on columns. Cells colour-coded (red <95% / purple 95–105% / teal >105%). Default 5 roles × 3 provinces; expandable. |
| 16 | `16_RISKS_ALTERNATIVES` | Rejected options / risk audit | 3-column table: CONSIDERED OPTION (bold) / RISK (red) / MITIGATION. Default 4 rows. |
| 17 | `17_MARKET_POSITIONING_LONG` | Roll-up market positioning — **8 to 15 roles** | Same DNA as Layout 6 but at 9pt for higher density. Use when role count > 7. |
| 18 | `18_TOC_EXPANDED` | Table of contents — **7 to 9 sections** | 3×3 grid for decks with multi-banner or multi-province scope (e.g., multi-banner banner-by-banner analyses). |

### When to pick which variant

- **TOC:** Layout 2 for 4–6 sections; Layout 18 for 7–9.
- **Market positioning:** Layout 6 for ≤7 roles; Layout 17 for 8–15. For >15 roles, split across two slides.
- **Charts:** Layout 13 is the home for any chart. Don't chart-jam into Layout 12 (blank/flex).
- **Audit defense:** every deck that touches a CHRO / VP-level audience should include Layout 14 (methodology) and, when options were considered and rejected, Layout 16 (risks & alternatives).

## Brand application

The template applies all rules from the active brand kit. When no per-org override is present, the active kit is `_default` and rules come from `brand-guidelines.md`; when an engagement-config sets `deck.brand: <org-slug>` and a kit exists at `template_assets/branding/<org-slug>/`, the per-org kit's theme JSONs and any overridden masters take precedence (full mechanism: `references/brand-kit-protocol.md`).

The callouts below describe the **`_default` kit** (neutral placeholder) — per-org kits substitute their own logo/palette/typography:

- **`_default` kit logo: neutral placeholder wordmark** (replace with your own brand mark). Appears top-right on content slides, prominently centred on the title and closing slides. White-recoloured variants are used on green/dark backgrounds. Per-org kits ship their own logo set under `branding/<org-slug>/theme/logo*.png`.
- **`_default` kit palette** — Primary Green `#4AA447`, Off-white `#FAF8F7`, Deep Purple `#3C1E54`, Teal `#149390`, Vibrant Purple `#793CD6`, plus the muted red `#B53A3A` for below-market signaling. Per-org kits override via `branding/<org-slug>/theme/palette.json` (deep-merged over `_default`).
- **Typography:** Noto Serif for headings, Lexend Deca for body. Already wired into the template.
- **Layout tags** ("LAYOUT 7 · MARKET ANALYSIS — PER ROLE") appear in light grey across the top of content slides. They are gated by a build-time constant `INCLUDE_LAYOUT_TAGS` at the top of `build_template.js` — set to `true` for the orientation/template file, set to `false` for any deck shipped to a real audience. See "Stripping layout tags" below.
- **Footer** is simplified to `CONFIDENTIAL · [MONTH YEAR]` (no middle section label). The layout tag at top carries section context when on; on production decks the slide title carries it.

## How to use the template in skill workflow

### When producing a deck (Phase 6)

1. Read `template_assets/branding/_default/build_template.js` (entry point) and the master files in `template_assets/branding/_default/masters/` to understand the layout system.
2. Copy the brand tokens (resolved via `theme/palette.json` + `theme/typography.json`), the master definitions, and the helper functions from `masters/_helpers.js` (`cornerLogo`, `makeLayoutTag`, `makeFooter`, `addTitleSubtitle`) into the deck-specific build script.
3. For each slide in the deck, do `pres.addSlide({ masterName: "0X_..." })` and then add only the slide's content — never re-define the chrome.
4. Use the demo-slide patterns from `build_template.js` as starting points for content blocks (TOC card grid, stat callouts, two-column comparison flags, market analysis right panel, etc.).
5. Logo PNGs must be available in the build directory at the same relative paths used in the template (`theme/logo_*.png`). Either copy them from `template_assets/branding/_default/theme/` (or the active per-org override path) into the deck's working directory, or update the paths in the master definitions to point at `/mnt/skills/user/compensation-advisor/template_assets/branding/_default/theme/`.

### When the colleague opens the .pptx directly

The colleague can open the regenerated template (default name `default_Comp_Deck_Template.pptx`, or `<org>_Comp_Deck_Template.pptx` when the `ORG` env var is set at regen time) in PowerPoint, do **File → Save As** under a new name, and then either:

- Edit the existing demo slides in place (replace `[Deck Title]`, `[CODE]`, etc.), or
- Insert new slides by clicking **New Slide → [pick a layout]** in the Home ribbon. The 12 layouts will appear in the dropdown.

### Stripping layout tags before final delivery

The "LAYOUT 7 · ..." breadcrumbs are intentional during template orientation but distracting on a CHRO-facing deck. Two options:

1. **Build-time toggle (preferred)** — open `template_assets/branding/_default/build_template.js` and change the constant at the top:
   ```js
   const INCLUDE_LAYOUT_TAGS = false;  // was true
   ```
   Then re-run `node build_template.js` from the `branding/_default/` directory. The `masterObjects(...)` helper in `masters/_helpers.js` drops the layout-tag text frame from every master automatically. This is the cleanest fix because it works at the master level — every slide using that master loses the tag in one shot.
2. **In PowerPoint** — open the master view (View → Slide Master), find each layout, and delete the layout-tag text frame. Same effect, no rebuild. Useful when the colleague is editing in PowerPoint and doesn't want to rerun the script.

For internal HR-facing reviews the breadcrumbs are fine to leave on. For board / external decks, strip them.

## Regenerating the template

If the template needs to be modified (palette change, new layout, logo swap), edit the relevant file in `template_assets/branding/_default/` and re-run:

```bash
cd /mnt/skills/user/compensation-advisor/template_assets/branding/_default
node build_template.js
```

The script writes `default_Comp_Deck_Template.pptx` (or `<ORG>_Comp_Deck_Template.pptx` when the `ORG` env var is set) into the current directory. The output is a fresh artifact — there is no bundled `.pptx` to overwrite.

For per-org overrides (e.g., a client-specific brand kit), see `references/brand-kit-protocol.md` § Override granularity. The override mechanism deep-merges theme JSONs and accepts per-file master replacements.

Dependencies: `pptxgenjs` (npm), `cairosvg` (pip — only needed if regenerating logo PNGs from the SVG).

## Asset inventory

The default brand kit lives in `template_assets/branding/_default/` and follows the modular structure introduced in Batch E. Per-org overrides slot in at `template_assets/branding/<org>/` and inherit from `_default` via deep-merge. See `references/brand-kit-protocol.md` for the full structure spec.

```
template_assets/branding/_default/
├── build_template.js                 Entry point — theme resolution, master loop, ORG env override
├── footnotes.yaml                    Per-jurisdiction disclaimers
├── theme/
│   ├── palette.json                  color tokens (Primary Green, Off-white, Deep Purple, etc.)
│   ├── typography.json               Fonts + size scales (Noto Serif headings, Lexend Deca body)
│   ├── logo.svg                      Neutral placeholder wordmark
│   ├── logo_large.png                600×161 — for title/closing slides
│   ├── logo_small.png                300×81  — for content-slide top-right corner
│   ├── logo_white_large.png          White recolour — for green/dark backgrounds, large
│   └── logo_white_small.png          White recolour — for green/dark backgrounds, small
└── masters/
    ├── _helpers.js                   Shared factories (cornerLogo, makeLayoutTag, makeFooter, addTitleSubtitle)
    ├── 01-title.js                   Layout 1 — TITLE
    ├── 02-toc.js                     Layout 2 — TOC (4-6 sections)
    ├── 03-stat-callout.js            Layout 3 — STAT_CALLOUT
    ├── 04-section-divider.js         Layout 4 — SECTION_DIVIDER
    ├── 05-two-column-comparison.js   Layout 5 — TWO_COLUMN
    ├── 06-market-positioning-table.js  Layout 6 — MARKET_POSITIONING (≤7 roles)
    ├── 07-market-analysis-per-role.js  Layout 7 — MARKET_ANALYSIS
    ├── 08-wage-scale-proposal.js     Layout 8 — WAGE_SCALE_PROPOSAL
    ├── 09-cost-analysis.js           Layout 9 — COST_ANALYSIS
    ├── 10-next-steps.js              Layout 10 — NEXT_STEPS
    ├── 11-closing-decision-ask.js    Layout 11 — CLOSING_DECISION
    ├── 12-blank-flex.js              Layout 12 — BLANK_FLEX
    ├── 13-chart-slide-new.js         Layout 13 — CHART
    ├── 14-methodology-new.js         Layout 14 — METHODOLOGY
    ├── 15-multi-province-compare-new.js  Layout 15 — MULTI_PROVINCE
    ├── 16-risks-alternatives-new.js  Layout 16 — RISKS_ALTERNATIVES
    ├── 17-market-positioning-long-new.js  Layout 17 — MARKET_POSITIONING_LONG (8-15 roles)
    └── 18-toc-expanded-new.js        Layout 18 — TOC_EXPANDED (7-9 sections)
```

The regenerated `.pptx` is written into the build directory at runtime as `default_Comp_Deck_Template.pptx` (or `<ORG>_Comp_Deck_Template.pptx` when `ORG` env var is set). It is not a checked-in asset.

## Known limitations

- pptxgenjs's `placeholder.text` default-text feature does not render reliably in LibreOffice and inconsistently in PowerPoint. The template instead adds explicit demo text on each slide. When generating real decks, never rely on placeholder defaults — always add the slide's text explicitly.
- The template uses Noto Serif and Lexend Deca. On locked-down corporate machines without these fonts, PowerPoint will substitute. The substitutes are tolerable but the brand feel suffers — flag this to the colleague if they're delivering on a sensitive audience.
- Layout 11 (closing/decision ask) and Layout 4 (section divider) use the master `objects` block to position the heading/badge/footer chrome but rely on the build script to add the actual title/subtitle text. This is by design — different decks need different decision-ask wording, and the section-divider title is always slide-specific.
