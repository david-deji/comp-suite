# Verify Engagement State Before Mode Dispatch

> **Adaptation of**: `verify-upstream-before-specify.md` (verbatim TM port, sibling file)
> **TM source**: `.claude/rules/verify-upstream-before-specify.md` @ commit `4b1dd5d7`
> **Authoritative for**: pre-dispatch verification in `/comp <mode> --engagement <id>` and `/comp resume <id>`. The verbatim raw is review-baseline only.
> **Date**: 2026-05-08 | Pinned independently of TM.
>
> **What changed from TM**: Renamed because the comp-suite analogue isn't "upstream repo verification" (TM's /specify against external OSS forks) — it's "engagement state verification before mode dispatch in a cycle-recurring engagement." The discipline generalizes; the surface differs. The TM rule's failure mode taxonomy (sycophantic confirmation + silent failure + incorrect verification converging) applies identically.

---

## The Rule

When `/comp <mode>` will operate on an engagement that has prior session state, at least
one of the following must happen BEFORE the mode body executes:

1. **Read the engagement state on disk.** The orchestrator reads
   `$STATE_ROOT/_orgs/<slug>/engagements/<id>/engagement-state.yaml` and surfaces:
   - `last_active` (with delta from now)
   - `phase`
   - `working_artifacts[]` (paths)
   - `pending_decisions[]` (IDs + summaries)
   The session-protocol-comp.md companion already does this on every engagement-bearing
   `/comp` invocation; this rule formalizes it as the verification gate.

2. **Read the prior cycle's decision_log slice.** For cycle-recurring engagements where
   `master.yaml.cycles[]` has > 1 entry, the orchestrator dispatches the
   `$ASSET_ROOT/_core/primitives/cycle-awareness.md` primitive and reads the previous cycle's
   `decision_log` slice. This grounds the mode body in what was actually decided last
   cycle, not what the orchestrator's context might guess.

3. **Verify working_artifacts[] paths exist on disk.** The orchestrator runs the
   light doctor pre-check (per session-protocol-comp.md). If any
   `working_artifacts[].path` no longer exists on disk (filesystem drift between
   sessions), surface and STOP — do not let the mode body operate against phantom inputs.

4. **The orchestrator runs `$ASSET_ROOT/_core/primitives/engagement-loader.md` against actual disk
   state — NOT against memory of "what should be there".** Engagement state on disk is
   the authoritative source. Memory of prior sessions decays.

## Must-Nots

- **Never dispatch a mode body to an engagement without one of the four checks above
  passing.** The TM rule's anchor (a research-derived synthesis treated as verification)
  generalizes here as: "a memory of the prior session" treated as verification. Memory
  is not verification. Disk is.
- **Never accept "the prior session already verified this" as a substitute for re-read at
  the engagement's actual state.** Memory artifacts decay between sessions and the
  engagement state moves under the orchestrator (founder may have edited
  `engagement-state.yaml` directly between sessions).
- **Never silently work around a missing `working_artifacts[]` file.** If a path the
  state claims exists is gone from disk, that absence IS the signal that the mode body
  cannot proceed as planned. Surface and stop. (See companion: `assumption-verification.md`
  Recovery Process.)

## Anchor case

The parallel to TM's OB1/Hermes anchors: a `/comp resume <id>` on an engagement the
founder hasn't touched in 3 weeks. Without verification, the mode body dispatches on the
assumption that the prior session's working drafts at `engagements/<id>/advisor/` exist;
if they were moved or deleted (filesystem drift, or founder cleanup between sessions), the
advisor mode operates against phantom inputs and produces broken output that *looks*
plausible because the orchestrator's context retains the prior session's summary.

With verification, the orchestrator surfaces the drift before mode dispatch, offers
reconciliation paths (re-create the missing artifact from `master.yaml`, or pivot to a
different phase), and stops on `[ESCALATION]` if the founder needs to decide.

This is failure modes #3 (sycophantic confirmation) + #6 (silent failure) + #9 (incorrect
verification) from the agentic-workflow-principles.md taxonomy converging — three modes
at once because verification *appears* sound (the orchestrator "remembers" the prior
session) but the underlying check (memory vs. real disk state) is incorrect.

## How to Apply

Add a verification step to the orchestrator's mode-dispatch entry (`v2/.claude/skills/comp/SKILL.md`
§ 3, after step 6 "Apply primitives in order"). If the resolved engagement has any
`working_artifacts[]` AND `last_active` is more than 7 days ago, the orchestrator MUST
produce evidence of one of the four checks above before invoking the mode body.

For multi-cycle engagements (every advisor engagement after the first cycle): always run
check #2 (`$ASSET_ROOT/_core/primitives/cycle-awareness.md`). The prior cycle's `decision_log` is what makes
"recurring" actually recurring — without it, every cycle is a cold start.

## Cycle-recurring engagements: extra discipline

Comp-suite is built for engagements that recur on cycle (annual comp review, quarterly
maintenance, biennial pay-equity audit). The verification discipline scales with cycle
count:

| Cycles in `master.yaml` | Verification requirement |
|---|---|
| 0 (cold start) | None — there is no prior state to verify |
| 1 (mid-first-cycle) | Read engagement-state.yaml + verify working_artifacts |
| 2+ (recurring engagement) | All of the above + cycle-awareness primitive (read prior cycle's decision_log slice) |

The cost is 1-2 extra primitive invocations per dispatch. Negligible against the cost of
a full mode body operating on phantom state.

## Escalation Triggers

- **Disk state contradicts engagement-state.yaml.** A `working_artifacts[].path` claims
  a file exists; disk says it doesn't. Stop, surface, ask the founder to choose a
  reconciliation path (drop from array, re-create from `master.yaml`, restore from git).
- **`master.yaml.cycles[]` has more entries than `decision_log[]`.** Schema invariant
  violation — a cycle was added but no decisions were ever logged. Surface and stop;
  this is data corruption, not a normal state.
- **Two `/comp` sessions appear active on the same engagement.** Per
  `multi-terminal-git-safety.md` companion: warn and pause until founder confirms there's
  no concurrent session. Do not dispatch the mode body blind.
- **The founder edited `engagement-state.yaml` between sessions in a way that contradicts
  `checkpoint.yaml`'s `phase`.** Possible mid-cycle pivot. Stop and ask before running
  the mode body — the orchestrator's `phase` resolution may be on stale assumptions.

## See Also

- `$ASSET_ROOT/_core/policies/verify-upstream-before-specify.md` — verbatim TM raw (review baseline)
- `$ASSET_ROOT/_core/policies/assumption-verification.md` — the broader rule this operationalizes for /comp
- `$ASSET_ROOT/_core/policies/session-protocol-comp.md` — the session-start hooks that surface the state
- `$ASSET_ROOT/_core/primitives/engagement-loader.md` — reads engagement-state at dispatch time
- `$ASSET_ROOT/_core/primitives/cycle-awareness.md` — reads prior cycle's decision_log slice
- `$ASSET_ROOT/_core/primitives/engagement-create.md` — companion (creates state; this rule verifies it)
- `v2/.claude/skills/comp/SKILL.md` § 3 — the orchestrator entry that consumes this policy
- `v2/.claude/skills/comp/references/doctor-checks.md` — the full reconciliation procedure
