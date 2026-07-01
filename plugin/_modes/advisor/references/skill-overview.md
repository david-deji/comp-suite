# Skill Overview — Phase Map, Phase 0 Protocol, Core Principles

Loaded by SKILL.md when a phase needs the full phase map, the Phase 0 config-loading protocol detail, or the cross-deliverable core principles. Not a first-time-user document — for that, see `references/colleague-onboarding.md`.

---

## Full phase map

Every engagement track (C, D, R, R-lite) flows through Phase 0 (Config Loading) plus 7 phases. Each phase has a checkpoint that blocks the next phase until the user explicitly confirms.

| Phase | Purpose | Checkpoint | Artifact (END or interim) | Reference file |
|-------|---------|-----------|---------------------------|----------------|
| 0 — Config Loading | Parse pasted engagement-config YAML; identify which sections are populated; note which phases can skip prompts | (autonomous; loaded summary shown) | (none — loaded-config summary chat-only; backend mode + ledger context surfaced) | `references/engagement-config-template.md` |
| 1 — Discovery | 5-beat peer interview: trigger, audience, hypothesis, constraints, brief — **skip Beat 2 if `audience` config matches** | A — engagement brief confirmed | Confirmed engagement brief (in-memory; auto-checkpointed to `checkpoint.yaml` at Checkpoint A) | `references/consulting-protocol.md` |
| 2 — Data Gathering | Parse Excel, classify pay structures, pull market data via Market MCP, compute derived metrics | (autonomous; validation summary shown) | Validated dataset + appended `tool_calls[]` entries (per-MCP/web call) into engagement-state | `references/consulting-protocol.md` |
| 3 — Interpretation | Present 2-3 headline findings, integrate org context, push back when data contradicts hypothesis | B — anything else to factor in | Confirmed interpretation (in-memory; auto-checkpointed at Checkpoint B with running `tool_calls[]`) | `references/consulting-protocol.md` |
| 4 — Option Modeling | Do-nothing baseline + 2-3 costed scenarios with side-by-side comparison | C — chosen direction or blend | Chosen scenario direction; `selection_log[]` entry appended; auto-checkpoint at Checkpoint C | `references/costing-engine.md` |
| 5 — Narrative Workshop | Build Situation → Tension → Resolution arc, layer audience psychology, produce NARRATIVE FRAME block | D — argument arc confirmed | NARRATIVE FRAME block (chat); auto-checkpoint at Checkpoint D | `references/consulting-protocol.md` |
| 6a — Section Plan | Propose 6-section deck spine; confirm sections, slide counts, audience adjustments | (lightweight confirmation) | Confirmed section plan (in-memory) | `references/production-and-qa.md` |
| 6b — Per-Section Choice Loop | For each section: describe intent, present 2 framing options with pros/cons (no static recommendation — see § Recommendation discipline in production-and-qa.md), build approved direction, show preview, move on. Track D runs silent. | E — each section confirmed before next | Per-section `selection_log[]` entry appended; section preview chat-only until 6c | `references/production-and-qa.md` |
| 6c — Final Assembly | Concatenate section fragments into final .pptx; generate secondary artifacts | (autonomous) | **`.pptx` file artifact** (always); `cost-scenarios.xlsx` and/or `market-data.csv` when `deck.artifacts` requests them | `references/production-and-qa.md` |
| 7 — QA Loop | 8-dimension QA (7 mechanical + 1 adversarial — self-generated audience objections checked against slide coverage), present deck with QA summary, route revision requests back to appropriate phase | User accepts or re-enters earlier phase | **Close-time close-time write sequence**: `engagement-state.yaml` (closed), all deliverables to `engagements/<slug>/deliverables/`, stub append to `ledger/outcome-history.yaml`, delete `checkpoint.yaml` | `references/production-and-qa.md` + `references/persistence-and-ledger.md` § Session end |

Full artifact catalog (filenames, gating per artifact, owning protocol): `references/artifact-generation.md` § Artifact Catalog.

---

## Phase 0 — Config Loading (engagement tracks: C, D, R, R-lite)

Before entering the consulting flow, scan the user's first message for a YAML code block matching the engagement-config schema. If present:

1. Parse the block. Validate required keys per section (see `references/engagement-config-template.md` § Validation rules).
2. For each populated section, note `last_verified` age. Warn if >180 days old (or >60 days for `cycle`).
3. **For `engagement_scope`**: confirm the budget owner is named. If `budget_owner_role` references multiple budget owners or is missing, surface immediately — strongest signal of a malformed engagement.
4. **For `cycle`**: compute the gap between `current_week_offset` and `effective_date`. If today's date implies a different week offset, ask the user to confirm or correct. Surface `last_cycle.headline_decision` and `this_cycle_goals.primary_objective` in the loaded-config summary so they're visible from turn 1.
5. Report parsed sections and gaps:
   ```
   Loaded engagement config:
   - engagement_scope: ✓ (Pharmacy FY26, owner: VP Ops Pharmacy)
   - cycle: ✓ (May cohort, week -10, "Discovery")
   - org: ✓
   - audience: ✓ (3 archetypes)
   - costing: ✓
   - benchmark: ⚠ stale (218 days)
   - deck: ✗ not provided

   Last cycle: 3% ATB + meat-cutter compression fix ($3.8M, May 2025).
   This cycle's primary objective: close pharmacy assistant gap to P50,
   envelope ceiling $4M.

   Will skip: Beat 2 audience questions, Phase 4 costing input prompts.
   Will prompt at the relevant phases: deck preferences, benchmark refresh.
   ```
6. Hold the parsed config in conversation context. Each phase reads its section as needed.

If no YAML block is in the first message, proceed to the appropriate track entry point. Each phase prompts for its inputs at activation. **If the engagement looks substantial (Track C or R) and no `engagement_scope` was provided, surface the budget-owner question early** — Phase 1 Beat 1 is the natural place: "Who's the budget owner — single, or are we trying to cover multiple?"

If the user is new to the skill and config-curious, suggest Init mode at the end of the engagement: "If you'll run engagements like this regularly, `/init` builds a reusable config so you don't answer these questions again. Or `/help` to see the full command list."

---

## Core principles across all deliverables

### Data integrity

- Always cite data sources (survey name, year, cut, percentile)
- Distinguish between base salary, total cash, and total direct compensation
- State the aging/trending methodology when comparing data across time periods
- Flag where sample sizes are small or data is interpolated

### Audience calibration

- **Board / C-suite**: Lead with strategic implications, keep to 6-10 slides, emphasize risk and competitiveness
- **HR leadership**: Balance strategy with methodology, include options and trade-offs
- **HR ops / comp team**: Full methodology, data tables, implementation details
- **Employees**: Plain language, focus on "what this means for you," no jargon

### Analytical standards

- Default market positioning reference is P50 (median) unless the user specifies otherwise
- When comparing across geographies, note whether data is geo-adjusted or national
- Use consistent job matching criteria (scope, level, industry, revenue size)
- Present ranges as min-mid-max or P25-P50-P75 depending on context

### Wage scale competitiveness

When the user provides a pay scale or wage grid:

- Use `mcp__market__compare_pay_scale_to_market(role, province, steps, band_min, band_max, rate_type)` as the primary tool — it returns entry vs P10/P25 (entry-rate floor check), top vs P75/P90 (top-step ceiling check), middle steps vs P50, sub-step verdicts, and an overall competitiveness flag in one call. It computes against all five percentiles internally (P10 is the effective floor for the min-wage compression check, P90 the effective ceiling) — there is **no** `percentiles` argument to pass (unlike `get_role_intelligence`, which does accept one).
- Use `get_cba_wage_scale` to anchor unionized scales against negotiated rates (mandatory for UFCW grocery, construction, healthcare, public sector)
- Compute compa-ratios: Internal Pay / Market P50
- Classify each role: **Below Market** (<0.95), **At Market** (0.95-1.05), **Above Market** (>1.05)
- Assess overall scale positioning and flag any systemic patterns
- Identify roles with highest attrition or recruitment risk (cross-reference Indeed `get_company_data` for competitor pay)
- Produce actionable recommendations

### Formatting defaults

- Currency: Use the currency appropriate to the market being analyzed (CAD for Canadian, USD for US, etc.)
- Tables: Always include role title, benchmark source, percentile, and internal vs. market delta
- Charts: Use bar or waterfall charts for gap analysis; scatter plots for regression-based equity analysis
- Callout stats: Use large-number callouts (60-72pt) for key figures

### Push-back behavior

When data contradicts the user's requested narrative or hypothesis: present both angles with implications and let the user decide. Do not silently comply with a narrative the data does not support. Frame it as: "The data shows X, which supports angle A. Your initial framing was angle B. Here's the case for each — which direction do you want to take?"
