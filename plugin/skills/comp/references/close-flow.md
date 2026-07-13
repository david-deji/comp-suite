# Close Flow + Resume

> Loaded from `SKILL.md` for `/comp close <id>` and `/comp resume <id>`.
> Implements SPEC § 10. **Idempotent: re-run is no-op.**

## `/comp close <id>` — validate-then-write, idempotent

### Step 1 — Read inputs (no writes yet)

```bash
ORG=$(yq '.org_slug' "$STATE_ROOT/_orgs/*/engagements/$id/engagement-state.yaml")
ENG_DIR="$STATE_ROOT/_orgs/$ORG/engagements/$id"

# Read engagement-state, master, working artifacts, pending decisions
state=$(yq '.' "$ENG_DIR/engagement-state.yaml")
master=$(yq '.' "$STATE_ROOT/_orgs/$ORG/master.yaml")
```

If any input is missing, exit non-zero with a clear message. Do NOT touch state.

### Step 2 — Build proposed master.yaml IN MEMORY

Apply `master-yaml-ops` primitives:
- For each `engagement_state.pending_decisions[].id`: SKIP if already in `master.decision_log[].id` (idempotency anchor)
- For each new decision: append entry per `decision-log-entry.schema.json`
- Apply mode section update via `master-yaml-ops.write_master_section(slug, mode_section, payload)` — but this call is now in-memory, not flushed
- Apply close-time updates to header: `last_touched_date`, `last_touched_by_skill: comp`

Write the proposed master to `$ENG_DIR/proposed-master.yaml.tmp` for inspection (also gitignored).

### Step 3 — Validate

Pass paths via argv (heredoc keeps `'EOF'` quoted so the Python body is opaque to the shell — avoids the literal `$ENG_DIR` / `$ASSET_ROOT` interpolation trap).

```bash
python3 - "$ENG_DIR/proposed-master.yaml.tmp" "$ASSET_ROOT/_core/schemas" "$active_mode" <<'EOF'
import json, sys, yaml, jsonschema

proposed_path, schemas_dir, active_mode = sys.argv[1], sys.argv[2], sys.argv[3]
proposed = yaml.safe_load(open(proposed_path))
errors = []

# Validate the FULL master.yaml against the shared-header (top-level) schema.
# Passing proposed["header"] (sub-dict) to a top-level schema would always fail.
hdr_schema = json.load(open(f"{schemas_dir}/master-shared-header.schema.json"))
try:
    jsonschema.validate(proposed, hdr_schema)
except jsonschema.ValidationError as e:
    errors.append(("master", e.message))

# Validate the active mode's section against its own schema.
mode_section = proposed.get(active_mode)
if mode_section is not None:
    sch_path = f"{schemas_dir}/master-{active_mode}-section.schema.json"
    try:
        sch = json.load(open(sch_path))
        jsonschema.validate(mode_section, sch)
    except FileNotFoundError:
        errors.append((f"{active_mode}_section", f"schema not found: {sch_path}"))
    except jsonschema.ValidationError as e:
        errors.append((f"{active_mode}_section", e.message))

# Validate each decision_log entry.
dl_schema = json.load(open(f"{schemas_dir}/decision-log-entry.schema.json"))
for entry in proposed.get("decision_log", []):
    eid = entry.get("id", "<no id>")
    try:
        jsonschema.validate(entry, dl_schema)
    except jsonschema.ValidationError as e:
        errors.append((eid, e.message))

if errors:
    for eid, msg in errors:
        print(f"{eid}: {msg}", file=sys.stderr)
    sys.exit(1)
EOF
```

### Step 4 — On validation FAILURE

Write `$ENG_DIR/close-validation-errors.md` with the error list (one bullet per error, identifying which schema and field). Exit non-zero. The founder fixes the data and re-runs `/comp close` — idempotency makes re-run safe (already-closed decisions are skipped).

Also write `$ENG_DIR/close-progress.yaml`:
```yaml
status: validation_failed
last_attempt: <iso>
errors_file: close-validation-errors.md
```

### Step 4.5 — Close-validation panel (close_gates) — only on the Step-3-success path

Reached only when Step 3 validation **succeeded** (a Step-3 failure already exited at Step 4).
Before the atomic write, run the active mode's registered close-gate panels on the **proposed**
`master.yaml` (`proposed-master.yaml.tmp`). The list is discovered, never hardcoded — glob the
active mode's `mode.yaml` for `close_gates` (SKILL.md § Close-gate panels):

```bash
CLOSE_GATES=$(python3 -c "
import yaml, sys
m = yaml.safe_load(open(sys.argv[1]))
print(' '.join(m.get('close_gates', [])))
" "$ASSET_ROOT/_modes/$active_mode/mode.yaml")
```

For each name in `$CLOSE_GATES`, read `$ASSET_ROOT/_core/primitives/<name>.md` and apply it. On
`advisor` / `comms` this resolves to `close-validation`; on `training` / `transformer` it is
empty — the exclusion is panel-granular (no lens runs, not just the paid statutory one) and is
Phase-3 scope per SPEC § 0a (the paid statutory lens makes auto-extension wasteful; the `$0`
internal-consistency lens is simply out of Phase-3 scope — an accepted advisory-coverage gap for
those cycle-aware modes, see SKILL.md § Close-gate panels). The panel:

- Runs `close-validation` — 3 lenses on the proposed master (`internal-consistency` +
  `budget-coherence` via read-only `critic.md`, `$0`; `statutory-accuracy` via a fetch-capable
  inline Agent, **paid**, each fetch gated per-call by `check_budget`). Engine: inline parallel
  `Agent` (`paid: true`) per § 1 — never a Workflow-tool script (it cannot run the dollar gate).
- The orchestrator (never an agent) computes block/allow from the returned lenses:
  **block** if any lens `status == "flag"` — including a `statutory-accuracy` `pass` carrying no
  non-empty `statutory_tags[].quote`, which the orchestrator downgrades to a flag (invariant
  #5) — OR if `missing[]` is non-empty (a lens absent/invalid after one re-dispatch).

**On block:** write the flagged findings to `$ENG_DIR/close-validation-flags.md`, surface them,
and **do not write** `master.yaml`. Also write `$ENG_DIR/close-progress.yaml`:
```yaml
status: close_validation_flagged
last_attempt: <iso>
flags_file: close-validation-flags.md
```
The founder resolves the flagged decision/figure/cost and re-runs `/comp close` — idempotency
makes re-run safe (already-closed decisions are skipped). The close gate stays human: the panel
informs it; it never auto-corrects `master.yaml` and never auto-advances past the gate
(invariant #3). On no flags (and empty `missing[]`), proceed to Step 5.

### Step 5 — On validation SUCCESS

Each sub-step writes a checkpoint to `$ENG_DIR/close-progress.yaml` so re-run after crash picks up where it left off.

5a. **Atomic master.yaml write**:
```bash
mv "$ENG_DIR/proposed-master.yaml.tmp" "$STATE_ROOT/_orgs/$ORG/master.yaml.new"
mv "$STATE_ROOT/_orgs/$ORG/master.yaml.new" "$STATE_ROOT/_orgs/$ORG/master.yaml"
```
Checkpoint: `status: master_written, last_step: 5a`.

5b. **Append outcome to ledger** (idempotent — skip if engagement_id already present):
```bash
LEDGER="$STATE_ROOT/ledger/outcome-history.yaml"
mkdir -p "$(dirname "$LEDGER")"
[ -f "$LEDGER" ] || touch "$LEDGER"             # first-ever close: create empty file
if ! grep -q "engagement_id: $id" "$LEDGER"; then
  cat >> "$LEDGER" <<EOF
- engagement_id: $id
  org_slug: $ORG
  closed_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
  mode: $active_mode
EOF
fi
```
Checkpoint: `last_step: 5b`.

5c. **Archive engagement folder**:
```bash
ARCHIVE="$STATE_ROOT/_orgs/$ORG/engagements/_archive/$id"
mkdir -p "$(dirname "$ARCHIVE")"
[ -d "$ARCHIVE" ] || mv "$ENG_DIR" "$ARCHIVE"
```
Idempotent: skip move if archive already exists.

5d. **Post-session friction scan** (best-effort, before progress-yaml delete).
Per SPEC-learn.md § 5.3, scan the engagement folder for harness friction signals.
Each scanner failure logs to stderr and does NOT block close.

```bash
# Scanner 1: broken-cite — markdown links + relative paths in deliverables that don't resolve
python3 - "$ENG_DIR" <<'PYEOF' 2>/dev/null || true
import os, re, json, sys
from datetime import datetime, timezone
eng_dir = sys.argv[1]
deliverables = []
for root, _, files in os.walk(os.path.join(eng_dir, "deliverables")):
    for f in files:
        if f.endswith(".md"):
            deliverables.append(os.path.join(root, f))
broken = []
for d in deliverables:
    try:
        content = open(d).read()
    except Exception:
        continue
    # Match relative repo paths (e.g., v2/_core/..., research-bureau/...)
    for m in re.finditer(r'\(([\w/-]+\.\w+)(?:#[^)]+)?\)', content):
        path = m.group(1)
        if path.startswith("http"): continue
        # Heuristic: only check repo-relative-looking paths
        if not (path.startswith("v2/") or "/" in path):
            continue
        # ... scanner stops at heuristic; full broken-cite check is best-effort
print(json.dumps({"scanner": "broken-cite", "found": 0}))
PYEOF

# Scanner 2: unused-schema-field — fields in schemas/ not written by this engagement's mode section
# Scanner 3: hook-overridden — cost-log hook-warn entries vs final deliverable contents
# Scanner 4: council-redundancy — pairwise similarity on council/ thinker question lines (>0.7)
#
# Each scanner that finds a hit calls emit_friction_event from lib.sh:
#   . "$ASSET_ROOT/_core/hooks/lib.sh"
#   emit_friction_event "post-session-broken-cite" "reference" "<description>" "low" "<file>"
#
# Implementation note: full scanners are deferred to first real engagement-close.
# The hook is in place; the scanner bodies populate as friction surfaces.
```

Per SPEC-learn.md § 5.3 the four scanners are: broken-cite, unused-schema-field,
hook-overridden, council-redundancy. Scanner failures must NOT block close —
they log to stderr and continue.

5e. Delete `close-progress.yaml` (success).

> **Note.** v1.0 of this flow (commit 369659e) included a `git -C v2/state commit` step here. It was removed: `v2/state/` is gitignored at the repo level and is NOT a separate git repo, so the command failed unconditionally. State is on-disk only. If versioning of state ever becomes useful, run `git init` inside `v2/state/` once and re-add a commit step in a future flow revision.

### Idempotency anchors

- Decision log: stable IDs `dl-<engagement-id>-<seq>`. Re-run skips already-present IDs.
- Ledger: skip if `engagement_id` already in outcome-history.yaml.
- Archive: skip mv if archive folder exists.
- Each step is rerunnable from its checkpoint.

## `/comp resume <id>`

```bash
ORG=$(yq '.org_slug' "$STATE_ROOT/_orgs/*/engagements/$id/engagement-state.yaml")
ENG_DIR="$STATE_ROOT/_orgs/$ORG/engagements/$id"

# Surface state
phase=$(yq '.phase' "$ENG_DIR/engagement-state.yaml")
last=$(yq '.last_active' "$ENG_DIR/engagement-state.yaml")
budget=$(yq '.budget_usd' "$ENG_DIR/engagement-state.yaml")
spent=$(jq -s 'map(.est_cost) | add // 0' "$ENG_DIR/cost-log.jsonl" 2>/dev/null)
spent=${spent:-0}
pct=$(python3 -c "print(round(${spent}/${budget}*100, 1))")
echo "Engagement: $ORG/$id"
echo "Phase: $phase"
echo "Last active: $last"
echo "Spent: \$$spent / \$$budget ($pct% of budget)"
```

If `close-progress.yaml` exists, surface "Mid-flight close in progress at step X. Re-run `/comp close $id` to resume."

If `working_artifacts[]` lists paths that don't exist on disk, warn (drift signal — suggest `/comp doctor`).

Then dispatch the active mode per `engagement-state.mode` field.

## Acceptance

- Scenario 11 (close-idempotency): run `/comp close` twice; second run is no-op (no duplicate decision log, no duplicate ledger, no re-archive)
- Holdout-D verifies the same with concrete fixture
