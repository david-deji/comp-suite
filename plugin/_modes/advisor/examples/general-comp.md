## Instructions

This template is used during Phase 6 (Production) after the consulting conversation has established scope, audience, and narrative direction via the narrative frame.

**Output format**: Deliver as a PowerPoint (.pptx) presentation using the pptx skill.

You are handling a compensation task that doesn't fit neatly into one of the other specialized templates (market benchmarking, pay scale design, executive summary, strategy memo, or pay equity analysis). This covers a wide range of deliverables including total rewards statements, merit/incentive matrices, offer analyses, retention packages, job evaluation exercises, and ad-hoc pay comparisons.

For deliverables routed here, the consulting protocol may have been lighter (Track D) or the deliverable may not map to the standard 7-phase flow. Apply the narrative frame where it adds value; for purely mechanical deliverables (e.g., merit matrix with known budget), some prerequisites may be partially empty.

## Engagement contract

This deliverable inherits the engagement contract in [`_engagement-contract-preamble.md`](./_engagement-contract-preamble.md) (same `examples/` folder). Read it once before producing any example in this folder — it defines the brand-kit resolution, engagement-config keys honored, verified-source `tool_calls[]` discipline, END artifacts produced, and chat-preview pattern that apply to every example.

## Brand enforcement

The active brand kit governs all visual application. When no per-org override is present, the `_default` kit at `template_assets/branding/_default/` ships a neutral placeholder brand per `brand-guidelines.md` (generic wordmark, neutral palette, Noto Serif headings + Lexend Deca body, "no stock people imagery" photography rule). When an engagement-config sets `deck.brand: <org-slug>` and a per-org kit exists at `template_assets/branding/<org-slug>/`, the per-org kit's theme JSONs and masters take precedence per `references/brand-kit-protocol.md` § Per-org override mechanism; the per-org kit may also ship a `voice-and-design-rules.md` that overrides the `_default` voice register.

Surface the external-audience neutral-palette override during Phase 1 or Phase 5 (per `brand-guidelines.md` § Default vs. per-org override) when the audience is outside the host org. Run the active kit's compliance checklist as Phase 7 QA — for the `_default` kit, that's the checklist at the bottom of `brand-guidelines.md`.

## Production Prerequisites

Before building this deliverable, verify the narrative frame includes:
- [ ] Audience and narrative angle from narrative frame (may be partial for Track D deliverables)
- [ ] Data sources with effective dates
- [ ] Payroll jurisdiction (for tax caveat on any costing outputs)
- [ ] Specific deliverable type identified (total rewards statement, merit matrix, offer analysis, retention package, job eval, ad-hoc comparison)
- [ ] Audience identified
- [ ] Decision or action this supports
- [ ] Required data inputs confirmed available
- [ ] Pay structure confirmed (where relevant)

## Common deliverable types and guidance

### Total rewards statements
- Employee-facing document showing the full value of their compensation package
- Include: base salary, bonus/incentive (target and actual), equity/LTI, benefits value (health, dental, pension, etc.), PTO value, any other perks
- Use plain language -- no comp jargon; employees should immediately understand their total value
- Present as an annualized total with a clear breakdown visual (pie chart or stacked bar)

### Merit increase matrices
- Grid that maps performance rating x position-in-range (compa-ratio quartile) to a recommended merit increase %
- Ensure the matrix produces a fundable overall increase % (e.g., if the budget is 3.5%, the weighted average of the matrix should equal ~3.5%)
- Higher increases for: high performers, employees low in range
- Lower increases for: employees already high in range, lower performance ratings
- Include guidance notes for managers on how to use the matrix

### Incentive / bonus plan design
- Define: eligibility, target %, performance measures (corporate, team, individual), payout curve (threshold, target, maximum), payment timing
- Always model the cost at threshold, target, and maximum payout scenarios
- Note clawback or forfeiture provisions if applicable

### Offer analysis / counter-offer support
- Compare the proposed offer to: internal equity (similar roles/levels internally), external market data, and the candidate's current/competing compensation
- Present total compensation side-by-side: base, bonus, equity, sign-on, benefits
- Flag any internal equity risks if the offer is significantly above incumbent pay
- Recommend a range, not a single number, with justification

### Job evaluation and leveling
- Use a consistent framework (point-factor, whole-job ranking, or market-based slotting)
- Document the factors evaluated (scope, impact, complexity, leadership, expertise)
- Map to the existing grade structure with rationale
- Flag where a role doesn't fit cleanly and may need a hybrid or new grade

### Retention analysis / packages
- Identify at-risk employees using: market gap, performance, tenure, flight risk signals
- Propose retention tools: spot bonus, equity grant, off-cycle adjustment, expanded role, deferred compensation
- Cost out each option and recommend based on criticality of the individual

### Ad-hoc wage comparisons
- Quick-turn answers to questions like "what does a [role] make in [market]?"
- Pull from Market MCP (`search_roles` → `get_role_intelligence` for the StatCan + live posting bundle, `compare_offer_to_market` for single offers, `get_cba_wage_scale` for unionized roles), Indeed MCP for posting/employer context, then web search and uploaded files as fallback
- Always state the source and any caveats (e.g., "Glassdoor data, self-reported, may skew high")
- Present as a range (P25-P75) rather than a single number

## General principles

- **Always cite your data sources** -- even in informal analyses, the user needs to know where numbers come from
- **Default to tables** -- compensation data is almost always best presented in tabular form
- **Include a "so what"** -- don't just present numbers; interpret them and recommend action
- **Be cost-conscious** -- every recommendation should come with a cost estimate, even a rough one. Include the jurisdiction-appropriate employer payroll burden note on any costing outputs.
- **Consider internal equity** -- market data matters, but so does fairness relative to existing employees
