# Engagement Modes — comp-team-transformer

Named taxonomy of work-shape modes within the skill's tracks. Closes the gap
where an agent invents partial-flow shapes mid-session because the skill has
no name for them. Modes refine WHICH variant of a command runs.

---

## Mode taxonomy (v1, 6 modes)

| Mode | Steps run | Steps skipped | Typical artifact | Example trigger |
|---|---|---|---|---|
| `full-discovery-to-roadmap` | /discover → /diagnose → /transform → /roadmap chain | none | All 4 artifacts (current-state, diagnosis, transformation-brief, roadmap-Qx) | First-time engagement covering full chain |
| `discovery-only` | /discover (interview + current-state synthesis) | /diagnose, /transform, /roadmap | current-state.md only | "/discover <process-slug>" — scoped to mapping only |
| `diagnose-only` | /diagnose on existing current-state.md | /discover (re-interview), /transform, /roadmap | diagnosis.md (+ optional PPTX) | "/diagnose <process-slug>" with current-state already in folder |
| `transform-only` | /transform on existing diagnosis | /discover, /diagnose | transformation-brief.md + required PPTX + council-state.yaml | "/transform <process-slug>" with diagnosis already in folder |
| `roadmap-refresh` | /roadmap rebuild, reuses existing transformation-briefs | /discover, /diagnose, /transform | Updated roadmap-Qx.md + PPTX | "/roadmap" mid-cycle for a new quarter |
| `council-deliberation` | /council standalone | all production tracks | council-state.yaml + optional decision-memo.md | "/council" on contested process change |

---

## Per-mode detail

### `full-discovery-to-roadmap`

- **mode_id:** `full-discovery-to-roadmap`
- **steps_run:** `/discover`, `/diagnose`, `/transform`, `/roadmap`
- **steps_partial:** none
- **steps_skipped:** none
- **state_shape_variant:** `full`
- **artifact_shape:** current-state.md + diagnosis.md + transformation-brief.md + roadmap-Qx.md + required PPTX for /transform and /roadmap
- **trigger_examples:** "First engagement on this team", "map the whole process end-to-end and build a roadmap", "we're starting fresh"
- **decision_log:** `full-discovery-to-roadmap` — no null-out required

---

### `discovery-only`

- **mode_id:** `discovery-only`
- **steps_run:** `/discover`
- **steps_partial:** none
- **steps_skipped:** `/diagnose`, `/transform`, `/roadmap`
- **state_shape_variant:** `partial`
- **artifact_shape:** current-state.md only; `diagnosis_pending: true` in frontmatter
- **trigger_examples:** "/discover annual-wage-scale-review", "just map the process — we'll diagnose later", "I need a current-state document this week"
- **decision_log:** `null_out_rules_pending_v1_1` (v1.1 will enumerate null-out fields)

---

### `diagnose-only`

- **mode_id:** `diagnose-only`
- **steps_run:** `/diagnose`
- **steps_partial:** none
- **steps_skipped:** `/discover` (re-interview), `/transform`, `/roadmap`
- **state_shape_variant:** `partial`
- **pre_condition:** `processes/<slug>/<process-slug>/current-state.md` must exist. If absent, refuse and route to `discovery-only`.
- **artifact_shape:** diagnosis.md + optional PPTX
- **trigger_examples:** "/diagnose annual-wage-scale-review", "we already have the current-state — run the systems-thinking pass"
- **decision_log:** `null_out_rules_pending_v1_1`

---

### `transform-only`

- **mode_id:** `transform-only`
- **steps_run:** `/transform`
- **steps_partial:** none
- **steps_skipped:** `/discover`, `/diagnose`
- **state_shape_variant:** `partial`
- **pre_condition:** `processes/<slug>/<process-slug>/diagnosis.md` must exist. If absent, refuse and route to `diagnose-only`.
- **artifact_shape:** transformation-brief.md + required PPTX + council-state.yaml
- **trigger_examples:** "/transform annual-wage-scale-review", "diagnosis is done — build the transformation spec"
- **decision_log:** `null_out_rules_pending_v1_1`

---

### `roadmap-refresh`

- **mode_id:** `roadmap-refresh`
- **steps_run:** `/roadmap`
- **steps_partial:** none
- **steps_skipped:** `/discover`, `/diagnose`, `/transform`
- **state_shape_variant:** `partial`
- **pre_condition:** ≥2 `transformation-brief.md` files already exist for the team. Reuses existing briefs — does NOT run /transform again.
- **artifact_shape:** Updated roadmap-Qx.md + required PPTX
- **trigger_examples:** "/roadmap", "we need to re-sequence for Q3", "quarterly roadmap refresh"
- **decision_log:** `null_out_rules_pending_v1_1`

---

### `council-deliberation`

- **mode_id:** `council-deliberation`
- **steps_run:** `/council` standalone
- **steps_partial:** none
- **steps_skipped:** all production tracks
- **state_shape_variant:** `standalone`
- **artifact_shape:** council-state.yaml + optional decision-memo.md
- **trigger_examples:** "/council on whether to automate the approvals step", "run a council on this contested change", "stress-test this decision"
- **decision_log:** `null_out_rules_pending_v1_1`

---

## Mode declaration — uniform syntax

Every partial-flow engagement writes the following fields to its artifact frontmatter
and to the engagement state file:

```yaml
engagement_mode: <mode_id>           # required — must match a v1 mode above
mode_steps_run: [...]                # populated from taxonomy
mode_steps_skipped: [...]            # populated from taxonomy
mode_steps_partial: []               # populated from taxonomy
pre_engagement_only: false           # true only when artifact lands in pre_engagement_artifacts[]
state_shape_variant: full | partial | standalone | pre_engagement
decision_log: null_out_rules_pending_v1_1  # emit when mode has no v1 null-out rules
```

`engagement_mode` MUST be declared before the first artifact write (C08 contract).

---

## Null-out scope (v1)

No comp-team-transformer mode ships explicit field-level null-out rules in v1.
Workers populating partial-flow state MUST emit `decision_type: null_out_rules_pending_v1_1`
to `decision_log[]` so the gap is visible. v1.1 will add per-mode null-out rules
based on operational friction.

---

## Anti-pattern

Do NOT declare a mode mid-session without a name. If the work shape doesn't fit
any v1 mode, surface the options:
> "This looks like a sub-shape we don't have a name for. Should we (a) shoehorn
> into the closest mode and accept the schema mismatch, or (b) propose a v1.1 mode
> and document the gap?"

Do NOT silently invent a mode.

---

## One process slug per engagement

`council-deliberation` is `state_shape_variant: standalone` — it runs outside
the canonical chain and does not produce cycle_state_pointers entries.
All production modes (`discovery-only`, `diagnose-only`, `transform-only`,
`roadmap-refresh`, `full-discovery-to-roadmap`) scope to one process slug per
session. Multi-process bundles trigger a split recommendation (see C07 in
`contracts.md`).
