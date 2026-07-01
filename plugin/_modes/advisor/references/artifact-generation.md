# Artifact Generation

The skill produces 1-4 file artifacts depending on track and `deck.artifacts` config. This file specifies when each artifact is generated, what it contains, and the discipline rules that prevent silent failures.

Loaded by SKILL.md when generating any non-PPTX artifact.

---

## Artifact Catalog

Every track and every utility command produces an END deliverable file artifact (except `/help`, which is informational). The skill ships ≥12 artifact types; the table below names each, when it's produced, what gates production, and which protocol owns it. PPTX is the **primary** Phase 6 deliverable for engagement tracks (C, D); the rest are secondary or per-utility.

| Artifact | When generated | Gating | Loaded by |
|----------|---------------|--------|-----------|
| **Engagement-config + state** | | | |
| `engagement-config-{slug}.yaml` | End of Init mode; optionally at Phase 0 if user added inline answers | Always (Init mode) | `references/init-mode-protocol.md` |
| `engagement-state.yaml` | End of Phase 7 (after user accepts deck) | Always (all non-Init engagement tracks: C, D, R, R-lite) | `references/production-and-qa.md` § Phase 7 + `references/persistence-and-ledger.md` § Session end |
| `checkpoint.yaml` | Mid-engagement at every checkpoint (auto + manual `/checkpoint`) | Always (market MCP backend via `engagement_put`) | `references/persistence-and-ledger.md` § /checkpoint |
| `outcome-history.yaml` ledger entry | End of Phase 7 (close-time write sequence) — append a stub with `outcome_observed_*` null | Always (backend via `engagement_append_decision`) | `references/persistence-and-ledger.md` § /ledger |
| **Phase 6 deck companions** | | | |
| `cost-scenarios.xlsx` | Phase 6 (alongside PPTX) | `deck.artifacts` includes `xlsx` | `references/artifact-generation.md` § cost-scenarios.xlsx (this file) |
| `market-data.csv` | Phase 6 (alongside PPTX) | `deck.artifacts` includes `csv` | `references/artifact-generation.md` § market-data.csv (this file) |
| **Intake (one-shot)** | | | |
| `intake-form-{cycle-slug}-{date}.pdf` | `/intake` track — Stage 4 PDF render | Always (`/intake` track is the deliverable) | `references/intake-mode-protocol.md` |
| `intake-form-meta-{cycle-slug}-{date}.yaml` | `/intake` track — Stage 4 alongside PDF; captures variant choices, validation grounding sources, distribution metadata | Always (`/intake` track) | `references/intake-mode-protocol.md` § Output discipline |
| **Quickbench (one-shot)** | | | |
| `quickbench-{role-slug}-{province}-{YYYY-MM-DD}.md` | `/quickbench` track — END deliverable | Always (`/quickbench` track) | `references/quickbench-mode-protocol.md` |
| **Council** | | | |
| `council-state-{date}-{slug}.yaml` | End of Council track (standalone or integrated) — captures full reasoning trace, perspectives, votes, synthesis | Always (Council track) | `references/council-mode.md` |
| `council-memo-{date}-{slug}.md` | Council track in `memo` mode | `council.default_mode: memo` OR `mode: memo` flag at council invocation | `references/council-mode.md` § Memo mode |
| **Persistence repo writes (utility commands)** | | | |
| Brand-kit scaffold (`branding/<org-slug>/*`) | `/brand-kit init <org-slug>` — multi-file write of theme JSONs + masters skeleton + logo placeholders | `/brand-kit init` invocation | `references/brand-kit-protocol.md` |
| Custom persona file (`personas/<persona-id>.yaml`) + index update | `/persona add` (or `/persona init` for first-time setup) | `/persona add` invocation | `references/persona-library.md` |
| CBA library entry (`cba-library/<agreement-id>.yaml`) | `/cba ingest` — user pastes a CBA, skill normalizes + writes; prior version moves to `cba-library/_history/` on overwrite | `/cba ingest` invocation | `references/cba-library-protocol.md` (or persistence-and-ledger.md § cba-library) |
| Survey archive entry (`survey-archive/<vendor>/<year>/<cut>.yaml`) | `/survey ingest` — user pastes a survey block, skill normalizes; prior version moves to `_history/` on overwrite | `/survey ingest` invocation | `references/survey-house-protocol.md` § Auto-save to survey archive |
| Vocabulary promotion (`vocabulary/fr-ca-glossary.yaml`) | `/glossary promote` — promote N user-confirmed FR-CA terms from session memory to canonical | `/glossary promote` invocation | `references/fr-ca-glossary.md` |
| Quickbench archive (`quickbench-archive/{date}-{role-slug}-{province}.md`) | End of `/quickbench` track (the same MD as the user-facing artifact, archived locally for ledger queries) | `/quickbench` track; written to `$STATE_ROOT` | `references/persistence-and-ledger.md` § quickbench-archive |

**PPTX is always generated** in Phase 6 of engagement tracks (C, D) — that's the primary deliverable, not an optional artifact. The PPTX is built per `template_assets/branding/<active-kit>/build_template.js` and styled per the active brand kit; per-deck variation is added on top of the regenerated template. Secondary artifacts above are the focus of the discipline rules in this file.

**Loading rule**: this catalog is read by `/help` (so users discover what each track produces), by `references/intent-router.md` § Phase 0 (so the router knows which artifact to tag the engagement-state with), and at Phase 7 production close (verify all expected artifacts emitted before the close confirmation).

---

## 1. `engagement-config.yaml` — Init Mode Output

### When

- End of Init mode walkthrough (after Section 5 completes)
- Optional: end of Phase 0 if the user provided answers inline that weren't in their pasted block (skill offers "want me to save these as a config file?")

### Format

YAML file matching the schema in `engagement-config-template.md`. Sections the user filled are populated; sections they skipped are absent (not empty stubs — absent).

### Filename suggestion

`engagement-config-{org-name-slug}.yaml` — e.g., `engagement-config-acme.yaml`.

### Generation pattern

In claude.ai, use the file artifact primitive directly. Output the YAML content as the artifact body. The user gets a downloadable file; no chat-block copy-paste.

### Discipline

- Include a `_meta:` block at the top of the YAML (provenance lives in fields, not header comments):
  ```yaml
  _meta:
    schema_version: 1
    created_date: YYYY-MM-DD
    created_by_skill: compensation-advisor
    created_via: /init
    shared_folder_id: <drive-folder-id>
    sibling_skills: [comp-comms-builder, comp-team-transformer, comp-training-designer]
  ```
- Include a usage hint at the top as a YAML comment: `# Paste this file's content as your first message in future engagements to skip discovery prompts.`
- Never overwrite a user-provided file. If the user pasted a config block AND completed Init mode in the same session (anti-pattern but possible), produce a NEW filename: `engagement-config-{slug}-merged.yaml`.

---

## 2. `engagement-state.yaml` — End-of-Engagement State

### When

End of Phase 7, after the user accepts the deck. Generated automatically — do not ask "do you want a state file?" Just produce it as a follow-up artifact and tell the user what it's for.

### Format

YAML file matching the engagement-state schema in `engagement-config-template.md` § Output: end-of-engagement state file, **extended with the four blocks defined in `references/persistence-and-ledger.md` § engagement-state.yaml — schema additions**:

- `schema_version: 2` (REQUIRED — skill refuses to load files with newer schema_version than skill's known max)
- `scope_slug` and `engagement_slug` (derived deterministically from engagement_scope)
- `selection_log` (append-only array of Phase 4 + Phase 6b picks — see § Selection-log block below)
- `prior_engagement_refs` (read-only, populated from ledger at session start)
- `tool_calls` (append-only — every Market MCP, Indeed MCP, web_search, web_fetch call leaves a trace; canonical container per `references/tools-available.md` § Container for tool_calls[])
- `engagement_status: closed` + `closed_date: today` + `closed_by` at close-time

### Filename pattern

The file is written to the market MCP backend via `engagement_put` (engagement body — schema state) and simultaneously delivered as a download artifact. The canonical path for local reference is `$STATE_ROOT/_orgs/<org_slug>/engagements/<engagement_slug>/engagement-state.yaml` (local read cache, not a write target). One canonical state file per engagement, no date in filename — the engagement slug already encodes the cycle.

### Required fields at generation time

The skill must fill these from conversation context:
- `schema_version: 2`, `scope_slug`, `engagement_slug` (derived)
- `engagement.date`, `client`, `cycle`, `audience`, `decision_sought`, `scope`
- `findings.headline` (top 2-3 from Phase 3)
- `findings.do_nothing_cost`, `recommendation`, `recommendation_cost`, `cost_breakdown`
- `scenarios_modeled` (full list from Phase 4 with `chosen: true` on the picked one)
- `selection_log` (full accumulated array — Phase 4 scenario pick + every Phase 6b section pick with timestamps, options presented, audience archetype)
- `prior_engagement_refs` (carry forward from session-start ledger query)
- `tool_calls` (single flat array; each entry has `tool`, `args`, `timestamp`, `result_hash`, `used_in` per `references/tools-available.md` § Container for tool_calls[])
- `data_sources` (counts of MCP calls, last pull date)
- `assumptions_used` (the actual values from costing config or interactive prompts)
- `deliverables.pptx` (filename of generated deck)
- `deliverables.xlsx` and `csv` if generated
- `engagement_status: closed`, `closed_date`, `closed_by`

### Fields left null

- `outcome.*` — entire block is null. User fills via `/ledger update <slug>` after the board meeting (windows: 30d, 90d, 180d, 1y). Skill says: "After the meeting, run `/ledger update <slug>` to fill the outcome windows. Next cycle's discovery will surface these from the ledger."

### Selection-log block

Maintained per `references/persistence-and-ledger.md` § engagement-state.yaml — schema additions. Phase 4 appends one entry on scenario pick (`type: scenario`); Phase 6b appends one entry per section approval (`type: section_framing`). Each entry carries: `phase`, `type`, `section` (6b only), `timestamp`, `options_presented`, `skill_recommended` (or null when no recommendation given), `user_chose`, `rationale` (or null).

Future engagements with matching audience archetype + scope read this log to surface prior-pick patterns instead of relying on a static recommendation.

### tool_calls block

Maintained per `references/persistence-and-ledger.md` § engagement-state.yaml — schema additions and `references/tools-available.md` § Container for tool_calls[]. One flat append-only array. Every Market MCP call (`mcp__market__get_role_intelligence`, `mcp__market__compare_pay_scale_to_market`, `mcp__market__get_cba_wage_scale`, etc.), every Indeed MCP call, and every `web_search` / `web_fetch` call appends one entry (CPI/unemployment/econometric context is `web_fetch`-sourced). Sub-fields per entry: `tool` (full MCP-style name), `args`, `timestamp`, `result_hash` (SHA-256 of JSON response for MCP calls, SHA-256 of fetched body for `web_fetch`, null for `web_search`), `used_in` (list of slide/section IDs or deliverable surfaces). Used for cache and verified-source audit, not displayed in the deck.

### Presentation to user

After generating the PPTX (and any xlsx/csv), produce the state file via the close-time close-time write sequence (see § Close-time write below). Surface the close confirmation:

> "Engagement saved (commit `a3f2c91`).
> - State: `engagements/pharmacy-fy26/engagement-state.yaml`
> - Deck: `engagements/pharmacy-fy26/deliverables/deck-v3-final-2026-04-29.pptx`
> - Ledger entry appended (slug: pharmacy-fy26).
> - Repo: `comp-advisor-state`
>
> After the meeting: run `/ledger update pharmacy-fy26` to fill the 30/90/180/365-day outcome windows."

In paste/download mode, deliver the state file as a download with the same instruction adapted: "Save this alongside the deck. After the meeting, fill the `outcome` block manually or paste both files back when running `/ledger update` in a future session."

### Close-time write (close-time write sequence)

Sequenced MCP backend writes — order matters; binary deliverables are chat-downloaded first:

1. `engagement_put` — write engagement body with `engagement_status: closed`, `closed_date: today`, `closed_by: user_acceptance` (pass `expected_version`; retry read-modify-write on stale-reject per D optimistic-concurrency).
2. Deliver PPTX (and PDF when available), any `council-state-*.yaml`, cost-scenarios.xlsx, market-data.csv as chat-download artifacts. Sanitized workforce data CSV also delivered as download. Binaries never go through any backend.
3. `engagement_append_decision` — append a stub entry with `decision_type: engagement_closed` and all `outcome_observed_*` fields null (idempotent on `id`).
4. Locally, delete `checkpoint.yaml` from `$STATE_ROOT` if present — engagement is closed.

**Failure handling:** if any MCP write fails, do NOT report success. Surface the error, offer retry. Never declare close without a confirmed backend response. Per `references/persistence-and-ledger.md` § D2: on write failure, escalate/halt — never write-local-and-reconcile.

### engagement_mode block

Every `engagement-state.yaml` produced by this skill must include the `engagement_mode` block. The block mirrors the fields documented in `references/persistence-and-ledger.md` § engagement-state.yaml — schema additions and is reproduced here for generation-time reference:

```yaml
# engagement_mode block — required on every engagement-state.yaml
engagement_mode: full-engagement                       # mode_id from references/engagement-modes.md
mode_phases_run: [0, 1, 2, 3, 4, 5, 6, 7]              # populated from the mode taxonomy
mode_phases_partial: []                                 # populated from the mode taxonomy
mode_phases_skipped: []                                 # populated from the mode taxonomy
pre_engagement_only: false                              # true when state_shape_variant is pre_engagement
state_shape_variant: full                               # full | partial | standalone | pre_engagement

# Pre-engagement modes (e.g., narrative-frame-only) additionally null these fields:
# scenario_chosen: null
# costed_scenario_summary: null
# selection_log: []                          # NOT pretending Phase 4 ran
# ledger_treatment: pre_engagement_artifact  # routes to master.advisor.pre_engagement_artifacts[],
#                                            # NOT cycle_state_pointers[]
```

**Field rules (mirror of persistence-and-ledger.md § Field rules):**

- `engagement_mode` MUST be present. If absent, skill defaults to `full-engagement` AND emits a `decision_log` entry of `decision_type: mode_defaulted_silently`.
- `state_shape_variant` enum: `full | partial | standalone | pre_engagement`.
- `mode_phases_run`, `mode_phases_partial`, `mode_phases_skipped` are populated from the mode taxonomy in `references/engagement-modes.md`. Do not fabricate values — read the taxonomy.
- When `state_shape_variant` is `pre_engagement`, the artifact routes to `master.advisor.pre_engagement_artifacts[]` in master.yaml, NOT to `cycle_state_pointers[]`. The ledger treatment must be set accordingly.
- Field-level null-out rules for all modes are in `references/engagement-modes.md`. The `narrative-frame-only` mode null-outs are the reference implementation for v1; all other partial modes emit `decision_log: null_out_rules_pending_v1_1` when partial-flow state is written.

### Discipline

- Never include client-confidential narrative text (specific objections, political context) — those stay in the deck speaker notes, not the state file. Keep the state file machine-parseable: numbers, IDs, summary phrases.
- Engagement_slug uniquely identifies the cycle — never overwrite a prior cycle's state file. New cycle = new slug.
- `schema_version` MUST be present and MUST be a known value. Skill refuses to load files with newer schema_version than its known max — surfaces the error and instructs upgrading the skill bundle.

---

## 3. `cost-scenarios.xlsx` — Optional Excel Companion

### When

Phase 6, alongside PPTX, only when `deck.artifacts` includes `xlsx`.

### Sheet structure

| Sheet | Contents |
|-------|----------|
| `Summary` | Side-by-side scenario comparison table (matching the deck's Phase 4.7 table). Inputs at top: roll-up, payroll burden, target percentile. Outputs at bottom: total cost per scenario. |
| `Roles` | One row per role: title, classification, headcount, current pay, market P25/P50/P75, gap %, gap $, scenario A/B/C cost contribution. |
| `Step Tables` | One section per step-rate classification: rates per step, headcount per step, scenario rates after lift. (Only if pay_structure includes step.) |
| `Merit Matrix` | Performance × compa-ratio quartile matrix with cell budget %. (Only if pay_structure includes merit.) |
| `Assumptions` | All inputs used: roll-up, pay-attribution, replacement multipliers, payroll burden, rounding, aging factor, target percentile. |
| `Data Sources` | List of every Market MCP / Indeed / web call with date pulled. |

### Formula vs values

Use Excel formulas where possible — let the client adjust inputs and see scenario costs recompute. Scenario formulas reference the `Assumptions` sheet so a single input change ripples through. Static values only for raw market data and headcount (those don't change post-engagement).

### Generation pattern

Inside the Python sandbox: `openpyxl` to construct the workbook. Apply the active kit's brand colors to header rows when `deck.brand` is set. Save and surface as a file artifact.

### Filename

`{client-slug}-cost-scenarios-YYYY-MM-DD.xlsx` — e.g., `acme-qc-retail-cost-scenarios-2026-04-21.xlsx`.

### Discipline

- Every numeric cell must trace to either an input (yellow-highlighted on the `Assumptions` sheet) or a formula referencing inputs. No magic numbers.
- Include the same payroll-burden caveat as a footer row on the `Summary` sheet.
- If generation fails, do NOT silently omit. Tell the user: "PPTX generated successfully, but cost-scenarios.xlsx generation failed: [error]. Want me to retry or skip?"

---

## 4. `market-data.csv` — Optional Raw Data Companion

### When

Phase 6, alongside PPTX, only when `deck.artifacts` includes `csv`.

### Columns

```
role_title, role_id, noc_code, classification, province, economic_region,
percentile, value_hourly, value_annual, source, source_date, match_method, confidence_tag
```

One row per (role × percentile × source) combination. A role with P10/P25/P50/P75/P90 from Market MCP becomes 5 rows. A role with both Market MCP and CBA data becomes 5 + N rows.

### Filename

`{client-slug}-market-data-YYYY-MM-DD.csv` — e.g., `acme-qc-retail-market-data-2026-04-21.csv`.

### Discipline

- UTF-8 encoding with BOM (Excel-friendly for Quebec users with French accents).
- Include the same source citations as deck footnotes.
- One row = one fact. No aggregation, no derived metrics — that's what the .xlsx is for.
- If generation fails, same protocol as #3: surface the failure, do not silently omit.

---

## Generation Order in Phase 6

When `deck.artifacts: [pptx, xlsx, csv]`:

1. Build PPTX first (primary deliverable).
2. Generate xlsx if requested.
3. Generate csv if requested.
4. Run Phase 7 QA on all artifacts (data values must match across PPTX, xlsx, csv).
5. Present all artifacts together in the QA delivery message.

When any non-PPTX artifact fails generation:
- Continue with PPTX as primary.
- Report failures explicitly: "PPTX ✓ | xlsx ✗ (sandbox timeout) | csv ✓"
- Offer retry: "Want me to retry xlsx, or proceed with what we have?"

---

## Generation Order in Phase 7

After deck acceptance:

**Close sequence:**
1. Deliver binary artifacts as chat-downloads (PPTX, xlsx, csv, council-state files, sanitized CSV).
2. `engagement_put` — write engagement body closed (see § Close-time write).
3. `engagement_append_decision` — append closed stub with outcome fields null.
4. Delete local `checkpoint.yaml` from `$STATE_ROOT` if present.
5. Surface close confirmation: backend confirmation + local paths + `/ledger update <slug>` instruction.
6. Engagement complete.

**On backend transport failure:** deliver binary artifacts as chat-downloads unchanged; surface the schema-write error; offer retry. Do not silently fall back to a local-only write — per D2 in `references/persistence-and-ledger.md`, halt on write failure.

---

## Cross-Cutting Discipline

- **Naming:** every artifact filename includes either client slug + date (state, xlsx, csv) or org slug (config). No collisions across cycles.
- **Never silently fail.** Always report which artifacts succeeded and which didn't.
- **Never include secrets.** Pasted credentials, internal Slack threads, or anything client-confidential beyond engagement scope stays out of artifacts.
- **PPTX is the primary.** All other artifacts are secondary — failures don't block the primary deliverable.
- **No hidden artifacts.** Every artifact produced is named in the final delivery message. No surprises in the user's downloads folder.
