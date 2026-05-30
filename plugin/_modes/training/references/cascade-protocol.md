# /cascade Protocol

`/cascade` derives a 30-min team-meeting variant from the manager training deck. The manager runs the derived deck WITH their team, not AT them. **Mechanical restructure** — no contested decisions, no council auto-fire.

---

## Mode-keyed step routing

At session start, read `engagement_mode` from `engagement-training-config.yaml` (or
per-cycle override). Look up step routing in `references/engagement-modes.md`. Apply:

| engagement_mode | Routing |
|---|---|
| `cascade-only` | RUN all steps. Requires existing manager deck (C06). Derives team-meeting variant from manager deck, not from scratch. |
| `full-bundle` | RUN all steps when the operator invokes /cascade after /generate managers completes. /cascade is optional in full-bundle mode. |
| `single-audience` | SKIP — cascade derives from the manager deck; single-audience mode targeting managers can be followed by /cascade. If audience is not managers, surface: "Cascade requires the manager deck — run /generate managers first." |
| `ingest-only` | SKIP — no deck exists to cascade from. |
| `audience-design-only` | SKIP — no deck exists to cascade from. |
| `council-deliberation` | SKIP — use /council instead. |

Write the active `engagement_mode` into cascade-kit frontmatter so future sessions
resume with the same routing.

If `engagement_mode` is absent: default to `full-bundle` treatment and log
`decision_type: mode_defaulted_silently` to master.yaml.

Loaded by SKILL.md when intent-router classifies as `/cascade`. Loads `cascade_kit_template.md`, plus `production-and-qa.md` + `template-master.md` + `brand-kit-protocol.md` (all mirrored) for the PPTX render.

---

## Prerequisites

`/cascade` requires:
- `cycles/<engagement>/<cycle-slug>/managers.pptx` exists (the manager training deck)
- `cycles/<engagement>/<cycle-slug>/managers-facilitator.md` exists
- `cycles/<engagement>/<cycle-slug>/managers-interactive-blocks.md` exists
- `cycles/<engagement>/<cycle-slug>/message-map.yaml` exists (for cascade-prompt extraction)

If any prerequisite is missing: refuse with friendly message ("No manager deck found for `<cycle-slug>`. Run `/generate managers` first?").

---

## Restructuring rules (mechanical)

### Drop slides

Remove from the manager deck:
- **Anti-FAQ slides** — questions the manager facilitator was told NOT to answer in their session. These are facilitator-only context; cascading them creates confusion.
- **Escalation-path slides** — HRBP-handoff references, "if employee asks X, route to Y". Manager-only operational content.
- **Exec-only context slides** — any slide flagged in source as depth-4 (tradeoff / budget / governance). Cascade is depth-1 + depth-2 only.
- **Council-dissent slides** — internal debate context that doesn't belong in a team meeting.
- **Detailed objection-handling slides** — keep the message; drop the multi-slide deep dive on how to handle objections (the manager handles objections live; the team meeting kit doesn't need the playbook).

### Keep slides

- **Cover** (re-titled to "Team Meeting: <cycle-slug>")
- **Depth-1 content** — every message tagged for employees survives (manager will re-deliver these)
- **Depth-2 content** — most depth-2 manager content survives, EXCEPT the dropped categories above
- **Closing** (re-titled to "Discussion + Next Steps")

### Add slides (cascade prompts)

Before each major content block, insert one cascade-prompt slide:
- Slide layout: large prompt text, small attribution ("Manager: ask your team")
- Content: pulled from `message-map.yaml`'s `messages[].audiences.managers.cascade_prompt` field, where set
- Example: "Manager: ask your team — how do you understand this cycle's merit-vs-market split?"

Skip insertion if no `cascade_prompt` is set for the block's source message.

### Compress timing

Target 25-35 min total walkthrough (vs 60-90 min for manager training):
- Cover + closing: ~3 min
- Per content slide: ~1.5 min average (faster pace than manager training, more team interaction)
- Per cascade-prompt slide: ~3-5 min (open team discussion)

### Lighten interactive blocks

- **Keep retrieval prompts** — fast, cheap, reinforce key messages.
- **Drop scenario cards** — too long for team meetings.
- **Drop polls** — manager + team = small audience, polls feel forced.
- **Convert quizzes to retrieval prompts** — "Without looking at the slide — what was the headline?" replaces multi-choice quizzes.

---

## Render pipeline

### Step 1 — Load source artifacts

Read in order:
1. `managers.pptx` — extract slide structure (titles, text content, master inheritance, slide ordering)
2. `managers-facilitator.md` — extract slide-by-slide intent and audience-action notes
3. `managers-interactive-blocks.md` — extract block schemas
4. `message-map.yaml` — extract `cascade_prompt` field for each manager-scope message

### Step 2 — Apply restructuring rules

Walk slide-by-slide through `managers.pptx`. For each slide:
- Read its source message (cross-ref via `slide_ref` in `managers-interactive-blocks.md` or message-map)
- Apply DROP / KEEP / ADD rules above
- Compute new slide ordering (dropped slides removed; cascade-prompt slides inserted)

### Step 3 — Brand template regeneration

Same as `/generate` Step 4a, per `brand-kit-protocol.md` (mirrored). `node build_template.js ORG=<org_slug>` in Claude.ai scratch space. Cover slide subtitle: "Team Meeting: <cycle-slug>" (vs the manager deck's "<cycle-name> Manager Briefing").

### Step 4 — Render

Build slides into the new PPTX:
- Cover (re-titled)
- Surviving content slides (kept depth-1 + depth-2)
- Cascade-prompt slides (inserted before each major content block)
- Closing (re-titled)

`delivery_target` metadata: stamped on cover slide. Computed as: `cycle.current_stage` + operator-supplied delivery offset (defaults to manager deck's `delivery_target` shifted by 1 week for cascade timing). Per `cycle-awareness.md`.

### Step 5 — Render facilitator guide (lighter)

`managers-cascade-facilitator.md` — lighter than the manager facilitator guide. One section per slide:

- Slide [N]: [title]
  - Time: [N min cumulative]
  - Manager says: [1-2 sentences — terse, conversational]
  - Team does: [discusses / answers retrieval prompt / asks question]
  - Cascade prompt: [if this slide IS a cascade-prompt slide, the exact prompt to read aloud]

Drop from manager facilitator guide:
- Anti-FAQ sections
- Escalation paths
- Detailed objection-handling
- Anticipated-questions deep dives

Keep:
- Cover slide setup notes
- Per-content-slide brief direction
- Cascade-prompt direction (NEW vs manager guide)

Frontmatter per `artifact-generation.md` § `managers-cascade-facilitator.md` schema.

### Step 6 — PPTX QA pass

Per `production-and-qa.md` (mirrored). 8 dimensions, with cascade-specific overrides:

| Dimension | Cascade-specific override |
|---|---|
| 1. Data accuracy | Same as `/generate` |
| 2. Narrative consistency | Cascade ordering preserves manager-deck narrative; cascade-prompts inserted at sensible breakpoints |
| 3. Audience calibration | Slide count: 8-15 (vs manager 12-18). Pace: ~1.5 min/slide content + 3-5 min/cascade-prompt. |
| 4. Cost figures | Same — but generally absent (cascade rarely surfaces dollar amounts) |
| 5. Formatting | Same |
| 6. Decision ask | Closing slide: "Discussion + Next Steps", not a decision ask (manager doesn't ask team to ratify) |
| 7. Brand compliance | Same brand kit; subtitle changes |
| 8. Adversarial — likely objections | Cascade objections are different — focus on "this isn't fair to my team specifically" / "why didn't we get more". The dropped objection-handling slides should still leave manager-equipped — verify via the kept depth-2 content. |

### Step 7 — Update engagement-training-config

Update `cycles_trained[]` entry for this cycle:
```yaml
- cycle_slug: <cycle-slug>
  state: cascaded                # was: rendered
  audiences_rendered: [..., managers-cascade]   # add the special tag
  last_render: YYYY-MM-DD        # update
  delivery_targets:
    managers-cascade: <delivery_target string>
```

---

## Soft warnings (not blocking)

| Condition | Warning |
|---|---|
| Derived deck has <8 slides | "Cascade kit is thin (<8 slides). Manager deck may be heavier on objection-handling than depth-1+2 content. Want to proceed, or revise the manager deck first?" |
| No cascade_prompt fields populated in message-map | "No cascade-prompts marked in message-map. Cascade kit will have no team-discussion slides — it'll be a slide-walkthrough only. Want to proceed, or run `/ingest --update-cascade-prompts` first?" |
| Manager deck has slides flagged depth-4 (exec-only) | "Manager deck has <N> exec-only slides. These are dropped in cascade. Verify manager deck didn't accidentally include exec context (run `/ingest --review-depths` if needed)." |
| Delivery target before manager deck delivery target | "Cascade target (Week -1) is BEFORE manager deck target (Week 0). Cascade typically runs AFTER manager training. Verify timing." |

Operator decides on each warning. None blocks the render.

---

## Output files (every `/cascade` run)

- **PPTX:** `cycles/<engagement>/<cycle-slug>/managers-cascade-kit.pptx`
- **Facilitator guide:** `cycles/<engagement>/<cycle-slug>/managers-cascade-facilitator.md`
- **(No new interactive-blocks file — retrieval prompts are inline in the facilitator guide)**

Engagement-training-config: `cycles_trained[]` entry updated to `state: cascaded` with `delivery_targets[managers-cascade]`.

---

## What this protocol does NOT contain

- Manager deck construction — that lives in `generate-protocol.md` (managers audience).
- Cascade-prompt extraction logic — those are populated during `/ingest` per `audience_design_block.json` § cascade_cue_marking.
- Brand kit regeneration — that lives in `brand-kit-protocol.md` (mirrored).
- PPTX QA dimensions — those live in `production-and-qa.md` (mirrored).
- Interactive block schemas — those live in `interactive-blocks.md`. Cascade kit uses retrieval-prompt blocks only.
- delivery_target stamping logic — that lives in `cycle-awareness.md`.

This file is the mechanical-derivation layer between the manager bundle and the cascade kit.
