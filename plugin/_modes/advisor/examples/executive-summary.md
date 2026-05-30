## Instructions

This template is used during Phase 6 (Production) after the consulting conversation has established scope, audience, and narrative direction via the narrative frame.

**Output format**: Deliver as a PowerPoint (.pptx) presentation using the pptx skill.

You are producing a compensation summary for executives, the C-suite, or the board. This is the highest-stakes compensation deliverable -- it must be concise, visually clean, strategically framed, and decision-ready. Executives don't want methodology details; they want implications, risks, and recommended actions.

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
- [ ] Audience specified (CHRO, CEO, full board, comp committee)
- [ ] Purpose confirmed (inform, approve budget, support decision, annual review)
- [ ] Scope defined (company-wide, BU, exec team)
- [ ] Decision/ask identified and costed
- [ ] Key findings (3-5) with supporting numbers from interpretation
- [ ] Anticipated objections and pre-emption strategy from narrative workshop

Optional enrichments (include when available):
- [ ] Replacement cost multiplier data for do-nothing baseline (16-20% entry, 50-60% professional, 100-150% management, 150-213% executive)
- [ ] Pay-attributable turnover estimate (~35% of voluntary turnover attributable to below-market pay)

## Format: strict 1-2 pages

Executive summaries must fit on 1-2 pages maximum, plus an optional appendix for supporting data. Structure:

### Page 1: The story

**Header block**:
- Title (e.g., "2025 Compensation Competitiveness Review")
- Date, prepared by, confidentiality notice

**Situation** (2-3 sentences):
What prompted this analysis? What's the business context?

**Key findings** (3-5 bullets, one line each):
Lead with the most impactful finding. Use numbers. Example:
- "Distribution center roles in GTA are 12% below market median, contributing to 28% annualized turnover"

**Risk / opportunity** (1-2 sentences):
What happens if we do nothing? What's the upside of acting?

When replacement cost data is available and the audience is board or c-suite, include a "cost of inaction" callout using the replacement cost multipliers by level. This strengthens the business case for compensation investment. Source the multipliers (HRPA, Conference Board of Canada) on the slide.

**Recommendation** (numbered list, 2-4 items):
Specific, costed, time-bound. Include the jurisdiction-appropriate employer payroll burden note on any costing data. Example:
1. "Increase DC hourly rates by $2.50/hr in GTA (est. annual cost: $420K) effective Q2"
2. "Conduct targeted retention review for Supervisor roles by end of Q1"

### Page 2 (optional): Supporting data

One summary chart or table that reinforces the narrative. Keep it to one visual -- don't overwhelm. Good options:
- Compa-ratio heatmap by role and market
- Bar chart of internal vs. market by role family
- Waterfall chart showing cost of proposed adjustments

## Tone
- Assertive but not alarmist
- Data-backed -- every claim should have a number behind it
- Forward-looking -- frame findings in terms of business outcomes (retention, hiring velocity, cost risk), not just pay gaps
- Avoid comp jargon where possible; if you must use a term (compa-ratio, TDC), define it in a footnote
- Use "we" and "our" -- position yourself as part of the leadership team, not an outside consultant

## What NOT to include
- Full methodology (put in appendix if needed)
- Detailed role-by-role breakdowns (put in appendix)
- Multiple options without a clear recommendation -- always lead with your recommended path, then note alternatives
- Caveats and qualifications in the main body -- put them in footnotes or appendix

## Decision framing
Always end with a clear ask:
- "We recommend Option A and request approval to proceed with implementation in Q2."
- "We seek the Committee's endorsement of the revised pay philosophy before we update salary bands."
- "For discussion: should we prioritize closing gaps in critical roles (lower cost, targeted) or implement a broad-based adjustment (higher cost, equitable)?"
