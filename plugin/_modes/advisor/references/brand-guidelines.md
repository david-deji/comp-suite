# Default Brand Kit (`_default`) — Seed Content for Compensation Decks

This document is the **seed content for the `_default` brand kit** that ships in the bundle at `template_assets/branding/_default/`. It defines the visual, photographic, and tonal rules every compensation deliverable inherits when no per-organization override is present.

The bundled `_default` kit is a **neutral placeholder**: a generic wordmark, a neutral palette, and the structural design rules below. It is meant to be replaced — every organization using this skill should create a per-organization brand kit at `template_assets/branding/<org-slug>/` (per `references/brand-kit-protocol.md`), at which point the per-org files override the matching `_default` files via deep-merge for theme JSONs and full-file replacement for masters/logos. Read this document to understand what the bundled `_default` kit provides and which rules survive a per-org override; read `references/brand-kit-protocol.md` to understand the override mechanism; read `references/library-resolution.md` for the broader resolution rules between repo files and bundled fallbacks.

**What's brand-specific vs. structural.** The *visual specifics* below (palette hex, logo, font choices) are placeholders that a per-org kit replaces. The *structural rules* (chart colour semantics, the 60-30-10 dominance rule, "no stock people imagery", open-space minimums, one-message-per-slide, voice register) are calibrated for the **compensation context**, not for any one brand, and apply across kits unless a per-org `voice-and-design-rules.md` explicitly overrides a specific item.

**Template reference.** All compensation decks are built from the regenerated brand template at Phase 6a — entry point `template_assets/branding/_default/build_template.js`, modular masters at `template_assets/branding/_default/masters/<NN>-*.js`. There is no bundled binary `.pptx`. See `references/template-master.md` for the full layout inventory + usage guide and `references/brand-kit-protocol.md` for the regeneration contract — including how a per-org kit declares which masters and theme JSONs to override.

## Governance

This document governs compensation deliverables produced by the skill **in its `_default` kit configuration** — i.e., when no per-org override is present in `template_assets/branding/<org-slug>/`. Visual rules (colour, typography, logo, photography, iconography) reflect the neutral default palette/typography; voice, tone, and narrative framing reflect a generic professional comp-deck register.

**Per-org override precedence**: when an engagement-config sets `deck.brand: <org-slug>` and a kit exists at `template_assets/branding/<org-slug>/`, the per-org kit's theme JSONs (palette, typography, footnotes) and any overridden masters take precedence over this document's defaults. The per-org kit may also ship its own `voice-and-design-rules.md` (or equivalent) that overrides this file's voice/tone/narrative-framing sections. See `references/brand-kit-protocol.md` § Per-org override mechanism.

**When this document still governs even with a per-org kit present**: chart semantic rules (colour-coding by data meaning), open-space rule (≥0.5" margins, ≤70% fill), one-message-per-slide rule, "no stock people photography" rule, and the compliance checklist's structural items (logo present on title/content/closing, single-colour icons paired with text). These are calibrated for the **comp context** (chart semantics, decision-ask framing, audience register) and apply across kits unless a per-org `voice-and-design-rules.md` explicitly overrides a specific item.

Where rules below appear to conflict with any external brand reference a user surfaces, **the rules in this document govern** for compensation decks produced by this skill in `_default` kit mode — surface the conflict to the user and proceed with this spec unless they direct otherwise. With a per-org kit active, follow the per-org kit's rules; surface conflicts the same way.

## Default vs. per-org override

**Default behaviour (`_default` kit, no override present):** Apply the neutral default branding (generic wordmark + neutral palette and typography) to every compensation deliverable. This is the starting assumption for all tracks (R-lite, R, D, C) when no per-org kit is loaded. The default brand kit at `template_assets/branding/_default/` is the canonical starting point — Phase 6a regenerates the template fresh from those masters.

**Per-org override path:** When an engagement-config sets `deck.brand: <org-slug>` and a kit exists at `template_assets/branding/<org-slug>/`, the per-org kit's theme JSONs and masters take precedence per `references/brand-kit-protocol.md`. The per-org kit may also ship its own copy of this document (e.g., `template_assets/branding/<org-slug>/voice-and-design-rules.md`) that overrides voice/tone/narrative framing.

**External-audience override (still within `_default` kit):** For external-audience decks (board members who are outside the host org, potential acquirers, external consultants, regulators, arbitrators in labour disputes), a neutral palette may be preferable. Claude must surface the choice during Phase 1 (Discovery) or Phase 5 (Narrative Workshop), not silently deviate:

> "This is for [external audience]. Usually I apply [host-org] branding, but for external audiences a neutral palette can read as more objective. Want [host-org]-branded or neutral?"

If the user confirms neutral, fall back to the pptx skill's "Midnight Executive" palette and note the deviation in the deck's speaker notes or a hidden metadata slide. Do not strip the host-org logo from the title slide unless the user explicitly requests it — even neutral-palette decks identify the authoring organization.

Internal audiences (CHRO, VP HR, HR ops, comp team, Canadian leadership, banner-level leadership, union bargaining team, employees) always get the active brand kit (default or per-org).

---

## Colour palette

The hex values below are the **neutral default** palette (`theme/palette.json`). A per-org kit replaces them with its own; the colour *roles* and the chart-semantic mapping carry across kits.

### Primary palette (pptx skill format)

| Role | Name | Hex | RGB | Usage |
|---|---|---|---|---|
| **Primary** | Primary Green | `#4AA447` | `74, 164, 71` | Title slide background, section dividers, hero colour-blocks, primary chart series, decision-ask slide background |
| **Secondary** | Off-white | `#FAF8F7` | `250, 248, 247` | Content slide backgrounds, table backgrounds, large-area backdrops |
| **Accent 1** | Primary Dark | `#4B2E83` | `75, 46, 131` | Headline type on light backgrounds, strong text emphasis, contrast callouts |
| **Accent 2** | Accent Teal | `#2A8C82` | `42, 140, 130` | Secondary chart series, positive-delta callouts (YoY gains, above-market positioning) |
| **Accent 3** | Vibrant Purple | `#793CD6` | `121, 60, 214` | Tertiary chart series, highlights, call-to-action elements |

### Dominance rule (from pptx skill)

One colour dominates at 60-70% visual weight. For compensation decks, that dominant colour is **either Primary Green** (hero/divider slides) **or Off-white** (data-heavy content slides). Never give all five colours equal weight on a single slide.

### Chart colour mapping

Compensation decks lean heavily on bar charts, gap analyses, and waterfall charts. Apply colours by data meaning, not by aesthetic rotation:

| Data meaning | Colour |
|---|---|
| Internal pay (our org) | Primary Green `#4AA447` |
| Market P50 (primary benchmark) | Primary Dark `#4B2E83` |
| Market P25 / P75 (range bounds) | Accent Teal `#2A8C82` (P25) and Vibrant Purple `#793CD6` (P75) |
| Positive delta / above-market / YoY gain | Accent Teal `#2A8C82` |
| Negative delta / below-market / YoY loss | A muted red for comp-specific use: `#B53A3A`. Not a core palette colour, but necessary for gap signaling. Use sparingly and only when red/green semantic signaling is required. |
| Neutral / at-market | Off-white `#FAF8F7` with `#4B2E83` border |
| Do-nothing baseline | Solid Primary Dark `#4B2E83` |
| Scenario options | Rotating Accent Teal → Vibrant Purple → Primary Green |

### Chart slide pattern (Layout 13)

Layout 13 (defined in `template_assets/branding/_default/masters/13-chart-slide-new.js`) is the home for any chart in a comp deck. Its standard composition:

- **Left ~65% of the slide** — the chart frame (8.5" wide × 4" tall). The chart itself is added per-deck via pptxgenjs `addChart()` or as drawn shapes. Use the chart-colour-mapping table above; do not switch palettes for visual variety.
- **Right ~30%** — a Primary-Dark **KEY TAKEAWAY** callout box with:
  - One-sentence headline finding (Noto Serif, 17pt, white)
  - 2-3 supporting bullets (Lexend Deca, 11pt, white)
- **Bottom-left** — a one-line source footnote (`Source: [Survey + year] · [Geo] · n=[N] · …`).

Why this composition: the chart does the data work; the takeaway box does the persuasion work. Without an explicit takeaway, audiences read charts however they want. With one, the slide commits to a finding the speaker can defend.

For waterfall charts (cost build-up): use Primary Green for the positive bars (additions to cost), muted red `#B53A3A` for the negatives (offsets / savings), Primary Dark for the start/end totals.

For range/distribution charts (compa-ratio bars): use red for <95%, Primary Dark for 95–105%, Accent Teal for >105% — same semantic rotation as the colour-coded compa cells in Layouts 6, 15, and 17.

### What not to do

- Do not put text directly on Primary Green body copy (white or off-white type only on green).
- Do not introduce palette colours from outside the active kit's `theme/palette.json` (no "I'll just add a gold for callouts").
- Do not hardcode hex values in master JS — always read from the palette `C` lookup so per-org overrides work.

---

## Typography

### Font system

| Role | Font | Notes |
|---|---|---|
| **Headings** | Noto Serif | Titles, slide headers, section dividers, large-stat callouts. Never body copy. |
| **Body** | Lexend Deca | All body text, bullet copy, table cells, chart labels, footnotes, captions. |

Both fonts are free and available via Google Fonts. pptxgenjs accepts them by name. A per-org kit overrides them via `theme/typography.json`.

### Fallback

If Noto Serif or Lexend Deca is unavailable in the target rendering environment (some locked-down corporate machines), fall back in this order:

1. Noto Serif → Georgia → Times New Roman (serif fallback)
2. Lexend Deca → Segoe UI → Arial (sans fallback)

The Arial fallback rule applies only when the brand fonts literally cannot render.

### Size hierarchy (compensation deck defaults)

| Element | Font | Size | Weight |
|---|---|---|---|
| Title slide title | Noto Serif | 44pt | Regular |
| Slide title | Noto Serif | 28pt | Regular |
| Section divider | Noto Serif | 36pt | Regular |
| Large stat callout | Noto Serif | 60-72pt | Regular |
| Body copy | Lexend Deca | 14pt | Regular |
| Table cells | Lexend Deca | 11pt | Regular |
| Table headers | Lexend Deca | 12pt | Bold |
| Chart labels | Lexend Deca | 10pt | Regular |
| Footnotes / source citations | Lexend Deca | 9pt | Regular |
| Decision ask | Noto Serif | 32pt | Regular |

---

## Logo usage

The `_default` kit ships a **neutral placeholder wordmark** (`theme/logo.svg` + four PNG variants). A per-org kit replaces all five with its own logo set. The skill ships four PNG variants under `template_assets/`:

| File | Size | When to use |
|---|---|---|
| `branding/_default/theme/logo-large.png` | 600 × 161 px | Title slide, closing/decision-ask slide, anywhere the logo is a hero element |
| `branding/_default/theme/logo-small.png` | 300 × 81 px | Top-right corner of every content slide (renders ~1.55" wide × 0.42" tall on a 13.3"-wide widescreen layout) |
| `branding/_default/theme/logo-white-large.png` | 600 × 161 px | Hero placement on dark/green backgrounds (title slide green column, section dividers if logo is hero) |
| `branding/_default/theme/logo-white-small.png` | 300 × 81 px | Top-right corner on dark/green backgrounds (Primary Green section dividers) |

The placeholder SVG (`branding/_default/theme/logo.svg`) is also bundled for vector-based regeneration. All paths are under `template_assets/`. Per-org overrides slot in at `template_assets/branding/<org>/theme/` — full-file replacement for binaries (no merge).

### Placement

- **Title slide:** White wordmark (secondary version) top-left of the green column, ~1.95" wide. Clear space ≥ ~0.5" on all sides.
- **Content slides:** Dark wordmark (primary version) top-right corner, ~1.55" wide × 0.42" tall, with ~0.30" of clear space from the right edge.
- **Section divider slides (full Primary Green):** White wordmark top-right corner, same dimensions as content slides.
- **Closing / decision-ask slide:** Dark wordmark, centred horizontally near the top of the slide, larger scale (~2.5" wide).

### Primary vs. secondary

| Version | When to use |
|---|---|
| Primary (dark) | Default. All slides with off-white or light backgrounds. Files: `logo-large.png`, `logo-small.png` |
| Secondary (white recolour) | Any slide with a Primary Green or Primary Dark background. Files: `logo-white-large.png`, `logo-white-small.png` |

Per-org kits override these by shipping their own `theme/logo*.png` set in `template_assets/branding/<org-slug>/theme/` — full-file replacement for binaries (no merge).

### Clear space

Minimum clear space around the logo = roughly the cap-height of the wordmark. Do not crop, rotate, recolour beyond the white-recolour variant, or apply effects (drop shadows, glows, etc.). Do not place the logo on busy imagery or photographs.

### Co-branding (rare in comp decks)

If a survey provider (Mercer, Radford, WTW, Aon) or market data source needs to be credited visually, place their logo in the footer of the source-citation slide at secondary prominence. The host-org branding always dominates. Partner logos never appear on the title slide.

---

## Photography & iconography

### Photography in compensation decks

Compensation decks generally should not contain stock people photography. This is a structural rule (the comp context) and applies across kits — a per-org kit may name its own equivalent in `voice-and-design-rules.md`, but the rule itself ("no stock people imagery; use real org imagery the user provides, or typographic hero treatments") survives any per-org override:

- **Do not** generate, web-search, or insert stock photos of people, hands shaking, generic office scenes, piles of money, or "business meeting" imagery.
- **Do not** insert illustrative human imagery to "warm up" a data-heavy deck. Data-heavy decks are fine without it.
- **Do** accept and use imagery the user uploads (real teammates of the active host org, real workplace contexts — a per-org kit's `voice-and-design-rules.md` names the equivalent).
- **Do** use a single brand-coloured hero block (default kit: Primary Green) with typography as the hero element on the title slide instead of an image. A per-org kit substitutes its own narrative anchor for the typographic hero treatment.

If the user explicitly requests people imagery and has not provided any, flag it:

> "Brand guidelines require real [active-org] teammates in context rather than stock photography. Do you have imagery you'd like to provide, or should we use typographic hero slides instead?"

(Substitute the active host-org name when speaking to the user.)

### Iconography

Icons are welcome in comp decks (they clarify categories, reinforce structure, add visual pacing). Rules:

- **Always paired with text.** An icon never carries meaning alone.
- **Single colour per icon.** That colour should come from the palette — typically Primary Dark `#4B2E83` on light backgrounds or Off-white on green backgrounds.
- **Equal prominence with the accompanying text** — not decorative tiny icons, not dominating huge icons.
- **Simple and recognizable at a glance** — prefer line or filled silhouettes from a cohesive icon set (Lucide, Heroicons, Phosphor are all fine). Mixing icon styles across a deck is a brand violation.
- **Semantic, not decorative.** A chart icon next to a "methodology" header = fine. A random pie icon on an unrelated slide = drop it.

### Icon mapping for comp decks

| Category | Suggested icon concept |
|---|---|
| Market benchmarking | bar chart, scales |
| Pay equity | balance scale, equals sign |
| Merit matrix | grid |
| Cost scenarios | dollar sign, calculator |
| Scope / roles | people silhouette (single figure, not a crowd) |
| Timeline / implementation | arrow, calendar |
| Decision / recommendation | check mark, pointer |
| Risk / attrition | warning triangle |

---

## Open space

Every slide must leave generous open space. Specifically:

- Minimum margin: 0.5 inch on all edges.
- Never fill more than ~70% of a slide with content (text + charts + imagery combined).
- One key message per slide. If a slide is trying to say two things, it is two slides.
- Do not cluster bullet points into dense blocks. Lexend Deca at 14pt with 1.4 line spacing or looser.

"Ensure your layouts include plenty of open space so it's inviting to read."

---

## Voice and tone

### Core tone

- **Direct, personable, jargon-light.** Compensation has its own technical vocabulary (compa-ratio, P50, geo-differential) — use it accurately, but translate for non-comp audiences. Board decks: minimize jargon. HR ops decks: full technical register is fine.
- **Address the reader.** Headlines speak to the audience ("Your [classification] top rate sits below market P50"), not in third-person abstract ("Analysis of top rate positioning").
- **Values-connected when appropriate.** The host org's narrative or values can appear on framing slides or closing slides for internal-audience decks. Do not force it onto every slide.
- **Sincere, not selling.** Internal comms voice: more straightforward, not selling, sincere.
- **Do not sacrifice clarity for cleverness.** No puns on slide titles. No "Payday!" style flourishes.

### Employer Brand Promises as framing (per-org)

For strategic decks (compensation strategy, pay equity, total rewards), anchoring the argument in a small set of named Employer Brand Promises (EBPs) is an effective structural pattern: pick 2-3 promise themes (e.g., a great place to work / growth opportunities / work that fits my life) and frame retention, pay-progression, and flexibility arguments under them. Use sparingly — one or two references per deck, not on every slide.

The `_default` kit ships **no** specific EBP names (it is brand-neutral). A per-org kit supplies its own EBP framing in its `voice-and-design-rules.md`. The structural pattern (a small set of named brand promises that anchor strategic decks, used sparingly) carries across kits; the specific promise names are per-org.

### What to avoid

- Informal "Team [Org]" / "The [Org] Family" labels in formal compensation deliverables — use the formal legal entity name.
- Corporate-speak fillers: "leverage," "synergies," "best-in-class" — cut them.
- Passive voice on recommendations: "It is recommended that..." → "We recommend..."
- Vague cost framing: "significant investment" → actual dollar figures.

---

## Slide-by-slide application guide

### Title slide

- Background: Primary Green `#4AA447` left column (40% width) + Off-white right column (60% width). Wordmark (white variant) top-left of the green column.
- Title: Noto Serif on the green side, white or off-white type, left-aligned, 44pt.
- Subtitle: Lexend Deca, same side, 16pt.
- Date and audience: Lexend Deca 12pt, lower portion of the green column.
- Right column: "SCALES IN SCOPE" header (Lexend Deca 11pt bold tracked, Primary Dark) followed by the in-scope role list with green accent bars per row.

### Executive summary / decision ask

- Large Noto Serif headline stating the recommendation directly.
- Three to five Lexend Deca bullets underneath, each starting with a verb.
- Dollar figure (do-nothing cost or chosen scenario cost) as a 60pt Noto Serif callout in Primary Dark `#4B2E83` on Off-white.

### Data slides (benchmarking, gap analysis, cost)

- Off-white `#FAF8F7` background.
- Slide title: Noto Serif 28pt, Primary Dark `#4B2E83`, top-left.
- Charts: use the chart colour mapping table above.
- Tables: Lexend Deca, alternating row shading with `#FAF8F7` and pure white, 1pt border in `#4B2E83` for headers only.
- Source footnote: Lexend Deca 9pt, bottom-left, e.g. "Source: Statistics Canada, Table 14-10-0064-01, 2024. Geo: Quebec. Percentile: P50."
- Payroll tax caveat (where applicable) as a separate footnote, Lexend Deca 9pt.

### Section dividers

- Full Primary Green `#4AA447` background.
- Noto Serif 36pt white type, centred or left-aligned.
- Section number in small off-white Lexend Deca above the title.

### Scenario comparison slide

- Split-column layout, 2 or 3 columns.
- Each scenario labelled in Noto Serif 24pt.
- Cost figures as Lexend Deca 36pt bold.
- "Recommended" scenario gets a Primary Dark `#4B2E83` border or background tint.

### Closing / decision ask

- Wordmark (primary, dark), centred near the top of the slide, ~2.5" wide.
- "DECISION ASK" eyebrow label in Lexend Deca 12pt bold tracked, Primary Dark, centred.
- Noto Serif 32pt decision ask in Primary Dark `#4B2E83`, centred.
- Three next-action bullets in Lexend Deca 14pt below the decision ask.
- Author / contact line in Lexend Deca 11pt italic at the bottom.

---

## Compliance checklist

Before delivery, verify every item against the **active brand kit** (the `_default` kit unless an engagement-config sets `deck.brand: <org-slug>` and a per-org kit exists at `template_assets/branding/<org-slug>/`):

**Kit-specific items** (substitute per-org values when a kit overrides — the `_default` kit values are listed in parentheses):

- [ ] Colour palette strictly matches the active kit's `theme/palette.json`; no out-of-palette colours introduced (`_default` kit: the 5-colour neutral palette + `#B53A3A` muted red for negative deltas).
- [ ] Primary brand colour is the active kit's primary (`_default` kit: Primary Green `#4AA447`).
- [ ] Heading + body fonts match the active kit's `theme/typography.json` (`_default` kit: Noto Serif headings only, Lexend Deca body).
- [ ] Active kit's wordmark logo present on title slide, content slides (top-right), and closing slide (`_default` kit: the placeholder wordmark from `branding/_default/theme/logo*.png`).
- [ ] Logo uses correct variant (primary on light, secondary on dark — both kits ship `logo-*.png` and `logo-white-*.png`).

**Structural items** (apply across kits — comp-context rules):

- [ ] No stock people photography; only real org imagery the user provided, or typographic hero treatments.
- [ ] Icons single-colour, paired with text, consistent style across deck.
- [ ] Every slide has ≥ 0.5 inch margins and open space (≤70% fill).
- [ ] One key message per slide.
- [ ] Voice is direct and jargon-calibrated to audience.
- [ ] If neutral palette was used (external-audience override), deviation is documented and user confirmed.
- [ ] If a per-org kit was active, the per-org kit's `voice-and-design-rules.md` (if present) was applied alongside this document, with per-org rules taking precedence per `references/brand-kit-protocol.md`.
