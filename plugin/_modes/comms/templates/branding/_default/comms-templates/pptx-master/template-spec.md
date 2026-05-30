# PPTX Master — Exec One-Pager Template Spec

> Version: 1  
> Artifact: `exec-one-pager`  
> Channel: `pptx_distributable`  
> Audience: `exec_board`  
> Speaker: CHRO  
> Slide cap: 1-3 slides  
> Language: EN primary (FR-CA variant on request)  

This spec describes the 1-3 slide exec one-pager template. The runtime renderer reads this file to drive pptxgenjs slide construction. This is NOT a binary file.

Org-specific overrides: copy to `branding/<org-slug>/comms-templates/pptx-master/template-spec.md` and update the values under each slide definition.

---

## Master Layout Defaults

```yaml
slide_size:
  width_in: 13.33
  height_in: 7.5
  # Standard widescreen 16:9 (matches compensation-advisor PPTX master)

base_font_family: "Calibri"
# Replace with org font after /brand init

colors:
  primary: "#003087"       # Replace with org primary brand color hex
  secondary: "#F2A900"     # Replace with org secondary brand color hex
  background: "#FFFFFF"
  body_text: "#1A1A1A"
  muted_text: "#6B6B6B"
  table_header_bg: "#003087"
  table_header_text: "#FFFFFF"
  table_row_alt_bg: "#F5F7FA"

logo:
  path: "branding/<org-slug>/logo.png"
  # Falls back to empty if file not found
  position: top-right
  height_in: 0.5
  top_in: 0.2
  right_in: 0.3
```

---

## Slide 1 — Decision Summary (Required)

Purpose: Board or exec committee sees the decision, the rationale, and the ask in 30 seconds.

### Regions

| Region | Position (top/left/width/height in inches) | Content |
|---|---|---|
| Title bar (colored band) | top: 0, left: 0, width: 13.33, height: 1.2 | Background = `colors.primary` |
| Headline | top: 0.2, left: 0.4, width: 10.5, height: 0.8 | Decision headline. Font: 28pt bold, white. Max 90 chars. |
| Subtitle / cycle label | top: 0.9, left: 0.4, width: 10.5, height: 0.35 | Cycle name + effective date. Font: 14pt, white, muted. |
| Logo | top: 0.2, right: 0.3, height: 0.5 | Org logo (top-right corner of title bar) |
| Body — Rationale bullets | top: 1.4, left: 0.5, width: 7.5, height: 4.5 | 3-5 bullets. Font: 18pt body. Bullet char: dash. Line spacing: 1.3. |
| Body — Key metric box | top: 1.4, left: 8.3, width: 4.5, height: 2.2 | Highlighted box (background: `colors.secondary`, border-radius: 4pt). Contains: metric label (12pt bold) + metric value (28pt bold) + sub-label (10pt muted). Use for annualized cost impact. |
| Ask / governance note | top: 6.1, left: 0.5, width: 12.3, height: 0.7 | Single sentence: the ask of the board. Font: 13pt italic. Color: `colors.muted_text`. Prefix with "Board ask:" or "Note pour information:" |
| Footnote bar | top: 7.1, left: 0, width: 13.33, height: 0.4 | Background: `colors.table_header_bg` at 20% opacity. Font: 10pt, muted. Contains: source reference + confidentiality notice. |

### Typography for Slide 1

```yaml
headline_font_size_pt: 28
headline_font_bold: true
headline_font_color: "#FFFFFF"
headline_max_chars: 90

subtitle_font_size_pt: 14
subtitle_font_color: "#E0E0E0"

bullet_font_size_pt: 18
bullet_line_spacing: 1.3
bullet_max_per_slide: 5
bullet_char: "-"
bullet_font_color: "#1A1A1A"

metric_label_font_size_pt: 12
metric_value_font_size_pt: 28
metric_value_font_bold: true
metric_font_color: "#1A1A1A"

ask_font_size_pt: 13
ask_font_italic: true
ask_font_color: "#6B6B6B"

footnote_font_size_pt: 10
footnote_font_color: "#6B6B6B"
```

### Sample content (do not render as-is — replace with engagement data)

```
Headline: 3% Wage Scale Increase — All Hourly Grades — Effective May 1, 2026
Subtitle:  FY26 Annual Wage Review | comp-advisor scenario: Option B (market-parity)

Bullets:
- Closes 4% gap to Quebec retail market median for pharmacy assistant grades
- Covers all hourly employees in all banners (union and non-union)
- Within approved FY26 compensation budget envelope ($X.XM annualized run rate)
- CBA obligation: ratified by [union name] on [date]
- No change to incentive plan or benefit structure this cycle

Metric box: label="Annualized run rate" | value="$X.XM" | sub-label="vs. prior cycle: $Y.YM"

Ask: Note for information — no board approval required for increases within the approved envelope.
```

---

## Slide 2 — Cost Impact + Governance (Required)

Purpose: Financial detail and compliance anchors for board package.

### Regions

| Region | Position | Content |
|---|---|---|
| Section header | top: 0, left: 0, width: 13.33, height: 0.6 | Background: `colors.primary` at 85%. Text: "Cost Impact & Governance". Font: 18pt bold, white. |
| Cost table | top: 0.8, left: 0.4, width: 6.5, height: 4.5 | 3-5 row table: Grade / Prior rate / New rate / Delta / Headcount. Header row background: `colors.table_header_bg`. Alt row: `colors.table_row_alt_bg`. Font: 14pt. |
| Governance bullets | top: 0.8, left: 7.2, width: 5.7, height: 3.5 | 3-4 bullets on compliance drivers. Font: 16pt. |
| Total envelope callout | top: 4.5, left: 0.4, width: 6.5, height: 1.5 | Bold total row summary below the table. Background: `colors.secondary` at 20%. Font: 16pt bold. |
| Risk note | top: 5.5, left: 0.4, width: 12.5, height: 0.8 | 1-2 sentences on key risks if delayed or reduced. Font: 13pt italic, muted. |
| Footnote bar | top: 7.1, left: 0, width: 13.33, height: 0.4 | Source reference + confidentiality notice. |

### Cost table columns

```yaml
columns:
  - header: "Job Grade / Classification"
    width_pct: 30
  - header: "Prior Rate"
    width_pct: 17
    format: "$XX.XX/hr"
  - header: "New Rate"
    width_pct: 17
    format: "$XX.XX/hr"
  - header: "Delta"
    width_pct: 13
    format: "+X.X%"
  - header: "Headcount"
    width_pct: 23
    format: "~XXX FTEs"
```

### Governance bullets — suggested structure

```
- Legal anchor: [CBA article / pay equity legislation / Bill 96 requirement]
- Market anchor: [market data source and percentile position after increase]
- Budget anchor: [within approved envelope / requires supplementary approval]
- Timeline: [approval date / effective date / payroll system update date]
```

---

## Slide 3 — Prior-Year Comparison (Optional)

Include when: prior-year data is available AND board has not seen a prior-cycle summary in the same meeting package.

Omit when: this is the org's first cycle with comp-comms-builder, or when the board received a prior-cycle summary already in the same package.

### Regions

| Region | Position | Content |
|---|---|---|
| Section header | top: 0, left: 0, width: 13.33, height: 0.6 | Background: `colors.primary` at 85%. Text: "Year-over-Year Comparison". Font: 18pt bold, white. |
| Comparison table | top: 0.8, left: 0.5, width: 12.3, height: 4.0 | 3-row table: rows = prior cycle / this cycle / delta. Columns = envelope / median % increase / % employees covered / CBA or market trigger. |
| Trend note | top: 5.0, left: 0.5, width: 12.3, height: 1.2 | 2-3 sentences on trend across cycles. Font: 14pt. |
| Footnote bar | top: 7.1, left: 0, width: 13.33, height: 0.4 | Source reference + confidentiality notice. |

### Prior-year comparison table columns

```yaml
columns:
  - header: "Cycle"
    width_pct: 18
  - header: "Total Envelope"
    width_pct: 22
    format: "$X.XM"
  - header: "Median Increase"
    width_pct: 20
    format: "X.X%"
  - header: "Employees Covered"
    width_pct: 22
    format: "~X,XXX"
  - header: "Primary Driver"
    width_pct: 18
```

---

## Renderer Notes

```yaml
renderer: pptxgenjs
# See references/template-master.md for pptxgenjs integration details.
# comp-comms-builder does NOT modify compensation-advisor's existing PPTX master.
# This template is loaded from branding/<org-slug>/comms-templates/pptx-master/
# or falls back to branding/_default/comms-templates/pptx-master/ on cold start.

on_missing_data:
  metric_value: "TBD"
  cost_table_row: "(row omitted if no data)"
  prior_year_slide: "(slide 3 omitted if prior_engagement_refs[] is empty)"

confidentiality_footer_text:
  fr_ca: "CONFIDENTIEL — Usage interne — Ne pas distribuer"
  en: "CONFIDENTIAL — Internal use only — Do not distribute"

source_footnote_convention: "Source: compensation-advisor scenario <scenario_id>, locked <date> | comp-comms-builder v1"
```
