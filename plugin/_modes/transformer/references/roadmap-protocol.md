# Roadmap Protocol

## Mode-keyed step routing

At session start, read `engagement_mode` from team-config or the session-level
declaration.

Look up step routing in `references/engagement-modes.md`:

| Mode | This protocol runs | Pre-condition |
|---|---|---|
| `full-discovery-to-roadmap` | RUN — full 6-step sequencing + council auto-fire | ≥2 transformation-briefs (C06) |
| `discovery-only` | SKIPPED | — |
| `diagnose-only` | SKIPPED | — |
| `transform-only` | SKIPPED | — |
| `roadmap-refresh` | RUN — reuses existing transformation-briefs; re-sequences for new quarter | ≥1 transformation-brief (C06); ≥2 recommended |
| `council-deliberation` | SKIPPED | — |

Write `engagement_mode` into `roadmap-Qx.md` frontmatter before the Executive
Summary section. `roadmap-refresh` MUST NOT run `/transform` steps — it loads
existing briefs only.

---

The `/roadmap` track sequences ≥2 transformation briefs into a quarterly schedule. Cycle-fit gating is mandatory — no rollout into `live` or `prep` weeks without explicit override. Council auto-fires on sequence locks.

Loaded by SKILL.md when the Intent Router classifies the request as `/roadmap`. Loads `roadmap-protocol.md` (this file), `cycle-discovery-and-gating.md` (gating rule), `council-mode.md` (auto-fire), `persona-library.md`, `production-and-qa.md`, `template-master.md`, `brand-kit-protocol.md`. Loads `template_assets/roadmap_template.md` as the output scaffold.

---

## Pre-flight

`/roadmap` requires:

1. ≥2 `transformation-brief.md` files for the team. If only one exists, surface: "Only one transformation brief found. Roadmap is most useful with 2+ candidates — proceed anyway, or run `/transform` on another process first?" Accept user's call.
2. `team-config.cycle.stages` must be populated (cycle discovered). If `cycle.stages == []`, surface: "No cycle discovered. Roadmap cycle-fit gating depends on it. Run `/discover` first to map the cycle, or proceed without gating (you'll lose live/prep protection)?" Accept user's call.

---

## The 6 steps

### Step 1 — Load all transformation briefs for the team

Read every `processes/<slug>/<process-slug>/transformation-brief.md`. Extract:

- Strong Candidate specs (these are the schedulable items)
- Their pre-computed `Earliest viable rollout: <Qx YYYY>` annotations
- Any `Cycle-gating exception` notes (where the user overrode gating in `/transform`)
- Council dissents (carried forward — relevant to sequencing)
- Needs Groundwork dependencies (will affect sequencing if a Needs Groundwork item blocks a Strong Candidate)

Quick Wins are NOT scheduled in the roadmap — they're already P0 in the diagnosis and shipped or deferred outside the cycle.

### Step 2 — Dependency graph

Map explicit dependencies between Strong Candidates. Sources:

- **Cross-spec data dependencies** — e.g., "Auto-roster-reconciliation depends on HRIS data quality fix" → if HRIS data quality fix is a Needs Groundwork item, Strong Candidate is blocked until it ships.
- **Cross-spec interface dependencies** — e.g., "Survey-export-format-adapter must precede agentic benchmarking" because the latter consumes the former's output.
- **Resource dependencies** — e.g., two Strong Candidates need the same Comp Analyst — can't both land in the same quarter.

Render as mermaid:

```mermaid
flowchart LR
    A[Auto-roster-reconciliation] --> B[Agentic benchmarking pipeline]
    C[HRIS data quality fix - Needs Groundwork] --> A
```

Surface the graph for user review before sequencing.

### Step 3 — Cycle-fit windowing

For each Strong Candidate, map its `Earliest viable rollout: <Qx YYYY>` annotation onto the team's cycle stages.

For each candidate:

1. Walk forward from `current_week_offset` through cycle stages.
2. Find slack windows by quarter.
3. Reject any rollout that lands during a `live` or `prep` window — even if the calendar quarter is correct.

Example: `Q3 2026` may contain a slack window from week +2 to week +5, but weeks +6 to +12 are `prep` for the next cycle. A 4-week rollout starting week +5 would cross into `prep` — reject and surface.

### Step 4 — Sequencing — now / next / later

Slot every Strong Candidate into one of:

- **Now (this quarter)** — earliest viable rollout is this quarter, dependencies are clear, slot fits in slack window.
- **Next (next quarter)** — earliest viable rollout is next quarter, OR dependencies block this quarter.
- **Later (out beyond)** — earliest viable rollout is 2+ quarters out, OR dependencies are deeper than next quarter.

The orchestrator's pre-council slotting is a starting point. Council may re-slot.

### Step 5 — Council auto-fire

Required. Per `council-mode.md` § Auto-fire matrix.

Fire trigger: pre-council slotting is complete. Fire prompt:

> "Council auto-fire: review roadmap sequence for `<team-slug>`. <N> Strong Candidates across now / next / later. 5 personas (HRBP, comp-manager, comp-analyst-operator, hris-tooling, change-management). Per-spec slot vote per persona. Synthesis follows."

Council output: `council-states/<slug>/<date>-roadmap.yaml` per the schema in `council-mode.md`.

Each persona votes one slot per Strong Candidate (Now / Next / Later). Synthesis surfaces:

- **Consensus slots** (≥3 personas aligned) — adopt unless user overrides.
- **Split slots** — surface tension; user picks.
- **Compression dissents** — e.g., `comp-manager` says "compress two Now items into one — can't afford the analyst time" while `change-management` says "spread them out — too much change at once."
- **Sequence-violating dissents** — e.g., a persona votes a candidate Now when it depends on a Needs Groundwork item that won't ship until Next.

### Step 6 — User approval of sequence

Surface the council synthesis with per-spec consensus / split status. Use AskUserQuestion to walk through any split slots one at a time.

User may override any slot. Override reason captured in `council-state.user_decision.decided_sequence[].override_reason`.

After user closes review, locked sequence feeds into the roadmap output.

---

## Output

`roadmap/<slug>/roadmap-<YYYY-Qx>.md` — markdown working artifact (schema in `roadmap_template.md`). Naming convention: `<YYYY-Qx>` is the quarter the roadmap targets — typically the "Now" quarter.

`roadmap/<slug>/pptx/roadmap-<YYYY-Qx>.pptx` — required executive deck. Three production checks before write per `production-and-qa.md`.

`council-states/<slug>/<date>-roadmap.yaml` — council state YAML capturing per-persona slot votes, synthesis, and user decisions.

Updated `team-config.processes[]` — bump `state` for each Strong Candidate from `spec'd` to `roadmapped`.

---

## Audience and rendering

Audience tag in roadmap frontmatter determines render:

- `audience: comp-team-internal` — full roadmap, dependency graph visible, council vote table, dissents preserved.
- `audience: vp-people` — narrative summary, dependency graph rendered as mermaid (still visible — VPs can read graphs), no per-persona vote table, dissents redacted to "alternative views considered" + council split summary.
- `audience: external` — narrative only, no council references, redaction pass strips internal terminology, mermaid retained but stripped of internal naming.

Default audience: `vp-people` (roadmaps are upward-facing). User can override at PPTX entry.

---

## Cycle-gating exceptions

Any sequence placement that violates gating (rollout lands in `live` or `prep` window) requires an explicit user override. Captured in:

```yaml
roadmap:
  cycle_gating_exceptions:
    - spec: <name>
      slot: <Qx>
      gating_violation: live | prep
      override_reason: <user's stated reason>
      acknowledged_risk: <user's acknowledgment>
```

Rendered in `roadmap-<Qx>.md § Cycle-gating exceptions` (visible at all audiences). Never silent — accepting risk requires acknowledging it on record.

---

## Edge cases

- **Single Strong Candidate across all team processes** — surface: "Only one Strong Candidate this cycle. Roadmap is sparse. Continue with single-spec roadmap, or wait for `/transform` on more processes?"
- **Every candidate slots Later** — surface: "Council placed every Strong Candidate in Later. The roadmap shows no actionable work this cycle. Surface the gating constraints driving this — likely a `live`-heavy cycle stage right now?"
- **Dependency cycles** — if A depends on B and B depends on A (rare but possible), surface and refuse to sequence: "Circular dependency between `<A>` and `<B>`. Resolve before sequencing. Likely fix: re-band one to Needs Groundwork until the dependency is broken."
- **Council split 50/50 on every slot** — bundled-5 council usually has odd numbers, but with persona absences it can split. Surface: "Council unable to reach majority on any slot. The decision space is genuinely ambiguous. Want me to expand the persona pool with a custom persona, or proceed with user-only override of every slot?"
