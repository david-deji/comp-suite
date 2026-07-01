## Instructions

This template is used during Phase 6 (Production) after the consulting conversation has established scope, audience, and narrative direction via the narrative frame.

You are assessing whether a user-provided wage scale or pay grid is competitive relative to the external market. The user has given you their actual pay data -- your job is to benchmark each role or grade against market data, calculate how competitive the scale is, and present findings and recommendations in a clear PowerPoint deck.

This deliverable answers the question: **"Is our pay competitive, and where are our risks?"**

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
- [ ] User's wage scale/pay grid parsed (roles, grades, steps or min/mid/max)
- [ ] Markets/geographies confirmed
- [ ] Industry/sector identified (affects benchmark selection)
- [ ] Compensation element clarified (base, hourly, total cash)
- [ ] Target percentile set (default P50)
- [ ] Pay structure confirmed

When `pay_structure = step`:
- [ ] Step table parsed with rates per step
- [ ] Headcount per step available (not just per role)
- [ ] Top rate (job rate) identified as benchmark anchor
- [ ] Hours-to-advance threshold documented (if hours-based progression)
- [ ] Roll-up factor identified (benefits, pension, premiums riding on base)

When `pay_structure = merit`:
- [ ] Band min/mid/max parsed
- [ ] Compa-ratio distribution computed
- [ ] Midpoint used as benchmark anchor

All structures:
- [ ] Compa-ratios, gaps ($, %), and market positions pre-computed
- [ ] Aggregate metrics computed (% below/at/above, weighted avg compa-ratio, cost-to-market if headcount provided)

## Step 1: Pull market benchmarks

If data was already computed during Phase 3, use the pre-computed values. If additional granularity is needed for slides, compute here.

For each role or grade in the user's scale, gather external market data:
- Use **`compare_pay_scale_to_market`** as the primary tool — pass the full step grid (or band min/max) and it returns entry/top positioning, sub-step verdicts, and an overall competitiveness flag in one call
- Use **`get_role_intelligence`** with `include_economic_regions=true` for the full distribution (P10/25/50/75/90), live posting rates, YoY trends, and economic-region breakdowns
- Use **`get_cba_wage_scale`** to anchor unionized scales against negotiated rates (mandatory for UFCW grocery, construction, healthcare, public sector)
- Use **Indeed MCP** (`mcp__claude_ai_Indeed__search_jobs`, `mcp__claude_ai_Indeed__get_company_data`) to validate posting matches and pull competitor pay/ratings — or the v2-native `mcp__market__company_get_posting_history` + `mcp__market__search_companies` (Job-Bank-sourced, in registry.yaml) for company/posting intel without the account connector
- Use **web search** for fallback only — Job Bank Canada, Glassdoor, LinkedIn Salary, BLS (US roles)
- For specialized roles, note the data source quality and any proxies used
- Aging is built into Market MCP responses (YoY trend); apply a separate aging factor only when source data predates the live posting window or comes from an older external survey

Record for each role:
- Market P25, P50, P75 (and P90 if available)
- Source and effective date
- Match quality (direct match, proxy, interpolated)

## Step 2: Compute competitiveness metrics

If data was already computed during Phase 3, use the pre-computed values. If additional granularity is needed for slides, compute here.

For each role or grade, calculate:

| Role / Grade | Internal Mid (or Flat Rate) | Market P25 | Market P50 | Market P75 | Compa-Ratio | Market Position |
|---|---|---|---|---|---|---|

- **Compa-ratio** = Internal Mid / Market P50
- **Market Position**:
  - Below Market: compa-ratio < 0.95
  - At Market: 0.95 - 1.05
  - Above Market: > 1.05
- **Gap ($)** = Internal Mid - Market P50 (negative = underpaying)
- **Gap (%)** = Gap / Market P50

Also calculate at the aggregate level:
- % of roles Below / At / Above Market
- Weighted average compa-ratio across the scale
- Total annualized cost-to-market (if headcount is provided)

When `pay_structure = step`, comparison slides use top rate as the market anchor and show step distribution. When `pay_structure = merit`, comparison slides use midpoint and show compa-ratio spread. Do not mix these approaches within a single role's analysis.

## Step 3: Slide deck structure

Build a **6-10 slide deck** (plus appendix) using the pptx skill. Suggested structure:

### Slide 1 -- Title
- Title: "Wage Scale Competitiveness Review -- [Org/Department] -- [Date]"
- Subtitle: market(s) covered, data sources, prepared by

### Slide 2 -- Methodology & Assumptions
- Data sources, effective dates, aging factors
- Target percentile (e.g., "Benchmarked to P50")
- Job matching approach
- Any caveats or data limitations

### Slide 3 -- Executive Summary / Scorecard
- Bold callout stats: "X of Y roles are below market", weighted compa-ratio
- Color-coded summary table: green (at/above market), yellow (borderline), red (below market)
- 2-3 bullet "headline findings"

### Slide 4 -- Competitiveness Heatmap / Gap Chart
- Horizontal bar chart: each role's compa-ratio, sorted from lowest to highest
- Mark the "at market" band (0.95-1.05) as a shaded zone
- Roles below the band should be in a highlight color (e.g., red/amber)

### Slide 5 -- Role-by-Role Benchmark Detail
- Full comparison table: Internal Mid vs. Market P25 / P50 / P75, compa-ratio, gap $, market position
- Color-code rows by market position
- Include data source per row

### Slide 6 -- Risk Assessment
- Which roles carry the highest attrition or recruitment risk due to below-market pay?
- Frame by: gap severity, role criticality, labour market tightness for that role
- Use a 2x2 risk matrix if helpful (x-axis: gap size, y-axis: role replaceability)

### Slide 7 -- Recommendations
- Specific, actionable, prioritized
- For each recommendation, include: action, rationale, estimated cost impact (if data available), suggested timeline
- Example: "Increase Grade 3 midpoint from $52,000 to $57,000 to reach market P50. Estimated annual cost: ~$X across N incumbents."
- Include the jurisdiction-appropriate employer payroll burden note on any cost-to-market or scenario costing slides

### Slide 8 (optional) -- Cost-to-Market Model
- If headcount is provided: table showing cost-to-close gaps by role/grade
- Total annualized investment to bring all below-market roles to P50

### Appendix slides
- Full data table with all benchmark sources
- Methodology detail
- Raw `get_role_intelligence` output (StatCan + live posting bundle) and CBA scale data if relevant

## Narrative and tone

- Lead with the overall verdict: is the scale competitive, partially competitive, or materially below market?
- Be specific -- avoid vague language like "some roles may be below market." State which roles, by how much, and what the risk is.
- Frame gaps in both $ and %, and in plain English (e.g., "Warehouse Associates are paid 12% below the median for this role in the GTA, which is likely contributing to turnover pressure")
- Audience default: HR leadership or executive -- strategic framing with data to back it up
