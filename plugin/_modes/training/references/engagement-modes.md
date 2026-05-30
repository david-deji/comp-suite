# Engagement Modes — comp-training-designer

Named taxonomy of work-shape modes. Closes the friction where the agent invents
partial-flow shapes mid-session because the skill has no name for them.

**Anti-pattern (refused):** declaring a mode mid-session without a name. If the work
shape doesn't fit any v1 mode, the agent surfaces: "this looks like a sub-shape we
don't have a name for. Should we (a) shoehorn into the closest mode and accept the
schema mismatch, or (b) propose a v1.1 mode and document?" — does NOT silently invent.

---

## Mode taxonomy (v1, 6 modes)

| Mode | Steps run | Steps skipped | Typical artifact | Example trigger |
|---|---|---|---|---|
| `full-bundle` | /ingest (if no message-map), /generate for all 4 audiences (employees + managers + hrbps + execs), /cascade optional | none | All 4 audience PPTXs + facilitator guides + interactive blocks | Standard engagement post-/ingest |
| `single-audience` | /generate for one audience only | other audiences | One PPTX + guide + interactive blocks for the chosen audience | "/generate execs" |
| `cascade-only` | /cascade derive team-meeting variant from existing manager deck | /generate (manager deck must already exist) | managers-cascade-kit.pptx + managers-cascade-facilitator.md | "/cascade" after manager deck shipped |
| `ingest-only` | /ingest workflow | /generate, /cascade | message-map.yaml only | "/ingest <source>" with no render request |
| `audience-design-only` | /generate audience-design interview, no render | full PPTX render | Updated audiences block in engagement-training-config + per-audience message-map slices | "/generate" with `design-only: true` |
| `council-deliberation` | /council standalone on contested message-map decision | all production modes | council-state.yaml + optional decision-memo.md | "/council" on per-audience message-map slice |

---

## Per-mode detail

### `full-bundle`

- **steps_run**: ingest (if no message-map exists), generate (all 4 audiences sequentially), cascade (optional, operator-triggered)
- **steps_partial**: none
- **steps_skipped**: none
- **state_shape_variant**: `full`
- **artifact_shape**: All 4 audience PPTX decks + facilitator guides + interactive blocks. message-map.yaml.
- **trigger_examples**:
  - "run the full training bundle"
  - "/generate batch"
  - Standard engagement post-/ingest with no audience restriction

### `single-audience`

- **steps_run**: generate (one audience only)
- **steps_partial**: none — full /generate protocol runs, scoped to one audience
- **steps_skipped**: generate for other audiences; cascade (unless separately invoked)
- **state_shape_variant**: `partial` — `audiences_out_of_scope` populated; other audience fields null
- **artifact_shape**: One PPTX + guide + interactive blocks for the specified audience
- **trigger_examples**:
  - "/generate execs"
  - "/generate managers"
  - "just the employee deck"
  - "generate training for HRBPs only"

### `cascade-only`

- **steps_run**: /cascade derivation logic only
- **steps_partial**: none
- **steps_skipped**: /ingest, /generate (manager deck must already exist in the cycle)
- **state_shape_variant**: `partial` — only cascade-kit fields populated; other audience fields inherited from manager deck state
- **artifact_shape**: managers-cascade-kit.pptx + managers-cascade-facilitator.md
- **prerequisite**: `cycles/<engagement>/<cycle-slug>/managers.pptx` must exist. If absent, refuse with: "No manager deck found for `<cycle-slug>`. Run `/generate managers` first?"
- **trigger_examples**:
  - "/cascade"
  - "cascade kit"
  - "team-meeting variant"
  - "derive the cascade from the manager deck"

### `ingest-only`

- **steps_run**: /ingest workflow (full interview arc through scripted close)
- **steps_partial**: none
- **steps_skipped**: /generate, /cascade
- **state_shape_variant**: `partial` — message-map.yaml produced; no deck metadata populated
- **artifact_shape**: message-map.yaml only
- **trigger_examples**:
  - "/ingest <source>"
  - "ingest these sources, I'll generate later"
  - "build the message map only"

### `audience-design-only`

- **steps_run**: /generate audience-design interview (Steps 1-2 of generate-protocol.md)
- **steps_partial**: /generate (interview only, no render)
- **steps_skipped**: full PPTX render, facilitator guide, interactive blocks
- **state_shape_variant**: `pre_engagement` — lands in `master.training.pre_engagement_artifacts[]`, not `cycle_state_pointers[]`
- **artifact_shape**: Updated `audiences` block in engagement-training-config + per-audience message-map slices
- **trigger_examples**:
  - "/generate" with `design-only: true` flag
  - "just the audience design, no decks yet"

### `council-deliberation`

- **steps_run**: /council standalone
- **steps_partial**: none
- **steps_skipped**: all production modes (/ingest, /generate, /cascade)
- **state_shape_variant**: `standalone` — only council-relevant fields populated
- **artifact_shape**: council-state.yaml + optional decision-memo.md
- **trigger_examples**:
  - "/council"
  - "deliberate on the message-map slice for managers"
  - "council on this audience framing decision"

---

## Mode declaration in state files

```yaml
engagement_mode: single-audience      # required — must match a v1 mode above
audiences_in_scope: [execs]           # mode-specific — populated for single-audience
audiences_out_of_scope: [employees, managers, hrbps]
mode_steps_run: [generate]
mode_steps_skipped: [cascade-derive]
mode_steps_partial: []
pre_engagement_only: false
state_shape_variant: full             # full | partial | standalone | pre_engagement
```

**Null-out scope (v1):** `audience-design-only` is the only mode with explicit pre-engagement
semantics. All other modes with `state_shape_variant: partial` do NOT enumerate field-level
null-out rules in v1 — workers MUST emit a `decision_log` entry of
`decision_type: null_out_rules_pending_v1_1` so the gap is visible. v1.1 will add per-mode
null-out rules driven by production friction.

**If `engagement_mode` is absent from the state file:** default to `full-bundle` and log
`decision_type: mode_defaulted_silently`.

---

## Uniform mode declaration syntax (all commands)

At session start for any command other than `/help`, `/checkpoint`, `/resume`:

1. Read `engagement_mode` from `engagement-training-config.yaml` (or per-cycle override).
2. Look up the mode's step routing in the taxonomy table above.
3. Apply RUN / PARTIAL / SKIPPED routing for this session.
4. Write `engagement_mode` into every artifact frontmatter produced so future sessions
   resume with the same routing.

**Mode can be overridden at session start** via explicit user signal:
- "single audience — execs only" → override to `single-audience` + set `audiences_in_scope: [execs]`
- "cascade only" → override to `cascade-only`
- Log any mid-session mode override as `decision_type: org_metadata_updated` in decision_log.
