# Assumption Verification

When the harness operates on beliefs about infrastructure, deployment targets, or architectural state, those beliefs may be stale. A resolved issue may have moved a service. A prior session may have migrated infrastructure. The agent's world model decays between sessions — specs, issue files, and deployment configs are the ground truth, not memory or context.

This rule defines when to verify, how to verify, and what to do when an assumption breaks.

**Anchor example:** A session spent hours debugging Eva on Fly.io after she'd already been migrated to the 5950X per issue 0210. No rule told the agent to check deployment state before debugging. This rule prevents that class of failure.

## Trigger Conditions

Not every action needs verification. Verify only at these high-impact moments:

| Trigger | What to check | Why |
|---------|--------------|-----|
| Before debugging a deployed service | Read the latest resolved issue for that service. Check deployment config files. Confirm the service is where you think it is. | The Eva/Fly.io incident: debugging a target that no longer existed. |
| Before building on infrastructure another issue set up | Verify the service, database, or system actually exists and matches expectations. Read the issue that created it. | Building on phantom infrastructure wastes an entire session. |
| When a tool call fails with "not found", connection refused, or unexpected 404 | Before retrying or working around: consider whether the target has moved or been decommissioned. | Retrying a stale target compounds the error. The failure IS the signal. |
| When referencing a resolved issue's architectural output | Verify the output files still exist and the decisions still apply. Check if a later issue superseded them. | Resolved issues are snapshots. Later work may have changed the architecture. |
| Session start involving a specific deployed service or infrastructure | Add to session-start checks: verify deployment target for the active issue's system. | Cheapest time to catch drift — before any work begins. |

**Cost**: 1-3 extra tool calls per trigger point. This is not per-action overhead — it fires only at the moments above.

## Musts

- **Verify before debugging.** Before running any debugging workflow against a deployed service, confirm where that service is currently deployed. Read the most recent resolved issue that touched that service. Check deployment config files or infra docs. Do not rely on memory, context, or assumptions from prior sessions.
- **Verify before building on infra.** Before building features, integrations, or configurations that depend on infrastructure another issue claimed to set up, verify the infrastructure exists. Read the issue file. Check actual state (file existence, service response, config presence).
- **Stop on broken assumption.** When you discover a mismatch between what you assumed and what you find, execute the recovery process (see below). Do not continue the current approach.
- **Produce deterministic evidence.** Verification means reading a file, running a command, or checking a response — not reasoning about what should be true. "I believe the service is on the 5950X" is not verification. Reading the deployment config and seeing `host: 5950x` is verification. WHY: Per NBJ, "we cannot trust the model self-report." Self-assessed confidence is the most common source of Phantom Verification failures.
- **Document every broken assumption.** When an assumption breaks, append to the active issue's Log table: date, what was assumed, what was actually true, which source of truth was wrong. This creates an institutional record of drift patterns.

## Must-Nots

- **Never silently work around a broken assumption.** If a URL doesn't respond, a service isn't where expected, or a file doesn't exist — do not quietly try alternatives. The absence IS the signal that your world model is wrong. WHY: Silent workarounds mask drift. The next session inherits the same broken assumption.
- **Never retry without investigating.** When a tool call fails unexpectedly, do not retry the identical call. First ask: "Is the target where I think it is?" Check the assumption, then decide whether to retry, redirect, or escalate.
- **Never claim "verified" without evidence.** Do not write "I verified the service is running" unless you can cite the specific tool output that confirmed it. Statements like "this should work based on the code structure" are not verification — they are confidence without evidence.

## Preferences

- **Prefer configs over memory.** Check deployment configs, resolved issue files, and infra docs over relying on what you recall from context or prior sessions. Files are ground truth; memory decays.
- **Prefer one upfront check over mid-task recovery.** A 2-call verification at the start of a debugging session costs less than discovering the wrong target 30 calls in.
- **Prefer high-impact assumptions.** Focus verification energy on deployment targets, service locations, infrastructure state, and architectural decisions. Do not verify low-impact assumptions like file formatting conventions or naming patterns.
- **Prefer the most recent resolved issue.** When multiple issues have touched the same system, read the most recently resolved one first — it has the latest architectural state.

## Escalation Triggers

- **Undocumented change.** Verification reveals the system has changed in a way not reflected in any issue file, deployment config, or knowledge doc. The source of truth is missing — escalate to the founder before proceeding. WHY: If no document reflects reality, the agent cannot self-correct. The founder needs to know the gap exists.
- **Multi-issue impact.** The broken assumption affects 2+ active issues (e.g., a shared service has moved). Escalate immediately — continuing on one issue while others depend on the same wrong assumption compounds damage.
- **Session-scale cost.** The work done under the wrong assumption exceeds a trivial amount (e.g., multiple files edited, tests written against wrong target). Stop and escalate rather than silently unwinding — the founder should know time was spent on a wrong premise.

## Recovery Process

When an assumption breaks, in order:
1. **STOP** — halt immediately, do not "finish this one thing first"
2. **DOCUMENT** — append to issue Log: `| [DATE] | Harness | Assumption broken: [assumed] → actual: [true]. Drift source: [file]. |`
3. **UPDATE SOURCE OF TRUTH** — fix the wrong document (stale issue output, wrong deployment config, outdated knowledge file). This prevents recurrence.
4. **RESUME** — continue with corrected assumption. Re-evaluate plan if scope changed. Report to founder if task is now moot.

---

## v2 adapter footer (comp-suite, 2026-05-08)

This rule was ported verbatim from TM `.claude/rules/assumption-verification.md` @ commit `4b1dd5d7`.
The TM body above is authoritative — read it first. This footer is comp-suite-specific scope clarification only.

**Path substitutions applied** (TM → comp-suite):
- TM repo paths and bureau-issue references → comp-suite analogues do not exist; ignore them
- "Last resolved issue" → in comp-suite, the analogue is `engagement-state.yaml` and the prior cycle's `decision_log` slice (see `_core/primitives/cycle-awareness.md`)

**TM-specific references comp-suite ignores:**
- Eva/Fly.io anchor incident — TM-product-specific; the failure class generalizes
- Bureau-issue file references (e.g., `internal-ops-bureau/issues/0210-OPS-...`) — comp-suite has no bureau system
- "Most recent resolved issue" lookups — comp-suite uses the engagement's `master.yaml.decision_log` instead

**Comp-suite anchor:**
- `/comp resume <engagement-id>` after a multi-week gap, where `engagement-state.yaml.last_active` is stale or `working_artifacts[]` paths have been moved/deleted from disk — verify state against actual disk before dispatching the active mode. See `verify-engagement-state-before-mode.md` for the comp-adapted procedure.

**Companion adapted rule**: `verify-engagement-state-before-mode.md` operationalizes this discipline for the `/comp` orchestrator entry point.
