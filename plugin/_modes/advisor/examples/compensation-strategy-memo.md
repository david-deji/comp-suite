## Instructions

This template is used during Phase 6 (Production) after the consulting conversation has established scope, audience, and narrative direction via the narrative frame.

**Output format**: Deliver as a PowerPoint (.pptx) presentation using the pptx skill.

You are writing a compensation strategy memo -- a document that proposes or revisits the organization's compensation philosophy, positioning, or policy. Unlike a benchmarking report (which is data-driven) or an executive summary (which is action-oriented), the strategy memo is about the "why" behind pay decisions. It articulates principles, trade-offs, and a forward-looking approach.

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
- [ ] Strategic trigger identified (M&A, retention crisis, IPO prep, annual review, new market)
- [ ] Current philosophy documented (or confirmed absent)
- [ ] Pain points and constraints surfaced in discovery
- [ ] Approving audience identified
- [ ] Chosen scenario: which philosophy direction from option modeling
- [ ] Cost implications of philosophy change estimated

## Structure

### 1. Context and business case (1 paragraph)
Why are we revisiting compensation strategy now? Connect to business goals -- growth, retention, cost management, culture, equity commitments.

### 2. Current state assessment (3-5 bullets)
Summarize where the organization stands today:
- Current pay positioning vs. market
- Turnover trends and exit interview themes related to pay
- Known structural issues (compression, inequities, band misalignment)
- Competitive landscape changes (new entrants, remote work impact, union activity)

### 3. Recommended compensation philosophy

State the proposed philosophy clearly and completely. A good philosophy statement addresses:

- **Market positioning**: Where do we target for each comp element? (e.g., "P50 base, P60 total cash, P75 total comp for critical talent segments")
- **Internal equity**: How do we balance market competitiveness with internal fairness? (e.g., "We use structured pay bands with defined ranges; we do not match external offers on an ad-hoc basis")
- **Pay-for-performance**: How does performance link to pay? (e.g., "Merit increases are differentiated by performance; top performers receive 1.5-2x the standard increase")
- **Transparency**: What do we disclose? (e.g., "We share salary ranges in job postings and provide band information to all employees")
- **Geographic approach**: How do we handle location? (e.g., "We use geo-adjusted pay zones" or "We pay nationally regardless of location")

### 4. Implementation considerations

For each element of the philosophy, outline:
- What needs to change from the current state
- Estimated cost impact (include the jurisdiction-appropriate employer payroll burden note on cost projections)
- Timeline to implement
- Dependencies (system changes, manager training, comms plan)

### 5. Trade-offs and alternatives

Present at least one alternative approach for the key decisions and explain the trade-offs. Example:
- "Option A (P50 positioning): Lower cost, adequate for most roles, but may not attract top talent in competitive segments. Option B (P65 positioning for critical roles): Higher cost, targeted investment, better hiring competitiveness for hard-to-fill roles."

### 6. Governance and review cadence

Recommend:
- How often the philosophy should be reviewed (annually is standard)
- Who owns compensation decisions at each level (HR, hiring manager, comp committee)
- Escalation path for exceptions
- How market data will be refreshed

## Tone
- Strategic and consultative -- you're advising leadership, not just presenting data
- Frame everything in terms of business outcomes: talent attraction, retention, engagement, cost efficiency
- Be honest about trade-offs -- don't oversell any single approach
- Use a confident, recommendation-forward voice

## Common strategy frameworks to reference where appropriate

- **Lead / match / lag**: Positioning above, at, or below market
- **Total rewards lens**: Base pay is one lever; consider benefits, equity, development, flexibility, culture
- **Segmented approach**: Different positioning for different talent segments (e.g., tech vs. operations vs. corporate)
- **Pay transparency continuum**: From "ranges available upon request" to fully published bands with individual positioning
