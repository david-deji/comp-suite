# /ingest Protocol

`/ingest` extracts content from existing source material (transformation-briefs, process docs, prior PPTX, policy guidelines) into a canonical `message-map.yaml` with audience+depth tagging. Output drives all downstream `/generate` and `/cascade` runs.

---

## Mode-keyed step routing

At session start, read `engagement_mode` from `engagement-training-config.yaml` (or
per-cycle override). Look up step routing in `references/engagement-modes.md`. Apply:

| engagement_mode | Routing |
|---|---|
| `ingest-only` | RUN all steps. END artifact is message-map.yaml only. Do NOT prompt for or imply a /generate step at close. |
| `full-bundle` | RUN all steps. At scripted_close, surface: "Ready to run /generate batch when you are." |
| `single-audience` | RUN all steps. At scripted_close, surface: "Ready to run /generate <audience> when you are." |
| `audience-design-only` | PARTIAL — run scripted_opening, source_identity, message_extraction. Skip audience_depth_assignment (the generate-protocol audience-design interview handles depth separately). |
| `cascade-only` | SKIP — cascade-only mode derives from the manager deck directly. If /ingest is called in cascade-only mode, surface: "cascade-only mode does not require ingestion — use /cascade instead, or switch mode." |
| `council-deliberation` | SKIP — use /council instead. |

Write the active `engagement_mode` into message-map.yaml frontmatter so future
sessions resume with the same routing.

If `engagement_mode` is absent: default to `full-bundle` treatment and log
`decision_type: mode_defaulted_silently` to master.yaml.

Loaded by SKILL.md when intent-router classifies as `/ingest`. Loads `meta-protocol.md` first (universal IE techniques, mirrored), then this file (training-domain flow), plus `audience-depth-rules.md` for the depth-layer constraint, plus `redaction-rules.md` for the input scan.

Question banks live in `template_assets/audience_design_block.json` — the canonical source for `scripted_opening_ingest`, `source_identity`, `message_extraction`, `audience_depth_assignment`, `objection_anticipation`, `cascade_cue_marking`, `scripted_close_ingest` blocks.

---

## Interview model

`/ingest` is a single continuous conversational interview. The skill asks one question at a time; the operator answers. There is no third-party interviewee — the operator IS the SME being interviewed. The interview runs as one arc from scripted opening to scripted close; there are no mode transitions mid-session.

If no `<cycle-slug>` was supplied, open with: "What's the cycle slug? (e.g., `year-end-2026`, `mid-year-refresh-2027`, `policy-update-2026-q3`)"

Then proceed directly to scripted opening.

---

## Interview arc

Standard arc (~30-60 min depending on source volume):

| Sub-phase | Purpose | Primary Q-format |
|-----------|---------|-----------------|
| **scripted_opening** | Ground rules, scope confirmation, what the operator will see at the end | conversational |
| **source_identity** | Identify sources, establish canonical truth, note anything still in flight | pros/cons table |
| **message_extraction** | Surface candidate messages per source: claim, evidence, audience-relevance flags, depth flags | mixed (Mom Test + pros/cons for signal-phrase triggers) |
| **audience_depth_assignment** | Assign each message to audiences at depth; enforce HRBP ≥ manager ≥ employee inline | pros/cons table for depth pattern; conversational for individual assignments |
| **objection_anticipation** | Per audience+message pair, surface anticipated questions or pushback | conversational |
| **cascade_cue_marking** | For manager-scoped messages, flag cascade-prompts and exclusions | conversational |
| **reflect_and_verify** | Paraphrase the running message-map back; gap check | conversational |
| **scripted_close** | Next steps, output file path, confirm operator is done | conversational |

The operator can pause at any point ("hold on", "give me a sec") — the skill waits. The operator can also jump back ("actually, on the previous question, I want to add...") — the skill amends the prior answer in working memory and continues.

---

## Sub-phase detail

### scripted_opening

One short paragraph establishing scope. Example:

> "Ingesting for `<engagement-slug>` / `<cycle-slug>`. I'll walk through source identity, extract candidate messages, assign audiences and depth, surface anticipated objections, and flag cascade cues. At the end I'll write `message-map.yaml` for you to review before locking. Ready to start with which sources you're working from?"

### source_identity

Confirm sources from `engagement-training-config.sources.*` and accept ad-hoc additions. Use a pros/cons table to establish which source is canonical truth vs supplementary. Example:

**Q1. How should we treat these sources relative to each other?**

| Option | Pros | Cons |
|---|---|---|
| **A. Transformation-brief is canonical; process doc is supplementary** | Brief already has audience-sorted messages; less re-adjudication | May miss policy nuances in the process doc |
| **B. Process doc is canonical; brief is supplementary** | Policy language is authoritative; reduces contradiction risk | Brief's audience flags will need re-validation against policy |
| **C. Both equally canonical; adjudicate conflicts manually** | Nothing is pre-decided; operator controls every conflict | Slower; every conflict needs an explicit call |
| **D. Brief is canonical; PPTX is supplementary only for prior framing** | Strongest for refreshes — reuse prior framing, update claims | PPTX layout may anchor operator to prior structure |
| **E. Other** | (describe) | |

Follow up on anything "still in flight" (sources not yet available): "Want to flag those as pending and proceed with what we have, or wait?"

### message_extraction

For each source in priority order, walk through the `message_extraction` block. Operator surfaces candidate messages. The skill uses Mom Test ("walk me through this section — what's the actual claim the audience needs to act on?") and pattern-trigger follow-ups per `meta-protocol.md`.

For the depth-classification pattern (when operator is unsure which depth a message belongs at), use a pros/cons table:

**Q. What depth does this message belong at?**

| Option | Pros | Cons |
|---|---|---|
| **A. Depth 1 — employees** | Headline fact; every employee needs this to understand their pay | Too thin for managers who need to answer questions; may create equity confusion if not paired with depth-2 context |
| **B. Depth 2 — managers** | Managers need the mechanic to run their team conversations | Employees don't need this level; could create manager burden without depth-1 anchor |
| **C. Depth 3 — HRBPs** | Edge-case or policy nuance; HRBPs need it to handle escalations | Too technical for managers; risks HRBP overload if every message is depth-3 |
| **D. Depth 4 — execs** | Tradeoff / budget / governance framing; exec ratification | Execs don't need the mechanic; employees definitely don't |
| **E. Multiple depths (describe which)** | Some messages genuinely belong at 2+ depths with different framing | Each depth needs its own framing — confirm the operator will supply both |

Track: claim, evidence, audience-relevance flags, depth flags per message. Surface silently; show running count on request.

### audience_depth_assignment

Per message: confirm which audiences see it at which depth. Enforce the constraint inline: HRBP depth ≥ manager depth ≥ employee depth (when all three are non-null). Execs see different cuts (tradeoffs / budget / governance), not deeper-of-the-same.

If the operator inverts the constraint (e.g., assigns manager depth-3 and employee depth-1 on the same fact at depth-2 is fine, but employee depth-2 and manager depth-1 is a violation), flag immediately:

> "That would make the employee message deeper than the manager message on the same fact — HRBP ≥ manager ≥ employee is required. Adjust which depth manager sees, or split this into two messages?"

### objection_anticipation

For each audience+message pair, ask: "What will this audience push back on or need clarified?" Conversational. One pair at a time.

Common prompt: "For `<audience>` on `<msg-slug>`, what's the predictable question they'll raise?"

### cascade_cue_marking

For manager-scoped messages only. Two checks per message:

1. "Is there a cascade-prompt here — something you want the manager to explicitly ask their team?" (If yes, capture verbatim wording.)
2. "Is there anything in this message that must NOT cascade?" (If yes, capture exclusion.)

### reflect_and_verify + gap check

Paraphrase the running message-map back before scripted_close. Use the operator's words. Example:

> "Let me make sure I have this straight. You said the main employee headline is `<msg-001>`, and the manager-level mechanic is `<msg-002>` — is that right?"

Gap check (run before close): surface thin coverage:

> "Execs only have 2 depth-4 messages — is that intentional, or are we missing the strategic framing?"
> "Employees have no depth-1 messages yet — what's the headline they need to leave with?"

Coverage gaps are captured in message-map.yaml § Coverage Gaps.

### scripted_close

> "That's the full ingest for `<cycle-slug>`. I'll synthesize the message-map now and show you the draft before writing. [N] messages extracted: [N] depth-1, [N] depth-2, [N] depth-3, [N] depth-4. [N] cascade-prompts. [N] coverage gaps flagged."

---

## Workshop synthesis (after scripted_close)

What the skill does, in sequence:

**1. Capture summary.** Present the running message-map for operator review:

```
Captured during the ingest:
- Sources processed: <list of source IDs>
- Messages extracted: <N>
  - depth-1 (employees): <N>
  - depth-2 (managers): <N>
  - depth-3 (HRBPs): <N>
  - depth-4 (execs): <N>
- Cascade-prompts flagged: <N>
- Objections anticipated: <N>
- Coverage gaps flagged: <list of audiences with thin coverage>
```

**2. Review gate.** Surface:

> "Here's the message-map. Anything to correct, add, or remove before I lock it?"

Wait for operator input. Accept corrections; do not synthesize until operator confirms.

**3. Synthesis.** Populate `cycles/<engagement>/<cycle-slug>/message-map.yaml` per `message_map_template.yaml`. Run redaction pass per `redaction-rules.md` (refuse write on banned-pattern detection). Validate the depth constraint (HRBP ≥ manager ≥ employee on same fact when all non-null) — refuse to write if violated.

**4. Update `engagement-training-config`.** Append entry to `cycles_trained[]`:
```yaml
- cycle_slug: <cycle-slug>
  state: ingested
  audiences_rendered: []   # populated by /generate
  last_render: null
  sources_used: [list of source IDs]
```

**5. Effort note for next steps.** Surface:

> "Estimated post-ingest work: 30-45 min message-map review + `/generate` per audience (~10-15 min each, plus council auto-fire)."

**6. Validation.** Flag thin sections:

> "Manager objection-handling has 1 entry — consider a 10-min follow-up, or accept as-is."

Output: `discovery/<engagement>/<cycle-slug>/YYYY-MM-DD-ingest-self.md` (raw capture) + `cycles/<engagement>/<cycle-slug>/message-map.yaml` (synthesized).

---

## Source-type-specific extraction notes

### transformation-brief (preferred — schema-aware)

Loose coupling, but if the source is a recognized comp-team-transformer transformation-brief.md, the skill applies schema-aware extraction:

- Pull `Strong Candidates` section → these become candidate messages with strong evidence
- Pull `Quick Wins` section → these become depth-1 candidate messages (action-oriented)
- Pull `Council dissents` section → these become objection-anticipation entries
- Pull `Cycle-fit annotation` → this populates `delivery_target` candidates per audience

### process_docs (markdown / PDF)

Generic parsing. Skill extracts headings, bullet points, and explicit policy clauses. Operator drives the audience-depth assignment manually — no schema heuristics.

For PDFs: Claude.ai handles PDF reading natively. The text content is available; figures/diagrams are referenced by page but not auto-extracted as candidate messages.

### prior_pptx (repurpose / reskin)

Skill extracts text content from slide titles, bullets, callouts, speaker notes. Layout / images are NOT preserved — the new render goes through the engagement brand kit, not the prior deck's brand.

Operator decides which prior messages survive vs which get dropped (e.g., a prior message that's no longer accurate this cycle is dropped at message extraction).

---

## Session-state-as-running-notes

Three sections only. Lives in working-state file, overwritten on each checkpoint.

```markdown
# Session State: <engagement-slug> / <cycle-slug>
# Last checkpoint: <ISO timestamp>

## Current position
- Sub-phase: source-identity | message-extraction | audience-depth-assignment | objection-anticipation | cascade-cue-marking | reflect-and-verify | close
- Active source: <source-id>

## Key data points collected
- Sources processed: <N of <total>>
- Messages extracted: <N>
- Audience-depth coverage: employees:<N>, managers:<N>, hrbps:<N>, execs:<N>
- Cascade-prompts flagged: <N>
- Objections anticipated: <N>

## Questions remaining
- [ ] Source identity (if multiple sources, which are still pending)
- [ ] Message extraction (per source)
- [ ] Audience-depth assignment (per message)
- [ ] Objection anticipation (per audience)
- [ ] Cascade-cue marking
- [ ] Reflect-and-verify + gap check
```

**Checkpoint triggers:**
- On every sub-phase transition
- At midpoint of any sub-phase running >15 minutes

Auto-checkpoint writes are silent — surface only on write failure. Operator can also invoke `/checkpoint` manually.

---

## Output files (every `/ingest` run)

- **Raw capture:** `discovery/<engagement>/<cycle-slug>/YYYY-MM-DD-ingest-self.md` — append-only record. Contains scripted_opening, full Q&A, scripted_close. Useful for re-ingest and audit trail.
- **Synthesized message-map:** `cycles/<engagement>/<cycle-slug>/message-map.yaml` — structured per `message_map_template.yaml`. Input to `/generate`.
- **Engagement-training-config update**: `engagement-training-configs/<slug>.yaml` — `cycles_trained[]` entry appended with `state: ingested`.

All writes go through the persistence backend per `persistence-and-ledger.md` (mirrored). Redaction pass runs before every write.

---

## What this protocol does NOT contain

- Universal IE techniques (Mom Test, SIPOC, 5 Whys, reflect-and-verify, pattern-trigger table) — those live in `meta-protocol.md` (mirrored).
- Audience-depth constraint logic — that lives in `audience-depth-rules.md`.
- Redaction patterns — those live in `redaction-rules.md`.
- Question banks — those live in `template_assets/audience_design_block.json`.
- message-map.yaml schema — that lives in `template_assets/message_map_template.yaml`.
