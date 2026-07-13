# Council Mode — Strategic Deliberation Protocol

Loaded when the intent router classifies a request as **Track Council** or when the user explicitly invokes a council mid-engagement (e.g. "run council on this recommendation before we go to Phase 5").

Council is a reasoning mode, not a deliverable track. It produces decision-quality analysis by running multiple named perspectives over the same question, then synthesizing. No slides are produced in reasoning or memo mode. Integrated mode feeds council output into Phase 4 (option modeling) or Phase 5 (narrative workshop) of a standard consulting engagement.

## When to use

Use Council track for strategic compensation decisions where one lens is not enough:

- Aggressive vs. conservative merit matrix under a budget constraint
- Band compression remediation — ATB lift vs. top-step addition vs. targeted adjustment
- Pay philosophy shift (P50 → P65, or lead/lag/match change)
- Pay equity remediation sequencing and ceiling
- Union bargaining stance and precedent exposure
- Executive comp package structure trade-offs (base / STI / LTI mix)
- Multi-jurisdiction harmonization — equalize vs. differentiate
- Any question the user frames as "should we do X or Y" where both have real merit

Do NOT use Council for:

- Pure data questions ("what does the market pay for X?") — use Phase 2 directly
- Single-answer technical questions ("what is the QC pay equity maintenance interval?") — answer directly, cite source
- Deliverable production when the strategic direction is already settled — use Track D

## Execution model (claude.ai single-context, no subagents)

On claude.ai, skills run single-context. Council is not parallel subagent dispatch — it is **one Claude playing multiple named perspectives sequentially within one response**, then synthesizing in the same response.

Each perspective gets its own clearly-labeled voice block. The model speaks as that persona, cites its lens, tags confidence, and produces a position. Between personas, do not break character. After all personas speak, the orchestrator voice returns and synthesizes across them.

This is intentionally different from a multi-context council pattern that uses parallel subagent dispatch. The single-context constraint means council here runs faster and cheaper but with less true perspective independence. Mitigation: write each persona block in full before drafting the next; do not draft synthesis until all persona blocks exist.

## Configuration resolution

At Council track entry, resolve configuration in this order:

1. If the engagement config (Phase 0) included a `council` section, use those defaults
2. For any field not set in config, use skill defaults (below)
3. Prompt for missing required fields only if they cannot be defaulted

### Required fields

- `question` — the specific decision or trade-off being deliberated. If not stated in the user's message, ask in one turn: "What's the decision or trade-off you want the council to weigh?"
- `perspectives` — 4 to 6 names from the pool below. Default if unset: `[employment-lawyer, total-rewards-strategist, cfo-finance, hr-business-partner, dei-pay-equity]`
- `mode` — `reasoning` | `memo` | `integrated`. Default: `reasoning`

### Skill defaults (used when config is silent)

```yaml
default_perspectives: [employment-lawyer, total-rewards-strategist, cfo-finance, hr-business-partner, dei-pay-equity]
default_mode: reasoning
synthesis_style: consensus-tensions
confidence_tags: [statcan-wage, live-postings, cba, indeed-company, econometric, statutory, market-data, survey-house, user-provided-cba, professional-judgment, assumption]
memo_length_cap_words: 800
```

## Perspective pool

Seven bundled comp-scoped personas, plus any custom personas resolved per `references/library-resolution.md` (bundled + local `personas/` library). Pick 4-6 per run based on the question. Do not run all seven (or all available) by default — more personas dilute rather than add.

**Pool resolution**: bundled-7 ∪ custom personas from `personas/_index.yaml`. See `references/persona-library.md` for custom persona schema, loading procedure, and collision rules. Custom personas appear in the roster declaration tagged `(custom)`; bundled appear tagged `(bundled)`.

| ID | Persona | Lens |
|---|---|---|
| `employment-lawyer` | Employment Lawyer | CBA interpretation, pay equity maintenance exposure, constructive dismissal via comp change, wrongful dismissal precedent, human rights code. Grounded in the province(s) stated in `benchmark.scope_provinces` — if QC, centers CCQ / Loi sur l'équité salariale / CNESST. |
| `total-rewards-strategist` | Total Rewards Strategist | Market positioning coherence, philosophy alignment (lead/lag/match), lead-market selection, internal equity bands, merit-matrix design, incentive-plan interactions. Speaks the comp-philosophy language. |
| `cfo-finance` | CFO / Finance | Budget envelope, multi-year roll-up, cost-of-capital framing, ROI per dollar of comp spend, labour-cost ratio, EBITDA impact. Pushes back on "spend your way out" solutions. |
| `hr-business-partner` | HR Business Partner | Line-manager reality, internal equity friction, precedent-setting across the org, employee-relations fallout, retention stories from the field. The voice of "what will actually happen when managers try to explain this." |
| `dei-pay-equity` | DEI & Pay Equity | Systemic gap analysis, disparate impact, QC Pay Equity Act predominance logic, accommodation duty, legal obligation under federal Pay Equity Act for federally-regulated employers. Names fairness consequences the other lenses miss. |
| `employee-union` | Employee / Union perspective | Fairness perception, acceptance likelihood, grievance risk, bargaining leverage, reopener clause exposure. Voice of the recipient, not the designer. |
| `ceo-board` | CEO / Board | Strategic messaging, optics, talent narrative, investor/board reaction, precedent across business units. Thinks in quarters and reputation, not pay grades. |

### Persona selection heuristics

- Unionized scope → always include `employee-union` and `employment-lawyer`
- Budget-constrained question → always include `cfo-finance`
- Cross-gender or cross-demographic implications → always include `dei-pay-equity`
- Executive or tier-0 question → always include `ceo-board`
- 4-perspective minimum. 6-perspective soft maximum. Never run 7 unless the user explicitly asks.

## Confidence tagging

Every substantive claim in a persona block and in synthesis carries one tag. The full 11-tag set is canonical in `references/tools-available.md` § Verified-source discipline; the council-mode usage is a strict subset of the same vocabulary. **Do not use the legacy 4-tag shorthand** (statutory / market-data / professional-judgment / assumption) for anything new — fine-grained tags enable per-source-class auto-downgrade.

| Tag | Meaning | Required verification artifact | Example |
|---|---|---|---|
| `[statcan-wage]` | The `benchmarks.statcan` percentiles block from a real `mcp__market__get_role_intelligence` call (Market MCP wraps StatCan's wage tables in this block). | Captured `tool_calls[]` entry with `role_id`, `province`, `percentiles`, retrieval timestamp, and field path `benchmarks.statcan.<percentile>`. | "P50 (StatCan-wage block) for Meat Cutter in QC is $27.40/h `[statcan-wage: mcp__market__get_role_intelligence(role_id=X, province=QC, percentiles=[10,25,50,75,90]) 2026-04, benchmarks.statcan.p50]`" |
| `[live-postings]` | `benchmarks.live_posting_*_rate` block from `get_role_intelligence` OR a real Indeed `search_jobs` result with job_id list. | Captured `tool_calls[]` entry with field path `benchmarks.live_posting_top_rate.<percentile>` (or `start_rate` / `midpoint`) AND retrieval timestamp. | "Live-posting P50 top rate is $24.04/h `[live-postings: mcp__market__get_role_intelligence(role_id=X, province=ON) 2026-04, benchmarks.live_posting_top_rate.p50]`" |
| `[cba]` | A real `mcp__market__get_cba_wage_scale` return for unionized roles (UFCW grocery, construction, healthcare, public sector). | Captured `tool_calls[]` entry with agreement reference, scope, and retrieval timestamp. | "TUAC 501 Acme QC top step is $30.95/h `[cba: mcp__market__get_cba_wage_scale(union='UFCW 501', employer='Acme', province=QC) 2026-03]`" |
| `[indeed-company]` | A real `mcp__claude_ai_Indeed__get_company_data` return — competitor intel, ratings, posting volume. | Captured `tool_calls[]` entry with company name, query, and retrieval timestamp. | "Loblaws posts ~440 grocery clerk roles QC-wide last 90 days `[indeed-company: get_company_data(company='Loblaw', province=QC) 2026-04-22]`" |
| `[econometric]` | Grounded in StatCan MCP econometric series (CPI, unemployment, GDP) **OR** `web_fetch` against `statcan.gc.ca` — **NOT wages**. | StatCan MCP table number + retrieval date OR fetched URL with access date. | "QC CPI year-over-year is +2.4% `[econometric: StatCan Table 18-10-0004, retrieved 2026-04-21]`" |
| `[statutory]` | Grounded in named statute, regulation, or CBA article. | **Mandatory `web_fetch` URL on the statute domain + verbatim quote of the article text in the same line.** See § Statutory discipline below. | "QC Pay Equity Act requires maintenance exercise every 5 years `[statutory: legisquebec.gouv.qc.ca/fr/document/lc/E-12.001 art. 76.1, fetched 2026-05-02 — quoted: 'L'employeur doit, tous les cinq ans, évaluer le maintien de l'équité salariale dans son entreprise.']`" |
| `[market-data]` (web fallback) | A `web_fetch` return for market data outside Market MCP coverage. **Avoid for any role/province Market MCP serves** — use `[statcan-wage]` or `[live-postings]` instead. | A real `web_fetch` return with URL + access date. | "BLS Pharmacy Tech US national P50 is $19.10/h `[market-data: bls.gov/oes/current/oes292052.htm, fetched 2026-04-15]`" |
| `[survey-house]` | Grounded in user-uploaded third-party survey data (Mercer, WTW, Korn Ferry, etc.) — see `references/survey-house-protocol.md`. | Vendor + survey year + cut + aging note. Without all four, auto-downgrade to `[professional-judgment]`. | "Pharmacy assistant P50 in QC retail is $25.40/h `[survey-house: Mercer, 2026 Total Compensation Survey, QC retail cut, aged +1.2% to 2026-04]`" |
| `[user-provided-cba]` | Grounded in a CBA the user pasted/uploaded (NOT in Market MCP) — see `references/survey-house-protocol.md`. | Agreement ID + expiry date. Without both, auto-downgrade to `[assumption]`. | "Top step for meat cutter is $31.00/h `[user-provided-cba: TUAC 501 Acme QC retail 2024-2028, expires 2028-04-30]`" |
| `[professional-judgment]` | Experienced comp-professional inference, not directly sourced. **Not a source claim** — excluded from the verification rule. | Persona name + one-line rationale. | "Retention risk compounds when compression exceeds 12 months `[professional-judgment: hr-business-partner — observed pattern across 3 unionized retail engagements]`" |
| `[assumption]` | Stated belief not yet verified; flagged for follow-up. **Not a source claim** — but if a persona leans on it heavily, that signals weak grounding. | One-line statement of what would falsify it. | "Assuming the comp committee prefers implementation speed over philosophical purity `[assumption: would be falsified by a committee preference for multi-cycle structural change]`" |

Count tags per persona in the state file — a persona leaning heavily on `[assumption]` signals weak grounding and lower weight in synthesis. The auto-downgrade table is canonical in `references/tools-available.md` § Verified-source discipline; never duplicate it here.

## Statutory discipline (item 3.2 enforcement)

Any `[statutory]` tag carries an enforcement obligation: a `web_fetch` against the actual statute text on `legisquebec.gouv.qc.ca` / `laws-lois.justice.gc.ca` / `canlii.org` (or, for CBAs, the published agreement URL on the union local's site or the employer's labour-relations portal), with the cited article text quoted in the same claim.

**Enforcement procedure** (runs at three points):

1. **Pre-block (in Step 4 grounding)**: when an `employment-lawyer` or `dei-pay-equity` persona is assigned a statute as its grounding source, the `web_fetch` MUST execute before the block is written. If the fetch fails (404, rate-limit, paywall) the persona writes its block but tags every would-be-statutory claim as `[professional-judgment]` and notes the failed fetch in `flags_raised`. The skill never invents the statute text.
2. **Mid-block (during persona writing)**: any `[statutory]` tag that appears in a persona block must include the URL fetched in Step 4 + a verbatim quoted excerpt. A bare `[statutory: Loi sur l'équité salariale]` reference with no URL and no quote is auto-downgraded to `[professional-judgment]`. Generic `web_search` snippets (search-result previews) are not sufficient — the fetched URL must point at the statute itself.
3. **Synthesis (in Step 6)**: the orchestrator scans every claim tagged `[statutory]` and verifies a fetched URL is present. Any unfounded `[statutory]` claim is rewritten in synthesis as `[professional-judgment]` with a "(downgraded — no statute fetch)" note. Synthesis surfaces the count of downgrades — a council with multiple statutory-tag downgrades is weak grounding.

**Why this discipline**: comp decisions get re-litigated in HR, in legal review, and (occasionally) in arbitration. A `[statutory]` claim cited in a deck that turns out to be paraphrased recall — not the actual statute — is a credibility failure. The fetch + quote pattern is the smallest enforceable hook that makes the claim auditable.

### Verified-source discipline — applies to all tags

Every tagged claim (not just `[statutory]`) must trace to a captured tool-call output in the engagement-state `tool_calls[]` array. Full rule + per-tag verification artifact requirements + auto-downgrade table in `references/tools-available.md` § Verified-source discipline. Council synthesis (Step 6) scans every claim and downgrades any tag without its required artifact.

Particularly load-bearing for council quality:
- `[market-data]` claims must name the specific Market MCP function call and field path (e.g., `benchmarks.statcan.p50` vs `benchmarks.live_posting_top_rate.p50` — these are different metrics, conflating them is a downgrade trigger).
- `[econometric]` is for StatCan MCP series only (CPI, unemployment, GDP). A wage claim tagged `[econometric]` auto-downgrades to `[professional-judgment]` — wage data is `[market-data]`, not `[econometric]`.
- `[market-data]` claims that name "StatCan" without specifying it came from Market MCP's `benchmarks.statcan` block (vs a separate StatCan MCP call) get flagged in synthesis as "source-conflated" and the persona is asked to disambiguate.

**Anchor list of authoritative URLs** (extend as needed; never substitute a different domain):
- Quebec statutes: `https://www.legisquebec.gouv.qc.ca/fr/document/lc/...`
- Canadian federal statutes: `https://laws-lois.justice.gc.ca/eng/acts/...`
- Canadian case law: `https://www.canlii.org/...`
- Federal Pay Equity Act: `https://laws-lois.justice.gc.ca/eng/acts/P-4.2/`
- Loi sur l'équité salariale (QC): `https://www.legisquebec.gouv.qc.ca/fr/document/lc/E-12.001`
- Loi sur les normes du travail (QC): `https://www.legisquebec.gouv.qc.ca/fr/document/lc/N-1.1`
- Code canadien du travail: `https://laws-lois.justice.gc.ca/eng/acts/L-2/`

## Session flow

### Step 1. Frame the question

Restate the decision in one sentence. Explicitly name what IS being decided and what is NOT. If the user's framing was vague, tighten it before dispatching personas:

> "Council question: Given an approved $4.2M envelope for QC retail, should we apply 2.5% across-the-board to all step grids, or add a new top step at +3% with a smaller 1.5% across-the-board?"

### Step 2. Declare the roster

State which 4-6 personas will run and why, in one line each:

> Personas running:
> - employment-lawyer (CBA reopener exposure under TUAC 501)
> - total-rewards-strategist (which option aligns with P50 philosophy)
> - cfo-finance (multi-year roll-up of top-step addition)
> - hr-business-partner (manager-explainability and precedent)
> - dei-pay-equity (differential impact on predominantly-female classes)

### Step 3. Adversarial pre-pass

Before any persona writes, generate the **3 hardest objections to the question itself** — not to any one option, but to the framing. The point is to surface real disagreement upstream of the persona blocks, so personas have something concrete to contend with rather than rationalizing toward consensus.

The objections target the question's premises: hidden assumptions, omitted alternatives, framing bias, time-horizon mismatch, scope mis-cut. Pattern:

> Adversarial pre-pass — 3 hardest objections to the question:
>
> 1. **Premise objection**: "The question assumes [X is true]. If [counter-evidence], the framing collapses." (e.g., "The question assumes the envelope is fixed at $4.2M. If the board would approve $5M for a defensible retention case, top-step + larger ATB becomes viable and changes the trade-off.")
> 2. **Omitted-option objection**: "Both options ignore [Z]. If Z were on the table, the math changes." (e.g., "Both ATB and top-step ignore targeted role-family adjustment. A surgical lift on meat cutters only might cost $1.8M and beat both options on retention ROI.")
> 3. **Time-horizon objection**: "The question is one-cycle. If the next 2-3 cycles are considered, [the structurally-locked option / the reversible option] looks materially different." (e.g., "Top-step addition locks structure for ≥3 cycles; ATB is annual. The right choice depends on whether next year's envelope tightens.")

These three objections become **constraints on the persona blocks**: each persona's reasoning must address at least one of them explicitly. Personas that ignore all three are flagged in synthesis as having stayed in the comfortable framing.

If the question is genuinely narrow (one-shot, scope-locked, time-locked), surface that explicitly: "Adversarial pre-pass found no material framing objections — question is well-bounded." Do not fabricate objections to fill the slots.

### Step 4. Per-persona grounding (live fetch, asymmetric)

Each persona triggers **one targeted live source fetch** before writing its block. The grounding is asymmetric — no two personas hit the same source — to maximize the diversity of evidence the council surfaces.

| Persona type | Default grounding source | Tool |
|---|---|---|
| `employment-lawyer` | The actual statute / CBA article being cited | `web_fetch` against `legisquebec.gouv.qc.ca` / `laws-lois.justice.gc.ca` / `canlii.org` (mandatory for any `[statutory]` claim — see § Statutory discipline below) |
| `total-rewards-strategist` | A market data point relevant to the philosophy claim | `mcp__market__get_role_intelligence` or `mcp__market__compare_roles` |
| `cfo-finance` | A cost-of-capital / finance reference (sectoral comp-to-revenue ratio, EBITDA-impact comparable) | `web_search` + `web_fetch` against StatCan, sectoral surveys, or competitor 10-K / annual report |
| `hr-business-partner` | A comparable-company case (recent comp change at a peer with reported aftermath) | `web_search` + `web_fetch` against careers page, press release, or industry publication |
| `dei-pay-equity` | The actual pay-equity statute text or a published predominance methodology | `web_fetch` against the statute URL or CCDP / CDPDJ guidance page |
| `employee-union` | The actual CBA bulletin or the local union's news page | `web_search` + `web_fetch` against the local's site |
| `ceo-board` | A recent named competitor's strategic comp signal (board statement, IR call snippet, executive-comp filing) | `web_search` + `web_fetch` against IR / SEC / SEDAR+ page |
| `<custom-persona-id>` | Resolved from the persona's `default_grounding_source_type` field per `references/persona-library.md` § Grounding source types | Tool selected by source type (e.g., `actuarial-valuation-report` → user upload; `competitor-careers-page` → `web_fetch`) |

Surface the source assignment after the adversarial pre-pass:

> Per-persona grounding (one live fetch each, no overlap):
> - employment-lawyer → `web_fetch` Loi sur l'équité salariale art. 76.1
> - total-rewards-strategist → Market MCP `compare_roles` for QC retail meat-cutter top step
> - cfo-finance → `web_fetch` StatCan grocery-sector labour-cost ratio (Table 33-10-XXXX)
> - hr-business-partner → `web_fetch` Loblaws career-page rate change Q1 2026
> - dei-pay-equity → `web_fetch` CCDP guidance on systemic gap remediation in unionized scope

Run the fetches before writing any persona block. The fetched text + URL becomes the persona's primary citation. Two failure modes to avoid:

1. **No two personas share a source.** If the lawyer and DEI persona both want to fetch the same Loi sur l'équité salariale article, reassign one to a different evidence base (e.g., DEI fetches CCDP guidance instead) so the council surfaces two different evidence streams.
2. **Skip a fetch only when the persona's contribution is genuinely lens-only** (no factual claim). Most persona contributions include at least one factual claim; the fetch is the rule, not the exception.

Failed fetch (404, paywall, content unavailable) → fall back to `web_search` for an equivalent source from a different domain, then `web_fetch` that. If both fail, the persona writes its block but tags every claim it would have grounded as `[professional-judgment]` rather than `[market-data]` or `[statutory]`. Note the failed-fetch attempt in the persona block's `flags_raised` so synthesis surfaces the gap.

### Step 5. Persona voice blocks

One block per persona, in the order declared. **The Position line is the first content of the block** — written before any reasoning — to lock in the persona's stance up front and prevent rationalization-after-the-fact (the failure mode that produces unanimous synthesis from diverse personas). Each block:

```markdown
## [Persona Name]

**Position** (write FIRST, before any reasoning): [1-2 sentence recommendation in this persona's voice]

---

**Lens**: [one-line framing]

**Live source consulted**: [URL + access date for web_fetch grounding, or tool call descriptor for Market MCP grounding]

**Key reasoning**:
- [Point 1 with confidence tag — must address adversarial-pre-pass objection 1, 2, or 3 if applicable]
- [Point 2 with confidence tag]
- [Point 3 with confidence tag]

**Adversarial objection addressed**: [which of the 3 pre-pass objections this block engaged with, in 1 sentence]

**What I weigh heavily**: [the trade-off this lens refuses to accept]

**What I would flag for legal / finance / founder**: [any hard stop or verification item]
```

Keep each block to 120-200 words. Longer blocks dilute. Do not let one persona reference another persona by name mid-block — personas speak in parallel, not in dialogue. The Position line is non-negotiable: write it first, on its own line, before drafting any of the supporting reasoning. Reasoning that does not match the position is the failure signal — rewrite the position OR rewrite the reasoning, not both at once.

### Step 6. Synthesis

After all persona blocks, return to orchestrator voice and produce the synthesis per the style specified in config (`synthesis_style`). Default: `consensus-tensions`. The synthesis must explicitly call out which adversarial-pre-pass objections the council engaged with and which it left unresolved — orphaned pre-pass objections are themselves a finding.

### Step 7. Mode-specific output

- `reasoning` mode: stop after synthesis. The full persona + synthesis text IS the deliverable.
- `memo` mode: follow synthesis with a separate memo block (see Memo Template below).
- `integrated` mode: follow synthesis with an Integration Handoff block that names which phase the council feeds into and what it contributes (see Integrated Handoff below).

### Step 8. State file

After output completes, produce the `council-state-YYYY-MM-DD-{slug}.yaml` artifact. Council-state is **council scratch — a local non-schema artifact** (per `references/persistence-and-ledger.md` § Where each thing lives): write it to `$STATE_ROOT/_orgs/<slug>/...` alongside the engagement's other local scratch. For standalone council runs (no engagement slug), write to a session-tagged local path under `_orgs/_council-standalone/<derived-slug>/`. Council-state is never written to the `market` backend — only schema-shaped state (engagement bodies, cycles, the decision log) persists over the wire.

Next year's R-lite reads the engagement body from the backend (`engagement_get` + `engagement_get_master`) and the `council-state` scratch from the local `$STATE_ROOT` cache for full reasoning continuity.

## Synthesis styles

### consensus-tensions (default)

```markdown
## Synthesis

**Consensus** (all personas or 4+ of N agree):
- [claim with confidence tag]
- [claim with confidence tag]

**Tensions** (personas disagree — name the disagreement):
- [Persona A] prefers X because [reason]; [Persona B] prefers Y because [reason]. The underlying trade-off is [what is actually being traded].

**Single-source claims** (only one persona raised this — verify before weighting):
- [claim] — only [Persona]

**Unresolved** (council surfaced but did not settle):
- [question the user or a follow-up research task must answer]

**Recommended path**:
[2-4 sentence articulation of the path the synthesis supports, acknowledging the remaining tension the user must own.]
```

### vote-count

Used when the question has 2-3 named options. Tally persona votes, note the split, articulate which option survives the strongest objection.

### severity-triage

Used when the council is evaluating a proposed action (not choosing between options). Personas flag concerns; synthesis ranks CRITICAL / HIGH / MEDIUM / LOW and lists blockers before proceeding.

## Memo template (memo mode)

Following synthesis, produce a standalone memo block. Voice: practitioner, peer-tone, no jargon-explanations. Length cap: 800 words default (override via `council.memo_format.length_cap_words`).

```markdown
---
# DECISION MEMO

**Date**: YYYY-MM-DD
**Client / Engagement**: [from config org.name]
**Question**: [one-sentence question from Step 1]
**Audience**: [from config audience.archetypes, matching id if specified]

## Situation

[2-3 paragraphs. What decision is on the table. Why it matters now. What constrains it. Pull from the engagement config where set — pay philosophy, governance, scope.]

## Options

**Option A — [name]**
[2-3 sentence description. Cost range. What it optimizes for.]

**Option B — [name]**
[2-3 sentence description. Cost range. What it optimizes for.]

**Option C — [name]**  (if applicable)
[2-3 sentence description. Cost range. What it optimizes for.]

## Recommendation

[The recommended path, in 2-4 sentences, with the trade-off named honestly. Cite the persona consensus that supports it.]

## Risks

- [Risk 1 — which persona raised it, severity]
- [Risk 2 — which persona raised it, severity]
- [Risk 3 — which persona raised it, severity]

## Unresolved

- [Open question the user must answer before execution]
- [Verification item — what needs legal / finance / data confirmation]

## Next Step

[The concrete next action: approve, pilot, verify, escalate.]
```

## Integrated handoff (integrated mode)

When council runs inside a consulting engagement and feeds back into Phase 4 or 5, produce a handoff block instead of (or in addition to) a memo:

```markdown
## Council → Phase [N] Handoff

**Feeds into**: [Phase 4 — Option Modeling | Phase 5 — Narrative Workshop]

**What council contributes**:
- [Scenario constraint the council narrowed to: "only B and C are on the table after council; A was rejected on [grounds]"]
- [Narrative anchor: "the decision ask should be framed as [risk-first / retention-first / equity-first] per council consensus"]
- [Slide count delta: +1-3 strategic framing slides justified by council tensions]

**Carry-forward assumptions**: [list the `[assumption]`-tagged claims the user should validate before the deck goes out]
```

## `council-state` output schema

At the end of every Council session, produce a YAML artifact. Naming: `council-state-YYYY-MM-DD-{client-slug}.yaml`.

```yaml
# council-state — produced at Council session completion, saved by user
council:
  date: 2026-04-21
  client: "[from config org.name]"
  engagement_ref: "[engagement-state filename if this council ran inside an engagement, else null]"
  mode: reasoning   # reasoning | memo | integrated
  synthesis_style: consensus-tensions

question:
  text: "Given a $4.2M envelope for QC retail, ATB 2.5% or new top step at +3% with 1.5% ATB?"
  what_is_being_decided: "Allocation method within the approved envelope"
  what_is_not_being_decided: "The envelope size, the effective date, the scope of roles"

adversarial_pre_pass:
  - id: 1
    type: premise
    objection: "The question assumes the envelope is fixed at $4.2M. If the board would approve $5M for a defensible retention case, top-step + larger ATB becomes viable and changes the trade-off."
    addressed_by: [cfo-finance, total-rewards-strategist]
  - id: 2
    type: omitted-option
    objection: "Both options ignore targeted role-family adjustment. A surgical lift on meat cutters only might cost $1.8M and beat both options on retention ROI."
    addressed_by: [hr-business-partner]
  - id: 3
    type: time-horizon
    objection: "Top-step addition locks structure for ≥3 cycles; ATB is annual. The right choice depends on whether next year's envelope tightens."
    addressed_by: [cfo-finance, employment-lawyer]
    orphaned: false   # set true if no persona engaged it; surface in synthesis as unresolved
  pre_pass_finding: "Three live objections; all engaged."   # or "Well-bounded — no material objections."

per_persona_grounding:
  employment-lawyer:
    source_type: statute
    url: "https://www.legisquebec.gouv.qc.ca/fr/document/lc/E-12.001"
    fetched_at: 2026-04-21T14:08:00
    article_quoted: "art. 76.1 — L'employeur doit, tous les cinq ans, évaluer le maintien de l'équité salariale dans son entreprise."
    fetch_status: success   # success | failed
  total-rewards-strategist:
    source_type: market_mcp
    tool_call: "compare_roles(roles=[meat-cutter], provinces=[QC, ON])"
    # When a market_mcp grounding row returns SUPPRESSED or thin coverage (confidence_tier),
    # carry that into the claim's tag so a low-coverage row down-weights the claim in synthesis.
    called_at: 2026-04-21T14:09:00
    fetch_status: success
  cfo-finance:
    source_type: web_fetch
    url: "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=33100XXXX"
    fetched_at: 2026-04-21T14:10:00
    fetch_status: success
  # ... etc per persona; record fetch_status: failed and fallback URL when applicable

perspectives_run:
  - employment-lawyer
  - total-rewards-strategist
  - cfo-finance
  - hr-business-partner
  - dei-pay-equity

persona_outputs:
  employment-lawyer:
    position: "Prefers top-step addition. Reduces compression liability under QC pay equity maintenance (art. 76.1)."
    confidence_tag_counts: { statutory: 3, statcan-wage: 0, live-postings: 0, cba: 0, professional-judgment: 2, assumption: 0 }
    statutory_downgrades: 0   # claims tagged [statutory] in draft that lacked a fetch + quote, downgraded to [professional-judgment] in synthesis
    objections_addressed: [3]
    flags_raised: ["Verify TUAC 501 reopener clause before committing to top-step structural change"]
  total-rewards-strategist:
    position: "..."
    confidence_tag_counts: { statutory: 0, statcan-wage: 2, live-postings: 2, cba: 0, professional-judgment: 2, assumption: 1 }
    statutory_downgrades: 0
    objections_addressed: [1]
    flags_raised: []
  # ... etc per persona — use the full 11-tag set; zero-counts allowed

synthesis:
  consensus:
    - "Do-nothing creates measurable retention risk in top quartile"
    - "Minimum wage encroachment pressure is low this cycle (QC entry $16.85 vs $16.10 min)"
  tensions:
    - description: "Lawyer + DEI favor top step; CFO favors ATB"
      underlying_tradeoff: "Compression remediation durability vs. cost-recovery flexibility"
  single_source_claims:
    - claim: "Top-step addition may trigger TUAC 501 reopener"
      source_persona: employment-lawyer
      verification_needed: true
  unresolved:
    - "Confirmation of TUAC 501 reopener language"
    - "Whether next-cycle budget tolerates a locked-in new top step"
  recommended_path: "Hybrid: new top step at +3% + 1.5% ATB, contingent on legal review of TUAC 501 reopener clause"

feeds_into:
  phase_4: "Narrows Phase 4 to Scenarios B (top step only) and B+ (hybrid). Scenario A (pure ATB) withdrawn per council."
  phase_5: "Narrative anchor: retention-first framing with compression remediation as the controlling risk."

outcome:
  adopted: null          # yes | partial | no | null (pre-decision)
  adopted_path: null     # user fills after decision
  modifications: null    # how the adopted path differed from the recommendation
  lessons: null          # free text for next cycle

# outcome block is the highest-value field. User fills after the decision lands.
```

## Anti-patterns

Avoid in council sessions:

1. **Personas agreeing too quickly** — if all 5 personas reach identical conclusions in the first pass, the question was not genuinely contested. Either the council is wasted (answer directly) or personas collapsed into one voice. Re-run with sharper persona lens. The adversarial pre-pass (Step 3) is the upstream defense — if pre-pass surfaces no real objections AND personas converge, the question was indeed well-bounded; if pre-pass surfaces three real objections AND personas converge anyway, that's the failure mode.
2. **Synthesis that flattens tensions** — "all perspectives agree with minor variations" is almost always wrong. If synthesis reads like unanimous consent, go back and surface the disagreement the personas were actually papering over. Use the adversarial-pre-pass objections as the litmus: if synthesis claims consensus on a question that pre-pass framed as having three live objections, name which objections were dismissed and on what grounds.
3. **Skipping the adversarial pre-pass** — the pre-pass is non-negotiable. Without it, persona blocks rationalize toward the question's framing rather than contending with its premises. Use the pre-pass at all three modes (reasoning / memo / integrated) — including integrated mid-engagement councils.
4. **Two personas hitting the same source** — defeats the asymmetric-grounding purpose. Reassign one persona to a different evidence base (different domain, different statute, different market data slice).
5. **Position written after reasoning** — the position-before-reasoning lock is the structural defense against rationalization-after-the-fact. If a persona's position was edited to match its reasoning rather than the other way around, the block is invalid — rewrite from the position down.
6. **Unsourced `[statutory]` tags** — auto-downgrade to `[professional-judgment]`. See § Statutory discipline above. Uncited `[statutory]` is the highest-impact council failure because it travels into the deck and into the decision memo where it gets re-cited as gospel.
7. **Memo longer than 800 words** — memos are read under time pressure. If you need more room, the synthesis was not compressed enough.
8. **Running council on data questions** — "what does market pay for X" does not need a council. Use Phase 2 tools directly.
9. **Dropping a persona after it surfaces uncomfortable findings** — the persona's job is to raise what the others would miss. The discomfort is the signal.
10. **Not writing `council-state`** — without the state file, the reasoning is irrecoverable. The state file is the reproducibility mechanism — produce it every time, not just in memo mode.

## Quality gate

Before declaring a Council session complete, verify:

- [ ] Question stated, including what is NOT being decided
- [ ] **Adversarial pre-pass produced 3 objections (or explicit "well-bounded — no material objections" finding)**
- [ ] **Per-persona grounding assigned — no two personas share a source; live fetches executed before blocks written**
- [ ] 4-6 personas ran — no fewer, no more unless user explicitly asked
- [ ] **Every persona block opens with its Position line, written before any reasoning**
- [ ] Every persona produced a position + key reasoning with confidence tags
- [ ] **Each persona block addresses at least one adversarial-pre-pass objection (or explicitly states "objections do not apply to this lens")**
- [ ] **Every `[statutory]` tag has a fetched URL + quoted article text in the same line; otherwise downgraded to `[professional-judgment]` with a "(downgraded — no statute fetch)" note**
- [ ] **Every source-tagged claim (`[statcan-wage]`, `[live-postings]`, `[cba]`, `[indeed-company]`, `[econometric]`, `[survey-house]`, `[user-provided-cba]`, `[statutory]`, `[market-data]` web-fallback) names its required verification artifact per `references/tools-available.md` § Verified-source discipline**
- [ ] Synthesis shows consensus AND tensions (not unanimous consent)
- [ ] **Synthesis explicitly addresses each adversarial-pre-pass objection — engaged or unresolved (orphaned objections are themselves a finding)**
- [ ] Unresolved items are named, not elided
- [ ] Recommended path acknowledges the trade-off it is making
- [ ] Mode-specific output produced (reasoning stops here; memo adds memo block; integrated adds handoff)
- [ ] `council-state-YYYY-MM-DD-{slug}.yaml` produced and offered to the user
- [ ] **`council-state` records the pre-pass objections, per-persona grounding sources (URL + access date or tool call), and any `[statutory]` downgrades**
