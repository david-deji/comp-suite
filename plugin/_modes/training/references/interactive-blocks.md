# Interactive Blocks

Schemas and placement rules for the four broadcast-with-checkpoints block types: poll, knowledge check (quiz), scenario card, retrieval prompt. Loaded by `/generate` Step 4c (interactive blocks rendering). Block templates live at `template_assets/interactive_block_templates.json`.

Posture: **broadcast-with-checkpoints** (v1 default). Facilitator-led explanation with periodic comprehension checks every 3-5 content slides. Suits 200+ rooms and async/recorded delivery. Knowles 80/20 active-learning is deferred to v2.

---

## Block types

### 1. Poll

Quick group-vote. 2-4 options. Facilitator reads question, audience picks (raised hands, polling tool, or async response). Facilitator reveals expected distribution; if surprise distribution, runs a discussion prompt.

Use when:
- The audience needs to commit to a position before hearing the answer
- The expected distribution itself is informative ("most of you said A — that's the typical reaction; here's what the data shows")
- You want to surface disagreement without forcing individual identification

Skip when:
- Stakes are low (don't poll on trivia)
- The "right" answer is obvious from prior context (poll feels patronizing)
- Async delivery — polls without live response collection are pointless

### 2. Knowledge check (quiz)

Comprehension test on a specific message. Single correct answer + 2-3 distractors. Facilitator reads, audience answers (silently or via polling tool), facilitator reveals correct answer + addresses distractor reasoning.

Use when:
- The audience just learned a mechanic and you need to verify it landed
- Common misunderstandings are predictable — distractors expose them
- Async delivery — quiz with self-grading works well

Skip when:
- The message is opinion / framing, not factual (no "correct" answer)
- The quiz feels like a test the audience can fail publicly (use retrieval prompt instead)

### 3. Scenario card

3-5 sentence vignette describing a concrete situation the audience would actually face. Open prompt: "what would you do?" Audience discusses (3-5 min), facilitator synthesizes. No single correct answer — the discussion IS the value.

Use when:
- The message has nuance that breaks down only in real situations
- The audience needs to translate abstract policy → concrete decision
- Multiple defensible answers exist (depth-3 HRBP edge cases especially)

Skip when:
- The training is depth-1 employee level (scenarios are too rich for headline-only content)
- Time-constrained delivery (<30 min) — scenarios eat 5+ min each
- Async delivery — without facilitator synthesis, scenarios become free-form ramble

### 4. Retrieval prompt

Fast comprehension reinforcement. Without looking at the slide, audience recalls the key message of a prior section. 30 seconds total.

Use when:
- You want to reinforce retention before moving to a new section
- Pacing is tight — retrieval prompts cost almost no time
- Async delivery — retrieval prompts work cold (audience writes answer mid-recording)
- Cascade context — manager runs retrieval prompts with their team after each major content block

Skip when:
- Nothing has been said yet (no prior message to retrieve)
- The message is too short to retrieve meaningfully ("how to spell merit") — feels patronizing

**Cascade kit specifically uses retrieval prompts only.** Polls / quizzes / scenarios are dropped per `cascade-protocol.md` § Lighten interactive blocks.

---

## Placement rules

### Cadence

Every 3-5 content slides → 1 checkpoint slide. Tighter cadence (every 2-3) for high-stakes / high-density audiences (execs, HRBPs). Looser cadence (every 5) for low-stakes audiences (employees) where pacing matters more than reinforcement.

### Block-type selection per audience

| Audience | Preferred blocks | Avoid |
|---|---|---|
| **employees** | poll (low-stakes), retrieval prompt | quiz (feels like test), scenario (too rich) |
| **managers** | poll (commit-then-reveal), quiz (mechanic verification), retrieval prompt | scenario (too rich for live group; reserve for cascade) |
| **hrbps** | scenario card (edge cases), quiz (mechanic verification) | poll (HRBPs hate group-vote on technical questions) |
| **execs** | poll (force-commit-on-decision), retrieval prompt (sparingly) | quiz (feels patronizing), scenario (execs want decision asks, not deliberation) |

### Block-type selection per depth

| Depth | Preferred blocks |
|---|---|
| **1** (headline) | retrieval prompt (reinforce), poll (audience commit) |
| **2** (mechanics) | quiz (verify mechanic), poll (commit-then-reveal) |
| **3** (edge cases) | scenario card (edge case role-play), quiz (rule application) |
| **4** (tradeoffs) | poll (force decision-commit), retrieval prompt (compress dense content) |

### Operator override

During `/generate` Step 2c (audience-design interview, interactive checkpoint placement), operator may override block-type placement per slide. Skill records overrides and uses operator-supplied placement at render. Defaults are applied only when operator hasn't specified.

---

## Block schemas

Each block in `<audience>-interactive-blocks.md` follows one of four schemas (per `template_assets/interactive_block_templates.json`).

### Poll schema

```markdown
## Block <N>: Poll

**Slide ref:** Slide <M>
**Question:** <single question, 1-2 sentences>
**Options:**
- A: <label>
- B: <label>
- C: <label>  (optional)
- D: <label>  (optional, max 4 total)

**Expected distribution:** <e.g., "Most A, some B, almost none C">
**If surprise distribution:** <follow-up the facilitator runs to explore the unexpected lean>
**Time:** ~2 min
```

### Quiz schema

```markdown
## Block <N>: Knowledge Check

**Slide ref:** Slide <M>
**Question:** <single comprehension question>
**Options:**
- A: <label>
- B: <label>
- C: <label>  (optional, max 4 total)

**Correct answer:** <letter>
**Distractor handling:**
- If audience picks <wrong-letter>: <one-line explanation>
- If audience picks <wrong-letter>: <one-line explanation>

**Time:** ~2-3 min
```

### Scenario card schema

```markdown
## Block <N>: Scenario Card

**Slide ref:** Slide <M>
**Scenario:**
<3-5 sentence vignette — concrete, role-specific, decision-forcing>

**Prompt:** <e.g., "What would you do? What information would you need first?">
**Discussion frame:** <what the facilitator is listening for during open discussion>
**Synthesis prompt:** <facilitator's 1-line closer that ties discussion back to the message>

**Time:** ~5-7 min
```

### Retrieval prompt schema

```markdown
## Block <N>: Retrieval Prompt

**Slide ref:** Slide <M>
**Prompt:** <e.g., "Without looking at the slide — what was the key message of [prior section]?">
**Purpose:** <reinforce retention | signal pacing | break content density>

**Time:** ~30 seconds
```

---

## Embedded vs separate (config-driven)

`engagement-training-config.interactive_blocks.embedded_or_separate` controls rendering:

- **`embedded`** (default) — interactive blocks render as PPTX slides inline within the deck. The slide layout uses an existing master (`04-section-divider.js` or `09-callout.js` per `brand-mode-polock-protocol.md` § Training-deck masters) with the block content rendered as bullets / callouts. The audience sees the block as a slide; the facilitator runs it from the deck.
- **`separate`** — interactive blocks render as standalone markdown cards alongside the deck. The deck contains placeholder slides ("Checkpoint — see card <N>"); the facilitator pulls the card from `<audience>-interactive-blocks.md` to run the block. Useful when the org wants printed handouts or async-delivery contexts.

v1 ships both options. `embedded` is the default for live/recorded delivery. `separate` is useful for facilitator-led with handouts.

---

## Failure handling

| Failure | Response |
|---|---|
| Operator places a poll/quiz on a depth-4 exec slide | Soft warning: "Execs typically resist polls/quizzes. Consider a retrieval prompt or commit-decision poll instead." Operator decides. |
| Block lacks `slide_ref` | Refuse to write. Surface to operator for completion. |
| Quiz has no correct answer specified | Refuse to write. (Quiz schema requires correct answer.) |
| Scenario has no synthesis prompt | Refuse to write. (Scenario schema requires synthesis prompt.) |
| Cascade-kit accidentally includes poll / quiz / scenario | Soft warning at /cascade Step 6 QA: "Cascade kits typically use retrieval prompts only. Found N non-retrieval block(s). Drop or convert?" |

---

## What this protocol does NOT contain

- Block-content authoring guidance (writing good poll questions, etc.) — that's a creative skill of the operator + audience-design interview, not a configurable rule.
- The full JSON schemas — those live in `template_assets/interactive_block_templates.json`.
- PPTX slide-master selection per block type — that lives in `template-master.md` (mirrored) and `brand-mode-protocol.md` § Training-deck masters.
- Per-audience block-type defaults — those are the placement rules table in this file. They are starting points; operator overrides at audience-design interview Step 2c (interactive checkpoint placement).
