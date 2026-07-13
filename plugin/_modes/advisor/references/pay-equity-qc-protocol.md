# Pay Equity Exercise Protocol — Quebec (RLRQ c E-12.001)

> Loaded by `compensation-advisor` SKILL.md when the operator invokes `/init pay-equity-qc`
> (or types one of the trigger phrases). This is a comp-advisor reference document — not a
> standalone skill. Routes to itself via `references/intent-router.md`.
>
> Trigger phrases: "pay equity", "équité salariale", "run pay equity exercise",
> "exercice d'équité salariale", "maintenance audit", "évaluation du maintien",
> "audit de maintien", "diagnostic salarial".
>
> **Expert mode only.** v1 supports a single operator profile (consultant-led).
> The dual expert/guided mode from the standalone skill is collapsed; the AVIS DE RÉVISION
> JURIDIQUE gate is preserved in code but currently unreachable.
>
> **See also:**
> - `references/pay-equity-engagement-template.md` — schema for `pay-equity-engagement.yaml`
> - `references/pay-equity-render-branching.md` — CNESST-vs-side-deliverable branching rule
> - `scripts/pay_equity/` — the in-skill Python module (pure compute/validate/render, called via `call_tool(name, **kwargs)`)
> - `template_assets/pay_equity_cnesst/` — 7 affichage `.template.md` files
>
> **Persistence model.** Engagement DATA and the heavy CNESST math live in the org-scoped
> MCP backend, exposed as `payequity_*` tools. The in-skill Python tools are PURE
> compute/validate/render over data passed in — they persist nothing. The orchestration
> is the only layer that calls `payequity_*`: it **fetches** engagement data
> (`payequity_get_*` / `payequity_list_*`), passes it to the pure Python tool via
> `call_tool(<logical_name>, <data>)`, then **persists** the result back to the backend
> (`payequity_put_*` / `payequity_compute_*` / `payequity_append_audit_log`). There is no
> sandbox-FS engagement store and no Google Drive sync on the pay-equity surface — the
> backend IS the store.

---

## Overview

Guide an operator through a complete Quebec pay equity exercise under the *Loi sur l'équité
salariale* (RLRQ c E-12.001). The heavy numerical work (scoring, predominance, comparison,
adjustments) is performed server-side by the `payequity_compute_*` backend tools; pure
input-shaping, statutory gates, cross-class summaries, and document rendering are performed
by the in-skill Python module at `scripts/pay_equity/`. The skill authors only narrative
prose; all financial data and tables are rendered by tool calls.

**Architecture principle:** The LLM never writes numbers. Every table, dollar amount, score,
gap, and schedule comes from `render_document`. Templates use `{{RENDERED:document_type}}` for
tool output and `{{NARRATIVE:section_name}}` for prose written by the skill.

**Two call surfaces — keep them distinct:**
- `payequity_*` (e.g. `payequity_get_engagement`, `payequity_put_job_class`,
  `payequity_compute_comparison`, `payequity_append_audit_log`) — the org-scoped MCP backend.
  The orchestration calls these by their `payequity_*` names to fetch, persist, and run heavy math.
- `call_tool("<logical_name>", **kwargs)` — the in-skill PURE Python tools, invoked by logical
  name (`build_class_compensation`, `summarize_predominance`, `validate_adjustment_inputs`, …).
  These never touch the network or persist; they compute/validate/render over data the
  orchestration passes in.

---

## In-skill pure tools + backend compute tools

Pure input-shaping, validation, cross-class summaries, and rendering are performed by Python
functions in `scripts/pay_equity/`, invoked by logical name with `call_tool("name", **kwargs)`.
The heavy CNESST math and ALL persistence are server-side `payequity_*` backend tools. The
orchestration wires the two together: fetch (`payequity_get_*`/`payequity_list_*`) →
`call_tool(<pure fn>, <data>)` → persist (`payequity_put_*`/`payequity_compute_*`/`payequity_append_audit_log`).

**Pure in-skill tools (`call_tool`):**

| Logical name | Module | Notes |
|------|--------|-------|
| `create_engagement` | engagement.py | Builds engagement + retention-policy models for persist |
| `get_obligations` | engagement.py | Pure matrix over `size_tier` + `exercise_type` |
| `record_posting_date` | engagement.py | Re-anchors retention floor (Loi 25) over passed-in models |
| `process_deletion_request` | engagement.py | Loi 25 retention-floor advisory check; returns audit entry |
| `set_maintenance_committee` | engagement.py | 100+ only; builds committee model |
| `add_job_classes` | job_classes.py | Validates/normalizes/merges classes |
| `validate_class_groupings` | job_classes.py | Pay-spread + similar-description warnings |
| `summarize_predominance` | job_classes.py | Cross-class no-male signal (`global_comparison_eligible`) |
| `override_predominance` | job_classes.py | Validates evidence; returns the one overridden class |
| `list_grid_templates` | evaluation.py | Packaged template assets (no engagement data) |
| `select_grid` | evaluation.py | Builds grid + sub-factors + weights for persist |
| `customize_grid` | evaluation.py | 5 hard rules (R6); only physical ≤ mental overridable |
| `all_classes_scored` | evaluation.py | Completeness gate before comparison |
| `get_evaluation_summary` | evaluation.py | Banding (G-01) + bias warnings; returns audit entry on override |
| `build_class_compensation` | compensation.py | Shapes one class-compensation input for persist |
| `validate_adjustment_inputs` | adjustments.py | Art.76.5.1 installments + R3 retroactive-event guards |
| `import_prior_exercise` | maintenance.py | Diff vs current classes (snapshot NOT persisted) |
| `record_participation_session` | maintenance.py | Art.76.2.1 60-day hard gate; returns session + audit entry |
| `render_document` | render.py | 16 valid `document_type` values; pure over passed-in entities |
| `log_observation` | observations.py | 60-day consultation window (50+) |
| `respond_to_observation` | observations.py | Operator reply to logged observation |

**Backend compute + persistence tools (`payequity_*`):** the orchestration calls these for the
heavy math and all state. Reads: `payequity_get_engagement` (+ `stale_entities`),
`payequity_get_job_class`/`payequity_list_*`, `payequity_get_evaluation_grid`,
`payequity_get_participation_session`, `payequity_get_posting_metadata`, `payequity_get_observations`, etc.
Compute (server runs the math AND persists): `payequity_compute_predominance` (per non-override class),
`payequity_compute_scoring` (per class), `payequity_compute_comparison` (job-to-job→regression→global),
`payequity_compute_adjustments` (interest + schedule). Writes: `payequity_put_*` per entity,
`payequity_put_cycle`, `payequity_put_retroactive_event`, `payequity_append_audit_log`.

> There is NO `payequity_list_engagements` (engagement is keyed by `engagement_id`, not enumerated)
> and NO audit-log READ tool (`payequity_append_audit_log` is write-only — legally-material decisions
> are appended for the trail; gates that need to re-check timing **recompute** from persisted data).

Engagement data lives in the org-scoped backend, keyed by `engagement_id` (the client slug). The
orchestration never writes engagement JSON to a sandbox or to Google Drive; it persists via `payequity_put_*`.

### Persist round-trip contract (assert the write landed — this backend is the SOLE store)

Every `payequity_put_*` / `payequity_compute_*` write is optimistic-concurrency guarded on the
entity's `version`. Because there is no local copy of statutory data, a write that does not land is
**silent legal-defensibility loss** — treat every persist as a round-trip you must confirm, never
fire-and-forget.

- **Success shape.** A landed write returns `{ok: true, version: <new N>}` (or the persisted entity
  carrying its bumped `version`). Read the returned `version` and thread it into the next write of
  the same entity.
- **Conflict shape.** A stale write (the stored `version` moved under you, or a re-create of an
  existing `engagement_id`) arrives as a **JSON-RPC error**, not a success payload — the server
  raises, so it surfaces at the protocol layer with `data.error_code: "VERSION_CONFLICT"` and
  `data.retryable: true`. (This is uniform with engagement/brand/costing — payequity no longer
  returns a success-shaped `{error: version_conflict}` body; do not scan text for `version_conflict`.)
- **Recovery step (refetch → merge → retry once).** On `data.retryable == true`
  (`error_code == "VERSION_CONFLICT"`): re-`payequity_get_*` the entity, re-apply your change onto the
  fresh version, and retry the put **once**. If it conflicts again, escalate — do not loop and do not
  proceed as though the write persisted.
- **Never advance on an unconfirmed write.** Do not append the audit-log entry or move to the next
  compute stage until the put returned `ok:true` (or the retry landed). An advanced exercise built on
  a dropped write is the exact silent-data-loss failure this contract prevents.

Full error-code → action taxonomy (shared across all four backend families): see
`$ASSET_ROOT/_core/primitives/engagement-loader.md` § Error recovery (branch on `data.error_code`).

---

## Operator Mode (expert only in v1)

v1 supports `operator_mode: "expert"` only. Behavior:

| Aspect | Behavior |
|--------|----------|
| Target | Dave (consultant) |
| Data entry | Paste blocks accepted; bulk JSON |
| Validation gates | Warnings non-blocking; skill proceeds with operator acknowledgement |
| Explanatory text | Suppressed unless operator types `explain` |
| Grade banding | Result + override available |
| Method selection | Operator chooses; brief suggestion given |
| Pre-computation gate (Gate A) | Mandatory — cannot skip |
| Compensation review gate (Gate B) | Mandatory — cannot skip |
| Adjustment review gate (Gate C) | Mandatory — cannot skip |

Mode is set at engagement creation via `call_tool("create_engagement", operator_mode="expert", ...)`.
`operator_mode` is stored canonically in the backend engagement entity (`payequity_get_engagement`). The dual expert/guided mode from
the standalone skill is **collapsed**: all `# In guided mode:` branches are removed, and
the AVIS DE RÉVISION JURIDIQUE gate (which fires when `employee_count >= 100 AND
operator_mode == "guided"`, R8 D-D) is preserved in the ported tool code but is currently
unreachable. Future re-introduction of guided mode would re-activate the gate without
further code changes.

---

## Phase Counts

| Scenario | Phases | Progress Format |
|----------|--------|----------------|
| 10-49 initial | Phases 1–10 | `Phase X/10: [Nom]` |
| 50+ initial | Phases 1–11 | `Phase X/11: [Nom]` |
| Maintenance audit (any tier) | M1, M2, then 1–11 | `Phase X/13: [Nom]` |

Phase 0 (mode/entry selection) precedes Phase 1 and is not numbered.

---

## Skill-Layer Operations (NOT pure tools, NOT backend tools)

The pure tools + `payequity_*` backend cover every numeric or stateful operation. The skill
orchestration code also handles a few lightweight operations directly:

| Operation | Storage | Notes |
|-----------|---------|-------|
| `generate_reposting` | Operator deliverable | Produce reposting document by re-running `render_document` after observations + responses are recorded; delivered to operator (not engagement data) |
| `export_input_checklist` | Rendered inline | Assemble pre-computation checklist from the fetched `payequity_get_*` entities |

**Routed through tools (no longer free-standing skill-layer ops):**
- `set_committee` → `call_tool("set_maintenance_committee", ...)` → `payequity_put_maintenance_committee`
- `set_posting_date` → `call_tool("record_posting_date", ...)` → `payequity_put_engagement` + `payequity_put_retention_policy`
- `log_observation` → `payequity_get_observations` → `call_tool("log_observation", ...)` → `payequity_put_observation`
- (responses to observations) → `payequity_get_observations` → `call_tool("respond_to_observation", ...)` → `payequity_put_observation`

## Orchestration working-files — disposition

Only ephemeral sandbox cursors remain client-side. Everything that holds engagement DATA or a
legally-material decision goes to the backend.

| Working file | Disposition |
|---|---|
| `session-state.json` | **KEEP** — ephemeral sandbox cursor: phase pointer, pending inputs, gate bookkeeping, `operator_decisions`. Holds no engagement data; regenerable on resume. Legally-material decisions inside `operator_decisions` (comparison_method, grade-band rationale, schedule_type) ALSO go to the backend via `payequity_append_audit_log`. |
| `review-gate-A/B/C.json` | **KEEP** — ephemeral gate-confirmation bookkeeping. Confirmation milestones that must survive → `payequity_append_audit_log`. |
| `consultation.json` | **GONE** — observations → `payequity_put_observation`/`payequity_get_observations`; posting dates → `payequity_put_posting_metadata`/`payequity_get_posting_metadata`. |
| `operator-decisions.json` | **GONE** — every operator override/decision → `payequity_append_audit_log`. |
| `retention-policy-decisions.json` | **GONE** — Loi 25 deletion-decision trail → `payequity_append_audit_log`. |
| `participation.json` | **GONE** — engagement DATA → `payequity_put_participation_session`/`payequity_get_participation_session`. |
| `events.json` | **GONE** — retroactive events are compute inputs → `payequity_put_retroactive_event`/`payequity_list_retroactive_events`. |
| `prior-exercise.json` | **GONE** — prior exercise registered as a closed cycle via `payequity_put_cycle` (`prior_cycle_id` linkage); the imported snapshot is transient import provenance (diff surfaced, not stored). |
| `comite-pv.md`, reposting markdown | **KEEP** — skill-authored deliverable markdown (rendered output, not engagement data). Committee DATA itself → `payequity_put_maintenance_committee`. |

---

## Session State Schema

The skill maintains `session-state.json` in the engagement directory:

```json
{
  "client_slug": "string",
  "current_phase": "integer",
  "current_question": "string or null",
  "completed_phases": ["integer"],
  "stale_phases": ["integer"],
  "skipped_questions": ["string"],
  "language": "fr | en",
  "entry_mode": "guided | context_dump | csv",
  "operator_decisions": {
    "comparison_method": "string or null",
    "method_rationale": "string or null",
    "grade_band_width": "number or null",
    "grade_band_rationale": "string or null",
    "regression_weighted": "boolean or null",
    "regression_weight_rationale": "string or null",
    "schedule_type": "string or null",
    "num_installments": "integer or null"
  },
  "phase_timestamps": {},
  "last_updated": "ISO datetime"
}
```

Write to `session-state.json` after every operator response, not just at phase boundaries.
`session-state.json` is an ephemeral sandbox cursor — it holds no engagement data and is
regenerable on resume. `operator_mode` is NOT in `session-state.json` — read it from the
backend engagement (`payequity_get_engagement`). Legally-material entries in `operator_decisions`
(comparison_method, grade-band rationale, schedule_type) are also appended to the backend via
`payequity_append_audit_log`.

---

## Error Handling

**Stale entity warnings from the backend:** `payequity_get_engagement` returns a
`stale_entities` set (the backend marks downstream entities stale when an upstream entity is
re-persisted). Display the warning to the operator. Warn and proceed by default; the operator
may re-run the upstream phase or acknowledge and proceed with stale data.

**Tool errors:** Surface the error message verbatim to the operator — whether from a
`call_tool` pure function or a `payequity_*` backend call. Do not silently retry. State which
phase was affected and what data was missing.

**Stale warning structure:**
```
[AVERTISSEMENT] {entity} est obsolète: {stale_reason}
Pour recalculer: retournez à la Phase {N} et relancez {tool_name}.
Pour accepter les données existantes: tapez "continuer avec données obsolètes".
```

**`render_document` failure:** If any render call fails during document generation, stop the
entire document generation workflow. Do not write partial documents. Report: which document
type failed, the error from the tool, and offer to retry.

**Missing required operator decisions:** When `compare_compensation` or `calculate_adjustments`
require a parameter that has no value in `session-state.json`, stop and collect it before calling
the tool. Never pass null for: `grade_band_width`, `grade_band_rationale`, `regression_weighted`,
`regression_weight_rationale`, `schedule_type`.

---

## Phase 0: Mode and Entry Selection (unnumbered)

Present numbered options to operator:

**1. Operator mode:**
```
1. Expert (consultant) — données en masse, avertissements non bloquants
2. Guidé (client) — une question à la fois, explications complètes
```

**2. Data entry mode:**
```
1. Guidé — une question à la fois
2. Saisie groupée — collez les données connues; le système identifie les manquants
3. Import CSV — format: job_title, class_name, incumbent_count, pct_female, hourly_rate, benefits_value
```

**3. Language:**
```
1. Français (défaut)
2. English
```

**4. Exercise type:**
```
1. Exercice initial
2. Audit de maintien (5 ans)
```

**Resuming an existing engagement:** Engagement is keyed by `engagement_id` (the client slug),
not enumerated — there is no `payequity_list_engagements`. To resume, take the known
`engagement_id` and call `payequity_get_engagement(engagement_id)` (which returns the engagement
plus its `stale_entities` set); aggregate the rest of the state directly from the per-entity
getters/listers (`payequity_get_job_class`/`payequity_list_*`, `payequity_get_evaluation_grid`,
`payequity_list_class_compensations`, `payequity_list_comparison_results`,
`payequity_list_class_adjustments`, `payequity_get_adjustment_meta`). Display stale warnings.
Resume from the last completed phase per `session-state.json`.

---

## Phase 1: Intake

**Progress:** `Phase 1/N: Collecte d'information`

**Purpose:** Establish engagement metadata, determine legal obligations.

**Questions to collect:**
- Nom de l'entreprise
- N° d'entreprise du Québec (NEQ)
- Nombre d'employés (determines size tier)
- Type d'exercice (initial / maintien)
- Présence de syndicat (has_union)
- Période de référence (reference_period_start, reference_period_end)
- Établissements multiples? Si oui: nom, lieu, nombre d'employés par établissement

**Additional questions for `exercise_type = maintenance`** (determine Art. 76.2.1 participation trigger):

- L'exercice initial a-t-il été réalisé avec un comité d'équité salariale? (`initial_had_committee`: true/false)
- L'entreprise compte-t-elle au moins une **association accréditée** représentant des personnes salariées visées par l'évaluation du maintien? (`has_accredited_association`: true/false)
- Mode prévu pour l'évaluation du maintien (`intended_maintien_mode`: `employer_solo` / `committee` / `joint_with_union`)

The skill computes `participation_required` automatically:

```
participation_required = (intended_maintien_mode == "employer_solo")
                        AND (initial_had_committee OR has_accredited_association)
```

If `participation_required = true`, the maintien mode is set to `employer_solo_with_participation` and Phase M2.5 (Processus de participation) becomes mandatory and cannot be skipped. The operator cannot opt out — Art. 76.2.1 is a binding obligation.

**Orchestration:**

1. **fetch-before (existence guard):** `payequity_get_engagement(engagement_id=slug)`. If found, refuse — do not overwrite an existing engagement.
2. **call (pure):** `call_tool("create_engagement", ...)` — builds and returns BOTH the engagement and retention-policy models plus a summary dict. It receives no prior state (creation).
   ```
   create_engagement(
     client_name,
     neq,
     employee_count,
     exercise_type,                    # "initial" | "maintenance"
     operator_mode="expert",          # always "expert" in v1 (the dual mode collapsed)
     has_union,
     reference_period_start,
     reference_period_end,
     establishments,                   # list[{name, location, employee_count}]
     # Maintenance-only fields:
     initial_had_committee,            # required if exercise_type = "maintenance"
     has_accredited_association,       # required if exercise_type = "maintenance"
     intended_maintien_mode            # required if exercise_type = "maintenance"
   )
   ```
3. **persist-after:** `payequity_put_engagement(<engagement>)` then `payequity_put_retention_policy(<retention_policy>)`.

**After persist:** fetch `payequity_get_engagement(engagement_id)` to read `size_tier` + `exercise_type`,
call `call_tool("get_obligations", size_tier=..., exercise_type=...)`, and display the obligation matrix.

**Obligation routing:**

| Tier | Obligations | Next Phase |
|------|------------|-----------|
| 10-49 | No committee. Unilateral exercise. Final affichage required. | Phase 3 |
| 50-99 | Committee optional. If formed: same composition rules. Interim + final affichage. 60-day consultation. | Phase 2 (if committee), else Phase 3 |
| 100+ | Committee mandatory. Maintenance committee mandatory. Interim + final affichage. 60-day consultation. | Phase 2 |

For 50-99: ask "Souhaitez-vous former un comité d'équité salariale? (facultatif pour les 50-99 employés)"

**Acceptance criteria:**
- `client_slug` returned and saved to `session-state.json`
- Size tier auto-determined from employee count
- Obligation matrix displayed after `create_engagement`
- Multi-establishment clients: record each establishment in `establishments` array
- For maintenance: `participation_required` computed and reflected in maintien mode
- Phase advances only after operator confirms the displayed obligations

---

## Phase 2: Formation du comité (50+ seulement)

**Progress:** `Phase 2/N: Formation du comité`

**Purpose:** Collect committee composition. Validate legal requirements.

**This runs through `call_tool("set_maintenance_committee", ...)` → `payequity_put_maintenance_committee`.**

**Collect for each member:**
- Nom complet
- Rôle (représentant employeur / représentant employé)
- Genre (femme / homme / autre / non divulgué)
- Unité syndicale (if applicable)

**Validation rules (execute in skill layer):**
1. Employee reps ≥ 2 × employer reps (2/3 employee / 1/3 employer rule — art. 21)
2. Women among employee reps ≥ ⌈employee_reps / 2⌉ (majority of employee seats must be women)
3. If unionized: confirm each bargaining unit has a representative

**Blocking errors (hard stop in both modes):**
- Employee rep ratio not met → "Le comité doit avoir au moins 2/3 de représentants des employés."
- Women not majority of employee reps → "La majorité des sièges des employés doit être occupée par des femmes (Loi, art. 21)."

**Orchestration:**
- fetch-before: `payequity_get_engagement(engagement_id)` to confirm the engagement exists.
- call (pure): `call_tool("set_maintenance_committee", ...)` — builds and validates the committee model.
- persist-after: `payequity_put_maintenance_committee(<committee>)`.

**Storage:** Committee DATA lives in the backend (`payequity_put_maintenance_committee`), not in
`session-state.json`. The `comite-pv.md` deliverable is rendered from that data during Phase 10.

---

## Phase 3: Classes d'emplois

**Progress:** `Phase 3/N: Inventaire des classes d'emplois`

**Purpose:** Collect all job classes with employee counts and gender composition.

**Minimum required per class:**
- Titre de la classe
- Nombre total de titulaires (total_incumbents)
- Nombre de titulaires féminins (female_incumbents)
- Nombre de titulaires masculins (male_incumbents)
- Échelle salariale min/max (pay_range_min, pay_range_max) — recommended, not required

Accept paste block (JSON or CSV). Map fields automatically. Ask for any missing required fields.

**Orchestration:**
- fetch-before: `payequity_get_job_class(...)` / list the engagement's existing classes (so the pure tool can merge against them).
- call (pure): `call_tool("add_job_classes", existing_classes=..., classes=..., enterprise_female_percentage=...)` — validates the three-criteria Art.54 hard-fail, normalizes, merges, and returns the full validated class set (plus pay-spread and similar-description warnings).
  ```
  add_job_classes(
    existing_classes,        # the fetched current classes
    classes: [{
      title,
      description,
      total_incumbents,
      female_incumbents,
      male_incumbents,
      pay_range_min,   # optional
      pay_range_max    # optional
    }]
  )
  ```
- persist-after: `payequity_put_job_class(...)` per class (or batch) with the validated set. The backend sets `stale_entities` on downstream entities — there is no Python invalidation step.

**After persisting classes:** run `call_tool("validate_class_groupings", classes=...)` over the persisted set.

**Display validation results:**
- `pay_spread_flags`: Classes with >30% pay spread — ask operator to confirm grouping is correct
- `similar_description_flags`: Classes with >70% description overlap — ask if they should be merged
- `duties_warnings`: Duties-based warnings

**Warnings:** Non-blocking. Display; operator acknowledges and continues.

**Skill warnings (not from MCP):**
- If fewer than 2 classes total: "Attention: un exercice d'équité salariale nécessite au moins
  une classe féminine et une classe masculine (ou les catégories prescrites)."
- If no apparently female-predominant classes: "Attention: aucune classe ne semble à prédominance
  féminine. Vérifiez les données avant de continuer."

**Acceptance criteria:**
- All pay_spread_flags and similar_description_flags acknowledged
- At least 1 class submitted

---

## Phase 4: Examen de la prédominance

**Progress:** `Phase 4/N: Détermination de la prédominance`

**Purpose:** Determine gender predominance for all classes.

**Orchestration:**
1. **fetch:** `payequity_get_job_class(...)` / list all classes for the engagement.
2. **compute (server, per class):** loop `payequity_compute_predominance(engagement_id, class_id, disproportion_threshold_pp=...)` over each class **where `is_override` is false** — the backend tool is single-class, ports the 4-criteria test (R4), overwrites `predominance` with the algorithmic result, and persists it. Skip any class already marked `is_override=True` (the server tool does NOT preserve overrides — see Phase-4 override path below).
3. **summarize (pure, cross-class):** `call_tool("summarize_predominance", classes=...)` over the full class set (overridden + computed) to derive the cross-class `global_comparison_eligible` (= no male-predominant class) signal plus the female/male/neutral/override counts. The server's per-class compute does not emit this cross-class signal.

**Display results:** Table of class → predominance (féminine / masculine / neutre) with method
(quantitative) and female percentage.

**Four CNESST predominance criteria (any one suffices):**

1. **Numérique** — ≥60% one gender (the default test)
2. **Disproportion par rapport à l'entreprise** — class gender ratio differs from enterprise overall ratio by ≥ 20 percentage points (auto-applied to neutral 40-60% classes)
3. **Historique** — historically associated with one gender even if current ratio is neutral (operator-applied)
4. **Stéréotype** — culturally identified as men's or women's work even if current ratio is neutral (operator-applied)

The server `payequity_compute_predominance` applies tests 1 and 2 automatically (per non-override
class). Tests 3 and 4 are operator-applied via `override_predominance` for any class still neutral
after tests 1-2.

**For classes still `neutral` after tests 1-2:** Ask operator to apply stereotype
or historical test. If override needed:
- fetch-before: `payequity_get_job_class(engagement_id, class_id)` (the single target class).
- call (pure): `call_tool("override_predominance", job_class=..., predominance=..., evidence=...)` — validates the evidence and returns the one updated class with `is_override=True`.
  ```
  override_predominance(
    job_class,                 # the fetched target class
    predominance,   # "female" | "male" | "neutral"
    evidence: {
      evidence_type,             # "stereotype" | "historical"
      description,               # min 10 chars
      historical_period_years,   # if historical
      historical_period_start,   # if historical
      committee_decision,        # boolean
      cnesst_reference,
      decided_by,
      decided_date
    }
  )
  ```
- persist-after: `payequity_put_job_class(<updated class>)`. The backend sets stale on downstream entities. (Because overridden classes carry `is_override=True`, the Phase-4 compute loop above skips them on any re-run — the override is preserved client-side, not server-side.)

**Zero-male-class detection:** If `global_comparison_eligible = true` in the
`call_tool("summarize_predominance", ...)` output, inform operator:
```
Aucune classe à prédominance masculine n'a été détectée.
La méthode de comparaison globale (RLRQ E-12.001 r.2) est disponible.
Les catégories prescrites (Contremaître, Préposé à la maintenance) seront utilisées comme comparateurs.
```
Store this flag in `session-state.json` under `operator_decisions.comparison_method = "global"`.

**Acceptance criteria:**
- All classes have a predominance determination (not null)
- All overrides have a complete evidence record
- If global method: operator has acknowledged the route

---

## Phase 5: Sélection de la grille d'évaluation

**Progress:** `Phase 5/N: Grille d'évaluation`

**Purpose:** Select or customize the evaluation grid.

**Tool call** (pure, no engagement fetch): `call_tool("list_grid_templates")` — reads the packaged
template assets and displays the 3 available templates:

| ID | Nom | Secteur cible | Sous-facteurs | Points max |
|----|-----|--------------|--------------|-----------|
| general-smb | Grille générale PME | Services, administratif, professionnel | N | N |
| healthcare | Grille santé / services sociaux | Cliniques, CPE, CHSLD, org. communautaires | N | N |
| manufacturing | Grille fabrication / métiers | Fabrication, construction, métiers | N | N |

**Selection:**
- fetch-before: `payequity_get_engagement(engagement_id)` to confirm the engagement exists.
- call (pure): `call_tool("select_grid", template_id=...)` — reads the packaged template and builds the grid, sub-factor objects, and the `sub_factor_weights` (kept on the grid entity, not on sub-factors).
- persist-after: `payequity_put_evaluation_grid(<grid>)` (carries `dimension_weights` + `sub_factor_weights`); `payequity_put_sub_factor(...)` per sub-factor. The backend sets stale on downstream entities.

**Bias guidance (display after selection):**
```
Consigne anti-biais: L'effort physique ne devrait pas être pondéré plus fortement que
l'effort mental ou émotionnel (CNESST, Progiciel d'évaluation). Les 4 dimensions
doivent chacune avoir un poids entre 10% et 40%.
```

**Customization (optional):** If operator wants to modify the grid:
- fetch-before: `payequity_get_evaluation_grid(engagement_id)` — returns the grid plus its `sub_factor_weights`.
- call (pure): `call_tool("customize_grid", current_grid=..., current_sub_factor_weights=..., modifications=..., override_physical_dominance=..., override_rationale=...)` — runs the R6 5-rule check (`validate_grid_structure`) over the passed-in weights.
  ```
  customize_grid(
    current_grid,                # the fetched grid
    current_sub_factor_weights,  # the fetched weights
    modifications: {
      add: [{id, name, dimension, description, levels, points_per_level}],
      remove: ["sf_id"],
      modify: [{id, ...fields}]
    }
  )
  ```
- persist-after (only when `is_valid = true`): `payequity_put_evaluation_grid(<grid>)`; `payequity_put_sub_factor(...)` per factor. The backend sets stale.

Display `validation_warnings` from `customize_grid`. If `is_valid = false`, stop, do not persist, and
require the operator to fix the grid before advancing.

**Gate before scoring:** Require operator to type `confirmer la grille` before advancing to Phase 6.

**Acceptance criteria:**
- Evaluation grid persisted via `payequity_put_evaluation_grid` (+ sub-factors)
- `is_valid = true`
- Operator has explicitly confirmed grid

---

## Phase 6: Cotation des classes d'emplois

**Progress:** `Phase 6/N: Cotation`

**Purpose:** Score every job class on the evaluation grid using anchor-class methodology.

**Global comparison path:** If `comparison_method = "global"` in session state, first call:
```
get_prescribed_categories(client_slug)
```
Inform operator: "Les catégories prescrites (Contremaître et Préposé à la maintenance) doivent
être cotées sur la même grille que toutes les autres classes. Voici leurs descriptions."
Add them to the scoring queue.

### Étape 1: Sélection des classes-repères (anchor classes)

Before scoring all classes, select 2-3 anchor classes that represent the scoring extremes:

1. **Anchor haute** — the job class with the highest expected complexity/requirements
   (e.g., the management or senior technical role)
2. **Anchor basse** — the job class with the lowest expected complexity
   (e.g., entry-level or manual labor role)
3. **Anchor médiane** (optional but recommended for 6+ classes) — a role in the middle

Present the list of classes and ask the operator to confirm the anchors:
```
Identifiez vos classes-repères pour calibrer l'évaluation:
- Classe la plus complexe (anchor haute): [suggestion based on title/description]
- Classe la moins complexe (anchor basse): [suggestion]
- Classe médiane (recommandé si 6+ classes): [suggestion]
```

### Étape 2: Cotation des classes-repères

Score anchor classes first, completing all sub-factors for each. For each sub-factor,
present the level descriptions and ask the operator to select:

Show the sub-factor name, dimension, and each level with its description and points.
The operator selects a level number (1-N) — the tool accepts both level numbers and
raw point values.

**In expert mode:** Accept batch scoring as a JSON array. Level numbers (1-5) are
accepted as an alternative to raw point values. The scoring math is server-side and
**single-class** — the orchestration **loops** `payequity_compute_scoring` once per class
(it scores and persists that class's score), then runs the pure completeness gate:
```
# server, per class — loop over the batch:
for each {class_id, awarded}:
    payequity_compute_scoring(engagement_id, class_id, awarded, scored_by="operator_name")

# pure completeness gate (cross-class):
call_tool("all_classes_scored", class_ids=[...all class ids...], scored_ids=[...scored ids...])
```
`payequity_compute_scoring` does NOT compute completeness; `call_tool("all_classes_scored", ...)`
is the gate before comparison.

After scoring anchors, fetch the grid + classes and call
`call_tool("get_evaluation_summary", evaluation=..., job_classes=...)` to display the
anchor scores and verify the spread makes sense:
```
Classes-repères cotées:
  Anchor haute: [title] — [score] points
  Anchor basse: [title] — [score] points
  Écart: [diff] points

Cet écart semble-t-il raisonnable? (oui / ajuster)
```

If the spread is too narrow (<100 pts) or the operator wants to adjust, rescore anchors.

### Étape 3: Cotation des classes restantes

Score remaining classes by comparing each to the nearest anchor. For each class:

1. State which anchor it is closest to in expected complexity
2. For each sub-factor, reference the anchor's score: "L'anchor haute a reçu le
   niveau 4 (65 pts) sur ce sous-facteur. Cette classe devrait-elle être au même
   niveau, plus haut, ou plus bas?"
3. This relative framing prevents drift and ensures consistency

Display anchor scores as reference; accept batch input or sequential entry as the operator prefers.

### After all classes scored

- fetch: `payequity_get_evaluation_grid(engagement_id)`; `payequity_get_job_class(...)`/list all classes.
- call (pure): `call_tool("get_evaluation_summary", evaluation=..., job_classes=..., grade_band_width=..., grade_band_width_rationale=...)` — produces the ranked table, equal-width banding (R8 G-01), bias warnings, and any unscored classes. When the operator supplies a band-width override, the tool also returns an `operator_decision` audit entry.
- persist-after (only when an override is supplied): `payequity_append_audit_log(engagement_id, entry=<operator_decision>)` — the grade-band-width override is legally-material audit trail, not a sandbox file.

**Display evaluation summary:**
- Ranked table of classes by score
- Suggested grade bands (equal-width, auto-calculated)
- Bias warnings
- Distribution analysis
- Any unscored classes

**Grade band confirmation (Gate B prerequisite):**
```
Largeur de bande suggérée: {band_width_suggested} points
Méthode: largeur égale (5 bandes)
Plage de scores: {min} – {max}

Confirmez cette largeur de bande ou fournissez une valeur de remplacement:
> confirmer {band_width}
> remplacer {custom_band_width} — motif: [votre justification]
```

Store confirmed `grade_band_width` and `grade_band_rationale` in `operator_decisions`.

**Acceptance criteria:**
- All classes scored (including prescribed categories if global method)
- `all_classes_scored = true` in evaluation summary
- Grade band width confirmed and stored in `session-state.json`
- No unscored classes in `unscored_classes` list

---

## Phase 7: Porte de révision pré-calcul (obligatoire)

**Progress:** `Phase 7/N: Révision pré-calcul`

**Purpose:** Surface all judgment-dependent inputs before any gap calculation. Cannot be
skipped in either operator mode.

**This is a skill-layer operation (`export_input_checklist`).** Assemble the checklist from the
entities fetched via `payequity_get_*`/`payequity_list_*` (engagement, classes, grid, scores).
Do not call a backend compute tool.

**Checklist (display in full):**
```
PRÉ-CALCUL — REVUE DES DONNÉES DÉTERMINANTES
=============================================
[ ] Regroupements de classes d'emplois
    - {N} classes confirmées
    - {W} avertissements acquittés: {list}
[ ] Déterminations de prédominance
    - {F} classes féminines, {M} masculines, {N} neutres
    - {O} remplacements par l'opérateur (motifs enregistrés)
[ ] Niveaux de pointage par classe
    - {class_title}: {total_score} pts (Grade {grade})
    - [listing all classes]
[ ] Bandes de notes confirmées
    - Largeur de bande: {grade_band_width} pts
    - Motif: {grade_band_rationale}
[ ] Méthode de comparaison retenue
    Options:
      emploi-par-emploi   — comparateurs masculins clairs à chaque niveau de valeur
      proportionnelle     — nombreuses classes masculines couvrent le spectre
      hybride             — emploi-par-emploi si possible, régression pour les non-appariées
      catégories prescrites — aucun comparateur masculin
    Méthode sélectionnée: {method or "NON CONFIRMÉE"}
    Motif: {method_rationale or "[À FOURNIR]"}
[ ] Composantes de rémunération incluses
    - Salaire de base: Oui
    - Primes/commissions: {value or "0 (confirmé)"}
    - Différentiels de quart: {value or "0 (confirmé)"}
    - Assurance collective (part patronale): {value or "0 (confirmé)"}
    - Régime de retraite (part patronale): {value or "0 (confirmé)"}
    - Congés au-delà du minimum légal: {value or "0 (confirmé)"}
    - Autres avantages pécuniaires: {value or "0 (confirmé)"}
[ ] Base des heures annuelles
    - Par classe: [liste des classes avec annual_hours]
    - Si approximation utilisée: mention explicite requise
```

**If comparison method not yet selected:** Stop and collect it now with rationale. Store in
`session-state.json` under `operator_decisions`.

**Regression parameters (if method requires):**
- `regression_weighted` (true/false) + `regression_weight_rationale`

**Gate A — write `review-gate-A.json`** (ephemeral sandbox cursor — gate-confirmation bookkeeping, no engagement data):
```json
{
  "gate": "A",
  "timestamp": "ISO datetime",
  "operator_confirmed": false,
  "checklist_snapshot": {...},
  "operator_decisions": {...}
}
```

**To advance:** Operator types `confirmer` to proceed, or `modifier [item]` to return to
the relevant phase. Write `operator_confirmed: true` to `review-gate-A.json`, and append the
confirmation milestone (with the confirmed `operator_decisions` — comparison_method, grade-band
rationale, regression params) to the backend via `payequity_append_audit_log(engagement_id, entry=...)`
so the legally-material decisions survive the ephemeral gate file.

**This gate cannot be bypassed regardless of operator mode.**

---

## Phase 8: Revue de la rémunération

**Progress:** `Phase 8/N: Comparaison de la rémunération`

**Purpose:** Compare compensation, identify gaps.

**Collect compensation data if not already provided:**

For each class, the operator must provide the **pay structure rate** — not the actual
salary of individual employees:

- **Step scale (échelle à échelons):** use the **top rate** (maximum de l'échelle)
- **Merit/salary range (échelle de mérites):** use the **midpoint** of the range
- **Single rate:** use that rate

This distinction matters: the Act compares job class compensation structures, not what
individual employees happen to earn. Two classes with the same structure rate have no gap
even if their employees' actual pay differs due to seniority or performance.

Required per class: `total_compensation_hourly` (structure rate including all components),
`annual_hours`, and component breakdown (base_salary_hourly, bonuses_commissions,
shift_differentials, group_insurance_employer, pension_employer,
paid_leave_above_statutory, other_monetary). If you provide all component fields but omit
`total_compensation_hourly`, the tool computes it automatically as the sum of components.
If provided explicitly, `total_compensation_hourly` must equal the sum of all components.

When multiple male classes fall in the same grade band, the tool uses a **simple average**
of their structure rates (one rate per class). Headcount is irrelevant for this averaging.

**Orchestration:**
1. **fetch:** `payequity_get_job_class(...)`/list; `payequity_get_evaluation_grid(...)`; `payequity_list_class_compensations(...)` (preserve any operator-entered components).
2. **call (pure, per class — input shaping only):** `call_tool("build_class_compensation", payload=...)` for each class to assemble the `ClassCompensation` (component sum, score/grade fallbacks):
   ```
   build_class_compensation({
     class_id,
     total_compensation_hourly, # structure rate: top of step scale or midpoint of merit range
     base_salary_hourly,
     annual_hours,
     bonuses_commissions,
     shift_differentials,
     group_insurance_employer,
     pension_employer,
     paid_leave_above_statutory,
     other_monetary
   })
   ```
3. **persist input:** `payequity_put_class_compensation(<built class compensation>)` per class.
4. **compute (server — the keystone math):** `payequity_compute_comparison(engagement_id, method=..., grade_band_width=..., regression_weighted=...)`. The server reads classes + grid + compensations, runs the job-to-job → regression → global decision flow (ported verbatim, SC-01 parity, including the `total_gap_annual` 1950-hour fallback and the UNVERIFIED tagging), and persists `comparison_result`×N, `regression_result`, `global_result`, and `compensation_meta`. The decision flow is NOT done in Python.

`method`, `grade_band_width`, `grade_band_rationale`, `regression_weighted`, and
`regression_weight_rationale` come from `operator_decisions`.

**Display gap results:**
- Per-class table: female class, comparator, method, female comp, male comp, gap $/h, gap %
- Regression details if applicable: R², slope, intercept, data points, quality assessment,
  outliers
- Total annual gap

**Regression quality warnings (display but non-blocking in expert; require acknowledgment in
guided):**
- `n_male_classes < 3`: blocking error
- `n_male_classes 3–4`: acknowledgment required
- `R² < 0.50`: acknowledgment required
- `slope ≤ 0`: flag displayed

**For maintenance audits:** After the comparison computes, surface the prior-vs-current diff
produced by `call_tool("import_prior_exercise", ...)` at Phase M1 (the diff is computed against
the current classes and surfaced, not stored). Display: new classes, abolished classes, changed
scores, changed compensation, changed gaps, carry-forward gaps, auto-flagged classes.

**Gap-table skeptics (pré-confirmation, before Gate B):** Before presenting the Gate B prompt,
run the `gap-table-skeptics` panel (`$ASSET_ROOT/_core/primitives/gap-table-skeptics.md`) on the gap
analysis. Two read-only skeptics ($0, Workflow-tool eligible — dispatched via `critic.md`):

- **method-correctness** — reads the gap analysis + `session-state.json`. Does the applied
  method match `operator_decisions.comparison_method` (read from `session-state.json`, **not**
  `engagement.json` which holds `operator_mode`)? Was any female class silently dropped to
  warnings with no comparator?
- **regression-quality** — reads the gap analysis. Are `R² < 0.50`, `slope ≤ 0`, or
  `n_male_classes < 3` logged as warnings-only when they warrant blocking-class attention (the
  Phase-8 warnings above are non-blocking in expert mode — this is the check that they were not
  acknowledged away too fast)?

Each return validates against `gap-table-skeptic.schema.json` (`{skeptic, severity, findings[]}`,
`additionalProperties:false`, no `replacement_text`). Surface the findings **above** the Gate B
display, tagged "pré-confirmation", `severity: block` findings first. `severity` is advisory
routing only — it does **not** auto-block. **Gate B stays human:** the operator still types
`confirmer` (or `modifier`) — invariant #3, never auto-confirm a legal-compliance gate. A
skeptic absent/invalid after one re-dispatch is recorded in `missing[]` and surfaced above the
gate (never silently treated as "no concern").

**Gate B — write `review-gate-B.json`** (ephemeral sandbox cursor) after operator confirms the
gap analysis. Append the confirmation milestone to the backend via
`payequity_append_audit_log(engagement_id, entry=...)`.

**Acceptance criteria:**
- Compensation data submitted for all classes
- `compare_compensation` returned without error
- Gap-table skeptics run; findings surfaced above Gate B (pré-confirmation); skeptics never auto-confirm
- Operator has confirmed the gap table
- `review-gate-B.json` written

---

## Phase 9: Revue des ajustements

**Progress:** `Phase 9/N: Calcul des ajustements`

**Purpose:** Calculate adjustments and payment schedule.

**Interest formula (display to operator):**
```
Intérêts (méthode CNESST — par période de paie):
Pour chaque période de paie i dans la période de rétroactivité:
  Ajustement_i  = écart_par_heure × heures_travaillées_période_i
  Jours_i       = date_calcul − date_d'échéance_période_i
  Intérêts_i    = Ajustement_i × 5% × (Jours_i / 365)

Total intérêts = Σ Intérêts_i (toutes les périodes)

Base légale: C.C.Q. art. 1617 via Loi sur l'équité salariale, arts. 71 / 76.5
Convention: jours calendaires, base 365 jours
Référence: feuille de calcul officielle CNESST (intérêts simples par période de paie)
```

**Important — pas d'approximation par point milieu:** La méthode CNESST documentée
exige le calcul par période de paie, jamais une approximation à montant unique sur
la durée totale. Voir `r3-r9-spec-corrections.md` § R3 et `phase3-legal-interest.md`
finding 4.

**Collect schedule parameters:**
1. Type de versement: `versement unique` ou `versements échelonnés`
2. If installments: how many? (max 4 for initial, max 5 for maintenance)
3. Date du premier versement

**For maintenance audits:** Collect retroactive events. For each event:
```
{
  event_type,           # new_class | abolished_class | duty_change | compensation_change |
                        # cba_renewal | market_adjustment | predominance_shift | merger_restructure
  event_date,
  affected_class_ids,
  art_101_override,     # true if bad faith — shifts interest start to event date
  art_101_rationale     # required if art_101_override = true
}
```
Persist each via `payequity_put_retroactive_event(engagement_id, event=...)` — these are
computation inputs the server's adjustment engine consumes (replaces the old `events.json`).

**Orchestration:**
1. **validate (pure, pre-flight):** `call_tool("validate_adjustment_inputs", num_years=..., retroactive_events=...)` — enforces the Art.76.5.1 `num_years ∈ [1, MAX_INSTALLMENT_YEARS]` installments guard and the R3 retroactive-event `pay_periods`-required hard error as structured refusals BEFORE the heavy math runs. On a refusal, stop and collect corrected inputs.
2. **compute (server — interest + schedule):** `payequity_compute_adjustments(engagement_id, schedule=..., first_payment_date=..., num_years=..., retroactive_events=..., day_convention=..., interest_rate=..., custom_percentages=...)`. The server reads the comparison results + retroactive events, computes per-class adjustments + the per-pay-period interest breakdown (never midpoint, R3) + the payment schedule, and persists `class_adjustment`×N, the interest breakdown, the payment schedule, and `adjustment_meta`.
   ```
   payequity_compute_adjustments(
     engagement_id,
     schedule,              # "lump_sum" | "installments"
     first_payment_date,
     num_years,             # ≤4 initial; ≤5 maintenance (Art.76.5.1)
     retroactive_events     # maintenance only (already persisted above)
   )
   ```

**Display adjustment summary:**
- Per-class: gap $/h, gap annual, total class cost, incumbents
- Payment schedule: installment dates, amounts, percentages
- Retroactive events (maintenance): event, date, classes, amount, interest, total
- Total annual cost, total multi-installment cost, total retroactive cost

**Store** `schedule_type` and `num_installments` in `operator_decisions`.

**Gate C — write `review-gate-C.json`** (ephemeral sandbox cursor) after operator confirms.
Append the confirmation milestone to the backend via `payequity_append_audit_log(engagement_id, entry=...)`.

**Acceptance criteria:**
- `payequity_compute_adjustments` returned without error
- Payment schedule displayed and confirmed
- `review-gate-C.json` written

---

## Phase 10: Génération des documents

**Progress:** `Phase 10/N: Génération des documents`

**Purpose:** Produce all CNESST-compliant deliverables.

**Rule: Every `render_document` call must succeed before any document is written. If any call
fails, stop document generation entirely. Do not write partial documents.**

**Deliverables by tier:**

| Document | 10-49 | 50-99 | 100+ | Type |
|----------|-------|-------|-----|------|
| inventaire-classes | oui | oui | oui | Initial + Maintien |
| grille-evaluation | oui | oui | oui | Initial + Maintien |
| rapport-comparaison | oui | oui | oui | Initial + Maintien |
| ajustements | si écarts | si écarts | si écarts | Initial + Maintien |
| affichage-initial-interim (premier affichage) | non | oui | oui | Initial |
| affichage-initial-final (nouvel affichage) | non | oui | oui | Initial |
| affichage-initial-10-49 | oui | non | non | Initial |
| affichage-maintien | oui | oui | oui | Maintien |
| nouvel-affichage-maintien | oui | oui | oui | Maintien |
| demes-prep | oui | oui | oui | Initial + Maintien |
| comite-pv | non | optionnel | oui | Initial + Maintien |
| provenance-donnees | oui | oui | oui | Initial + Maintien |
| justification-methode | oui | oui | oui | Initial + Maintien |

**Affichage language rule:** Always generate affichage documents in French, regardless of
engagement language setting. If an English translation is requested, generate separately and
include header: "Ce document est une traduction. La version française fait foi."

**Multi-establishment rule:** When `establishment_count > 1`, generate one affichage set per
establishment. Filename pattern: `affichage-initial-final-[etablissement-slug].md`. Generate
a consolidated index. Fail explicitly if establishment list is missing.

**Document generation workflow:**

For each document:

1. **Fetch engagement data from backend.** Always:
   - `payequity_get_engagement(engagement_id)` — base engagement entity
   Then per document type fetch only what that document needs (see table below).
2. **Assemble entities** via pure `call_tool("assemble_<type>", ...)` helpers that reshape
   per-entity backend dicts into file-shaped models (OR-8). No heavy math here.
3. **Render** via `call_tool("render_document", document_type, engagement, *, job_classes,
   evaluation, compensation, adjustments, regression, participation_gate, language,
   include_disclaimer)` — pure Python, returns rendered string.
4. **Replace `{{RENDERED:document_type}}`** placeholders with the rendered output.
5. **Replace `{{NARRATIVE:section_name}}`** placeholders with prose authored by the skill
   (no numbers, no financial data — narrative prose only).
6. **Assemble the complete document** and return content to the operator as a deliverable.

**Affichage = operator deliverable (OR-9):** Return content + intended filename; do not
write to a sandbox path as a persistence source-of-truth. The operator publishes the
affichage; the backend records the posting date (see Phase M1.5 / posting metadata).

**Participation gate (OR-7):** For documents that include the 60-day participation section
(maintien affichage), recompute the gate at render time:
```
payequity_get_participation_session(engagement_id)  →  session
maintien_posting_date = engagement.maintien_posting_date
result = call_tool("has_participation_gate_satisfied", engagement, session, maintien_posting_date)
# → (bool satisfied, str reason)
```
Do NOT read the audit log to check gate status — `payequity_append_audit_log` is write-only.

**Backend fetches by document type:**

| Document stem | Additional `payequity_get_*` / `list_*` fetches |
|---------------|--------------------------------------------------|
| inventaire-classes | `payequity_list_job_classes(engagement_id)` |
| grille-evaluation | `payequity_get_evaluation_grid(engagement_id)`, `payequity_list_job_classes` |
| rapport-comparaison | `payequity_list_comparison_results(engagement_id)`, `payequity_get_regression_result(engagement_id)`, `payequity_get_global_result(engagement_id)` |
| ajustements | `payequity_list_class_adjustments(engagement_id)`, `payequity_list_payment_schedule(engagement_id)`, `payequity_list_interest_breakdown(engagement_id)`, `payequity_get_adjustment_meta(engagement_id)` |
| affichage-initial-interim | `payequity_list_job_classes` |
| affichage-initial-final | `payequity_list_job_classes`, `payequity_get_evaluation_grid`, `payequity_list_comparison_results`, `payequity_list_class_adjustments`, `payequity_list_payment_schedule` |
| affichage-maintien | `payequity_list_retroactive_events(engagement_id)`, `payequity_list_job_classes`, `payequity_list_class_adjustments`, `payequity_list_payment_schedule`, `payequity_list_interest_breakdown`, `payequity_get_participation_session(engagement_id)` |
| comite-pv | `payequity_get_maintenance_committee(engagement_id)` |
| provenance-donnees | `payequity_get_compensation_meta(engagement_id)` |
| justification-methode | `payequity_get_regression_result`, `payequity_list_payment_schedule` |
| demes-prep | (no additional fetches — checklist from base engagement entity) |

**call_tool("render_document", ...) rendered sections by document stem:**

| Document stem | `document_type` arg | Key assembled entities passed |
|---------------|--------------------|-----------------------------|
| inventaire-classes | `classes` | job_classes |
| grille-evaluation | `grid`, `scores` | evaluation, job_classes |
| rapport-comparaison | `gaps`, `regression_summary` | compensation, regression |
| ajustements | `adjustments`, `payment_schedule`, `retroactive`, `interest` | adjustments |
| affichage-initial-interim | `classes` | job_classes |
| affichage-initial-final | `classes`, `scores`, `gaps`, `adjustments`, `payment_schedule` | job_classes, evaluation, compensation, adjustments |
| affichage-maintien | `maintenance_events`, `maintenance_classes`, `maintenance_adjustments`, `maintenance_payment`, `maintenance_interest` | adjustments, participation_gate |
| comite-pv | `committee_composition` | (committee from engagement) |
| provenance-donnees | `provenance` | compensation |
| justification-methode | `regression_summary`, `payment_schedule` | regression, adjustments |
| demes-prep | (no render calls — checklist from metadata) | — |

**Disclaimer placement:**
- Affichage documents: disclaimer at bottom, after all legally mandated content
- All other documents: disclaimer immediately after title block, before first content section

**Disclaimer text (always French, hardcoded):**
> Ce document a été produit à l'aide d'un outil automatisé. Il doit être révisé par une
> personne qualifiée avant utilisation aux fins de conformité à la Loi sur l'équité salariale.

**refute-claim statutory verification (pré-affichage, before the founder review gate):** After the
document is assembled (workflow step 3) and before it is written/finalized, run the `refute-claim`
pre-Write gate (`$ASSET_ROOT/_core/primitives/refute-claim.md`) on the assembled affichage — `[statutory]`
tags only. Affichage carries no `[PROXY]`/`[ESTIMATED]` market figures, so only the statutory path
applies (N=3 skeptics per cited article; statutory dispatches → Opus, invariant #6b; each fetch
gated per-call by `check_budget`).

- It verifies the **cited articles/figures** — the `[statutory]`-tagged citations in the authored
  `{{NARRATIVE:…}}` prose (workflow step 2) — against current QC law, via a fetched verbatim quote
  (`statutory_evidence.{url, quote}`, F6). It does **not** touch the verbatim CNESST template text:
  the `.template.md` files and the deterministic `{{RENDERED:…}}` output are copied/rendered verbatim
  and must never be altered, and the hardcoded French disclaimer above is never rewritten. FLAG-only.
- A statutory `disputed` or `unverifiable` **blocks affichage finalization**; surface the cited
  citation and the fetched text side-by-side and have the operator resolve against the source before
  posting (re-cite / visibly correct / remove). A `fetch_failed` is non-blocking ("verify manually").
  No auto-correct (FLAG-only, invariant #2). Invariant #5 also applies: a `confirmed` with no fetched
  quote is re-mapped to `unverifiable` (no-evidence is never PASS).
- This **complements** the mandatory founder review gate below; it does not replace it. The human
  gate stays human (invariant #3) — refute-claim informs it.

**Founder review gate (mandatory):** After previewing the document list to the operator,
require `confirmer` to write files, or `modifier [document]` to revise a specific section.
This gate cannot be bypassed.

**After confirmation:** Deliver all documents to the operator (content + intended filenames).
Affichage documents are operator deliverables — not sandbox/Drive writes. The operator is
responsible for posting.

**Acceptance criteria:**
- All `payequity_get_*` / `list_*` fetches succeeded
- All `call_tool("render_document", ...)` calls returned without error
- All templates resolved (no unresolved placeholders remain)
- Operator confirmed the document list and received deliverables

---

## Phase 11: Gestion de la consultation (50+ seulement)

**Progress:** `Phase 11/11: Consultation des employés`

**Purpose:** Track two sequential 60-day posting periods. Legal basis: art. 75 (two postings),
art. 76 (60-day consultation, reposting within 30 days of first posting's expiry).

**Orchestration:** fetch-before → call_tool (pure) → persist-after.
`consultation.json` is GONE — all posting dates and observations are persisted to the
backend.

### Sous-phase A — Affichage provisoire

Collect `interim_posting_date` from operator. Compute and display:
```
Date d'affichage provisoire: {interim_posting_date}
Fin de la période de consultation: {interim_posting_date + 60 jours}
Date limite de réaffichage: {interim_posting_date + 60 jours + 30 jours}
```

Persist the posting date:
```
payequity_put_posting_metadata(engagement_id, interim_posting_date=..., status="interim_active")
```

### Sous-phase B — Suivi des observations (fenêtre de 60 jours)

Accept observations during the consultation window. For each observation:
```
log observation:
  date: YYYY-MM-DD
  source: employé | syndicat | autre
  contenu: [texte libre]
```

Orchestration:
1. `payequity_get_observations(engagement_id)` → existing observations list
2. `call_tool("log_observation", observations, date=..., source=..., content=...)` → updated
   observations list (pure — adds entry, computes running counts)
3. `payequity_put_observation(engagement_id, observation=...)` — persist new observation

Display running status from returned observation list:
```
Jours écoulés: {N} / 60
Jours restants: {R}
Observations reçues: {count}
```

### Sous-phase C — Réponse et réaffichage

When operator types `fermer consultation`:
- For each observation, collect operator response:
  - Décision: acceptée | rejetée | partiellement acceptée
  - Motif: [texte]

Orchestration per observation:
1. `payequity_get_observations(engagement_id)` → observations
2. `call_tool("respond_to_observation", observations, obs_id=..., decision=..., motif=...)` →
   updated observation (pure — sets response fields)
3. `payequity_put_observation(engagement_id, observation=...)` — persist response

Skill generates reposting document via `call_tool("render_document", "reaffichage", ...)`
and returns it to the operator as a deliverable (not a sandbox file write).

### Sous-phase D — Affichage final

Collect `final_posting_date`. Open second 60-day window (same structure as sous-phase B/C).

---

## Phase M1: Import de l'exercice antérieur (maintien seulement)

**Progress:** `Phase M1/13: Import des données antérieures`

**Purpose:** Import prior pay equity exercise for comparison baseline.

**Offer three entry paths:**

| Path | When | How |
|------|------|-----|
| **A. Paste-and-parse** | Operator has structured prior data (Excel, JSON, CSV, YAML) | Paste the block; orchestration detects format, parses to a `PriorExercise`-shaped dict, calls `import_prior_exercise` |
| **B. PDF upload via bundled `pdf` skill** | Operator has a CNESST PDF, lawyer-prepared report, or scanned paper exercise | Operator attaches PDF; orchestration invokes the **bundled Anthropic `pdf` skill** (Node.js — the same PDF capability comp-advisor already uses on Claude.ai web) for text extraction; orchestration parses the extracted text into a `PriorExercise` dict using regex + table-cell heuristics; presents line-by-line for operator confirmation; calls `import_prior_exercise` after confirm |
| **C. Saisie guidée (manual class-by-class)** | No structured prior data, no PDF, or PDF extraction unusable | Skill walks each class collecting title, predominance, score, total compensation, incumbents serially; assembles the dict; calls `import_prior_exercise` |

**Why no Python PDF dependency:** the Claude.ai web environment ships a bundled `pdf`
skill (Node.js). Pay equity reuses it instead of forking a parallel Python PDF stack
(`pdfplumber`, `pypdf`). The orchestration-layer parser is fed by the bundled skill's text
output, not by raw PDF bytes. v1 does **not** bundle OCR — for image-based PDFs, the
operator pre-OCRs locally and uses Path A, or falls back to Path C.

**Path B source material:** the source PDF is operator-supplied input — it is not stored as
a backend entity or via Drive. The extracted and operator-confirmed data is what the
orchestration passes to `call_tool("import_prior_exercise", ...)`. The prior cycle + class
diff live in the backend via `payequity_put_cycle`; the raw PDF is the operator's own file.

**Orchestration:**
1. Collect and parse `prior_data` via Path A / B / C above.
2. Fetch current job classes: `payequity_list_job_classes(engagement_id)` → `current_classes`.
3. Compute diff and register prior exercise:
   ```
   call_tool("import_prior_exercise", prior_data, current_classes=current_classes)
   ```
   Returns a `prior_exercise_diff` (class-level delta: new, abolished, changed, unchanged).
4. Register prior exercise as a closed cycle in the backend:
   ```
   payequity_put_cycle(
     engagement_id,
     exercise_type="initial",   # or "maintien" depending on the prior exercise type
     status="closed",
     prior_cycle_id=prior_data.exercise_date   # identifier for the closed cycle
   )
   ```
5. Surface the diff to the operator for confirmation.

The `prior_exercise_diff` is a transient computation result — it is not persisted as a
separate backend entity. The closed cycle registration via `payequity_put_cycle` is the
durable backend record.

**Display import summary:** imported_classes count, exercise date, prior method,
class diff (added / abolished / changed / unchanged counts).
Operator confirms before advancing.

---

## Phase M1.5: Processus de participation (maintien, art. 76.2.1)

**Progress:** `Phase M1.5/13: Processus de participation`

**Triggered when:** `participation_required = true` (computed at Phase 1).
**Skipped when:** `participation_required = false` OR maintien mode is `committee` or `joint_with_union` (the committee/joint process subsumes the participation obligation).

**Legal basis:** Art. 76.2.1 (added by Bill 10, c. 4, en vigueur 10 avril 2019).

**Triggering logic (recap):** Required if and only if employer conducts the maintien alone AND at least one of: (a) a committee was established at the initial exercise, OR (b) the enterprise has at least one accredited association representing employees covered by the maintien.

**Cannot be skipped or opted out.** The skill blocks advancement to Phase M2 until the participation process is recorded as completed.

**Mandatory components:**

1. **Information transmission** — Employer transmits written documents describing the maintien work in progress to:
   - All accredited associations covering affected employees
   - All non-unionized affected employees (or their designated representatives)

2. **Designation of representatives (if non-unionized employees are involved)** — Employer must facilitate a workplace meeting allowing non-unionized employees to designate representatives.

3. **Consultation** — Two-way dialogue allowing participants to pose questions, present observations, voice concerns/expectations/opinions/suggestions about the work in progress.

4. **Compensation** — Participating employees are deemed "at work" for the duration of consultation activities; must be compensated; no retaliation.

5. **Confidentiality** — Participants with access to information are bound by confidentiality.

6. **Documentation** — Employer records:
   - Documents transmitted (with dates and recipients)
   - Questions posed and observations presented
   - How each was considered

**Methodology flexibility:** The Loi does not prescribe a specific format. Acceptable methods include workplace meetings, written surveys, online portals, focus groups, or combinations. The skill collects the chosen method and records it.

**Skill-layer collection:**

```
participation_session = {
  participants: {
    accredited_associations: [{name, contact}],
    non_union_employees_count: integer,
    non_union_representatives: [{name, contact}]
  },
  methodology: "meetings | survey | portal | combined",
  information_transmission: [
    {date, recipients, documents}
  ],
  consultations_held: [
    {date, format, participants_count, summary}
  ],
  questions_and_observations: [
    {received_from, date, content, employer_response, considered_in_audit}
  ],
  participation_completion_date: "YYYY-MM-DD"
}
```

**Timing validation (hard gate):**

```
participation_completion_date + 60 days <= maintien_posting_date
```

The skill blocks advancement to Phase 7 (Gate A) if the planned `maintien_posting_date` is less than 60 days after `participation_completion_date`. The operator must either:
- Extend the planned posting date, OR
- Demonstrate participation completed earlier than the recorded date

**Orchestration:**
```
call_tool("record_participation_session", engagement, participation_session=...)
→ validated_session (pure — checks completeness, timing against maintien_posting_date)

If validated_session.timing_blocked:
    Block advancement; operator must correct dates.

payequity_put_participation_session(engagement_id, session=validated_session)
```

If operator requests a force-override of the 60-day timing gate (rare, with documented
rationale), append the override rationale to the audit log:
```
payequity_append_audit_log(engagement_id, entry={
  event: "participation_gate_override",
  rationale: ...,
  authorized_by: ...,
  timestamp: ...
})
```

`participation.json` and `operator-decisions.json` are GONE — all participation data
and operator decisions flow through the backend.

The session data feeds Section 2 of the maintien affichage
(`{{NARRATIVE:participation_outcomes}}`) at render time via
`payequity_get_participation_session(engagement_id)`.

**Acceptance criteria:**
- All required components recorded via `payequity_put_participation_session`
- `participation_completion_date` set
- Timing validation passes (or force-override documented in audit log)
- For non-unionized employees: representative designation either complete OR documented "no representative needed" (if all employees are unionized)

---

## Phase M2: Identification des changements (maintien seulement)

**Progress:** `Phase M2/13: Identification des changements`

**Purpose:** Record events that occurred since the prior exercise. Feed into retroactive
calculations.

**Event types:**

| Type | Description |
|------|------------|
| `new_class` | Nouvelle classe d'emploi créée |
| `abolished_class` | Classe supprimée ou fusionnée |
| `duty_change` | Changement significatif des tâches |
| `compensation_change` | Modification de la structure de rémunération |
| `cba_renewal` | Renouvellement de convention collective |
| `market_adjustment` | Ajustements salariaux au marché appliqués inégalement |
| `predominance_shift` | Changement de composition affectant la prédominance |
| `merger_restructure` | Fusion, acquisition, restructuration |

**Automated detection:** After `compare_to_prior` runs (Phase 8), auto-flagged classes
(>3% compensation change, no recorded event) are displayed. Operator must either:
- Record an event for the flagged class, or
- Explicitly acknowledge: "ce changement n'est pas un événement déclencheur"

**For each event, collect:**
```json
{
  "event_type": "...",
  "event_date": "YYYY-MM-DD",
  "date_precision": "exact | approximate | range",
  "description": "...",
  "affected_class_ids": ["JC-001"],
  "evidence": "...",
  "compensation_change_direction": "widens_gap | narrows_gap | creates_gap | no_gap_impact"
}
```

**Art. 101 override:** If the employer acted in bad faith (art. 76.9 contravention), ask:
"Y a-t-il eu contravention à l'art. 76.9? (mauvaise foi)" If yes, set `art_101_override = true`
and collect `art_101_rationale`. This shifts the interest start date from the payment due date
to the event date.

**Carry-forward gap warning (display whenever detected):**
```
[AVERTISSEMENT] Écart reporté détecté pour {class_title}.
La portée de la responsabilité rétroactive pour les écarts reportés est non vérifiée.
[UNVERIFIED: Does CNESST retroactivity for carry-forward gaps extend to original event date
or only current cycle? No primary source found.]
Signalez cette situation à un conseiller juridique avant de finaliser les ajustements.
```

**Persist each event to the backend:**
```
payequity_put_retroactive_event(engagement_id, event={
  event_type, event_date, date_precision, description,
  affected_class_ids, evidence, compensation_change_direction,
  art_101_override, art_101_rationale  # maintenance only
})
```

`events.json` is GONE — retroactive events are persisted as backend entities and fetched
by `payequity_list_retroactive_events(engagement_id)` when Phase 9 and document generation
need them.

---

## Review Gates Reference

| Gate | Trigger | Blocks |
|------|---------|--------|
| Gate A | Before compensation comparison (Phase 7) | Phase 8 |
| Gate B | After gap analysis confirmed (Phase 8) | Phase 9 |
| Gate C | After adjustment confirmed (Phase 9) | Phase 10 |

All three gates write ephemeral JSON cursors to the sandbox (`review-gate-A/B/C.json` — no
engagement data, gate bookkeeping only). All three also append the confirmation milestone
to the backend via `payequity_append_audit_log(engagement_id, entry=...)` so legally-material
decisions are durably recorded. All three require explicit `confirmer`. None can be bypassed
regardless of operator mode.

---

## Document Templates Reference

Templates live in `template_assets/pay_equity_cnesst/`.

**On disk in v1 (`template_assets/pay_equity_cnesst/`):** 7 templates ship as
`.template.md` files. The remaining 4 stems are drafted inline as LLM narrative in v1.0
(deferral preserved from `pay-equity-mcp/CLAUDE.md` v1.1 list).

| Template file | Document stem | Purpose | Status |
|---------------|--------------|---------|--------|
| affichage-initial-10-49.template.md | affichage-initial-10-49 | 10-49 initial CNESST posting | Shipped |
| affichage-initial-interim.template.md | affichage-initial-interim | 50+ interim CNESST posting | Shipped |
| affichage-initial-final.template.md | affichage-initial-final | 50+ final CNESST posting | Shipped |
| nouvel-affichage-initial.template.md | nouvel-affichage-initial | 50+ initial reposting | Shipped |
| affichage-maintien.template.md | affichage-maintien | Maintenance audit posting | Shipped |
| nouvel-affichage-maintien.template.md | nouvel-affichage-maintien | Maintenance reposting | Shipped |
| demes-prep.template.md | demes-prep | CNESST DEMES form prep checklist | Shipped |
| inventaire-classes.template.md | inventaire-classes | Job class inventory | LLM narrative (v1.1 deferred) |
| grille-evaluation.template.md | grille-evaluation | Evaluation grid + scores | LLM narrative (v1.1 deferred) |
| rapport-comparaison.template.md | rapport-comparaison | Compensation comparison report | LLM narrative (v1.1 deferred) |
| ajustements.template.md | ajustements | Adjustments + payment schedule | LLM narrative (v1.1 deferred) |
| comite-pv.template.md | comite-pv | Committee minutes | LLM narrative (v1.1 deferred) |
| provenance-donnees.template.md | provenance-donnees | Data provenance | LLM narrative (v1.1 deferred) |
| justification-methode.template.md | justification-methode | Method justification | LLM narrative (v1.1 deferred) |

---

## Placeholder Syntax — Reference

Only two placeholder types are valid in templates:

```
{{RENDERED:document_type}}
  — Replace with output of render_document(client_slug, document_type)
  — Valid document_type values: classes, grid, scores, gaps, regression_summary,
    adjustments, payment_schedule, retroactive, interest, maintenance_events,
    maintenance_classes, maintenance_adjustments, maintenance_payment, maintenance_interest,
    committee_composition, provenance

{{NARRATIVE:section_name}}
  — Replace with prose authored by the skill
  — No numbers, no financial data, no tables
  — section_name is a human-readable label for traceability
```

No other placeholder syntax is valid. If a template contains any other placeholder format,
report it as a template error before generating the document.

---

## CNESST Obligation Matrix Quick Reference

| Tier | Committee | Affichage | Consultation | Phases |
|------|-----------|-----------|-------------|--------|
| 10-49 | Not required | Final only | Not required | 1-10 |
| 50-99 | Optional | Interim + Final | 60 days | 1-11 |
| 100+ | Mandatory | Interim + Final | 60 days | 1-11 |

**Key legal thresholds:**
- 10 employees: law applies (art. 3)
- 50 employees: interim posting required, 60-day consultation (art. 75)
- 100 employees: committee mandatory, maintenance committee mandatory (arts. 32, Bill 10)
- 5-year maintenance cycle (art. 76.1)
- 5% simple interest on late adjustments (C.C.Q. art. 1617 via arts. 71, 76.5)
- 60-day employee consultation period (art. 76)
- Art. 76.5.1: up to 5 installments over 4 years for maintenance
- Pénalité administrative pour défaut de réaliser ou d'afficher: 1 000 $ à 45 000 $ (art. 115)
  Source: avis CNESST formulaire 2304 (rév. 2019-04), confirmé sur cas réel 2020-07-22
