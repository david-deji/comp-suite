# Council Dispatch

> Loaded from `SKILL.md` for `/comp council <topic>` and from any mode's `main.md` that invokes council on a deliberation point.
> Implements SPEC § 8 + the 5 council artifacts in `$ASSET_ROOT/_core/council/`.
> Dispatch sizing: see `$ASSET_ROOT/_core/policies/review-dispatch-budget.md` (per-reviewer tool-call budgets, file-list discipline, incremental-write requirement).

## The 5 council artifacts (read all 5 before dispatching)

| # | File | Role |
|---|---|---|
| 1 | `$ASSET_ROOT/_core/council/procedure.md` | TM rule, copied verbatim. The deliberation procedure. |
| 2 | `$ASSET_ROOT/_core/council/output-pattern.md` | TM rule, copied verbatim. Per-thinker unique files + dual-return. |
| 3 | `$ASSET_ROOT/_core/council/dispatch-anti-patterns.md` | TM rule, copied verbatim. Anti-patterns to avoid in dispatch prompts. |
| 4 | `$ASSET_ROOT/.claude/agents/thinker.md` | Agent definition. Dispatched via `Agent` tool with `subagent_type: thinker`. |
| 5 | `$ASSET_ROOT/_core/council/operations.md` | Inlined from TM ops reference. Dispatch template, perspective pool format, gap aggregation, tag propagation. |

## Procedure

### 1. Read engagement-state for `industry_outsider` (MCP-primary, P4b)

```
io = engagement_get {org_slug: ORG, engagement_id: id}.industry_outsider
```
(On MCP transport failure, fall back to the local cache:
`yq '.industry_outsider' "$STATE_ROOT/_orgs/$ORG/engagements/$id/engagement-state.yaml"`.)

If `industry_outsider` is null/missing — STOP. Per SPEC § 8, IO is mandatory for council. Surface to founder: "engagement-state.industry_outsider is unset. Council requires it. Pick: tech, pharma, nonprofit, public-sector, finance, manufacturing, retail, construction. Selection rule: closest-but-not-equal to engagement's primary industry."

### 2. Read perspective roster

```bash
yq '.perspectives' "$ASSET_ROOT/_core/council/perspectives.yaml"
```

Always-on (durable: true): Compensation Strategist, Total Rewards Architect, HR Operations Lead, Finance Partner, Employee Advocate.

Situational (durable: false): Legal & Compliance — rotate in for regulated contexts (pay transparency questions, DEI audits, etc.).

### 3. Compose dispatch list

- All 5 durable perspectives + situationals (judgment call by orchestrator based on `<topic>`)
- Plus 1 Industry Outsider (does NOT count against `perspective_count` per TM rule)

Example for a typical comp deliberation: 5 durable + 1 IO = 6 thinkers.
For a regulated context: 5 durable + Legal & Compliance + 1 IO = 7 thinkers.

### 4. Per-thinker unique files

Per `output-pattern.md` (read it):

```
$STATE_ROOT/_orgs/<slug>/engagements/<id>/council/<topic-slug>/<perspective-slug>.md
```

Each thinker writes to ITS OWN unique file. Never share a file across parallel thinkers (Write tool overwrites).

### 5. Dispatch via Agent tool

> Steps 5–7 are the `council-parallel` primitive (`$ASSET_ROOT/_core/primitives/council-parallel.md`):
> parallel dispatch → schema barrier → `{corpus[], missing[]}`. The prose below is the inline
> form; the primitive is the callable contract. Thinkers are `$0` (`thinker.md` disallows web
> tools), so either the Workflow tool (preferred — resumable journal skips completed thinkers) or
> inline parallel `Agent` is valid. Fan-out is capped at 7 (invariant #6 — the only bound on Opus
> thinker token spend, which `cost-log.jsonl` cannot see).

Use `Agent` with `subagent_type: thinker` and `run_in_background: true` for parallelism. Dispatch template per `operations.md`:

```
You are the [PERSPECTIVE] thinker for a comp-suite v2 council on:
"<topic>"

Read the operational reference at $ASSET_ROOT/_core/council/operations.md for the
gap-first output structure and the dual-return contract.

Engagement context:
- Org: <slug>
- Engagement: <id>
- Active mode: <mode>
- Industry: <primary industry>
- Industry outsider: <io>  (if you ARE the IO, your reference industry)

Persona: <persona from perspectives.yaml>
Focus: <focus from perspectives.yaml>

Write your full analysis to:
$STATE_ROOT/_orgs/<slug>/engagements/<id>/council/<topic-slug>/<perspective-slug>.md

ALSO return your full analysis as your final message (dual-return).

Stop when budget is half-spent and write whatever you have.
```

Dispatch all thinkers in a single message with multiple Agent tool blocks for parallelism. CC limit: 5 background agents at once. If 6+ thinkers, batch.

### 6. Wait for completion

The Agent tool sends notifications when each thinker finishes. Wait for all.

### 7. Validate output files (schema barrier — `council-parallel`)

Per `council-parallel` + `output-pattern.md`: for each thinker, read its unique file → fall back to its return message → **validate against `$ASSET_ROOT/_core/schemas/thinker-return.schema.json`**. A return that is absent or schema-invalid is **re-dispatched once**, then recorded in `missing[]` and surfaced in synthesis as a known gap — never silently dropped.

This is the one behavioral hardening over the prior prose (which skipped a missing perspective and only redispatched if the founder asked): the barrier now validates-or-re-dispatches structurally, so a thinner-than-intended council is surfaced rather than hidden (failure mode #6). Synthesis (Step 8) still runs on `corpus[]`; `missing[]` is reported alongside it.

### 8. Synthesize — ORCHESTRATOR ONLY

Per TM rule (in `procedure.md`): NEVER delegate synthesis to a subagent.

Synthesis style for comp deliberations: `consensus-tensions` (default). Sections:
- Consensus
- Tensions (where perspectives disagreed and why)
- Single-source claims (only one thinker said this — flag)
- Unverified assumptions
- Unresearched gaps
- Path forward (what the orchestrator recommends)
- Unresolved concerns

Write the synthesis to:
```
$STATE_ROOT/_orgs/<slug>/engagements/<id>/council/<topic-slug>/SYNTHESIS.md
```

### 9. Append the council decision to the backend decision log (P4b)

If the council resulted in a decision, append it via the MCP tool (not a local `master.yaml` write):
`engagement_append_decision {org_slug: ORG, timestamp, skill, decision_type: "council_outcome",
summary, cycle_slug (or null), tags, refs: {council_file: "<SYNTHESIS.md path>"}}`. Omit `id` to let
the server assign the next monotonic `dl-NNN`, or pass an explicit `id` to re-drive idempotently.
Append-only and idempotent on `id` (P4b D2). The per-thinker council files + SYNTHESIS.md remain LOCAL
scratch under `$STATE_ROOT/.../council/` (non-schema artifacts, P4b D3).

## Cost shape

A 6-thinker council with `model.overrides.council: opus` (per advisor mode default) is 6 opus dispatches + orchestrator synthesis. Typical cost: ~$2-5 per council. Counts toward engagement `budget_usd`. Run `budget-check` BEFORE dispatching the first thinker (estimate cost = 6 × $0.50 + synthesis $0.30 ≈ $3.30).

If budget would be exceeded, refuse cleanly and tell the founder "Council estimate $3.30 exceeds remaining budget $X. Raise via `/comp budget <id> <amount>` or accept fewer perspectives."

## Anti-patterns (from `dispatch-anti-patterns.md`)

Read it before composing dispatch prompts. The big ones:
- ALL-CAPS emphasis (don't)
- Conditional constraints (express always-active rules unconditionally)
- Instruction overload (cap at 25 instructions)
- Format rules competing with task (separate `<output>` from `<task>`)
- Bare prohibitions without alternatives (always pair "don't X" with "do Y instead")

## Acceptance

- Scenario 08 (council-dispatch): durable + 1 IO dispatched, per-thinker files written, synthesis ASSEMBLED BY ORCHESTRATOR (not subagent)
