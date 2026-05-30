---
# facilitator_guide_template.md — broadcast-with-checkpoints script template for <audience>-facilitator.md
# Loaded by /generate Step 4b (facilitator guide rendering).
# Frontmatter schema below is required per artifact-generation.md § Frontmatter discipline.

engagement_slug: <slug>
cycle_slug: <e.g., year-end-2026>
audience: employees | managers | hrbps | execs
date: YYYY-MM-DD
delivery_target: "Week <N> / <stage-name> / target date YYYY-MM-DD"
source_message_map: cycles/<engagement>/<cycle-slug>/message-map.yaml
source_council_state: council-states/<engagement>/<cycle-slug>-<audience>-generate.yaml
audience_tag: <audience>-internal | shareable-internal | external
posture: broadcast-with-checkpoints
---

# Facilitator Guide: <audience> Training — <cycle-slug>

> **Engagement:** <engagement name>
> **Audience:** <audience name>
> **Delivery target:** <delivery_target string>
> **Total target duration:** <N> minutes
> **Posture:** broadcast-with-checkpoints (facilitator-led with periodic comprehension checks)
> **Companion deck:** `<audience>.pptx`
> **Companion blocks:** `<audience>-interactive-blocks.md`

---

## Pre-session setup (5 min before audience arrives)

- Verify projector/screen-share works
- Open the deck at slide 1 (cover)
- Open the interactive blocks file in a second window
- Have a paper backup of the cascade prompts (managers) or escalation paths (HRBPs) — system failure recovery
- Confirm audience size matches expected; adjust pacing if size is dramatically off

---

## Slide 1: <Cover slide title>

**Time:** 0:00–0:01

**Facilitator says:**

> "Welcome. Today we're walking through <cycle-slug>. By the end of this <total time> minutes, you'll <one-line goal — audience-specific>."

**Audience does:**

Settles in. No checkpoint yet.

**Purpose:**

Set frame. Audience-specific goal sets expectation for what they walk out with.

**Resources needed:** none.

---

## Slide <N>: <Section divider title>

**Time:** [N min cumulative]

**Facilitator says:**

[1-3 sentences. Concise, direct. The facilitator's voice — not script-reading. Connect the just-completed section to the next.]

**Audience does:**

[Listens. Implicit action: take note if section was dense.]

**Purpose:**

[Why this section break is here — what it does for the argument arc.]

**Resources needed:** none.

---

## Slide <N>: <Content slide title>

**Time:** [N min cumulative / target slot]

**Facilitator says:**

[1-3 sentences — concise, direct, no script-reading. The voice the facilitator's actual voice will land best in.]

**Audience does:**

[The implicit action — listen, take note, raise hand if confused. If this is a checkpoint slide, name the block (poll / quiz / scenario / retrieval) and reference the block file.]

**Purpose:**

[Why this slide is in the deck — what it does for the audience.]

**Anticipated questions:**

- Q: [from `anticipated_objections` for this audience+message]
  A: [pre-answered]

**Anti-FAQ (questions we will NOT answer here):**

- "Why didn't [other team] get the same?" → "Different cycle scope. HRBP can follow up offline."
- "When will my actual letter come?" → "By [date] from <COMPANY>'s comp team — not from this session."

**Escalation path** (HRBP+ decks only):

- For [edge case]: route to [role] within [timeframe]
- For [escalation type]: [policy reference]

**Resources needed:** [companion block ID if checkpoint, otherwise none]

---

## Slide <N>: <Checkpoint slide title — POLL example>

**Time:** [N min cumulative]

**Facilitator says:**

> "Before we continue, quick poll. <Read the poll question.> A, B, or C?"

**Audience does:**

Picks A, B, or C (raised hand, polling tool, or async response). Facilitator counts/observes distribution.

**Purpose:**

Force commitment before reveal. Distribution is itself informative.

**After the vote:**

> "Most picked <expected option> — that's the typical reaction. Here's what the data shows..."

If surprise distribution: "<follow-up prompt from the poll block>"

**Block reference:** `<audience>-interactive-blocks.md` § Block <N>: Poll

**Resources needed:** companion block file open; polling tool if used

---

## Slide <N>: <Checkpoint slide title — RETRIEVAL example>

**Time:** [N min cumulative]

**Facilitator says:**

> "Quick check — without looking at the slide, what was the key message of [prior section]? <2-second pause> Take 30 seconds. <pause>"

**Audience does:**

Mentally retrieves (or writes down). No public answer required.

**Facilitator says (after 30 seconds):**

> "OK — what did you come up with?" <accept 1-2 voluntary answers> "Right — <reinforce the message>."

**Purpose:**

Reinforce retention. Signal pacing.

**Block reference:** `<audience>-interactive-blocks.md` § Block <N>: Retrieval Prompt

**Resources needed:** none

---

## Slide <N>: <Closing slide title>

**Time:** [final time slot]

**Facilitator says:**

> "Three things to walk away with: <key 1>, <key 2>, <key 3>. Questions?"

**For execs decks specifically:**

> "The decision in front of you is: <decision ask>. Ratifying today, or want to come back?"

**For HRBP decks specifically:**

> "Edge cases I haven't covered — bring them to me by [date]. Escalation path lives in the deck appendix; bookmark it."

**For manager decks specifically:**

> "Your cascade kit lands in your inbox by [date]. Run it with your team in week 0. The cascade prompts are in the kit — they're the script. Don't deviate from them."

**For employee decks specifically:**

> "Your letter arrives by [date]. Questions about your specific letter — that's a manager 1:1. Questions about the cycle in general — HRBP. We'll send out the FAQ tomorrow."

**Audience does:**

Asks Q&A. Facilitator addresses what they can; defers anti-FAQ items per the policy.

**Purpose:**

Compress the takeaways into 3 bullets. Set the next-action expectation.

**Resources needed:** appendix slides (escalation paths for HRBPs) on hand

---

## Post-session

- Capture follow-up questions in a tracking doc; route to HRBP queue
- For execs: log decision (ratified / deferred / dissented)
- For managers: confirm cascade kit delivery date
- For HRBPs: review escalation queue post-session
- For employees: confirm comms team has FAQ ready by promised date

---

## Time budget summary

| Section | Slides | Time | Cumulative |
|---|---|---|---|
| Cover + setup | 1 | 1 min | 1 min |
| <Section 1> | <N> | <N> min | <N> min |
| Checkpoint <type> | 1 | 2-5 min | <N> min |
| <Section 2> | <N> | <N> min | <N> min |
| Checkpoint <type> | 1 | 2-5 min | <N> min |
| ... | ... | ... | ... |
| Closing + Q&A | 1 | 5 min | <total> min |

Audience defaults (operator may override at /generate Step 2b audience-design):
- employees: 30-45 min
- managers: 60-75 min
- hrbps: 75-90 min
- execs: 30-45 min

---

## What this template does NOT contain

- The actual deck content — that comes from message-map.yaml + audience-design Whisper choices
- Block schemas — those live in `interactive_block_templates.json`
- Cover slide subtitle conventions — those live in `brand-mode-protocol.md` § Per-audience cover slide variants
- Brand kit application — that's auto-applied by pptxgenjs render against the resolved engagement brand kit
