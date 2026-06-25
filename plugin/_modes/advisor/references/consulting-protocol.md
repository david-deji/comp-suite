# Consulting Protocol — Phases 1, 2, 3, 5

Loaded by SKILL.md when running the consulting conversation (Tracks C and R). Phase 4 (Option Modeling / Costing) is in `references/costing-engine.md`. Phases 6-7 (Production / QA) are in `references/production-and-qa.md`.

This is the core of the skill. Run a 7-phase consulting engagement before producing any slides.

**Artifact discipline through Phases 1-5**: no PPTX or formal deliverable artifacts during the consulting back-and-forth — that's chat text. But the engagement carries two **structural artifacts** that update continuously and travel with the engagement:

- `engagement-state.yaml` — full audit trail (selections, tool_calls[], scenario picks, narrative frame). Auto-checkpoints at each phase boundary per `references/persistence-and-ledger.md`.
- `checkpoint.yaml` — pointer for resume mid-engagement.

These are not "shown to the user" inline as code blocks during conversation, but they ARE the persistent record of the engagement and survive across sessions. The first **END deliverable artifact** is the section-by-section .pptx in Phase 6b/c.

When `/council` runs as part of an engagement, it adds a third structural artifact: `council-state-{date}.yaml` (one per council invocation, every council). Standalone `/council` runs (outside an engagement) produce the council-state YAML as their END deliverable.

Each phase has a named checkpoint where the user explicitly confirms before advancing. If the user does not confirm, stay in the current phase.

---

## Cycle-stage gating (pre-phase, symmetric)

Before entering Phase 1 (or any phase), check `current_week_offset` against the
canonical stage spine. Two symmetric rules apply.

### Too-late rule (post-launch)

When `week_offset ≥ 0` (the new wage scale is live or past launch), decline new
strategy work for that cohort. The work has moved to payroll execution support;
new strategy at this point creates whiplash and contradicts a freshly-published
wage scale. Surface the conflict and recommend deferring to the next cycle.

Exception: corrections to a known error in the just-launched scale are NOT
strategy work — proceed but flag the correction shape (`engagement_mode:
data-light-decision` or similar).

### Too-early protocol

When `current_week_offset < target_stage_offset − 4` (the user is asking for
canonical work more than 4 weeks ahead of its scheduled stage), do NOT silently
run the canonical work. Surface a pre-engagement mode menu:

> "You're at week [W] but [DELIVERABLE] is canonically a week [TARGET_W]
> deliverable. Five options:
>
> A. **Pre-engagement narrative-frame**: 5-8 slide pre-read framing the
>    decision space, no costing. Mode: `narrative-frame-only`.
>    Schema: `pre_engagement_only: true`.
> B. **Data-light decision brief**: 1-page paragraph for the audience, no
>    deck. Mode: `data-light-decision`.
> C. **Wait for the spine**: defer to week [TARGET_W]. I'll save context.
> D. **Build the canonical [DELIVERABLE] anyway**: I'll flag in the
>    engagement-state that we're outside the canonical window and the closed-
>    engagement ledger should treat this as off-cycle.
> E. **Different deliverable**: tell me what you actually need and I'll route."

Wait for selection. Apply the chosen mode (per `references/engagement-modes.md`)
and append a `decision_log` entry with `decision_type:
too_early_pre_engagement_mode_chosen`.

### Mode handoff

If the user selects A, B, or E (anything that produces a pre-engagement
artifact rather than a canonical engagement), set `pre_engagement_only: true`
in engagement-state and route the artifact to
`master.advisor.pre_engagement_artifacts[]` per `references/master-yaml-ops.md`,
NOT to `cycle_state_pointers[]`. Drift-trajectory queries on the closed-
engagement ledger ignore `pre_engagement_artifacts[]` entries.

---

## Phase 1 — Discovery (2-4 turns)

Conduct discovery using 5 beats in a peer-to-peer tone. The user is a senior comp practitioner — use practitioner shorthand, assume domain fluency. Never phrase questions as tutorials. Surface your own hypotheses for the user to react to rather than asking open-ended questions with no anchor.

**Config-aware shortcuts** (when Phase 0 loaded an engagement-config):
- If `org` section provided: skip "what's your industry / banner / governance" probes; cite the loaded values when relevant.
- If `engagement_scope` section provided: skip Beat 1's budget-owner sub-question; cite the loaded `budget_owner_role` and confirm scope. If the user's framing in this engagement seems to spill outside `in_scope_role_families` or `out_of_scope`, surface the mismatch.
- If `cycle` section provided: open with cycle context — "We're at week [N] before [effective_date], in stage [current_stage]." Frame the discovery questions accordingly. If `cycle.last_cycle.headline_decision` is populated, ground Beat 1 in it: "Last cycle was [headline_decision]. What's different this time?"
- If `audience` section provided: at Beat 2, ask "Which audience archetype: [list ids from config]?" instead of full Beat 2 interview. Still ask Beat 2's "what they already believe" sub-question if the archetype's `beliefs` field is stale (>180 days) or the user signals it's changed.
- If `pay_philosophy` is in `org`: cite it in Beat 5 engagement brief instead of asking.

**Beat 1 — Trigger and scope** (1-2 questions, open-ended):
Ask what is driving this engagement. Pattern: "What's driving this? Board request, retention problem, annual cycle, something else?"
- Do not offer multiple choice. Let the user describe it.
- If the answer is vague, probe: "You mentioned retention — which roles, and do you have turnover data pointing to pay as the driver?"
- **If `engagement_scope` was not pasted in the config**: also ask "Who's the budget owner for this work — a single VP Ops, or are we covering multiple?" If the user names two, push back once: "Two budget owners usually means two engagements. Want to scope to one, or proceed knowing you'll likely split later?" Strong nudge, not a hard gate — accept the override and continue.
- **If `cycle` was not pasted**: ask "What cycle is this — what's the effective date for the new wage scale, and roughly where are we in the workback?" Use the answer to anchor the rest of discovery.

**Beat 2 — Audience + Decision** (1-2 questions):
Ask who sees the deck and what they need to decide. Pattern: "Who sees this deck and what do they need to decide? And what do they already believe about pay?"
- "What they already believe" is critical — it determines whether the deck confirms or challenges assumptions.
- When `audience.archetypes[]` is populated in the engagement-config (per `references/engagement-config-template.md` § audience), match the user's answer to an existing `id` and pre-fill the archetype's `beliefs`, `typical_objection`, and `preferred_framing`. Skip Beat 2's full interview unless the matched archetype's `last_verified` is stale (>180 days) or the user signals it's changed.
- If audience is board/comp committee: note risk-first framing is likely needed (or the matched archetype's `preferred_framing`).
- If audience is CHRO/SVP HR: note strategy-with-options framing is likely needed.
- If audience is HR ops: note implementation-detail framing is likely needed.

**Beat 3 — Hypothesis** (1 question):
Ask for the user's gut read. Pattern: "What's your gut? What do you think the data will show?"
- This is the most important discovery question. The hypothesis shapes whether the deliverable confirms or challenges.
- If the user has a strong hypothesis, test it against data in Phase 3.
- If the user says "I don't know," note the exploratory framing and proceed.

**Beat 4 — Constraints** (1 question):
Ask what is off the table. Pattern: "What's off the table? Budget caps, union restrictions, recent decisions, frozen headcount?"
- Compress if the user already surfaced constraints in earlier beats.

**Beat 5 — Engagement Brief** (1 confirmation):
Synthesize beats 1-4 into a 3-5 sentence engagement brief. Pattern: "So the engagement is: [synthesis]. Does that track, or should the deck tell a different story?"
- The brief must include: budget owner and scope, cycle context (cohort + week-offset + current stage if known), trigger, audience + their current beliefs, the user's hypothesis, key constraints, and the implied narrative direction.
- Example: "So the engagement is: Pharmacy FY26 (VP Ops Pharmacy as budget owner), May cohort, week −10, currently at Discovery (canonical stage; if your config overrides the label via `cycle.stages` — e.g., 'Strategy Kickoff & Market Review' — use your override). Driven by pharmacy-assistant turnover doubling since last cycle. Audience is the comp committee; they currently believe pharmacy is paying competitively. Your hypothesis: we're 6-8% behind market on assistants, and the fix is roughly $1.5M. Constraint: $4M envelope ceiling. The deck should make the case for closing the gap and frame the cost as retention-driven."
- Wait for explicit confirmation before proceeding.

**Checkpoint A**: "Here's my understanding of the engagement. Correct?" Block Phase 2 until confirmed.

**Auto-checkpoint on confirmation**: when the user confirms the engagement brief, call `engagement_put` (with `expected_version`) per `references/persistence-and-ledger.md` § /checkpoint command. Set `saved_at_phase: 1`, capture the confirmed `engagement_brief`, all populated `prior_engagement_refs` from Phase 0, and any `selection_log` entries (typically empty at this point). Silent unless write fails.

### Track R Adaptation (Prior Deck Uploaded)

When the user uploaded a prior-year .pptx, compress beats 1-4 into a single question:

1. Parse the uploaded PPTX via `markitdown`. Extract the prior narrative frame: situation, key findings, recommendation, decision ask.
2. Present the prior narrative: "Last year's deck argued [extracted narrative]. Anything changed since then — new roles, exits, budget shifts, strategic changes, union developments?"
3. If the answer is "no, just update numbers": proceed with prior narrative as default. Still run Phase 3 interpretation with a lighter checkpoint: "Anything in these updated numbers surprise you or change the story?"
4. If substantive changes: enter full beats 2-4 for the changed elements, treating the prior deck narrative as baseline context.

**Phase 1 output**: Confirmed engagement brief (chat text).

---

## Phase 2 — Data Gathering (autonomous)

Pull data shaped by the engagement brief. No user interaction unless data is missing or ambiguous.

**Config-aware shortcuts** (when `benchmark` section loaded):
- Use `default_percentiles`, `default_province`, `include_economic_regions` directly — do not prompt.
- Pre-resolve role aliases from `role_aliases` map before calling `search_roles` (skips fuzzy matching for known mappings).
- If `cba_lookup_required_for` is populated, auto-trigger `get_cba_wage_scale` for matching role categories.
- Pre-populate Indeed `get_company_data` calls with `peer_companies`.
- Use `source_priority` to determine fallback order.

### 2a. Parse Uploaded Excel

Read the uploaded Excel (.xlsx, .xls) or CSV using Python `openpyxl` or `pandas`. Identify the header row and map columns to canonical fields using fuzzy matching against known aliases:

| Canonical Field | Known Aliases |
|---|---|
| `role_title` | Job Title, Role, Position, Titre du poste, Titre, Job Family |
| `grade` | Grade, Level, Band, Echelon, Niveau, Classification |
| `headcount` | Headcount, HC, # Employees, FTE, Effectif, Nombre |
| `current_pay` | Current Pay, Avg Pay, Midpoint, Rate, Salary, Taux, Salaire |
| `pay_type` | Type, Pay Type, Hourly/Salary, H/S |
| `classification` | Classification, Job Class, Classe d'emploi, Union Class |
| `current_step` | Step, Echelon, Palier, Current Step |
| `weekly_hours` | Weekly Hours, Hrs/Week, Heures/Semaine, Standard Hours |
| `ft_pt` | FT/PT, Full-Time/Part-Time, Status, Statut |
| `performance_rating` | Performance, Rating, Perf Rating, Cote, Evaluation |
| `band_min` | Band Min, Range Min, Minimum, Min Salarial |
| `band_mid` | Band Mid, Range Mid, Midpoint, Point Milieu |
| `band_max` | Band Max, Range Max, Maximum, Max Salarial |

Present the column mapping for user confirmation: "I mapped 'Titre du poste' → role_title, 'Taux horaire' → current_pay (hourly). Confirm?"

If the workbook has multiple sheets, list sheet names and ask which to use. If one sheet is obviously the data sheet (largest row count, salary-like columns), suggest it.

### 2b. Pay Type Detection (hourly vs salary)

Determine whether each row is hourly or salaried. Detection priority:
1. Explicit `pay_type` column present — use it.
2. Column header contains "hourly" or "horaire" — hourly; "salary" or "salaire" — salary.
3. All values < 200 — infer hourly; all values > 10,000 — infer salary.
4. Mixed or ambiguous — ask: "I see values ranging from $22 to $85,000. Which rows are hourly vs salaried?"

Every row must have an assigned `pay_type` before computation begins.

### 2c. Pay Structure Classification (step vs merit vs flat)

Classify each role. **Config-key precedence**: when the engagement-config provides a `pay_structure` hint for the role (via `org.union_landscape` implying step for unionized roles, or via a per-role mapping in `org` if the analyst has captured one — see `references/engagement-config-template.md` § org for the schema), use that as the first detection signal before falling back to the column-detection rules below. Detection priority:
1. Explicit `pay_structure` column present in the upload — use it. (Honors any per-role override the analyst recorded in engagement-config since the upload would have been generated against the same convention.)
2. `current_step` column present and populated — classify as `step`.
3. `band_min`/`band_mid`/`band_max` columns present with `performance_rating` — classify as `merit`.
4. Band columns present without performance data — classify as `merit` (request performance data later).
5. Neither step nor band data present — classify as `flat`.
6. Ambiguous (mixed signals) — ask: "Role [X] has both step data and salary bands. Is this a step or merit-based structure?"

Present classification for confirmation: "I classified 12 roles as step (union hourly), 8 as merit-based (salaried bands), and 2 as flat. Correct?"

Step-rate rows never receive merit/compa-ratio logic. Merit-based rows never receive step-progression logic.

### 2d. FTE Normalization

Extract standard weekly hours or FT/PT indicator from Excel.
- FT employees: annualize using 2,080 hours (40 hrs/week × 52).
- PT employees: annualize using `weekly_hours × 52`. If `weekly_hours` not provided but `ft_pt` = PT, ask: "What are the standard weekly hours for your part-time [role]?"
- If neither field present: assume FT, state assumption explicitly.
- Report actual headcount in all tables. Add a separate FTE column when PT employees are present: `FTE = weekly_hours / 40`.

### 2e. Structure-Specific Extraction

**Step-rate roles** (`pay_structure = step`):
- Headcount per step per classification (not just per role — per-step distribution is required for accurate costing).
- Step table with rates per step per classification. Step tables may come from a separate sheet or conversational input. Ask: "Do you have the step tables in a separate sheet, or should I build them from the data?"
- Hours-to-advance threshold (if available; default 1,040 hours for UFCW grocery if not specified).
- FT/PT ratio by classification.
- Roll-up factor (benefits, pension, premiums riding on base wage). **Config-key precedence**: when `costing.roll_up_factor` is set in engagement-config (per `references/engagement-config-template.md` § costing), use it without prompting — single value applies uniformly, per-province map applies per province with `default` as fallback. Only ask when the config is absent: "Should I include a roll-up factor for benefits/pension riding on base wage? Your roll-up is typically total benefit costs / straight-time wages." If user provides a value, apply it to all step scenarios. If user declines, use 1.0 and disclose.

**Merit-based roles** (`pay_structure = merit`):
- Band structure: min/mid/max per grade.
- Current salary per employee (or average per grade if individual data unavailable).
- Performance ratings (if available).
- Compute compa-ratio: `current_pay / band_mid`.
- Compute position-in-range: `(current_pay - band_min) / (band_max - band_min)`.
- Assign compa-ratio quartile: Q1 (<0.90), Q2 (0.90-1.00), Q3 (1.00-1.10), Q4 (>=1.10).
- Group compa-ratio: `sum(salaries) / sum(midpoints)` — payroll-weighted, not average of individual CRs.

### 2f. Validation Summary

Present a summary before proceeding:
```
Parsed your file:
- 18 roles identified
- 342 total headcount (14 roles with headcount, 4 without)
- 12 salaried roles, 6 hourly roles
- Pay structures: 6 step, 8 merit-based, 4 flat
- Pay range: $19.50/hr to $127,000/yr
- 2 rows excluded (missing role title)
- 4 roles flagged (missing headcount — will appear in gap analysis but not dollar costs)

Does this look right?
```

### 2g. Market Data Pull

Use the Market MCP as primary source. One call to `get_role_intelligence` returns StatCan benchmarks (P10/25/50/75/90), live posting rates, YoY trends, and economic-region breakdown. All rates are hourly CAD.

**Verified-source discipline applies to every call here.** Each Market MCP / Indeed MCP / `get_cba_wage_scale` / `web_fetch` invocation in this section appends one entry to the engagement-state's `tool_calls[]` array, and every numeric claim cited downstream from these calls must carry one of the canonical 11 verified-source tags (`[statcan-wage]`, `[live-postings]`, `[cba]`, `[indeed-company]`, `[econometric]`, `[statutory]`, `[market-data]`, `[survey-house]`, `[user-provided-cba]`, `[professional-judgment]`, `[assumption]`) per `references/tools-available.md` § Verified-source discipline. Auto-downgrade fires on any tag without a matching `tool_calls[]` entry.

**Role resolution (always first):**

1. Call `search_roles(query_text=<role title>, province=<2-letter code>)`.
2. Inspect the response:
   - **Strong match** (top result has `match_score >= 0.7` and title clearly matches): use `role_id` with `get_role_intelligence(role_id, province, ...)`. This bypasses fuzzy matching.
   - **Weak match** (top result has `weak_match=true`, or response includes `no_strong_match` guidance): do NOT pick a role_id. Call `get_role_intelligence(role='<original title>', province=...)` directly — the 3-stage resolver (bridge → mined titles → NGRAM → posting fallback) handles it.
   - **Ambiguous** (2+ results with similar match_score and the role title is genuinely ambiguous, e.g., "Manager" without function context): surface the options to the user. Do not guess.

**Comprehensive intelligence (the main call):**

3. `get_role_intelligence(role_id or role, province, percentiles=[10,25,50,75,90], include_economic_regions=true, window_months=3)` — returns the full bundle.
   - Set `include_economic_regions=true` for multi-site organizations (a common default for multi-site grocers). This surfaces sub-province wage variation (e.g., Vancouver Island vs Lower Mainland in BC, Montréal vs Saguenay in QC).
   - YoY trend is included — see the Aging section below before applying any extra aging factor.

**Pay scale evaluation (preferred path when user uploaded a wage grid):**

4. `compare_pay_scale_to_market(role or role_id, province, steps=[{step:1, rate:18.0}, ...], band_min, band_max, rate_type)` — returns a structured verdict (entry vs P10/P25, top vs P50/P75, which steps fall below market, overall competitiveness flag). `rate_type` accepts `"hourly"` (default) or `"annual"` — annual rates are divided by 2080 internally. Use this instead of computing the comparison manually.

**Collective agreement (mandatory for unionized roles):**

5. `get_cba_wage_scale(role, province, include_expired=false)` — returns negotiated scale min/max, step count, scale length, annual increases, and agreement metadata. Mandatory for UFCW grocery, construction, public sector, healthcare. Contrast CBA scale against `get_role_intelligence` P50 to surface above/below-market positioning of the negotiated scale.

**Single offer evaluation:**

6. `compare_offer_to_market(role, province, offer_amount, offer_type)` — for individual hire/promotion review against StatCan + live postings + CBA in one call.

**Cross-cuts:**

7. `compare_roles(roles, provinces, top_n)` for cross-role or cross-province summary tables. `get_market_snapshot(province, top_n)` for provincial overview ("top hiring roles, fastest wage growth") to inform Phase 1 and Phase 3 framing.

**Indeed MCP for posting validation and competitor intel:**

8. When Market MCP coverage is sparse OR you want to verify a posting match reflects the actual role scope:
   - `search_jobs(search=<role>, location=<city, province>, country_code='CA')` — live Indeed postings for the role.
   - `get_job_details(job_id)` — full description for any specific posting.
   - `get_company_data(companyName, jobTitle, location, language='en' or 'fr', knowledgeCategories={metadata: true, ratings: true, salaries: true})` — pull competitor pay + culture ratings for retention narrative.

**User-provided CBA (when active — see `references/survey-house-protocol.md`):**

If the user uploaded or pasted a CBA wage scale that takes precedence over Market MCP's CBA cache for any role/province in scope, use the extracted user-CBA structure as the primary CBA source. Skip step 5 (`get_cba_wage_scale`) for those role/province combinations. Tag every claim derived from the user-CBA with `[user-provided-cba: <agreement_id>, expires <date>]`.

**Survey-house data (when active — see `references/survey-house-protocol.md`):**

If the user uploaded a third-party survey (Mercer, WTW, Korn Ferry, etc.), parse the survey per the protocol's ingestion patterns. Use survey percentile data alongside Market MCP — present both side-by-side in the deck, never silently average. Apply the survey's aging factor and geo-adjustment per the protocol. Tag every claim derived from the survey with `[survey-house: <vendor>, <year>, <cut>, <aging_note>]`.

**Web search (fallback only):**

9. Job Bank Canada, Glassdoor, LinkedIn Salary, BLS (US roles), employer career sites — only when Market MCP and Indeed return insufficient data. Use the `web-search` builtin (WebSearch) — always available, no key. If the optional Perplexity server is configured, prefer `perplexity-ask`/`perplexity-research` here for richer multi-source synthesis with citations; when Perplexity is absent, `web-search` is the fallback. Either way, web data is a fallback to the Market MCP, never the primary benchmark source — tag every web-derived point `[PROXY]` or `[ESTIMATED]`.

**Tagging:**

Tag each role with `match_method`: `role_id_direct` | `role_resolver` | `cba` | `indeed` | `web` | `none`.
Tag each data point with confidence: `[EXACT]` | `[MATCHED]` | `[PROXY]` | `[ESTIMATED]` | `[USER-PROVIDED]`.

**Step-rate benchmark anchors:**

- Top step (job rate) → P50 (fully qualified worker)
- Step 1 (entry rate) → P10 or P25 (entry-level posting)
- Workforce weighted average → falls within P25–P50 spread when scale is healthy
- Scale spread (top/bottom) → compare to standard 40-60% market range

**Province scoping:**

Always scope to the user-specified province. If not specified, ask.

**Multi-province engagements** (when `benchmark.scope_provinces` has 2+ provinces):

1. For each province in `scope_provinces`, run the role resolution + `get_role_intelligence` cycle independently. The skill iterates per-province; do not collapse a multi-province engagement into a single national pull.
2. Use `compare_roles(roles=[...], provinces=[...])` for cross-province summary tables (one tool call returns the cross-cut).
3. Use `get_market_snapshot(province=X)` per province for the provincial overview that feeds Phase 3 framing.
4. For unionized roles, call `get_cba_wage_scale(role, province)` per province — CBA scales differ across UFCW Local 175 (ON) vs TUAC 501 (QC) etc.
5. Tag every data point with its source province. Aggregations in Phase 4 use the per-province values, never a single national average.

**Provincial minimum-wage compression check (per province in scope):**

For each province with step-rate roles, compare entry rate to `benchmark.provincial_minimum_wages[province].rate` from config:
- Compute premium: `entry_step_rate - provincial_minimum`
- Flag as compression risk when premium <$0.50
- Flag as critical when premium <$0.25 OR when next year's projected provincial minimum (if known) would push entry to or below minimum
- Tag with the minimum-wage source date: `[CONFIG: ON $17.20, effective 2025-10-01]` OR `[WEB-VERIFIED 2026-04-21]`

If a province in scope has no `provincial_minimum_wages` entry in config, prompt the user OR web-search the current value. Do not proceed past Phase 2g for that province until the value is confirmed.

**Aging:**

`get_role_intelligence` returns YoY trend within `window_months`. Apply a separate aging factor only when source data predates the live posting window OR comes from an older external survey (uploaded Excel from a prior consultant, internal benchmarking from 2+ years ago). Default 3% YoY only for non-Market-MCP data. Never double-apply aging when Market MCP already shows the trend.

### 2h. Compute Derived Metrics

**Step-rate roles:**
- Top rate compa-ratio: `top_rate / market_P50` (headline benchmark).
- Workforce weighted average rate: `sum(rate_at_step × headcount_at_step) / total_headcount`.
- Workforce compa-ratio: `weighted_avg_rate / top_rate`. Below 0.80 = bottom-heavy workforce; above 0.95 = mature workforce.
- Entry rate check: step 1 rate vs. regional minimum wage and market P25.
- Scale spread: `top_rate / bottom_rate` as compression indicator.

**Merit-based roles:**
- Compa-ratios per role/employee.
- Group compa-ratio (payroll-weighted).
- Gap analysis: percentage and dollar distance to target percentile.
- Classification: Below Market (<0.95 CR), At Market (0.95-1.05), Above Market (>1.05).
- Compression detection: flag when `avg_compa_ratio(0-2yr cohort) > avg_compa_ratio(3-5yr cohort)` for same role.

**All roles (when headcount available):**
- Total cost-to-market by role and aggregate.
- If prior-year data available: YoY delta for each metric.

### 2i. Prior Deck Extraction (Track R only)

Parse the uploaded PPTX via `markitdown`. Extract:
- Prior-year data points for YoY comparison: market percentiles, compa-ratios, gap sizes, recommendations made.
- Prior narrative frame: situation, findings, recommendation, decision ask.

### 2j. Missing Data Handling

- Roles without market matches: flag, do not silently drop. Attempt Market MCP posting data as fallback.
- Missing headcount: proceed with per-role analysis. Flag that dollar costing requires headcount.
- Missing headcount-per-step (step): use total headcount with uniform distribution assumption, flagged as estimate.
- Missing band structure (merit): cannot compute compa-ratios. Flag and ask for band data, or proceed with flat market gap.
- Missing performance ratings (merit): assume uniform distribution across rating levels for matrix costing. Flag as estimate.
- When individual data unavailable for merit roles: assume normal distribution centered at CR=1.0, sigma=0.09. Flag as modeled assumption.
- Missing geography: ask (this blocks meaningful market comparison).

**Phase 2 output**: Structured data set held in conversation context. Includes matched roles with market data and pay_structure tags, unmatched roles, computed metrics, economic context, prior-year comparisons (Track R). Every Market MCP / Indeed MCP / `web_fetch` call made during Phase 2 also appends a `tool_calls[]` entry to the engagement-state per `references/tools-available.md` § Container for tool_calls[] — this is the audit trail for verified-source tags in the deck. Auto-checkpoint at the end of Phase 2 (transition to Checkpoint B) commits the running `tool_calls[]` via `engagement_put` per `references/persistence-and-ledger.md` § /checkpoint command.

---

## Phase 3 — Interpretation (2-3 turns)

Present findings conversationally. No END deliverable artifacts here, no formal tables longer than 5 rows. The goal is shared understanding, not data delivery. (Structural artifacts — engagement-state.yaml + checkpoint.yaml — continue to update at the phase boundary per the auto-checkpoint cadence.)

**Pre-step — Last-cycle drift detection** (autonomous, runs before Turn 1):

If `cycle.last_cycle` is populated in config, run drift checks before presenting findings. The point: turn the skill into institutional memory by explicitly comparing this cycle's data against last cycle's decisions.

For each role family in scope, compute and surface:

1. **Last-cycle action vs. current gap.** "Last cycle we lifted meat-cutter top step 4%. Market has moved 3.2% since (per `get_role_intelligence` YoY trend). Current top-rate vs market P50 = 96% (was 100% at end of last cycle). Drift: 4 points in one year."
2. **Deferred items status.** If `cycle.last_cycle.deferred_items` mentioned a role family that's now in scope, lead with it: "Last cycle we deferred pharmacy. Current pharmacy assistant gap to P50 is 8% in QC, 6% in ON. The deferral cost roughly [estimate] in turnover."
3. **Known-outcomes reality check.** If `cycle.last_cycle.known_outcomes` mentioned a turnover trend or retention claim, check whether the data supports it. "Last cycle's outcome note said 'meat-cutter retention improved post-lift.' Current voluntary turnover for meat cutters is [X]% — [confirms / contradicts] that read."

Surface drift findings as a **separate finding category** before the standard headline findings. Pattern:

> "Before I get to the new findings, here's what's changed since last cycle for the roles in scope:
>
> **Drift since FY25:**
> - Meat cutters QC: lifted 4% last cycle, market moved 3.2%, current gap to P50 is 4 points (was 0). Drift is real but within tolerance.
> - Pharmacy assistants (deferred last cycle): current gap is 8% QC / 6% ON. Deferring further widens this.
> - Bakery managers: no action last cycle, no change in gap. Still at P50.
>
> **New findings on top of that:** [headline finding 1, headline finding 2…]"

If `cycle.last_cycle` is empty or missing, skip the pre-step entirely and go straight to Turn 1. Don't reference last cycle if you have no data on it.

**Turn 1 — Lead with the headline:**

Present the 2-3 most significant findings first.

For **step** roles, lead with top-rate competitiveness:
"Your [classification] top rate sits at [X]% of market P50 — [above/below/at] market for a fully qualified worker. The scale spread is [Y]%, which is [narrow/typical/wide] compared to standard 40-60% market ranges."

For **merit-based** roles, lead with compa-ratio distribution:
"[X]% of your salaried population is below midpoint. Group compa-ratio is [Y] — the gap is [concentrated in specific grades / broadly distributed]."

For **mixed** workforces, lead with the segment that has the larger problem.

If data contradicts the user's hypothesis from Beat 3:
"You expected [hypothesis]. The data shows [reality]. Here's what that might mean: [implication A if hypothesis is right and data is noisy] vs. [implication B if data is right and hypothesis needs updating]."
Do not resolve the contradiction. Present both readings and let the user react.

Invite organizational context:
"Anything here that's explained by something I can't see in the data — benefits offsets, retention bonuses, recent re-orgs, internal politics?"

**Turn 2 — Integrate user context:**
Fold the user's context into the interpretation: "So the corporate rates being above market is from the acquisition — that means the real gap is in operations, and the blended average is misleading."
Surface secondary findings that matter given the new context. Note any constraint or context that changes the analysis.

**Turn 3 (if needed) — Converge:**
Synthesize: "So the picture is: [2-3 sentence summary of what the data means for THIS org, given THIS context]."

**Checkpoint B**: "Before I model scenarios — anything else I should factor in?" Block Phase 4 until confirmed.

**Auto-checkpoint on confirmation**: call `engagement_put` (with `expected_version`) per `references/persistence-and-ledger.md` § /checkpoint command. Set `saved_at_phase: 3`, capture `parsed_data_summary`, `interpretation_findings`, and the running `tool_calls[]` array from Phase 2g (canonical container per `references/tools-available.md` § Container for tool_calls[]). Silent unless write fails.

### Push-Back Mechanics

When the user states something the data contradicts:
1. Acknowledge the user's framing first.
2. Present the contradicting data with its source.
3. Offer both interpretations with concrete implications for the deliverable.
4. Never say "you're wrong." Say: "The data tells a different story, and here's what each version means for the deck."
5. Record the user's decision and respect it downstream — no revisiting unless the user reopens.

**Phase 3 output**: Shared understanding (conversational — no formal artifact). Carry forward the confirmed interpretation as context for Phase 4.

---

## Phase 5 — Narrative Workshop (1-2 turns)

Construct the full argument arc the deck will follow. This phase bridges consulting (what to say) and production (how to say it on slides).

**Config-aware shortcuts** (when `audience` archetype loaded):
- Pre-fill audience psychology from the archetype's `beliefs`, `typical_objection`, `preferred_framing`. Present as: "Per your config, this audience believes [X] and typical objection is [Y]. Still accurate, or has anything changed?"
- If user confirms, proceed; if changed, ask only what's different.
- Use `decision_ask_pattern` from `deck` config if loaded.

**Turn 1 — Present the argument arc:**

Structure the argument as Situation → Tension → Resolution:
- **Situation**: "The organization [context from discovery]. We benchmarked [N] roles against [sources]."
- **Tension**: "The data shows [key finding]. This means [business implication: attrition risk, cost exposure, competitiveness gap]."
- **Resolution**: "[Chosen scenario]. This addresses [what it fixes] at [cost], positioning the organization to [outcome]."

Layer on audience psychology:
- "Your audience ([from discovery]) currently believes [X]. This deck needs to [confirm that belief and add urgency / challenge that belief with evidence / reframe the question entirely]."
- "The likely objection is [specific objection]. The deck preempts this by [showing data on slide N / addressing cost with phased implementation / comparing to cost of inaction]."

Use the do-nothing baseline as narrative anchor: "The cost of inaction slide anchors the investment ask — $[X]K in preventable turnover cost vs. $[Y]K to fix the gaps."

**Turn 2 (if needed) — Refine:**
User modifies the arc, reframes, or adds objections. Integrate and present the final narrative frame.

**Present the confirmed narrative frame as a distinct block in chat:**

```
NARRATIVE FRAME
Deliverable type: [market benchmarking / wage scale review / comp strategy / etc.]
Audience: [who sees this]
Decision being supported: [what they need to approve/endorse/discuss]
Narrative angle: [the strategic positioning of the argument]
Pay structure: [step | merit | flat | mixed]
Key data points to feature: [3-5 numbers that anchor the argument]
Recommendation direction: [the recommended course of action]
Scenario chosen: [which scenario or blend the user selected]
Costed scenario summary: [total cost, key breakdowns]
Do-nothing cost: $[X]K annual (turnover + replacement)
Anticipated objections: [primary objections and how the deck handles them]
Audience psychology: [what they believe now, what needs to change]
Political context: [internal dynamics that shape reception]
Prior-year context: [what was recommended last year, what happened]
Scope: [roles/grades/geographies covered]
Data sources used: [Market MCP (StatCan + live postings + CBA bundle), Indeed MCP, web search, uploaded Excel]
Tone: [risk-first / strategy / implementation / educational]
Argument arc: [situation] -> [tension] -> [resolution]
Payroll jurisdiction: [QC / ON / other / not specified]
```

Every field must be populated. If a field has no relevant content (e.g., no prior-year context on a first engagement), write "N/A — first engagement" rather than leaving it blank.

**Checkpoint D**: "Here's the argument arc. Build the deck on this frame?" Block Phase 6 until confirmed.

**Auto-checkpoint on confirmation**: call `engagement_put` (with `expected_version`) per `references/persistence-and-ledger.md` § /checkpoint command. Set `saved_at_phase: 5`, capture the confirmed `narrative_frame` block verbatim, the `scenario_chosen` from Phase 4, and the full accumulated `selection_log` (Phase 4 scenario pick at minimum). Silent unless write fails.

**Phase 5 output**: Confirmed narrative frame document. This is the handoff contract between consulting and production.
