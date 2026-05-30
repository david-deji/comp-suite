# Council Mode

Persona deliberation mechanics. Used in two ways:

1. **Auto-fire** — required during `/generate`, on per-audience message-map slice locks (before render).
2. **Standalone `/council`** — operator invokes for ad-hoc deliberation on contested message-map decisions or render direction.

Loaded by SKILL.md when intent-router classifies as `/council`, OR when `/generate` reaches Step 3 (per-audience council auto-fire). Loads `persona-library.md` and `template_assets/persona_pack_comp-training-v1.yaml`.

**Single-context discipline.** Personas are sequential voice blocks within one response, not parallel subagent dispatch. Never draft the synthesis block until every persona block is complete. **No weighted scoring** — categorical depth votes only, with per-persona dissent preserved verbatim.

---

## Auto-fire matrix (v1)

| Decision point | Auto-fire? | Output |
|---|---|---|
| Lock `message-map.yaml` (post-/ingest) | NO | Operator reviews and accepts inline at `/ingest` Workshop |
| Lock per-audience message-map slice (pre-render in `/generate`) | YES | `council-states/<engagement>/<cycle-slug>-<audience>-generate.yaml` — per-message vote per persona, dissents preserved |
| Lock cascade-kit derivation | NO | Mechanical, no contested decisions |
| Standalone `/council` | n/a | Operator invokes |

---

## Persona pool

`comp-training-v1` — 5 personas (per `persona-library.md`):
1. **HRBP** — translation between business and comp; fairness narrative; training-room facilitation
2. **Comp Manager** — budget defender, decision-bearer, audience-of-execs
3. **Audience Recipient** — the actual person sitting in the training room (training-room-receiver lens)
4. **HRIS / Tooling Lens** — system-side accuracy of what's claimed in training
5. **Change Management Lens** — rollout sequencing, post-training backlash, manager-cascade fidelity

For per-audience auto-fires, the **audience-recipient persona is weighted heaviest** for the audience under render — they're the proxy for the actual receiver. Other personas vote, but the synthesis emphasizes audience-recipient signal.

Custom personas registered in `engagement-training-config.personas.custom: []` are additive.

---

## Single-response sequential block format

**Critical rule:** All persona voice blocks land in ONE response, sequentially. Synthesis block follows after the last persona. NEVER fire personas in parallel subagents.

Format (illustrative for per-audience auto-fire):

```markdown
## Council on: <cycle-slug> / <audience> message-map slice

### Persona 1 — HR Business Partner

[HRBP voice block — for each message in the slice, vote: fits / surface concern / drop. One-line rationale per vote. Dissents marked explicitly.]

For msg-001 (depth-2 manager — "merit-vs-market split"):
- Vote: fits
- Rationale: managers will receive this directly from team in 1:1s; depth-2 mechanics support their answer.

For msg-007 (depth-2 manager — "budget envelope"):
- Vote: surface concern
- Rationale: this commits us to the envelope number. If next cycle the envelope shifts, managers will quote this. Recommend reframing as "current-cycle envelope; subject to annual review."

For msg-015 (depth-2 manager — "compa-ratio philosophy"):
- Vote: drop
- Rationale: too technical for managers. Belongs in HRBP deck, not manager deck.

### Persona 2 — Compensation Manager

[Same per-message vote structure.]

### Persona 3 — Audience Recipient (Training-Room Proxy)

[Heavy-weighted for this audience. Speaks in the texture of the room.]

For msg-001:
- Vote: fits — but framing needs work
- Rationale: I'm a manager hearing this. "Merit-vs-market split" is jargon. Reframe as "two pieces of your raise: what the market did, what your performance did."

[continues for all messages]

### Persona 4 — HRIS / Tooling Lens

[Per-message vote with technical accuracy lens.]

### Persona 5 — Change Management Lens

[Per-message vote with rollout/backlash lens.]

### Synthesis (orchestrator-written)

**Consensus:**
- msg-001: 4/5 personas vote fits; audience-recipient flags framing concern (jargon). Recommend reframing per audience-recipient.
- msg-003: unanimous fits.
- msg-007: 3/5 vote fits; 2/5 surface concern (HRBP, change-mgmt — both flag commit-risk). Recommend reframing to scope-current-cycle.
- msg-015: 4/5 vote drop (audience-recipient strongest dissent: "too technical"); 1/5 vote fits (comp-manager — budget-defender lens). Recommend drop, route to HRBP deck.

**Tensions:**
- comp-manager wants msg-015 retained; everyone else wants drop. Comp-manager's defense: "managers need to understand WHY when they explain the merit number." Audience-recipient counter: "they don't actually understand compa-ratio; they understand 'we paid you X relative to band'. Use that."
- Recommendation: drop msg-015 from manager deck, add equivalent plain-language msg to manager deck, KEEP msg-015 in HRBP deck (already at depth-3 there).

**Operator approval needed on:**
1. Reframe msg-001 per audience-recipient suggestion?
2. Reframe msg-007 to scope-current-cycle?
3. Drop msg-015 from manager deck + add plain-language equivalent?

[Skill prompts operator via inline confirmation. Operator approves, modifies, or overrides each. Then locks the slice.]
```

---

## Standalone `/council` flow

Operator invokes `/council` for ad-hoc deliberation. Common use cases:
- Tension at `/ingest` close: "execs only have 2 depth-4 messages — should we dig deeper or accept?"
- Tension at `/generate` audience-design: "operator and stakeholder disagree on whether msg-X belongs in the manager deck"
- Cross-cycle question: "next cycle, do we keep this framing or pivot?"

Operator pastes the topic + context. Skill runs the same 5-persona sequential block format, with synthesis. Output: `council-states/<engagement>/<date>-<topic>.yaml` + optional `council-memo-<date>-<topic>.md` (operator requests).

---

## Output schemas

### `council-states/<engagement>/<cycle-slug>-<audience>-generate.yaml`

```yaml
schema_version: 1
engagement_slug: <slug>
cycle_slug: <e.g., year-end-2026>
audience: <audience>
generated_at: <ISO timestamp>
trigger: auto-fire (generate-step3)
persona_pack: comp-training-v1

votes:
  - msg_id: msg-001
    votes:
      hrbp: { vote: fits, rationale: "..." }
      comp_manager: { vote: fits, rationale: "..." }
      audience_recipient: { vote: fits-with-reframe, rationale: "...", reframe_suggestion: "..." }
      hris_tooling: { vote: fits, rationale: "..." }
      change_management: { vote: fits, rationale: "..." }
    consensus: fits-with-reframe
    operator_decision: accepted-reframe   # accepted-as-is | accepted-with-modification | overridden | deferred

  - msg_id: msg-007
    votes: { ... }
    consensus: surface-concern
    operator_decision: ...

  - msg_id: msg-015
    votes: { ... }
    consensus: drop-with-route-to-hrbp
    operator_decision: ...

dissents_preserved:
  - msg_id: msg-015
    dissenter: comp_manager
    dissent_text: "managers need to understand WHY when they explain the merit number"
    resolution: "added plain-language equivalent to manager deck; kept compa-ratio framing in HRBP deck"

operator_approved_at: <ISO timestamp>
locked_for_render: true
```

### `council-states/<engagement>/<date>-<topic>.yaml` (standalone)

```yaml
schema_version: 1
engagement_slug: <slug>
date: <YYYY-MM-DD>
topic: <free text>
trigger: standalone (operator-invoked)
persona_pack: comp-training-v1

deliberation:
  - persona: hrbp
    voice_block: |
      [verbatim persona's analysis]
  - persona: comp_manager
    voice_block: |
      [verbatim]
  - persona: audience_recipient
    voice_block: |
      [verbatim]
  - persona: hris_tooling
    voice_block: |
      [verbatim]
  - persona: change_management
    voice_block: |
      [verbatim]

synthesis:
  consensus: <summary>
  tensions: <list of disagreements>
  recommendations: <ordered list>

operator_action: <decision taken or deferred>
operator_resolved_at: <ISO timestamp>
```

### `council-memo-<date>-<topic>.md` (optional, standalone only)

Generated when operator says "write me the memo" after standalone deliberation. Length-capped at 800 words. Frontmatter per `artifact-generation.md`. Content: synthesis section in shareable narrative form (drops verbatim persona blocks; keeps only the consensus/tensions/recommendations).

---

## Failure handling

| Failure | Response |
|---|---|
| Persona returns thin output (single-line per message) | Re-dispatch with sharpened prompt citing specific message IDs the persona must address |
| Two personas disagree fundamentally on a message | Surface dissent verbatim in synthesis; operator decides; record in `dissents_preserved` |
| All personas vote drop on a message | Drop the message from this audience's slice; record in council-state |
| Operator rejects synthesis recommendation | Record override in `operator_decision` field; render proceeds with operator's call |
| Council auto-fire times out (rare) | Save partial state to council-state file with `partial: true`; operator re-runs `/council` standalone or skips with `--skip-council` flag |

---

## What this protocol does NOT contain

- Persona voice prompts — those live in `persona-library.md` and `template_assets/persona_pack_comp-training-v1.yaml`.
- Per-audience render flow — that lives in `generate-protocol.md`.
- Standalone vs auto-fire trigger logic — that lives in this file's auto-fire matrix; the per-mode protocols invoke it.
- Drive write discipline — that lives in `persistence-and-ledger.md` (mirrored).
