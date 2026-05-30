# Cycle Awareness — Delivery-Target Metadata Stamping

**No gating.** Every rendered deck (`/generate` per audience, `/cascade`) carries a `delivery_target` metadata field on the cover slide AND in deck frontmatter. The metadata is informational, not a blocker.

Loaded by `/generate` and `/cascade`. Reads `engagement-training-config.cycle.*` (populated at Phase 0 from anchor_event + today's date, or inherited from sibling `comp-team-transformer/team-configs/<slug>.yaml`).

---

## Why no gating?

`comp-team-transformer` uses cycle-gating for `/transform` and `/roadmap` — refuse to schedule **process changes** (rollouts) into `live` or `prep` weeks. Sound logic: a process change mid-cycle breaks the team's workflow.

`comp-training-designer` is different. **Rendering** training material is artifact production — zero operational disruption. **Delivering** training is a separate decision; even there, training is often INTENTIONALLY delivered in live/prep windows by design:

- **Cascade training** is typically delivered DURING live (week 0 announcement week). That's when employees need to hear the message.
- **Exec deck** is often delivered in PREP — execs ratify decisions before live.
- **HRBP cycle-mechanics training** is BEST delivered in PREP — they're about to use it on the floor.
- **Manager training** on cascade content is delivered in PREP or early-live. Slack-window delivery would arrive after the manager already needed to cascade.

Gating training renders into `slack` only is exactly backwards for most training use cases. Training timing is OPPOSITE of process-change timing.

---

## What the skill does instead

### Phase 0 (every mode except /help, /resume)

Read `engagement-training-config.cycle.*`. If `stages` is non-empty:
1. Compute `current_week_offset` = (today's date − anchor_date) in weeks.
2. Find `current_stage` by matching `current_week_offset` against `stages[].week_offset` ranges.
3. Cache both in in-memory state. Available to `/generate` and `/cascade`.

If `stages` is empty:
1. Skip cycle computation.
2. `delivery_target` becomes a free-text field at /generate Step 1 — operator types whatever target they want.

### `/generate` Step 1 (delivery-target stamp)

Per `generate-protocol.md` § Step 1. Procedure:

1. **Surface current cycle context.** "Cycle stage today: `<stage-name>` (Week `<N>` from anchor `<anchor_event>`, target date YYYY-MM-DD)."

2. **Ask operator for delivery target.** "Delivery target for `<audience>` deck — week offset from anchor? (Default: current week offset = `<N>`)" Operator may:
   - Accept default (deck delivers as soon as it's ready).
   - Supply explicit week offset (e.g., `-2` for 2 weeks before anchor, `+1` for 1 week after).
   - Supply explicit date (e.g., "2026-12-15") — skill back-computes the week offset.

3. **Compute delivery_target string.**

   ```
   delivery_target: "Week <N> / <stage-name> / target date YYYY-MM-DD"
   ```

   Examples:
   - `"Week -4 / Approval / target date 2026-11-15"`
   - `"Week 0 / Cascade / target date 2026-12-15"`
   - `"Week +1 / Effective / target date 2026-12-22"`

4. **Soft warning if target date is in the past.** "Delivery target Week -8 (Discovery) is 6 weeks in the past — proceed anyway, or update?" Operator decides; render proceeds regardless.

5. **Stamp the value into:**
   - Deck frontmatter (per `artifact-generation.md` § Frontmatter discipline)
   - Cover slide (small text below subtitle, per `brand-mode-protocol.md` § Per-audience cover slide variants)
   - `engagement-training-config.cycles_trained[].delivery_targets.<audience>` field (for next-cycle reference)

### `/cascade` Step 4 (delivery-target stamp)

Same procedure as `/generate` Step 1. Additional logic: default delivery target for cascade = (manager deck's delivery_target + 1 week). Operator may override.

Soft warning if cascade target is BEFORE manager deck target (cascade typically runs AFTER manager training, not before): "Cascade target Week -1 is BEFORE manager deck target Week 0. Cascade typically runs AFTER manager training. Verify timing."

---

## When cycle data is absent

If `engagement-training-config.cycle.stages` is empty:

1. `current_stage` = null, `current_week_offset` = null.
2. At `/generate` Step 1, prompt: "No cycle data configured for this engagement. What's the delivery target date? (Free text — e.g., 'November 15, 2026' or 'Q4 2026 — exec offsite')."
3. Operator supplies a free-text target. Skill stamps it as-is on cover slide and in frontmatter (no `Week / stage` prefix).
4. Suggest: "Want to populate cycle.stages? Either edit `engagement-training-configs/<slug>.yaml` directly, or inherit from sibling `comp-team-transformer/team-configs/<slug>.yaml` if that exists."

The skill does not block on missing cycle data — operator can render decks for engagements that don't have a structured cycle (e.g., one-off policy training, ad-hoc benefits update).

---

## Inheriting cycle from sibling skills

At Phase 0 (every mode), the skill checks if a sibling `comp-team-transformer/team-configs/<engagement-slug>.yaml` exists. If yes:

1. Read its `cycle.stages`, `cycle.anchor_event`.
2. Copy into in-memory state (NOT into the engagement-training-config — sibling skills share cycles by reference, not by duplication).
3. Mark `cycle.last_inherited: <today>` in the engagement-training-config.
4. Surface: "Cycle inherited from comp-team-transformer/team-configs/<slug>.yaml: anchor `<anchor_event>`, `<N>` stages."

Operator can override at any time by editing `engagement-training-configs/<slug>.yaml` directly. Override surfaces a warning at next Phase 0: "Cycle stages diverge from sibling team-config — last_inherited YYYY-MM-DD, but stages have been modified since. Re-inherit, or keep current?"

---

## Cycle stages reference (informational)

Stages typical in compensation cycles, with typical gating in comp-team-transformer (NOT used for gating in comp-training-designer):

| Stage | Typical week offset | comp-team-transformer gating | Typical training delivery context |
|---|---|---|---|
| Discovery | -16 to -12 | slack (transformations OK) | Discovery training: HRBP onboarding to new methodology |
| Market Analysis | -12 to -8 | slack | Pre-cycle benchmarking review for execs |
| Scenario Modeling | -8 to -4 | slack | Pre-decision scenario walkthrough for execs (depth-4) |
| Approval | -4 to -2 | prep | **Exec ratification training** — depth-4 decision deck |
| Cascade | -2 to 0 | prep | **HRBP cycle-mechanics training**; **Manager briefing** |
| Implementation | 0 to +1 | live | **Manager cascade kit** runs in week 0; **Employee announcement** |
| Live | +1 to +2 | live | Post-implementation Q&A; backlash monitoring |
| Effective | +2+ | slack | Retro / lessons-learned for next cycle |

Note: training delivery is **most concentrated in `prep` and early-`live` stages** — exactly where comp-team-transformer would refuse process changes. The cycle-gating asymmetry is by design.

---

## Output

`delivery_target` metadata appears in three places per render:

1. **Deck frontmatter** (in the PPTX file's metadata block):
   ```
   delivery_target: "Week <N> / <stage-name> / target date YYYY-MM-DD"
   ```

2. **Cover slide** (small text below subtitle, neutral palette):
   ```
   Delivery target: Week <N> / <stage-name>
   ```

3. **engagement-training-config.cycles_trained[].delivery_targets.<audience>** field, for next-cycle reference.

---

## What this protocol does NOT contain

- Cycle-mapping interview — that lives in `comp-team-transformer/cycle-discovery-and-gating.md` (cross-skill reference, not loaded here).
- Anchor-event computation logic — that lives in `persistence-and-ledger.md` (mirrored, Phase 0 procedure).
- Cover-slide construction — that lives in `brand-mode-protocol.md` § Per-audience cover slide variants.
- Frontmatter schemas — those live in `artifact-generation.md` § Frontmatter discipline.
- Cycle-gating rationale (why comp-team-transformer DOES gate) — that's documented in `comp-team-transformer/cycle-discovery-and-gating.md`. This skill deliberately deviates.
