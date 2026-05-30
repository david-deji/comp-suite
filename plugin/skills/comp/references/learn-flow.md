# Learn Flow

> Loaded from `SKILL.md` for `/comp learn`.
> Implements SPEC-learn.md § 3 (synthesis trigger) and § 10 (the flow).
> Cites `$ASSET_ROOT/_core/primitives/friction-aggregator.md` for the read-grouping-scoring step.

## Purpose

Synthesize accumulated friction events into proposed harness changes, present each
for founder ratification, apply accepted diffs, record outcomes, run meta-tracking
on previously-applied changes.

## Flow

### Step 1 — Threshold check

Count events in `friction.jsonl` since the last synthesis run:

```bash
HARNESS_DIR="$STATE_ROOT/harness"
JSONL="$HARNESS_DIR/friction.jsonl"

last_run=$(ls -1t "$HARNESS_DIR/synthesis/"*.md 2>/dev/null | head -1 || true)
if [ -n "$last_run" ]; then
  last_ts=$(grep '^> next_since_ts:' "$last_run" | head -1 | awk '{print $3}')
else
  last_ts="1970-01-01T00:00:00Z"
fi

count=$(awk -v ts="$last_ts" '
  { if (match($0, /"ts":"([^"]+)"/, m) && m[1] >= ts) c++ }
  END { print c+0 }
' "$JSONL" 2>/dev/null)
```

If `count < 5`, refuse with:

```
Insufficient friction events for synthesis: <count> events since last run (threshold: 5).
Add events with /comp friction "<text>", or wait until more accumulate.
```

Exit 0. Do NOT touch state. Do NOT create a synthesis file.

### Step 2 — Run aggregator

Apply `$ASSET_ROOT/_core/primitives/friction-aggregator.md` `aggregate(since_iso=last_ts)`.
Receives:

```python
{
  "proposals":      List[Proposal],   # sorted by priority
  "events_read":    int,
  "events_skipped": int,
  "meta_findings":  List[MetaFinding],  # recurrence detections
}
```

If `events_read - events_skipped < 5`, threshold fails after dedup — refuse
(same message, same exit).

### Step 3 — Generate run-id and write synthesis output

```bash
SYNTHESIS_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
RUN_HASH="$(echo "$SYNTHESIS_TS" | sha256sum | cut -c1-6)"
RUN_ID="$(date -u +%Y-%m-%d)-${RUN_HASH}"
SYNTHESIS_FILE="$HARNESS_DIR/synthesis/${RUN_ID}.md"
APPLIED_FILE="$HARNESS_DIR/applied/${RUN_ID}.md"
mkdir -p "$HARNESS_DIR/synthesis" "$HARNESS_DIR/applied"
```

Write the synthesis manifest with frontmatter:

```markdown
# Friction synthesis run YYYY-MM-DD-<hash>

> since_ts: <iso>
> events_read: <N>
> events_skipped: <N>
> proposals: <N>
> meta_findings: <N>
> next_since_ts: <SYNTHESIS_TS>

## Meta-findings (recurrence of previously-applied changes)

[List meta_findings if any. Each: applied_at, target_path, diff_summary, recurred_signatures, message.]

## Proposed changes (grouped by action class)

### <ACTION_CLASS_1>

#### Proposal 1: <target_path>
- **Confidence:** HIGH | **Evidence:** N events | **Signal pattern:** <signal_type>
- **Signature:** <12-char>
- **Evidence:**
  - <ts> | <signal_type> | <description first 80 chars>
  - ...
- **Proposed diff:**
  ```
  <unified-diff-style block>
  ```
- **Would prevent signatures:** [<sig1>, <sig2>, ...]
- **Outcome:** PENDING

(repeat per proposal, grouped by action_class)
```

The `Outcome:` field starts as `PENDING` and is updated in step 5.

### Step 4 — Surface meta-findings to founder first

If `meta_findings` is non-empty, surface them BEFORE the ratification loop. These
are higher-priority signals — a previous fix may not have worked.

For each meta-finding, AskUserQuestion (one at a time, max 4 batched):

```
Question: A change applied at <target_path> on <applied_at> was supposed to prevent
<N> friction signatures, but <M> recurred. Revisit?

Header: META-FINDING
Options:
  1. Open the file and re-edit (orchestrator opens via Read; founder edits inline)
  2. Skip — accept the change didn't fully fix it; will re-surface in proposals if pattern continues
  3. Mark as known limitation — record in this run's synthesis output
```

Apply per outcome. Append outcomes to synthesis file's Meta-findings section.

### Step 5 — Founder ratification loop

For each proposal in priority order, present via AskUserQuestion (batch up to 4
proposals per call to reduce dialog overhead):

```
Question: Apply proposed change to <target_path>?

Header: <action-class>

Options:
  1. Accept — apply the diff exactly as proposed
  2. Modify — open the file, founder edits, then apply + record
  3. Reject — never re-surface this pattern signature
  4. Defer — leave events in pool, will re-surface next synthesis
```

Per outcome:

#### ACCEPT path

The aggregator's `proposed_diff` is a **description**, not an executable diff. The
orchestrator must:
1. Read the target file at `target_path`.
2. Identify the smallest possible edit addressing all evidence (the orchestrator
   has the proposed_diff text and the target file content; it composes the
   minimal Edit call).
3. Apply via `Edit` tool.
4. Verify the file is unchanged in shape (e.g., still parses as YAML/JSON if it
   was structured) — if shape breaks, ROLLBACK by re-running Edit with the
   reverse change, mark proposal as ESCALATED, and surface to founder.
5. Append a record to `applied/<run-id>.md`:
   ```yaml
   - applied_at: <iso>
     proposal_signature: <12-char>
     target_path: _core/...
     action_class: <class>
     diff_summary: <one-line — orchestrator composes from the actual edit>
     would_prevent_signatures:
       - <sig1>
       - <sig2>
   ```
6. Update synthesis file: change proposal's `Outcome: PENDING` → `Outcome: ACCEPTED`.

#### MODIFY path

Open the target file at the relevant line. Surface a follow-up AskUserQuestion:
```
Question: Paste the modification you want, or 'cancel' to abort.
Header: Modify
Options:
  1. Use my paste verbatim
  2. Cancel
```

If `Use my paste verbatim`, prompt for free-text via the standard "Other" path.
Apply the founder's edit via `Edit` tool. Record per ACCEPT path (also includes
`would_prevent_signatures` since founder is refining a real fix).

Update synthesis: `Outcome: MODIFIED`.

#### REJECT path

Surface a follow-up AskUserQuestion for the rejection reason:
```
Question: Why reject? (one-line)
Header: Reject reason
Options:
  1. Noise / not actionable
  2. Wrong root cause identified
  3. Not worth the cost of fix
  4. Other (free-text)
```

Append to `$STATE_ROOT/harness/rejected.yaml`:

```yaml
- signature: <12-char>
  target_class: <class>
  target_path: <path>
  signal_pattern: <signal_type>
  rejected_at: <iso>
  reason: <founder's choice or free-text>
```

Future aggregator runs filter events with this signature.

Update synthesis: `Outcome: REJECTED`.

#### DEFER path

No state change. Update synthesis: `Outcome: DEFERRED`. Events remain in
`friction.jsonl` and will re-surface in the next run.

### Step 6 — Optional commit

After all ratifications, if any proposals were `ACCEPTED` or `MODIFIED`, surface:

```
<N> changes applied across <M> files.
Commit now?
  A. Yes — git add + commit "harness(learn): apply <N> friction-driven changes (run <id>)"
  B. No — leave changes uncommitted (you can commit manually later)
```

If A, run the commit. The commit message includes the run-id so the synthesis
file is the audit trail.

### Step 7 — Final summary

Echo to stdout:
```
Friction synthesis complete (run <id>):
  Events read:      <N>
  Events skipped:   <N>
  Proposals total:  <N>
    Accepted:       <N>
    Modified:       <N>
    Rejected:       <N>
    Deferred:       <N>
  Meta-findings:    <N>
  Synthesis output: $STATE_ROOT/harness/synthesis/<run-id>.md
  Applied record:   $STATE_ROOT/harness/applied/<run-id>.md (if accepts > 0)
```

Exit 0.

## No subagent dispatch

The entire `/comp learn` flow runs inline in the orchestrator. No `Agent` tool calls.
No paid tool calls. WHY: the steps are deterministic (read jsonl → group → propose
→ ratify → apply). The founder is the only decision-maker (at ratification). Adding
subagents = agent washing per `.claude/rules/agentic-workflow-principles.md`
anti-pattern #10.

## Edge cases

- **No prior synthesis run**: `last_ts` defaults to epoch. All events qualify.
- **Empty friction.jsonl**: count=0 < 5, refuse.
- **Aggregator returns 0 proposals despite events_read >= 5**: surface
  "5+ events but no group has ≥2 events with same target. Wait for more events
  to accumulate, or add `--target-path` hints to future captures." Write the
  synthesis file anyway with `proposals: 0` for audit trail.
- **Edit tool fails on ACCEPT**: rollback via reverse edit, mark proposal as
  ESCALATED in synthesis, do NOT add to applied/. Surface to founder with the
  error.
- **rejected.yaml malformed**: aggregator already tolerates this (returns empty
  set). No special handling needed here.

## Acceptance

- Test scenario 17 (`17-learn-synthesis.md`) — verifies threshold gate, grouping,
  confidence scoring, ratification dialog, reject path, meta-tracking after re-run.
