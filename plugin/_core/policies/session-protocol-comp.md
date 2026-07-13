# Session Protocol — Comp-Suite Adaptation

> **Adaptation of**: `session-protocol.md` (verbatim TM port, sibling file)
> **TM source**: `.claude/rules/session-protocol.md` @ commit `4b1dd5d7`
> **Authoritative for**: `/comp` session start, `/comp resume`, `/comp doctor`. The verbatim raw is review-baseline only.
> **Date**: 2026-05-08 | Pinned independently of TM.
>
> **What changed from TM**: Removed TM monorepo-specific session-start checks (multi-repo pull, BOARD.md, MEMORY.md, REGISTER.md, news digest, repos.yaml drift). Replaced with `/comp`-specific entry: lightweight engagement-state load, cost-log surfacing, doctor pre-check. Kept the pipeline phase boundary recovery and post-compaction recovery sections verbatim — those apply identically to long advisor/council sessions.

---

## On `/comp` Session Start

Run silently. Report only if something is wrong. Do not interrupt workflow to fix things — just note them.

### When `/comp` is invoked WITHOUT `--engagement <id>` (intent-router or mode pick)

1. No git pull. Solo-operator pet project, single working tree; pull is a deliberate `git`
   command, not a session-start hook. (See `multi-terminal-git-safety.md` companion policy
   for the rationale on why automatic branch operations are dangerous in multi-terminal
   contexts.)
2. Verify `$STATE_ROOT/_orgs/index.yaml` exists and is parseable. If missing, scaffold a fresh
   index (no orgs yet — first run).
3. If the user is dispatching to a mode or running `/comp doctor` without engagement
   context, proceed directly. The next steps fire only when an engagement is loaded.

### When `/comp <mode> --engagement <id>` OR `/comp resume <id>` is invoked

After resolving the engagement (per `$ASSET_ROOT/_core/primitives/engagement-loader.md`), run these
checks before dispatching the mode body:

1. **Engagement state load**: read `$STATE_ROOT/_orgs/<slug>/engagements/<id>/engagement-state.yaml`.
   Surface to user (one screen):
   ```
   Engagement: <slug>/<id>
   Mode: <active mode> | Phase: <phase>
   Started: <iso> | Last active: <iso> (<delta>)
   Industry Outsider: <industry>
   ```
2. **Stale-state nudge**: if `last_active` was more than 7 days ago, surface:
   ```
   ⚠ This engagement has been idle for <N> days. Verify state before
   continuing — see verify-engagement-state-before-mode.md.
   ```
   This nudge is informational, not blocking. The mode body proceeds; the verify-engagement
   discipline is a separate companion policy and runs at the orchestrator's pre-dispatch step.
3. **Cost-log surface**: read `$STATE_ROOT/_orgs/<slug>/engagements/<id>/cost-log.jsonl`. Sum
   `est_cost` field across all entries. Read `engagement-state.yaml.budget_usd`. Display:
   ```
   Spent: $X.XX / $Y.YY (Z% of budget)
   Last dispatch: <ts> — <tool> (<task>)
   ```
   If `Z >= 80`: surface a warning. If `Z >= 100`: refuse new tool dispatches with
   `est_call_cost_usd > 0` until budget is raised (see `cost-discipline.md`).
4. **Light doctor pre-check** (full `/comp doctor` is on-demand only):
   - Verify `$STATE_ROOT/_orgs/index.yaml` knows about `<slug>`
   - Verify `engagement-state.yaml.working_artifacts[].path` files exist on disk
   - Verify `master.yaml.schema_version` matches `$ASSET_ROOT/_core/version.txt`
   - Warn (do NOT auto-fix) on any drift. Surface 1-line summary: `Doctor pre-check: <N>
     drift signal(s) detected. Run /comp doctor for full reconciliation.`
5. **Pending decisions surface**: if `engagement-state.yaml.pending_decisions[]` is
   non-empty, list IDs + summaries. These are the decisions waiting on `/comp close <id>`
   to land in `master.yaml.decision_log`.
6. **Concurrent-session check**: if `last_active` was updated within the last 60 seconds,
   warn:
   ```
   ⚠ Another /comp session may be active on this engagement (last_active < 60s ago).
   See multi-terminal-git-safety.md for the collision discipline.
   ```

Silent if all checks pass.

---

## Pipeline Phase Boundary Recovery

When running a multi-phase mode body (advisor council loop, comms cascade fan-out,
training audience-bundle generation), write to `engagements/<id>/checkpoint.yaml` after
every phase — do not wait for compaction. Include: current phase + status, key file paths
written this phase, what's next.

Additionally, write a structured workflow state block at the top of `checkpoint.yaml`
after each phase completes:

```yaml
# Workflow State
phase: executing        # planned | executing | awaiting-approval | completed | failed
completed:
  - phase-research
  - phase-council-dispatch
current: phase-synthesis
side_effects:
  files_written:
    - engagements/<id>/advisor/draft-decision-doc.md
    - engagements/<id>/council/<topic>/compensation-strategist.md
  cost_log_appends: 5
safe_to_retry: true     # false if current phase has irreversible side effects (e.g., master.yaml.append)
next: phase-render-deck
updated: 2026-05-08T14:30:00Z
```

Workflow state enables safe retry after crash. Conversation state (recovery file,
below) is a pointer; workflow state (`checkpoint.yaml`) is the durable checkpoint.

---

## After Compaction

1. Read `.claude/recovery-{SESSION_ID}.md` first if it exists — that's the session-scoped
   recovery written by the PreCompact hook (race-safe across multiple terminals). Fall
   back to `.claude/recovery.md` only if the session-scoped file is missing.
2. If the recovery YAML's `pipeline.checkpoint_file` is set, read that file and resume
   from the current phase — do not restart completed phases.
3. Do not ask "what were we working on?" — recovery has the answer. Act on it.
4. If recovery is missing or stale (>2 hours old), check git log on the comp-suite repo
   for recent WIP commits and reconstruct context from changed files + the active
   engagement's `checkpoint.yaml`.

---

## During Normal Work (opportunistic)

- When editing a file with a `Last updated:` header older than 30 days, update the date.
- When creating a new mode reference under `$ASSET_ROOT/_modes/<name>/references/`, check the
  mode's `references` field in `mode.yaml` and add the entry if missing.
- When encountering a TODO that is a significant standalone task, mention it as a
  candidate post-engagement issue. Do not auto-file (comp-suite has no issue tracker).
- When reading a knowledge file with a stale-feel reference, mention it as potentially
  stale. Do not auto-update.

---

## Git Conventions

- "Commit" means commit; pushing is a deliberate operator action (no remote auto-push).
- Commit at natural checkpoints; reference engagement IDs in messages where relevant.
- Client comp data, headcount tables, and salary specifics never enter git outside the
  gitignored `$STATE_ROOT` subtree. Per spec, `$STATE_ROOT/.git/` is its own working tree;
  `$STATE_ROOT` is gitignored from the parent repo.
- Per `multi-terminal-git-safety.md`: confirm branch before any push.

---

## See Also

- `$ASSET_ROOT/_core/policies/session-protocol.md` — verbatim TM raw (review baseline)
- `$ASSET_ROOT/_core/policies/cost-discipline.md` — drives the cost-log surfacing rule
- `$ASSET_ROOT/_core/policies/verify-engagement-state-before-mode.md` — drives the stale-state nudge
- `$ASSET_ROOT/_core/policies/multi-terminal-git-safety.md` — drives the concurrent-session check- `$ASSET_ROOT/_core/primitives/engagement-loader.md` — reads engagement-state at dispatch time
- `v2/.claude/skills/comp/SKILL.md` § 3 — the orchestrator entry that consumes this policy
