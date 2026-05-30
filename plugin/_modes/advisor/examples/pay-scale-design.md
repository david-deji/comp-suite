## Instructions

This template is used during Phase 6 (Production) after the consulting conversation has established scope, audience, and narrative direction via the narrative frame.

**Output format**: Deliver as a PowerPoint (.pptx) presentation using the pptx skill. Structure content as slides: title, methodology, proposed pay scale table (as a slide table or visual), employee impact, and recommendations.

You are designing, harmonizing, or restructuring pay scales (salary bands / salary ranges). This is a structural deliverable -- it defines the min, mid, and max for each grade or level in the organization's pay framework. It's often triggered by a benchmarking exercise that reveals misalignment, a merger/acquisition, a move to a new geography, or a periodic refresh.

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
- [ ] Current pay structure documented (if exists)
- [ ] Scope: job families, levels, geographies
- [ ] Pay philosophy confirmed (target percentile per comp element)
- [ ] Pay structure confirmed
- [ ] Chosen scenario from option modeling (which bands/steps change, cost impact)

When `pay_structure = merit`:
- [ ] Range spread parameters set (IC, management, executive)
- [ ] Midpoint progression % between grades confirmed
- [ ] Market data anchoring midpoints identified
- [ ] Compa-ratio distribution for current employees computed
- [ ] Compression analysis completed (flag when compa-ratio for 0-2yr cohort > 3-5yr cohort)
- [ ] Green-circle and red-circle employee counts identified

When `pay_structure = step`:
- [ ] Current step table with rates
- [ ] Proposed step table with rates (from scenario)
- [ ] Headcount per step
- [ ] Progression rules (hours-based, calendar-based)

## Methodology

### Building bands from market data
1. Set midpoints to the target percentile (usually P50) of matched market data
2. Calculate min and max based on the chosen range spread:
   - Min = Midpoint / (1 + Spread/2)
   - Max = Midpoint x (1 + Spread/2)
   - Example: P50 = $80,000, Spread = 50% -> Min = $64,000, Max = $96,000
3. Validate midpoint progression between grades is consistent and reasonable
4. Check for overlap between adjacent grades (some overlap is normal; excessive overlap may indicate too many grades)

### Harmonization scenarios
When merging or aligning multiple existing structures:
- Map all existing roles to the proposed grade structure
- Identify employees below new minimums (red-circled below) or above new maximums (red-circled above)
- Calculate cost-to-minimum for underpaid employees
- Propose transition timelines for red-circled employees

## Data presentation

### Proposed pay scale table (required)

| Grade | Level | Min | Midpoint | Max | Spread | Midpoint Progression |
|-------|-------|-----|----------|-----|--------|----------------------|

### Employee impact analysis (when restructuring)

| Impact Category | Headcount | % of Population | Avg $ Gap | Total Cost |
|-----------------|-----------|-----------------|-----------|------------|
| Below new min   |           |                 |           |            |
| Within range    |           |                 |           |            |
| Above new max   |           |                 |           |            |

### Visual: range chart
If code execution is available, produce a horizontal bar chart showing min-mid-max for each grade, overlaid with current employee pay as scatter points. This is the single most effective visual for pay scale presentations.

## Narrative and recommendations

1. **Design rationale** -- Why these midpoints, spreads, and progressions were chosen
2. **Market alignment** -- How the proposed structure compares to the external market
3. **Employee impact** -- How many employees are impacted and the cost implications. Include the jurisdiction-appropriate employer payroll burden note on implementation cost slides.
4. **Implementation plan** -- Phased approach, timeline, budget requirements
5. **Governance** -- How often to refresh, approval process for exceptions

## Tone and audience
- Primary audience is typically HR leadership and finance for approval, then HR ops for implementation
- Be precise with numbers -- this deliverable drives real budget decisions
- Present options where trade-offs exist (e.g., "Option A: tighter spreads, lower cost, less flexibility. Option B: wider spreads, higher cost, more room for growth")
- Always include the cost impact -- decision-makers need a dollar figure

## Common pitfalls to flag
- Grades with no market data to anchor them
- Spreads that are too narrow for roles with long tenure
- Midpoint progressions that don't reflect the actual jump in scope between levels
- Ignoring geographic differentials in a multi-location structure
