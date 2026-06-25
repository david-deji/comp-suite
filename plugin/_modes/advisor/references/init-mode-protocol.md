# Init Mode Protocol

Init mode is a guided walkthrough that builds an engagement-config YAML block interactively. The user pastes the resulting block at the start of future engagements (or saves it personally on their corporate laptop) to skip discovery friction.

Loaded by SKILL.md when the Intent Router classifies a request as Init.

---

## When Init Mode Triggers

Init mode triggers when the user's first message contains any of:

- `/init`, "init", "initialize"
- "set up config", "set up the config", "configure", "configuration"
- "build me a config", "build a config", "create a config"
- "starter config", "config template", "config setup"

If the user uploads a `.pptx` or `.xlsx` AND mentions "init", treat the upload as ignored for this session — Init mode is config-only, no deck production.

---

## Walkthrough sequence — 10-step master.yaml flow

`/init` runs synchronously. Steps 1–9 are the master.yaml integration layer; Step 10 transitions to the original compensation-advisor intake (Sections 0–7 of the prior protocol, preserved below under "Step 10 — Skill-specific intake").

**Silent-skip rule (applies to every step below).** Steps execute silently when their preconditions yield no surfaceable content — empty inheritance, no near-miss on the slug, no pull-notifications, no prior cycles, no sibling-skill assets, no tree-view content. Do NOT narrate "Step N — nothing to inherit, skipping to Step N+1"; just proceed. Surface only steps that produce a user decision, a populated tree, a near-miss confirmation, or a visible artifact. The user knows from the section confirmations and the final summary which steps ran. Per-step narration on no-op steps is process performance, not progress, and inflates a 5-minute init into a 30-minute meeting.

### Step 1 — Parse slug

If the operator invoked `/init <org-slug>`, use that slug. If blank, ask:

> "Which org are we setting up comp work for? (Type a slug, e.g. `pharmacy-canada`, or type `show all` to list existing orgs.)"

Slug constraints: `^[a-z][a-z0-9-]{1,40}$`. If the operator types a slug that doesn't match, surface the constraint and re-prompt.

### Step 2 — Read `_orgs/index.yaml`

Call `find_or_create_org(slug)` from `master-yaml-ops.md`. Three outcomes:

- **Org exists in index** → continue to Step 3.
- **Fuzzy match found** (Levenshtein ≤ 2 against an existing entry) → surface the near-miss pros/cons table and ask the operator to pick: use existing / pick a different existing / create new.
- **No match at all** → the org is not provisioned. Org + master-header creation is **admin-path** (P4b D4) — comp-suite reads existing orgs via `engagement_get_master` but never creates an org the backend doesn't know. Surface:

  > "No org `<slug>` exists in the backend. Provisioning a new org (membership + `private.orgs` + master header) is an admin step, not something this skill does over the wire. Ask the backend admin to provision `<slug>`, then re-run `/init`."

  Stop the create path here. Do not write a local `_orgs/index.yaml` entry or a local `master.yaml`.

**Anti-pattern — do not invent comparison alternatives.** When no near-miss exists, do NOT serve a pros/cons table comparing the operator's slug against fabricated variants (e.g., `<slug>` vs `<slug>-region` vs `<slug>-line`). The operator already chose the slug; respect it. The pros/cons table is reserved for genuine fuzzy-match collisions where Levenshtein ≤ 2 surfaces a real prior entry. A single confirm-create line is the entire prompt. Adding ceremony here makes the operator decide twice for no benefit.

### Step 3 — Read the master header from the backend

Call `read_master(org_slug)` from `master-yaml-ops.md` (which reads `engagement_get_master` MCP-primary; local `$STATE_ROOT` cache only on transport failure, P4b D1).

- **Master found** → validate post-read per `master-yaml-ops.md` → `validate_against_schema`. On validation failure: warn operator, offer (A) proceed read-only / (B) repair / (C) abort.
- **Master not found** (org not provisioned) → this is the D4 admin-path case, not a local create. Do **not** synthesize a `master.yaml` locally. Surface the same provisioning message as Step 2 and stop. (A backend that returns a master with empty `cycles`/`decision_log` is a provisioned-but-fresh org — continue normally; "not found" specifically means the org does not exist.)

### Step 4 — Update `master.header.last_touched_*`

Set `last_touched_date: <today>` and `last_touched_by_skill: compensation-advisor`. (Last-writer-wins on advisory fields — acceptable.)

### Step 5 — Update `master.header.active_skills[]`

If `compensation-advisor` is not yet in `active_skills[]`, append an entry (`first_init_date: today`, `last_active_date: today`, `asset_pointers: ["branding/<slug>/brand-kit.json", "personas/<slug>-personas.yaml"]`). If already present, update `last_active_date: today`.

### Step 6 — Render tree view

Call `render_tree_view(master, "compensation-advisor")` from `master-yaml-ops.md`. Display the inheritable groups relevant to this skill with freshness signals (🟢 <6mo / 🟡 6–18mo / 🔴 >18mo):

- advisor-relevant groups: org_metadata, brand_kit, scenario_archetypes, preferred_council_perspectives, glossary_terms, framing_decisions, council_outcomes
- sibling-skill assets discovered via `walk_sibling_assets(master)` rendered under "From sibling skills" (read-only)

Groups not relevant to compensation-advisor (speaker_registers, audience_profiles, channel_rules, anti_patterns, prior_comms_registry, audience_archetypes, waste_patterns, team_identity) are omitted from the tree view for this skill's `/init`.

### Step 6.5 — Pull-notification check

Call `check_pull_notifications(master, "compensation-advisor")` from `master-yaml-ops.md`:

1. Find the most recent `decision_log[]` entry where `skill == "compensation-advisor"` — that timestamp is `last-this-skill-init-timestamp`.
2. Filter `decision_log[]` for entries where `skill != "compensation-advisor"` AND `timestamp > last-this-skill-init-timestamp`.
3. If any high-signal events found, render them with the pros/cons acknowledgment prompt:

   > "Since you last used compensation-advisor for `<slug>` (`<last-date>`), other skills have logged: ..."

   Options: A. Acknowledge + proceed / B. Acknowledge + open new advisor cycle for the referenced cycle / C. Show more detail per event.


4. If no cross-skill events, proceed silently.

### Step 7 — Cycle selection

Ask operator:

> "Use existing primary cycle `<primary-cycle-slug>` (status: `<status>`), or open a new cycle?"

| Option | Pros | Cons |
|---|---|---|
| **A. Use existing primary cycle** | Continues in-flight work | If work is done, opens a stale context |
| **B. Open new cycle** | Clean state for new round | Requires naming the cycle |
| **C. Switch primary to a different existing cycle** | Explicit choice | Use `/switch-cycle` after /init instead |

- **Use existing** → load `cycle_state_pointers[]` entry for this cycle from `master.advisor`, read `_orgs/<slug>/cycles/<cycle-slug>/advisor/engagement-state.yaml`.
- **Open new cycle** → ask for cycle slug (default: `<line>-<region>-<fiscal>`; surface pros/cons if the operator's input deviates from convention). Create the cycle via `engagement_put_cycle {org_slug, cycle_slug, status: open, primary: true}` (the server atomically demotes the prior primary). Append `engagement_append_decision {decision_type: cycle_opened, cycle_slug}`. Create the local `_orgs/<slug>/cycles/<cycle-slug>/advisor/` directory (non-schema artifact dir). Then walk the original engagement-config intake (Step 10 below) to produce the engagement body for this cycle.

### Step 8 — Inheritance prompts per group

For each advisor-relevant inheritable group (org_metadata, brand_kit, scenario_archetypes, preferred_council_perspectives, glossary_terms, framing_decisions, council_outcomes):

Call `prompt_inheritance(group, items)` from `master-yaml-ops.md`. Render the pros/cons table. Apply operator choices to the per-cycle state being built. For 🔴 red (>18mo) items, render the stale-inheritance prompt before asking.

If the operator picks drill-down (D), call `prompt_drill_down(group, items)` for item-by-item review with batch shortcuts.

### Step 9 — Save the advisor section + per-cycle state (backend)

Call `write_master_section(org_slug, "advisor", advisor_section_data)` from `master-yaml-ops.md` — which routes to `engagement_put_section {org_slug, section_name: "advisor", body, expected_version}` (MCP-only; on stale-reject re-read and retry; on transport failure escalate/halt, P4b D2):

1. Validate the section against `references/master-schema/master-shared-header.schema.json` + `references/master-schema/master-advisor-section.schema.json`. Refuse to write on failure.
2. The section write lands in the backend master — no local `master.yaml` write.
3. Write the per-cycle engagement body via `engagement_put {org_slug, engagement_id: <cycle-slug>, body, expected_version}` (`expected_version: 0` to create the cycle's body).
4. Each write threads `version → expected_version`; a stale-reject re-reads and retries rather than forcing.

### Step 10 — Skill-specific intake (compensation-advisor engagement-config flow)

After master.yaml integration is complete, continue to the engagement-config sections. For new cycles, walk Sections 0–7 of the original intake below. For existing cycles, surface the current config and ask the operator if they want to update any section.

---

## Step 10 detail — Section-by-Section Walkthrough

Open with a single message confirming the scope and starting Section 0:

> "Now building your engagement config. I'll walk you through 8 sections. You'll get a YAML block at the end to save and paste at the start of future engagements.
>
> Sections: engagement_scope, cycle, org, audience, costing, benchmark, deck, persistence. Each is optional from Section 2 onward — say 'skip' for any you want to defer. **Section 0 (engagement_scope) and Section 1 (cycle) I'll push hard on, because they're what makes the rest of the skill useful.** Section 7 (persistence) is recommended but optional.
>
> A note before we start: **one engagement = one budget owner.** Pharmacy goes to the Pharmacy VP. Atlantic retail goes to the Atlantic Retail VP. Ontario retail to Ontario, Western to Western, the discount banner to its own VP. They each have their own budget envelope, their own VP Ops, and they each warrant a separate engagement and a separate config. If you find yourself trying to cover two budget owners in one config, it's almost always better to split.
>
> **Section 0 of 8 — Engagement Scope**: Who is the budget owner for this engagement? (e.g., 'VP Ops, Pharmacy' or 'VP Ops, Atlantic Retail')"

Wait for response before proceeding. Each section is its own turn.

For each section, ask the questions in order. Group questions where the answers are short. Allow "skip" at any point — it leaves the section blank and proceeds to the next. Allow "use defaults" — it populates from the template with annotations.

Show the populated YAML chunk after each section so the user sees progress. Do not show the full final YAML until the end.

### Section 0 — Engagement Scope (6 questions, push hard)

This section is where the skill gets the most leverage. A well-scoped engagement has one budget owner, one approval path, one in/out scope statement. A poorly-scoped engagement gets stuck in Phase 1 trying to please two VPs at once. Push back if the answers are vague.

Ask in 1-2 turns:

1. Budget owner role? (the VP-level person accountable for approving the $ envelope — e.g., "VP Ops, Pharmacy" or "VP Ops, Atlantic Retail")
2. Budget owner name? (the actual person in role today)
3. Scope label? (a short tag for headers and filenames — e.g., "Pharmacy FY26", "Atlantic Retail May cohort")
4. Banner or region? (Pharmacy / Atlantic / Ontario / Western / banner-specific / etc.)
5. In-scope role families? Out-of-scope explicitly? (helps prevent scope creep — e.g., "in: pharmacy assistants, pharmacy techs, pharmacy managers; out: store managers, front-of-store, corporate")
6. HR lead? (the HRD or HRBP managing the analyst-side relationship — optional)

**The budget-owner rule — strong nudge.** If the user names two VPs, or says something like "this is for all of retail" without naming a single accountable VP, push back:

> "Two budget owners usually means two engagements. Each VP Ops owns their own envelope and their own approval path — bundling them creates approval friction and forces compromise scenarios neither one wants. Want to scope this to one of them, or proceed knowing you'll likely have to split later?"

If the user insists ("no, this really is one engagement — there's a single SVP signing off and the VPs are aligned"), accept the answer and proceed. Note in the YAML's `engagement_scope.budget_owner_role` field exactly what they said. Do not refuse — strong nudge, not a hard gate.

After answers, present:

```
✓ Section 0 — engagement_scope

engagement_scope:
  last_verified: [today's date]
  budget_owner_role: "[answer]"
  budget_owner_name: "[answer]"
  scope_label: "[answer]"
  banner_or_region: "[answer]"
  in_scope_role_families: [...]
  out_of_scope: "[answer]"
  hr_lead: "[answer]"
```

> "Section 1 of 8 — **Cycle**. Where are you in the end-to-end annual wage scale review for this scope? Last cycle's outcome and this cycle's goals?"

### Section 1 — Cycle (8 questions, push hard)

Cycle context is what turns each session from a one-off chart into a continuous relationship with VP Ops. The skill uses `current_stage` and `current_week_offset` to calibrate every subsequent phase — at week −12 the work is intake and scope; at week −7 it's the approval pitch.

Ask in 2 turns. Group the "what cycle / when" questions, then the "last year / this year" questions.

**Turn 1 — cycle anchor:**

1. Cycle name? (e.g., "FY26 Annual Wage Review")
2. Cohort? (Apr / May / Jun / Oct effective-date — pick the one this engagement belongs to)
3. Effective date? (the day the new wage scale goes live — day 0 anchor)
4. Current stage? Read the canonical 7-stage list from `references/engagement-config-template.md` § `cycle.stages` and present it to the user as a numbered menu. Ask them to pick by number, name, or describe a freeform stage if their process diverges. Whatever they pick goes into `cycle.current_stage`. Do not retype the stage list in this file — the template is the source of truth and the only place stage names are maintained.
5. Current week offset? (negative weeks before effective date, positive after — skill computes if user gives effective_date and "today's date is week X")

**Turn 2 — last cycle and this cycle:**

6. Last cycle's headline decision? (1-2 sentences — "We did 3% ATB plus step compression fix on meat cutters in QC, $3.8M, May 2025")
7. Anything from last cycle deferred to this one? (e.g., "We left pharmacy alone last year and committed to look at it this cycle")
8. This cycle's primary objective? Must-address items? Envelope ceiling if known? (e.g., "Close pharmacy assistant gap to P50, hold envelope under $4M, must include retention adjustment for licensed techs")

After answers, present the cycle block. **Do not ask the user to retype the 7 stages** — bundle them as a default in the YAML output. The user only specifies their cohort, effective date, current stage, and the last/this cycle context.

> "Section 2 of 8 — **Organization**. Company, industry, banner, governance."

### Section 2 — Organization (4-6 questions)

Ask in 1-2 turns:

1. Company name?
2. Industry? (grocery / manufacturing / healthcare / professional services / other)
3. Multi-banner? (list banners if yes; "no" if single brand)
4. Union landscape by province? (e.g., "ON: UFCW Local 175, QC: TUAC 501, others non-union")
5. Governance pattern? (who signs off — CHRO, comp committee, board?)
6. Pay philosophy stance? (P50 / P50+retention / P75 lead / unspecified)

Optional follow-ups if the user wants depth:
- Approximate scale (headcount tier, revenue range)?
- Last cycle's outcome (1-line summary)?

After answers, present:

```
✓ Section 2 — org

org:
  last_verified: [today's date]
  name: "[answer]"
  industry: [answer]
  banner: [...]
  union_landscape: { ... }
  governance: "[answer]"
  pay_philosophy: "[answer]"
```

> "Section 3 of 8 — **Audience archetypes**. Most engagements have 1-3 audience types you regularly present to (board, CHRO, HR ops, employees, union). Want to define one now, or all that apply?"

### Section 3 — Audience (1-3 archetypes, 6 fields each)

For each archetype:

1. Short id? (e.g., `comp-committee`, `chro`, `hr-ops`, `union-bargaining`)
2. Who specifically? (1-line description)
3. What do they currently believe about pay?
4. What's their typical hardest objection?
5. Preferred framing? (risk-first / strategy-with-options / implementation-detail / educational)
6. Slide count target for this audience?

After each archetype, ask: "Add another archetype, or move on?"

After Section 3, present the archetypes block.

> "Section 4 of 8 — **Costing parameters**. 7 inputs that drive Phase 4 cost modeling. I'll suggest defaults; override what you know."

### Section 4 — Costing (7 inputs)

Ask all 7 in one turn (the user can answer rapid-fire or accept defaults). For multi-province engagements, ask whether each parameter is national-uniform or per-province.

1. Roll-up factor — national-uniform OR per-province?
   - QC roll-up typically 1.36-1.40 (incl. QPP/QPIP/CNESST)
   - ON roll-up typically 1.30-1.34 (incl. CPP/EI/EHT)
   - NS / NB / NL / PE roll-up typically 1.28-1.32 (incl. CPP/EI; lower workers' comp than ON)
   - AB roll-up typically 1.26-1.30 (incl. CPP/EI; no provincial payroll tax; WCB)
   - BC roll-up typically 1.27-1.31 (incl. CPP/EI; EHT for employers > $500K payroll; WorkSafeBC)
   - SK / MB roll-up typically 1.28-1.32 (incl. CPP/EI; provincial payroll tax in MB > $2M payroll)
   - Other / unknown: 1.30 placeholder; verify with finance before any real engagement
   - All values above are bundled defaults requiring user verification — tag in YAML as `# placeholder — verify with finance` until user confirms. If you don't know, ask finance team for total benefit cost ÷ straight-time wages per province.
2. Pay-attribution % for turnover? (default 0.35)
3. Voluntary turnover rate % — national-uniform OR per-province? (default 0.15 if no actuals; per-province if you have HR data)
4. Replacement multipliers — confirm or override:
   - Hourly: 18%
   - Professional: 55%
   - Management: 125%
   - Executive: 180%
5. Payroll burden % per province (REQUIRED — no national fallback):
   - QC default 14.2% (incl. QPP, EI, QPIP, HSF, CNESST)
   - ON default 11.5% (incl. CPP, EI, EHT, WSIB)
   - Other provinces: ask the user or accept 12% placeholder
6. Default target market percentile? (default P50)
7. Rounding rules? (default per-role $100, aggregate $1K)

After answers, present the costing block.

> "Section 5 of 8 — **Benchmark defaults**. Sets up Phase 2 data pulls — percentiles, peer companies, role aliases, geography."

### Section 5 — Benchmark (6 inputs)

1. Default percentiles to pull? (default [10, 25, 50, 75, 90])
2. Default province? (2-letter code — primary province for single-province engagements)
3. Scope provinces? (list of all provinces this org operates in, e.g., `[QC, ON, AB, BC, NS]`. Drives multi-province calculation. Single-province orgs: same as default_province.)
4. Provincial minimum wages? For each province in scope, ask:
   - Current rate? (web-search if user doesn't know — `<province> minimum wage 2026`)
   - Effective date?
   - Next scheduled review date? (skill uses this to warn when stale)

   Example pattern: "I'll ask for each province in scope. ON: current rate, effective date, next review?"

   **Dummy-mode rule**: if the user has requested dummy/stub values for the whole config up front (e.g., "fill with dummy values", "stub it out", "I'll fill in real numbers later"), leave each `provincial_minimum_wages.<province>` block as:

   ```yaml
   ON:
     current_rate: TODO
     effective_date: TODO
     next_scheduled_review: TODO
     source: "TODO — verify before any real engagement"
   ```

   Do NOT web-search. Do NOT guess. The TODO markers carry forward into the produced config; the skill warns at Phase 0 of any future engagement loading this config that minimum-wage TODOs must be filled before Phase 4 costing.

   **The `never guess` rule still holds — TODO is not a guess; it's an explicit unfilled placeholder.**
5. Include economic regions? (default true for multi-site orgs)
6. Peer company list for Indeed lookups? (e.g., for grocery: Loblaws, Metro, Walmart Canada, Costco)
7. Role aliases — known role-to-NOC mappings to skip search_roles? (optional; can be added incrementally)

After answers, present the benchmark block.

**Note on minimum wage maintenance**: Section 5's `provincial_minimum_wages` block decays. Skill warns when `next_review` passes. Re-run `/init update` annually to refresh.

> "Section 6 of 8 — **Deck defaults**. Slide counts, voice, required appendix slides."

### Section 6 — Deck (6 inputs)

1. Brand? (per-org kit slug / neutral)
2. **Production mode for Phase 6** (how interactive should the deck build be)?
   - `interactive` — A/B framing prompts on every section (~12 extra turns for a 6-section deck). Best for first few engagements, or for high-stakes decks (board, CHRO, contested).
   - `silent` — skill picks the recommended option for every section, you see previews between sections but don't get prompted. Best for routine refreshes.
   - `hybrid` — interactive on high-stakes sections (Findings, Options, Recommendation), silent on routine ones (Cover, Market Context, Appendix). Best balance once you trust the skill.
   - Default: `interactive` — switch to `hybrid` after a few successful runs.
3. Slide count by audience? (defaults: board 8, chro 15, hr_ops 25)
4. Required appendix slides? (default: methodology, assumptions, data-sources)
5. Voice / tone preference? (default: practitioner peer-tone)
6. Decision-ask phrasing pattern? (default: "Approve $X over Y months for Z scope")

After answers, present the deck block.

---

### Section 7 — Persistence (informational, no questions)

> "Section 7 of 8 — **Persistence**. Your engagement state, cycles, decision log, and brand kits persist automatically to the `market` backend, keyed to your authenticated login (org membership). There's no folder to configure and no paste-back — prior-cycle context and resumable checkpoints are always available once you're signed in. Nothing to set here; on to the last section."

No questions in this section. The skill does not emit a `persistence` config block — persistence is not operator-configurable in v2. (A legacy config carrying a `persistence:` block is ignored as a backend selector; the backend is always `market`.)

**Ground truth**: see `references/persistence-and-ledger.md` for what is backend vs local, the read/write semantics (D1 fallback, D2 MCP-only writes), and the retired Google-Drive backend.

---

## Final Output

After Section 7 (or after the user explicitly skips through to the end), generate a file artifact (per `references/artifact-generation.md` § engagement-config.yaml):

- **Filename:** `engagement-config-{org-name-slug}.yaml` — derived from `org.name` (lowercase, hyphens for spaces, strip punctuation). If `org.name` is missing, use `engagement-config.yaml`.
- **Content:** the assembled YAML with only the sections the user populated. Sections marked "skip" are omitted entirely (not included as empty stubs).
- **Provenance block:** include a `_meta:` block at the top of the YAML (provenance lives in fields, not header comments):
  ```yaml
  _meta:
    schema_version: 1
    created_date: YYYY-MM-DD
    created_by_skill: compensation-advisor
    created_via: /init
    shared_folder_id: <drive-folder-id>
    sibling_skills: [comp-comms-builder, comp-team-transformer, comp-training-designer]
  ```
  Also include a YAML comment above it: `# Paste this file's content as your first message in future engagements to skip discovery prompts.`

Present the artifact with this delivery message:

> "Init complete — your engagement config is the file `engagement-config-{slug}.yaml` above. Save it to your corporate laptop / password manager / personal note app — wherever you keep reference material.
>
> **To use it:** paste the file's contents as your first message in a new compensation-advisor session. Skill loads it in Phase 0 and skips questions the config already answers.
>
> **To update:** re-run `/init` with 'update mode' (paste the existing config + say 'update') — I'll walk through sections one at a time, you keep what's still accurate.
>
> **Before your first real engagement — read this:** when Phase 4 needs your workforce data, **use the CSV templates in `template_assets/wage_data_template_step.csv` and `wage_data_template_merit.csv`**. They contain the minimum columns the skill needs (job code, job title, location code, hourly rate / salary, weekly hours, experience hours or years in role) and intentionally exclude PII — employee names, IDs, dates of birth, addresses, performance comments. **Do not upload a raw HRIS export.** The skill scans for disallowed fields and will refuse to proceed if any are found, but by then the data is already in conversation context. The right time to filter is before export. See `template_assets/wage_data_template_README.md` for the column-by-column reference.
>
> **What was captured:** [list populated section names]. **What was skipped:** [list skipped section names — those will prompt at the relevant phases when you use the config]."

If the file artifact primitive is unavailable in the current environment (skill running outside claude.ai), fall back to a chat code block with the same content and the same instructions adapted ("copy this block instead of downloading the file").

---

## Update Mode

Update is a separate command (`/update`) with its own dedicated protocol. See `references/update-mode-protocol.md`.

In short: if the user wants to refresh an existing config rather than rebuild from scratch, route to `/update` — it's the same 8-section schema but only walks stale or changed sections, takes 3-10 minutes typically, and emits a merged YAML preserving untouched sections verbatim.

The legacy phrasing `/init update` continues to work as an alias for `/update` and is detected by the Intent Router before Init mode triggers.

---

## Anti-Patterns

- **Do not produce a deck during Init mode.** Init is config-only. If the user uploads a `.pptx` mid-Init, acknowledge the upload, set it aside, complete the config first.
- **Do not ask all 30+ questions in one turn.** The 8-section structure is the user-friendly chunking.
- **Do not require sections beyond Section 0 and Section 1.** Sections 2-7 are all optional; "skip" is always valid. Sections 0 and 1 are also technically skippable, but if the user tries, push back once: "Engagement scope and cycle context are what make the skill useful across multiple sessions — without them every engagement starts cold. Want to take 5 minutes on these two and skip the rest?" Section 7 (persistence) is informational only — there is nothing to skip or configure.
- **Do not silently accept "two budget owners" as one engagement.** The strong-nudge protocol in Section 0 is a deliberate friction. If the user overrides, accept and proceed — but do not skip the conversation.
- **Do not combine Init with Track C/R/D/R-lite in one session.** Init sessions are dedicated; if the user wants to start an engagement after Init, they paste the config in a fresh session.

---

## Output Discipline

Init produces an `engagement-config-{slug}.yaml` **file artifact** as its END deliverable.

- **Schema state**: Init persists the engagement config to the backend as the engagement body / advisor section (`engagement_put` / `engagement_put_section`, per `references/persistence-and-ledger.md`). No PPTX from Init — that's a Phase 6 product.
- **Operator copy**: Init also delivers the config as a downloadable file artifact in the chat so the operator has a local copy. The backend remains the source of truth; the artifact is a convenience, not the persistence path.
- **Mid-walkthrough turns** (Sections 0-7 walkthrough): chat text + YAML code-block previews so the user can see the shape coming together. The final delivery is the backend write plus the file artifact, not a re-pasted code block.

The YAML must remain valid (one fenced code block worth of content, `yaml`-tagged) so a user can copy it from the file or from the previewable chat block interchangeably.
