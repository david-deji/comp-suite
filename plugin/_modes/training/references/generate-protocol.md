# /generate Protocol

`/generate` produces a per-audience training bundle: PPTX deck (rendered via pptxgenjs against the engagement brand kit) + facilitator guide (broadcast-with-checkpoints script) + interactive blocks (poll / quiz / scenario / retrieval). Single-audience or batch (all enabled audiences).

---

## Mode-keyed step routing

At session start, read `engagement_mode` from `engagement-training-config.yaml` (or
per-cycle override). Look up step routing in `references/engagement-modes.md`. Apply:

| engagement_mode | Routing |
|---|---|
| `full-bundle` | RUN all steps for all 4 audiences sequentially. Requires message-map.yaml to exist (C05). |
| `single-audience` | RUN all steps for the one audience declared in `audiences_in_scope`. Skip all other audiences. |
| `audience-design-only` | RUN Steps 1-2 (delivery-target stamp + audience-design interview). SKIP Steps 3-5 (render). Write updated message-map slices only. No PPTX produced. Land in `master.training.pre_engagement_artifacts[]`. |
| `cascade-only` | SKIP — /generate should not be called in cascade-only mode. If called, surface: "cascade-only mode is active — use /cascade instead." |
| `ingest-only` | SKIP — /generate should not be called in ingest-only mode. If called, surface: "ingest-only mode is active — run /ingest and then switch mode." |
| `council-deliberation` | SKIP — use /council instead. |

Write the active `engagement_mode` into every artifact frontmatter produced so future
sessions resume with the same routing.

If `engagement_mode` is absent: default to `full-bundle` and log
`decision_type: mode_defaulted_silently` to master.yaml.

Loaded by SKILL.md when intent-router classifies as `/generate`. Loads `meta-protocol.md` (mirrored) for audience-design interview techniques, this file for the per-audience render flow, `cycle-awareness.md` for `delivery_target` metadata stamping, `council-mode.md` for auto-fire on per-audience message-map slice locks, `persona-library.md` for the bundled-5 pack, `interactive-blocks.md` for the block schemas, and `production-and-qa.md` + `template-master.md` + `brand-kit-protocol.md` (all mirrored) for PPTX render discipline.

Templates loaded: `template_assets/facilitator_guide_template.md`, `template_assets/interactive_block_templates.json`, `template_assets/persona_pack_comp-training-v1.yaml`.

---

## Invocation forms

- `/generate` — prompts operator to pick single audience or batch
- `/generate <audience>` — single audience: `employees`, `managers`, `hrbps`, or `execs`
- `/generate batch` — sequential render of all audiences in `engagement-training-config.audiences.enabled`

If no `<cycle-slug>` is supplied OR no `message-map.yaml` exists for the implied cycle, prompt: "Which cycle?" or surface "No message-map found — run `/ingest` first."

---

## Per-audience pipeline (sequential within batch, isolated per single)

For each target audience, the skill executes:

### Step 1 — Delivery-target metadata stamp

Per `cycle-awareness.md`. **No gating.** The skill:

1. Reads `engagement-training-config.cycle.current_stage` and `current_week_offset` (computed at Phase 0).
2. Asks operator: "Delivery target for `<audience>` deck — week offset from anchor? (Default: current week offset)" Operator may accept default or supply explicit offset.
3. Computes `delivery_target` string: `"Week <N> / <stage-name> / target date YYYY-MM-DD"`.
4. Soft-warning ONLY if computed target date is in the past: "Delivery target Week -8 (Discovery) is 6 weeks in the past — proceed anyway, or update?" Operator decides; the skill renders regardless.
5. Stamps the value into deck frontmatter and onto the cover slide (small text below subtitle).

### Step 2 — Audience-design interview (conversational, scoped to one audience)

The skill interviews the operator directly using pros/cons option tables and Mom Test follow-ups. One question at a time. Total time ~10-15 min. Pattern-trigger table in `meta-protocol.md` governs follow-up routing.

Sub-phase progression:

**2a. Room context** — `audience_design_per_render.<audience>` block from `audience_design_block.json`. Use a pros/cons table for delivery posture:

**Q. How will this deck be delivered?**

| Option | Pros | Cons |
|---|---|---|
| **A. Facilitator-led live (in-room)** | Real-time Q&A; polls and scenarios work fully | Facilitator must be prepped; no rewind |
| **B. Facilitator-led live (virtual)** | Wider reach; async chat captures questions | Polling tool needed; scenario discussion is harder |
| **C. Async / self-paced recording** | Scales to any headcount; rewind available | No live Q&A; retrieval prompts and quizzes only (no live polls/scenarios) |
| **D. Manager cascade (team-meeting variant)** | Consistent message across teams; manager owns the room | Cascade kit replaces this deck — use `/cascade` instead |
| **E. Other** | (describe) | |

**2b. Friction calibration** — for each anticipated objection in the message-map slice, confirm: "Is this the real concern, or a sub-concern of something else?" Surface if a major objection is missing. Ask conversationally, one objection at a time.

**2c. Interactive checkpoint placement** — operator decides which messages get a poll / quiz / scenario / retrieval. Skill suggests placement (every 3-5 content slides per `interactive-blocks.md`). Use a pros/cons table when the operator is unsure which block type fits a slide:

**Q. What kind of checkpoint fits slide <N> (message: `<msg-slug>`)?**

| Option | Pros | Cons |
|---|---|---|
| **A. Poll** | Low-stakes commit; surfaces disagreement without individual exposure | Pointless in async delivery; needs polling tool for virtual |
| **B. Knowledge check (quiz)** | Verifies a mechanic landed; exposes common misunderstandings via distractors | Feels like a test if stakes are high; no correct answer for opinion/framing messages |
| **C. Scenario card** | Forces translation of abstract policy to concrete decision; discussion IS the value | Eats 5+ min; too rich for depth-1 employee content; weak in async |
| **D. Retrieval prompt** | Fast; works in any delivery posture; costs almost no time | Only reinforces — doesn't surface disagreement or verify comprehension |
| **E. No checkpoint here** | Keeps pacing tight for this block | Risks content density without a break |

**2d. Cascade-prompt fidelity** (managers-only) — for each cascade-prompt in the message-map, confirm wording. Ask: "As written, would a junior manager reading this cold know what to do with it?" Amend if not.

**2e. Tradeoff framing** (execs-only) — operator names the decision execs are ratifying. Drives Section 5 (Recommendation) of the deck. Conversational: "What specific decision are they approving or declining here?"

**2f. Gap check** — "We don't have an objection-handling angle for [tension] — intentional?"

After gap check: synthesize the audience-design findings. Capture summary (room context, friction calibrations, checkpoint placements, cascade-prompt confirmations, tradeoff framing). Write `discovery/<engagement>/<cycle-slug>/YYYY-MM-DD-audience-design-<audience>.md` (raw capture) per `artifact-generation.md`.

### Step 3 — Council auto-fire (on per-audience message-map slice lock)

Required. Per `council-mode.md`:

- **Pack:** `comp-training-v1` (5 personas — HRBP, comp-manager, audience-recipient, hris-tooling, change-management).
- **Input to council:** the audience-specific slice of `message-map.yaml` (filtered to this audience's messages with their depth, framing, anticipated_objections, cascade_prompt where relevant).
- **Per-persona output:** for each message in the slice, the persona votes "fits / surface concern / drop" with one-line rationale. Audience-recipient persona is weighted heaviest for this audience (they're the proxy for the actual receiver).
- **Synthesis:** orchestrator (the skill, single-context) reads all 5 persona blocks, surfaces dissents, presents to operator.
- **Operator approval:** via inline confirmation. Operator may override any persona's recommendation. Approved slice locks for render.

Output: `council-states/<engagement>/<cycle-slug>-<audience>-generate.yaml`.

### Step 4 — Render bundle (3 co-dependent artifacts)

Co-dependent — uses batched-folder-write per `artifact-generation.md` § Atomicity. Write to `_pending/`, then atomic move on full success.

#### 4a. PPTX deck

Per `production-and-qa.md` (mirrored) and `brand-kit-protocol.md` (mirrored).

1. **Brand template regeneration** — `node build_template.js ORG=<org_slug>` in Claude.ai scratch space. Same discipline as comp-advisor and comp-team-transformer.
2. **Slide-by-slide construction** — for each message in the locked audience slice, build slides per the template-master pattern. Layout discipline:
   - One idea per slide
   - Evidence beside claim
   - Neutral whitespace (Claude.ai pattern)
   - Callout for the one sentence the audience must remember
3. **Checkpoint cadence** — every 3-5 content slides → 1 checkpoint slide (poll / quiz / scenario / retrieval) per `interactive-blocks.md`.
4. **Cover slide** — title = "Comp Training: <engagement-name>"; subtitle = audience-specific (per `brand-mode-protocol.md` § Per-audience cover slide variants); below subtitle: `delivery_target` metadata.
5. **Closing slide** — decision ask if applicable (execs especially); Q&A prompt; HRBP escalation pointer (HRBP+ decks).
6. **Slide budget** (audience-default — operator may override during 2b interactive checkpoint placement):
   - employees: 6-10 slides
   - managers: 12-18 slides (including cascade-prompt slides)
   - hrbps: 15-25 slides (including edge-case + escalation slides)
   - execs: 6-12 slides (including tradeoff + budget slides)

Output: `cycles/<engagement>/<cycle-slug>/<audience>.pptx`.

#### 4b. Facilitator guide (markdown)

Time-blocked broadcast-with-checkpoints script per `template_assets/facilitator_guide_template.md`. One section per slide:

- Slide [N]: [title]
  - Time: [N min cumulative]
  - Facilitator says: [1-3 sentences]
  - Audience does: [the checkpoint OR implicit listen/note action]
  - Purpose: [why this slide is in the deck]
  - Anticipated questions: [from `anticipated_objections` for this audience+message]
  - Anti-FAQ: [questions we will NOT answer here]
  - Escalation path: [HRBP+ decks only]

Frontmatter per `artifact-generation.md` § `<audience>-facilitator.md` schema.

Output: `cycles/<engagement>/<cycle-slug>/<audience>-facilitator.md`.

#### 4c. Interactive blocks (markdown)

Per `interactive-blocks.md` and `template_assets/interactive_block_templates.json`. One file with all blocks for this audience's deck:

- Poll blocks
- Quiz blocks
- Scenario card blocks
- Retrieval prompt blocks

Each block carries `slide_ref` to the slide it targets.

Frontmatter per `artifact-generation.md` § `<audience>-interactive-blocks.md` schema.

Output: `cycles/<engagement>/<cycle-slug>/<audience>-interactive-blocks.md`.

### Step 5 — PPTX QA pass

Per `production-and-qa.md` (mirrored) § 8-Dimension QA Checklist. All dimensions apply unchanged for v1, with these training-domain mappings:

| Dimension | Training-domain mapping |
|---|---|
| 1. Data accuracy | Every numeric claim traces to message-map evidence with source_ref |
| 2. Narrative consistency | Slide order matches the audience-design's tradeoff-framing decision |
| 3. Audience calibration | Slide count matches the audience budget (Step 4a); jargon level matches `voice.audience_voice` |
| 4. Cost figures | (often N/A for training; when present, traces to message-map evidence) |
| 5. Formatting | Source citations on every data slide; consistent formatting per brand kit |
| 6. Decision ask | Closing slide has the explicit ask (especially execs) |
| 7. Brand compliance | Resolved palette/typography/logo per `brand-kit-protocol.md` |
| 8. Adversarial — likely objections | Generated 3-5 objections per audience are addressed in slides (preempted / implicit / missing). Direct mapping from `anticipated_objections` in message-map. |

Failure on any dimension → return to Step 2 (audience-design) for that audience. Do not silently deliver a broken deck.

### Step 6 — Update engagement-training-config

Append/update `cycles_trained[]` entry for this cycle:
```yaml
- cycle_slug: <cycle-slug>
  state: rendered                # was: ingested or message-mapped
  audiences_rendered: [..., <audience>]   # add this audience
  last_render: YYYY-MM-DD
  sources_used: [...]
  delivery_targets:
    <audience>: <delivery_target string>
```

---

## Batch mode

`/generate batch` runs Steps 1-6 sequentially for each audience in `engagement-training-config.audiences.enabled`. Order: employees → managers → hrbps → execs (predictable for operator who's running this in one sitting).

Between audiences:
- Surface progress: "✓ employees rendered (8 slides). Next: managers (~15 min)."
- Auto-checkpoint after each audience's bundle is written.
- If any audience fails QA: pause, surface failure, accept operator's decision (retry that audience or skip and continue).

---

## Operator override capabilities

At any step, operator may:

- **Skip the audience-design interview** — `/generate <audience> --skip-design`. Skill renders directly from message-map slice using defaults. (Risk: misses room-context calibration. Use only for routine refreshes.)
- **Skip the council auto-fire** — `/generate <audience> --skip-council`. Skill renders directly from operator-confirmed message-map slice. (Risk: misses persona dissents. Use only when operator has high confidence.)
- **Force a specific delivery_target** — `/generate <audience> --delivery-target "Week 0 / Cascade / 2026-12-15"`. Skips Step 1 prompt.
- **Override slide budget** — `/generate <audience> --slides <N>`. Skill respects operator's count.

Override flags are recorded in the deck frontmatter for audit.

---

## Failure handling

| Failure | Response |
|---|---|
| message-map.yaml missing | Refuse; suggest `/ingest <cycle-slug>` first |
| audience not in `audiences.enabled` | Refuse; suggest editing engagement-training-config or removing flag |
| brand kit regeneration fails | Per `brand-kit-protocol.md` § Failure handling — degraded mode (no master inheritance) with operator notice |
| QA dimension failure | Return to Step 2 (audience-design) with the failing dimension surfaced as the issue to fix |
| council auto-fire returns thin output (single-line per persona only) | Re-dispatch council with sharpened prompt citing specific message slices |
| delivery_target in past | Soft warning; operator decides |
| Drive write failure mid-batch | Leave artifacts in `_pending/`; surface to operator; do not advance to next audience |

---

## Output files (every `/generate` run)

Per audience:
- **Audience-design raw capture:** `discovery/<engagement>/<cycle-slug>/YYYY-MM-DD-audience-design-<audience>.md`
- **PPTX deck:** `cycles/<engagement>/<cycle-slug>/<audience>.pptx`
- **Facilitator guide:** `cycles/<engagement>/<cycle-slug>/<audience>-facilitator.md`
- **Interactive blocks:** `cycles/<engagement>/<cycle-slug>/<audience>-interactive-blocks.md`
- **Council state:** `council-states/<engagement>/<cycle-slug>-<audience>-generate.yaml`

Engagement-training-config: `cycles_trained[]` updated with `state: rendered` and `delivery_targets[<audience>]`.

---

## What this protocol does NOT contain

- Universal IE techniques (Mom Test, SIPOC, 5 Whys, pros/cons tables, pattern-trigger table) — those live in `meta-protocol.md` (mirrored).
- PPTX QA dimensions — those live in `production-and-qa.md` (mirrored).
- Brand kit regeneration — that lives in `brand-kit-protocol.md` (mirrored).
- Council mechanics — those live in `council-mode.md`.
- Persona pack — that lives in `persona-library.md` and `template_assets/persona_pack_comp-training-v1.yaml`.
- Interactive block schemas — those live in `interactive-blocks.md` and `template_assets/interactive_block_templates.json`.
- Facilitator guide structure — that lives in `template_assets/facilitator_guide_template.md`.
- delivery_target stamping logic — that lives in `cycle-awareness.md`.
- Cascade derivation — that lives in `cascade-protocol.md`.
