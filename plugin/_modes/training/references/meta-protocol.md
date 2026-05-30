<!--
MIRRORED from: comp-team-transformer/references/meta-protocol.md
Canonical owner: comp-team-transformer
Sync rule: when canonical changes, copy here. NEVER edit this file in this skill.
Last synced: 2026-05-03
-->

# Meta-Protocol — Universal Interview Techniques

These techniques are domain-agnostic. Every interview-style mode (`/discover`, `/ingest`) activates them; per-skill protocol files reference this file rather than duplicating the techniques inline.

The single guiding constraint: **the operator is the SME being interviewed by the skill, alone.** The skill asks one question at a time directly to the operator. There is no third-party interviewee, no "read this to them, paste back what they say", no live-call copilot. Every Q&A turn is between operator and skill in the same Claude.ai conversation.

The second guiding constraint: **prefer structured pros/cons option tables over open prose questions** wherever a reasonable set of patterns exists. A good options table reduces operator cognitive load (no blank-page problem), surfaces tradeoffs the operator may not have considered, and makes follow-up questions more targeted. Use open prose only for genuinely free-form input (names, descriptions, narrative answers).

Sources: internal process-discovery research, distilled from the original "Mom Test" / SIPOC / 5 Whys / SPIN canon, and adapted for AI-led structured interviews where the AI is the interviewer and the operator is the SME.

---

## The default question format — Pros/Cons option table

Every structured choice question follows this shape:

```markdown
**Q<N>. <Question text — clear, specific, behavioral when possible>**

| Option | Pros | Cons |
|---|---|---|
| **A. <Pattern name>** | <2-4 short pros> | <2-4 short cons> |
| **B. <Pattern name>** | <2-4 short pros> | <2-4 short cons> |
| **C. <Pattern name>** | <2-4 short pros> | <2-4 short cons> |
| **D. <Pattern name>** | <2-4 short pros> | <2-4 short cons> |
| **E. Other** | (describe in your own words) | |

Pick a letter. If "Other" or you want to combine letters, describe.
```

**Rules:**

- **3-5 options** is the sweet spot. Below 3, the question doesn't need a table; above 5, the operator skims rather than reads.
- **Always include "Other (describe)"** as the last option — operators have answers the skill didn't anticipate.
- **Pros and cons must be honest tradeoffs** — not marketing. The skill exists to help the operator pick well, not to sell one option.
- **Pros/cons are 2-4 short fragments**, not paragraphs. Dense tables read worse than sparse ones.
- **Bold the option name** so the operator can scan column 1.
- **One question per turn.** Never stack a pros/cons table with a follow-up open question in the same response — the operator answers one and the skill loses the other.

When the question is genuinely open-ended (e.g., "What's the name of your comp cycle?", "Walk me through the last review you ran"), skip the table and ask conversationally. Use the Mom Test (below) to keep it grounded.

When the question has only 2 options (e.g., a yes/no), skip the table and ask the binary directly.

---

## Core techniques (always active)

### The Mom Test

Focus on past behavior, never hypotheticals.

- **Use:** "Walk me through the last time you ran the annual wage scale review."
- **Avoid:** "Would it help if you had a tool that did X?"
- **Avoid:** "How satisfied are you with your current process?" (Satisfaction is downstream of behavior. Ask about behavior.)
- **Never lead the witness.** "It sounds painful — is it painful?" gets you a yes whether it's true or not. "How long did that step take last time?" gets you a number.
- **Ask about frequency and cost.** "How often does this happen?" "What did you do when it broke?"

Pros/cons tables apply Mom Test by anchoring options in observed patterns ("this is what most teams do", not "this is what we recommend").

### SIPOC framing

Establishes process boundaries at the start of every interview, before the deep-dive. Five questions, in order:

- **Suppliers:** Who provides the inputs? (HRIS team, payroll, vendors, regulators, internal HRBPs.)
- **Inputs:** What comes in? (Roster file, market data CSV, last-year scale, budget envelope, CBA terms.)
- **Process:** What happens? (One-line summary, not the deep-dive yet.)
- **Outputs:** What comes out? (New scale, comms doc, approval memo, payroll feed.)
- **Customers:** Who receives the outputs? (VP People, payroll, employees, regulators.)

Each SIPOC question is a candidate for a pros/cons table when common patterns exist. Example for "Suppliers":

```
**Who provides the inputs to this process?**

| Option | Pros | Cons |
|---|---|---|
| **A. Internal only (HRIS + payroll)** | Tight control; no vendor mgmt | Limited market view |
| **B. Internal + survey vendor (Mercer/Willis/etc.)** | Market benchmarks; comparable | Vendor cycle dependency; cost |
| **C. Internal + survey + regulators (CCQ, CBA, etc.)** | Full compliance footprint | Regulatory data lag; rigid format |
| **D. Internal + survey + business-unit HRBPs** | Distributed sourcing; faster updates | Coordination overhead |
| **E. Other** | (describe) | |
```

Prevents scope creep mid-interview. If the operator starts describing how a different process works, surface: "That sounds like a different process — let's note it and come back. Today's scope was `<process slug>`."

### 5 Whys

Deploy when a manual step, a workaround, or a "we just do it that way" surfaces. Dig past symptoms to root cause. Know when to stop.

Comp-domain example:

```
Q: Why does the analyst manually re-enter the market data into the scale model?
A: Because the export format from the survey vendor doesn't match the model's input columns.

Q: Why doesn't the export match?
A: Because the model was built before this vendor was selected.

Q: Why hasn't the model been updated?
A: Because no one has owned it since the prior analyst left, and the current analyst is busy doing the manual re-entry every cycle.

(Stop here — root cause is an ownership gap, not a process choice. Surface as a leverage point, not as a 5-whys-keep-going.)
```

Stop when the answer is a business constraint (budget, headcount, regulation, vendor contract) — those are inputs to transformation design, not deeper symptoms.

5 Whys is conversational, not pros/cons-table — each "why" is a follow-up to the operator's prior answer.

### Reflect-and-verify

Every 10-15 minutes during the interview, paraphrase what you've heard back to the operator.

- **Format:** "OK — let me make sure I have this straight. You said `<paraphrase>`. Is that right?"
- **Use the operator's words**, not your interpretation. If they said "it's a mess every January", do not paraphrase as "the process has quality issues at year-start." Repeat "mess every January" and ask what specifically that looks like.
- Doubles as an implicit checkpoint — captures structured notes the operator can correct in real time, not after the fact.
- For verification of a structured choice already picked, use a 2-option pros/cons table to confirm: "I have you down as `B (above)`. Confirm or pick again?"

### SPIN Implication / cost-of-inaction

After a pain point surfaces, quantify the cost of leaving it unsolved. Drive toward measurable units (hours, dollars, error rate, days of delay).

Banded quantification works well as a pros/cons table when the operator is unsure:

```
**How many hours does this absorb per cycle?**

| Option | Pros (signal) | Cons (signal) |
|---|---|---|
| **A. <5 hours** | Cheap to live with; low priority for transformation | Probably not worth the spec-and-build overhead |
| **B. 5-50 hours** | Real but bounded; quick-win territory | Easy to under-prioritize if no one tracks |
| **C. 50-500 hours** | Strong transformation candidate; payback visible | Likely cross-functional (multiple teams hit) |
| **D. 500+ hours** | Top priority; transformation is mandatory | Often hides 2-3 sub-processes that need their own decomposition |
```

(In a quantification table, "Pros/Cons" can be reframed as "signals about what this band typically means" — operators learn from the structure.)

If banded quantification doesn't fit (the operator has the actual number), ask directly: "How many hours per cycle? Across the whole team or one analyst?"

### Gap detection

Track which sub-phases have been completed during the interview. Sub-phases (per `discovery-protocol.md` and `discovery_interview_block.json`):

- scripted_opening
- intake (SIPOC)
- cycle_mapping (only if `cycle.stages == []`)
- process_walkthrough
- handoffs
- tools
- pain_points
- scripted_close

Before scripted_close fires, run a gap check:

> "We didn't get into `<sub-phase>` — is that intentional or worth a follow-up?"

Captures the deferred sub-phase in `current-state.md § Coverage Gaps` so the next interview knows where to pick up.

---

## Session sequencing — single-mode conversational arc

The skill drives the conversation. Operator types answers; skill asks the next question. There are no separate Prep / Whisper / Workshop modes — it's one continuous interview, with the skill periodically pausing for reflect-and-verify and gap-checks.

Standard arc (~45-75 min depending on process complexity):

| Time | Sub-phase | Purpose |
|------|-----------|---------|
| 0-3 min | scripted_opening | Ground rules, scope, what the operator will see at the end |
| 3-8 min | intake | Process identity + SIPOC framing (pros/cons tables for each S-I-P-O-C question) |
| 8-15 min | cycle_mapping (conditional) | Anchor event, stages, gating windows — only if `cycle.stages == []` |
| 15-50 min | process_walkthrough + handoffs + tools | The deep-dive — mix of pros/cons tables (for common patterns) and Mom Test conversation (for narrative answers) |
| 50-60 min | pain_points | SPIN cost-of-inaction quantification (banded pros/cons tables when operator unsure) |
| 60-65 min | reflect-and-verify + gap check | Synthesis preview, gap surfacing |
| 65-70 min | scripted_close | Next steps, what file the skill will write, when |

When the cycle-mapping block is not needed (cycle already discovered), the saved 7 minutes redistributes to process_walkthrough.

The operator can pause at any point ("hold on", "give me a sec") — the skill waits, never pushes. The operator can also jump back ("actually, on the previous question, I want to add...") — the skill amends the prior answer in working memory and continues.

---

## Pattern-trigger table — what to ask next when these appear

When the operator's answer contains one of these phrases or patterns, the skill follows up with the corresponding next question. This replaces the prior "Whisper-mode trigger" pattern — same triggers, but the skill asks the operator directly rather than coaching a separate interviewer.

| Operator says... | Skill asks next |
|---|---|
| "manual" / "copy-paste" / "re-enter" | Pros/cons table on the source of the manual step (which tool's export is the bottleneck?) |
| "wait for" / "stuck on" / "blocked by" | Open question on the upstream owner + the contract (what's promised, what's actually delivered, on what cadence?) |
| "no one knows" / "tribal" / "in [name]'s head" | Open question: "What would happen if that person was out for a full cycle?" |
| "happens once a year" / "we figure it out each time" | Pros/cons table on calibration drift patterns (re-learn from notes / re-learn from the prior person / re-derive from scratch / formal training) |
| "I think it's about" / "roughly" / "I'm not sure" | Banded pros/cons table for quantification (5 / 50 / 500 / 500+ hours) |
| "we always have to redo" / "rework" | 5-Whys conversational drill — "What causes the re-do?" then probe the answer |
| "it's a mess every <period>" | Reflect-and-verify verbatim — repeat "mess every <period>" and ask what that looks like in concrete terms |

Only fire one trigger per operator turn. If the operator's answer hits two triggers, pick the one most relevant to the current sub-phase; surface the other as a "want to come back to that?" at the next reflect-and-verify checkpoint.

---

## What this protocol does NOT contain

- Comp-domain question banks — those live in per-skill protocol files (`discovery-protocol.md` for /discover, `ingest-protocol.md` for /ingest) and `template_assets/*_question_block.json`.
- Systems-thinking diagnosis steps — those live in per-skill `diagnose-protocol.md` (where applicable).
- Persona deliberation mechanics — those live in `council-mode.md` (where applicable).
- Cycle-stage gating logic — that lives in `cycle-discovery-and-gating.md` (where applicable).

This file is the universal "how to interview" knowledge for any comp-* skill that runs a structured discovery or ingest interview. Every flow references it; no flow duplicates it.
