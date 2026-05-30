# Council Mode — Strategic Deliberation Protocol

Loaded when the Intent Router classifies a request as `/council` (standalone) OR when `/transform` (band lock) or `/roadmap` (sequence lock) auto-fires council. Loaded alongside `persona-library.md`.

Council is a reasoning mode, not a deliverable track on its own. It produces decision-quality analysis by running multiple named perspectives over the same question, then synthesizing.

---

## When to use

Standalone `/council` for contested process-transformation decisions where one lens is not enough:

- Should we replace this Excel template with a Power Query refresh, or build a full agentic pipeline?
- Is the rollout risk worth the cycle-time saving for transformation X?
- Should we sequence transformation A or B first this quarter?
- Does this transformation hit a fairness narrative that HRBP will need to pre-empt?

Auto-fire from `/transform` (band lock) and `/roadmap` (sequence lock) — see § Auto-fire matrix below.

**Do NOT use council for:**

- Single-answer questions ("what's the lowest-effort Quick Win?") — answer directly.
- Decisions where the strategic direction is already settled — produce the brief or roadmap.
- Factual lookups about a process — the diagnosis or current-state already answers.

---

## Execution model — single-context, no subagents

Council runs single-context within ONE response. **Not** parallel subagent dispatch. The model speaks as each persona sequentially:

1. Render persona block 1 in full (voice, lens, position, dissents).
2. Render persona block 2 in full.
3. ...
4. Render persona block N in full.
5. After every persona has spoken, the orchestrator voice returns and writes the synthesis block.

**Hard rule:** never draft the synthesis block until every persona block is complete. If you start synthesis early, you bias every subsequent persona toward the synthesis you've already written.

**No parallel subagents.** Even when the harness offers parallel dispatch, council runs single-context. The persona-independence loss is mitigated by writing each block in full before drafting the next, and by not letting the orchestrator interject between persona blocks.

---

## Auto-fire matrix (v1)

| Decision point | Auto-fire? | Output |
|---|---|---|
| Lock `current-state.md` (post-`/discover`) | NO | User reviews and accepts inline |
| Lock `diagnosis.md` (post-`/diagnose`) | NO | User's call after reviewing systems map and Quick Wins |
| Lock `transformation-brief.md` band assignments (per `/transform`) | YES | `council-states/<slug>/<date>-<process-slug>-transform.yaml` — per-candidate band votes per persona, dissents preserved |
| Lock `roadmap-<Qx>.md` sequence (per `/roadmap`) | YES | `council-states/<slug>/<date>-roadmap.yaml` — per-slot vote per persona, dissents preserved |
| Standalone `/council <topic>` | n/a — user invokes | `council-states/<slug>/<date>-<topic>.yaml` + optional `council-memo-<date>.md` |

**No weighted scoring in v1** (per IE directive D5). Council outputs categorical band votes (Quick Win / Strong Candidate / Needs Groundwork / Not Ready) or sequence votes (Now / Next / Later) — not numeric scores.

---

## Persona pool

Bundled-5 (`comp-team-v1`): `hrbp`, `comp-manager`, `comp-analyst-operator`, `hris-tooling`, `change-management`. Plus any custom personas registered in `team-config.personas.custom: []`.

See `persona-library.md` for full persona definitions, lens descriptions, voice prompts, custom persona schema, and collision rules.

For each council session:

- **Auto-fire from `/transform` or `/roadmap`:** run all bundled-5 + any custom. Council pool is fixed by team-config.
- **Standalone `/council`:** ask user "Run all bundled-5, or pick a subset?" Default to all-5 if user defers. Pick a subset only when the topic clearly excludes some lens (e.g., "no integration concerns here — skip hris-tooling").

Minimum: 3 personas. Maximum: bundled-5 + all custom (no hard cap, but surface "running 8 personas — are all needed?" if pool exceeds 6).

---

## Per-persona block format

Each persona block follows this structure:

```
### <Persona Name> (<slug>)

*<one-line lens declaration>*

**Position:** <one-paragraph position on the question>

**Per-candidate votes:** (only for /transform auto-fire)
| Candidate | Band | Rationale |
|---|---|---|
| <name> | Quick Win / Strong Candidate / Needs Groundwork / Not Ready | <one line> |

**Per-slot votes:** (only for /roadmap auto-fire)
| Spec | Now (Qx) | Next (Qx+1) | Later | Rationale |
|---|---|---|---|---|
| <name> | ✓ |  |  | <one line> |

**Dissents flagged:** (claims this persona disagrees with from prior personas)
- <one line>

**Confidence:** high | medium | low — <one-line reason>
```

Persona writes from their lens, in their voice. They do NOT speak for other personas. They MAY reference what a prior persona said, but only to disagree or extend.

---

## Synthesis (orchestrator voice)

After all persona blocks are complete, the orchestrator returns and writes:

```
## Synthesis

### Where the council agrees
- <consensus point — every persona aligned>
- <consensus point>

### Where the council splits
**Tension 1:** <one-line description of the disagreement>
- `<persona slug 1>` says: <position>
- `<persona slug 2>` says: <position>
- Resolution path: <how the user might decide between these — not the orchestrator's call>

**Tension 2:** ...

### Single-source claims (load-bearing on one persona only)
- "<claim>" — only `<persona>` made this claim. Verify before relying.

### Recommended path forward
<one paragraph — orchestrator synthesizes a recommended path, names what it depends on>

### Unresolved concerns
- <concern that no persona resolved>
- <concern>
```

**Synthesis discipline:**

- Every consensus point must be traceable to ≥3 personas (out of 5). Lower than 3 → it's not consensus, it's a tension.
- Every tension must name the personas on each side — no "the council split" without saying who.
- Single-source claims must be flagged. A vote of 1-of-5 is not consensus, even if no one disagreed.
- The orchestrator NEVER overrides a persona's vote. Synthesis names the path forward; the user decides.

---

## Output: council-state YAML

Every council run writes a `council-state` YAML. Schema:

```yaml
schema_version: 1
council_run:
  date: YYYY-MM-DD
  team_slug: <slug>
  topic: <free text — what was deliberated>
  trigger: standalone | transform-auto-fire | roadmap-auto-fire
  source_artifact: <path to /transform brief or /roadmap if auto-fire>
  persona_pool: [<list of slugs>]

per_persona:
  - slug: <persona-slug>
    position_summary: <one line>
    per_candidate_votes:                 # only for transform auto-fire
      - candidate: <name>
        band: Quick Win | Strong Candidate | Needs Groundwork | Not Ready
        rationale: <one line>
    per_slot_votes:                       # only for roadmap auto-fire
      - spec: <name>
        slot: Now | Next | Later
        rationale: <one line>
    dissents: [<list of one-liners>]
    confidence: high | medium | low

synthesis:
  consensus: [<list of one-liners>]
  tensions:
    - description: <one line>
      sides:
        - personas: [<slugs>]
          position: <one line>
        - personas: [<slugs>]
          position: <one line>
      resolution_path: <one line>
  single_source_claims: [<list of one-liners>]
  recommended_path: <paragraph>
  unresolved_concerns: [<list of one-liners>]

user_decision:                         # populated post-council, manually
  decided_band:                        # for transform: per-candidate final band after user override
    - candidate: <name>
      final_band: <band>
      override_reason: <if final differs from synthesis recommendation>
  decided_sequence:                    # for roadmap: per-spec final slot
    - spec: <name>
      final_slot: <slot>
      override_reason: <if differs from synthesis>
```

---

## Council memo (optional, standalone-only)

Standalone `/council` may produce a `council-memo-<date>.md` (audience: VP-people or external). Memo length cap: 800 words. Format:

```markdown
# Council Memo: <Topic>

> Date: YYYY-MM-DD
> Team: <name>
> Persona pool: <list>

## Question
<one paragraph>

## Where we agreed
<one paragraph>

## Where we split (and what it depends on)
<one paragraph per tension>

## Recommended path
<one paragraph>

## What I need from you
<one paragraph — explicit decision ask>
```

Auto-fired councils (from `/transform` / `/roadmap`) do NOT produce a memo. Memo is standalone-only.

---

## Override and dissent capture

When the user reviews the council output and overrides a band assignment or sequence slot, the override is captured in `user_decision.*` with a one-line `override_reason`. Overrides are explicit — never silent.

If the user accepts the synthesis as-is, `user_decision.*` mirrors the synthesis recommendation and `override_reason` is empty.

Dissents from individual personas are preserved verbatim in `per_persona[].dissents`. Even if the user accepts the synthesis, the dissent is on record for `/ledger` to correlate against outcome later.
