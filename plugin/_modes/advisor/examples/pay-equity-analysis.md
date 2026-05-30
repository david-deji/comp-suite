## Instructions

This template is used during Phase 6 (Production) after the consulting conversation has established scope, audience, and narrative direction via the narrative frame.

**Output format**: Deliver as a PowerPoint (.pptx) presentation using the pptx skill.

You are producing a pay equity analysis -- a structured review of whether pay differences across demographic groups (gender, race/ethnicity, age, disability, etc.) are explainable by legitimate factors or may indicate systemic bias. Pay equity is both a legal/compliance concern and a values-driven priority. Treat it with appropriate rigor and sensitivity.

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
- [ ] Scope confirmed (company-wide or specific BU/job family)
- [ ] Protected characteristics to analyze (gender, race, age, intersectional)
- [ ] Data availability confirmed (employee-level pay + demographics + tenure + performance + level + location)
- [ ] Jurisdiction and applicable laws identified
- [ ] Purpose confirmed (internal audit, board reporting, regulatory, proactive)
- [ ] Prior analysis results referenced (if any)
- [ ] Legal counsel involvement confirmed or flagged
- [ ] Constructive narrative framing agreed in narrative workshop

## Methodology

### Descriptive analysis (always start here)
- Calculate unadjusted (raw) pay gaps by group: mean and median base salary, total cash, and/or total comp
- Present gaps as both dollar amounts and percentages
- Show gaps at the aggregate level and broken down by job family, level, and geography

### Controlled (regression-based) analysis
If the data supports it, run a multivariate regression controlling for legitimate factors:
- Job level / grade
- Job family / function
- Tenure / years of experience
- Location / pay zone
- Performance rating (use with caution -- ratings themselves can be biased)
- Education (where relevant)
- Part-time / full-time status

The residual gap after controls is the "adjusted gap" -- the portion not explained by legitimate factors.

**Important caveats to always state:**
- A controlled analysis explains variance but does not prove or disprove discrimination
- The choice of control variables matters -- over-controlling (e.g., controlling for title when title assignment is itself biased) can mask real inequity
- Small group sizes reduce statistical reliability; flag where n < 30

### Cohort analysis (optional, for deeper investigation)
Compare pay outcomes for similarly situated employees:
- Same role, same level, same location, same tenure band -> are there persistent gaps?
- Look at starting pay, promotional velocity, and merit increase history

## Data presentation

### Summary gap table (required)

| Group Comparison | Headcount (A / B) | Unadjusted Gap (%) | Adjusted Gap (%) | Statistical Significance |
|------------------|--------------------|---------------------|-------------------| -------------------------|

### Visual: gap waterfall (recommended)
Show how the gap narrows as each control factor is added -- this is the most effective way to illustrate what the adjusted gap represents.

### Heatmap by job family (for large organizations)
Color-coded matrix of gaps across job families and levels -- quickly highlights hotspots requiring attention.

## Narrative

### Findings
- State the overall unadjusted and adjusted gaps clearly
- Identify specific hotspots (job families, levels, locations) where gaps are largest or most concerning
- Note where gaps are statistically significant vs. where sample sizes are too small for conclusions

### Context
- How do our gaps compare to industry or national benchmarks?
- Are there structural explanations (e.g., underrepresentation at senior levels driving aggregate gaps)?
- Have gaps improved or worsened over time?

### Remediation options
Present options on a spectrum from targeted to broad:
1. **Individual adjustments** -- Specific pay corrections for employees identified as underpaid after controlling for legitimate factors. Calculate cost. Include the jurisdiction-appropriate employer payroll burden note on remediation cost slides.
2. **Structural changes** -- Adjust salary bands, hiring ranges, or promotion criteria to prevent future gaps
3. **Policy changes** -- Ban salary history inquiries, mandate pay range transparency, require comp review at promotion
4. **Monitoring** -- Establish ongoing analytics cadence (quarterly or semi-annual reviews)

Always include estimated cost for individual adjustments and a recommended timeline.

## Tone and sensitivity
- This is one of the most sensitive compensation deliverables -- accuracy and nuance matter enormously
- Never overstate findings -- distinguish between "statistical significance" and "practical significance"
- Never dismiss gaps as fully explained just because the adjusted gap is small; acknowledge structural factors
- Frame findings constructively -- the goal is progress, not blame
- Be mindful that this document may be discoverable in legal proceedings; write accordingly

## Legal considerations (flag, don't advise)
- Recommend the user involve legal counsel before finalizing or distributing
- Note that in some jurisdictions, conducting and documenting a pay equity analysis creates obligations to act on findings
- Flag if privilege protections (attorney-client, self-audit) should be considered
