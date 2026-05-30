## Instructions

This template is used during Phase 6 (Production) after the consulting conversation has established scope, audience, and narrative direction via the narrative frame.

You are producing a market benchmarking presentation -- a comparison of internal compensation to external market data for one or more roles, levels, or geographies. Deliver this as a polished PowerPoint (.pptx) deck. This is the bread-and-butter deliverable of compensation analysis and the one most frequently requested by HR leadership, hiring managers, and executives.

## Engagement contract

This deliverable inherits the engagement contract in [`_engagement-contract-preamble.md`](./_engagement-contract-preamble.md) (same `examples/` folder). Read it once before producing any example in this folder — it defines the brand-kit resolution, engagement-config keys honored, verified-source `tool_calls[]` discipline, END artifacts produced, and chat-preview pattern that apply to every example.

## Brand enforcement

The active brand kit governs all visual application. When no per-org override is present, the `_default` kit at `template_assets/branding/_default/` ships a neutral placeholder brand per `brand-guidelines.md` (generic wordmark, neutral palette, Noto Serif headings + Lexend Deca body, "no stock people imagery" photography rule). When an engagement-config sets `deck.brand: <org-slug>` and a per-org kit exists at `template_assets/branding/<org-slug>/`, the per-org kit's theme JSONs and masters take precedence per `references/brand-kit-protocol.md` § Per-org override mechanism; the per-org kit may also ship a `voice-and-design-rules.md` that overrides the `_default` voice register.

Surface the external-audience neutral-palette override during Phase 1 or Phase 5 (per `brand-guidelines.md` § Default vs. per-org override) when the audience is outside the host org. Run the active kit's compliance checklist as Phase 7 QA — for the `_default` kit, that's the checklist at the bottom of `brand-guidelines.md`.

## Production Prerequisites

Before building this deliverable, verify the narrative frame includes:
- [ ] Audience and narrative angle from narrative frame
- [ ] Data sources with effective dates
- [ ] Payroll jurisdiction (for tax caveat language)
- [ ] Roles in scope identified and matched to NOC/survey codes
- [ ] Markets/geographies confirmed
- [ ] Compensation element specified (base, total cash, TDC)
- [ ] Target percentile set (default P50)
- [ ] Aging/trending factor confirmed (default 3% for Canadian markets)
- [ ] Compa-ratios and gaps pre-computed in interpreted data set
- [ ] Pay structure confirmed (affects benchmark anchor: top rate for step, midpoint for merit)

## Slide deck structure

Build a **8-14 slide deck** using the pptx skill. Suggested structure:

### Slide 1 -- Title
- Report title, subtitle with scope (role family / department), date, prepared by, data effective date

### Slide 2 -- Methodology
- Data sources used and effective dates
- Job matching approach (whole-job, point-factor, hybrid)
- Aging/trending factors applied
- Geographic adjustments (if any)
- Compensation elements compared
- Any exclusions or caveats

### Slide 3 -- Executive Summary
- 3-5 headline findings as bold callout stats or bullets
- Overall market positioning verdict (e.g., "The majority of roles are priced at or above the P50 median")

### Slide 4 -- Summary Benchmarking Table
Present a color-coded summary table:

| Role | Level | Internal Pay (Base) | Market P25 | Market P50 | Market P75 | Compa-Ratio | Position vs. Market |
|------|-------|---------------------|------------|------------|------------|-------------|---------------------|

- **Compa-ratio** = Internal Pay / Market P50
- **Position vs. Market**: Below Market (<0.95), At Market (0.95-1.05), Above Market (>1.05)
- Color-code rows: red = below market, green = at/above market

### Slide 5 -- Gap Analysis Chart
- Horizontal bar chart of compa-ratios by role, sorted low to high
- Shade the "at market" band (0.95-1.05)
- Highlight below-market roles in accent color

### Slides 6-N -- Detailed Role Cards (optional for deep-dives)
For each role or role family, include:
- Job title and internal job code
- Benchmark match details (survey job code, match quality)
- Market data by percentile (P10, P25, P50, P75, P90)
- Number of incumbents and their pay range
- Gap analysis ($ and % from target percentile)

### Slide N+1 -- Risk Assessment
- Which roles are most exposed to attrition or market pressure?
- Frame by gap severity and role criticality

### Slide N+2 -- Recommendations
- 3-5 specific, actionable next steps (adjust ranges, re-benchmark, conduct deeper review)
- Include priority, estimated cost impact, and suggested timeline
- Any cost-to-market slides must include the jurisdiction-appropriate employer payroll burden note

### Appendix slides
- Full data tables, survey source details, methodology notes

## Tone and audience
- Default audience is HR leadership -- balance data rigor with strategic framing
- Lead with "so what" -- don't just present data, interpret it
- If producing for executives, condense the main body to 6-8 slides and move detail to appendix
