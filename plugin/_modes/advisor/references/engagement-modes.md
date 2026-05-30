# Engagement Modes — compensation-advisor

Named taxonomy of work-shape modes within the existing tracks (C/D/R/R-lite/Council).
Closes the friction where the agent has to invent partial-flow shapes mid-session
because the skill has no name for them. Read this whenever a partial-flow request
arrives (anything less than a full Phase 1-7 engagement).

## Mode taxonomy (v1, 6 modes)

| Mode | Phases run | Phases skipped | Typical artifact | Example trigger |
|---|---|---|---|---|
| `full-engagement` | 0, 1, 2, 3, 4, 5, 6, 7 | none | Recommendation deck (15-25 slides) | Strategy Kickoff at week −11 with workforce data |
| `narrative-frame-only` | 0, 5 | 1, 2, 3, 4, 6 (partial — narrative-only slides), 7 (partial — pre-engagement state) | Pre-read deck (5-8 slides) | "narrative-first pre-read at week −22" — telescoping ahead of the spine |
| `data-light-decision` | 0, 1 (light), 5, 6, 7 | 2 (partial), 3 (partial), 4 | 1-page decision brief | "VP Ops needs a paragraph for Tuesday — no costing" |
| `numbers-refresh` (R-lite alias) | 0, 2, 6, 7 | 1, 3, 4, 5 | Refreshed deck (same shape as prior) | ".pptx upload + 'just numbers'" |
| `costing-only` | 0, 4 | 1, 2, 3, 5 | Scenarios spreadsheet (.xlsx) + memo | "I need cost models for Scenario A vs B vs C, no narrative" |
| `council-deliberation` | 0 + Council standalone | 1-7 | Decision memo (.md) + council-state.yaml | `/council` standalone |

## Per-mode detail

### `full-engagement`
- `phases_run`: [0, 1, 2, 3, 4, 5, 6, 7]
- `phases_partial`: []
- `phases_skipped`: []
- `state_shape_variant`: `full`
- `artifact_shape`: Recommendation deck, 15-25 slides, all sections present
- `trigger_examples`: "Strategy Kickoff at week −11", "build the kickoff deck", "full engagement on pharmacy fy27"

### `narrative-frame-only`
- `phases_run`: [0, 5]
- `phases_partial`: [6, 7]  (Phase 6 = narrative-only slides, no costing slides; Phase 7 = pre-engagement state declaration)
- `phases_skipped`: [1, 2, 3, 4]
- `state_shape_variant`: `pre_engagement`
- `pre_engagement_only`: true
- `artifact_shape`: Pre-read deck, 5-8 slides, narrative arcs only (Force/Option/Question framing)
- `trigger_examples`: "narrative-first pre-read", "frame the decision space", "no numbers yet, just the framing"
- **Field-level null-out rules (v1 — only mode with explicit rules):**
  - `scenario_chosen: null`
  - `costed_scenario_summary: null`
  - `selection_log: []` (do NOT pretend Phase 4 ran)
  - `ledger_treatment: pre_engagement_artifact` (NOT `closed_engagement`)
  - All `cost_*` fields: null
  - All `market_*` fields: null

### `data-light-decision`
- `phases_run`: [0, 1, 5, 6, 7]   (Phase 1 in light form — context only, no full discovery)
- `phases_partial`: [2, 3]   (skim survey-house + market data; no per-province pull)
- `phases_skipped`: [4]
- `state_shape_variant`: `partial`
- `artifact_shape`: 1-page decision brief (.md or single slide), no full deck
- `trigger_examples`: "VP Ops needs a paragraph for Tuesday", "single-page decision brief", "no costing"
- **Null-out rules**: emit `decision_log: null_out_rules_pending_v1_1` (rules deferred to v1.1)

### `numbers-refresh` (R-lite alias)
- `phases_run`: [0, 2, 6, 7]
- `phases_partial`: []
- `phases_skipped`: [1, 3, 4, 5]
- `state_shape_variant`: `partial`
- `artifact_shape`: Refreshed deck — same structure as prior, only numbers updated
- `trigger_examples`: ".pptx upload + 'just numbers'", "refresh the rates", "update the wage scale"
- **Null-out rules**: emit `decision_log: null_out_rules_pending_v1_1` (rules deferred to v1.1)

### `costing-only`
- `phases_run`: [0, 4]
- `phases_partial`: []
- `phases_skipped`: [1, 2, 3, 5, 6, 7]   (no deck, no narrative, no engagement-state close)
- `state_shape_variant`: `pre_engagement`
- `pre_engagement_only`: true
- `artifact_shape`: Scenarios spreadsheet (.xlsx) + cost memo (.md)
- `trigger_examples`: "I need cost models for Scenario A vs B vs C", "scenario costing only", "no narrative"
- **Null-out rules**: emit `decision_log: null_out_rules_pending_v1_1` (rules deferred to v1.1)

### `council-deliberation`
- `phases_run`: [0]   (Council standalone — runs outside Phase 1-7)
- `phases_partial`: []
- `phases_skipped`: [1, 2, 3, 4, 5, 6, 7]
- `state_shape_variant`: `standalone`
- `artifact_shape`: Decision memo (.md) + council-state.yaml
- `trigger_examples`: "/council on this question", "deliberate on Scenario A vs B", "run a council"
- **Null-out rules**: only mode-relevant fields populated; engagement-state schema does NOT apply (council has its own state file)

## Uniform mode declaration syntax (in state files)

Every state file in compensation-advisor that records mode-aware work carries:

```yaml
engagement_mode: <mode_id>           # required — must match a v1 mode in the table above
mode_phases_run: [...]                # populated from taxonomy
mode_phases_skipped: [...]            # populated from taxonomy
mode_phases_partial: [...]            # populated from taxonomy
pre_engagement_only: true|false       # true when state_shape_variant ∈ {pre_engagement}
state_shape_variant: full | partial | standalone | pre_engagement
                                      # full         = standard schema, all fields populated
                                      # partial      = mode-specific null-out applies (v1: only narrative-frame-only)
                                      # standalone   = mode runs outside the canonical phase chain (council-deliberation)
                                      # pre_engagement = mode produces a pre-engagement artifact (lands in master.advisor.pre_engagement_artifacts[], NOT cycle_state_pointers[])
```

## Null-out scope (v1)

Only `narrative-frame-only` ships explicit field-level null-out rules in v1
(documented above). Every other mode declares `state_shape_variant` per its
taxonomy entry but does NOT enumerate field-level null-out rules in v1.
Workers populating partial-flow state for a mode without v1 null-out rules
MUST emit a `decision_log` entry of `decision_type: null_out_rules_pending_v1_1`
so the gap is visible. v1.1 will add per-mode null-out rules driven by friction.

WHY: enumerating null-out for ~23 mode×skill combinations in v1 is the
cascading-failure shape; deferring with a visible marker is the
minimum-viable shape.

## How modes interact with tracks

- **Tracks (C/D/R/R-lite/Council)** are entry-point classifications from
  `intent-router.md`.
- **Modes** are work-shape declarations within a track.
- **Default mode per track:**
  - C → `full-engagement`
  - D → `full-engagement` (with silent 6b stage-keyed framing)
  - R → `full-engagement` from prior context
  - R-lite → `numbers-refresh`
  - Council → `council-deliberation`
- Track + mode combinations can be overridden in Phase 0 by:
  1. An explicit user signal ("narrative-first", "no costing", "data-light")
  2. A stage-vs-week mismatch the cycle-stage check surfaces (week −22 with
     a kickoff request → too-early protocol → may select narrative-frame-only
     or another pre-engagement mode)

## Anti-pattern (refused)

Declaring a mode mid-session without a name. If the work shape doesn't fit
any v1 mode, the agent surfaces:

> "This looks like a sub-shape we don't have a name for. Should we (a) shoehorn
> into the closest mode and accept the schema mismatch, or (b) propose a v1.1
> mode and document?"

Do NOT silently invent. Mid-session improvisation is what the named taxonomy
exists to prevent.
