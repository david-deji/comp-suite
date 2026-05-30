# Doctor Checks

> Loaded from `SKILL.md` for `/comp doctor [<id>] [--fix]`.
> Implements SPEC § 10 reconciliation. Read-only by default; `--fix` applies repairs (asks per drift before fixing).
> Drift-check rationale: `$ASSET_ROOT/_core/policies/assumption-verification.md` — the trigger
> conditions (deployment debugging, infra-dependent builds, stale issue references) generalize
> to engagement-state drift; doctor is the operational gate.

## Five reconciliation dimensions

### Check 1 — `_orgs/index.yaml` ↔ disk org folders

```bash
INDEX="$STATE_ROOT/_orgs/index.yaml"

# Index entries — field is `org_slug` per index.yaml shape (see master-yaml-ops.md).
mapfile -t indexed < <(yq '.orgs[].org_slug' "$INDEX" 2>/dev/null | grep -v '^null$')

# Disk orgs
mapfile -t on_disk < <(find "$STATE_ROOT/_orgs" -maxdepth 1 -mindepth 1 -type d ! -name "_archive" -exec basename {} \;)

# Diff: missing from index (orphan folder), missing from disk (stale entry)
for slug in "${on_disk[@]}"; do
  printf '%s\n' "${indexed[@]}" | grep -qx "$slug" || echo "DRIFT: orphan folder $slug not in index.yaml"
done
for slug in "${indexed[@]}"; do
  [ -d "$STATE_ROOT/_orgs/$slug" ] || echo "DRIFT: stale index entry $slug — folder missing"
done
```

`--fix` actions:
- Orphan folder → prompt founder: archive (`mv to _orgs/_archive/`) or add to index?
- Stale entry → prompt founder: remove from index?

### Check 2 — `working_artifacts[]` paths exist

For each engagement (or just the named one if `<id>` provided):

```bash
yq '.working_artifacts[].path' "$ENG_DIR/engagement-state.yaml" | while read -r p; do
  fullpath="$STATE_ROOT/_orgs/$ORG/engagements/$id/$p"
  [ -e "$fullpath" ] || echo "DRIFT: working_artifact $p not on disk"
done
```

`--fix`: drop missing entries from `working_artifacts[]` (in-place edit via yq).

### Check 3 — master.yaml `schema_version` ↔ codebase schema

The expected version is pinned in `$ASSET_ROOT/_core/version.txt` (single source of truth for
the master.yaml shape; bumped in lock-step with schema migrations). Master.yaml
stores `schema_version` at the top level (not under `header`).

```bash
expected=$(cat "$ASSET_ROOT/_core/version.txt" 2>/dev/null | tr -d '[:space:]')
actual=$(yq '.schema_version' "$STATE_ROOT/_orgs/$ORG/master.yaml" 2>/dev/null | tr -d '"')
if [ -z "$expected" ]; then
  echo "WARN: $ASSET_ROOT/_core/version.txt missing — schema-version check skipped"
elif [ "$expected" != "$actual" ]; then
  echo "DRIFT: master schema_version mismatch — actual=$actual expected=$expected"
fi
```

`--fix`: surface the migration path. v2.0 → v2.1 is manual (added `budget_usd` and `industry_outsider` fields per audit). Do NOT auto-migrate; prompt founder with the diff.

### Check 4 — `last_active < 60s` ago (concurrent session warning)

```bash
last=$(yq '.last_active' "$ENG_DIR/engagement-state.yaml")
now=$(date -u +%s)
last_epoch=$(date -d "$last" +%s 2>/dev/null || echo 0)
diff=$((now - last_epoch))
[ "$diff" -lt 60 ] && echo "WARN: engagement last_active was ${diff}s ago — possible concurrent session. Single-operator project, no locking. Pause the other session or wait."
```

`--fix`: NONE. Warn only. This is operator discipline per SPEC § 10 concurrent-session caveat.

### Check 5 — Spend log sum vs cost-log.jsonl

```bash
recompute=$(jq -s 'map(.est_cost) | add // 0' "$ENG_DIR/cost-log.jsonl" 2>/dev/null)
recorded=$(yq '.spent_usd // 0' "$ENG_DIR/engagement-state.yaml")
if [ -n "$recorded" ] && [ "$recorded" != "$recompute" ]; then
  echo "DRIFT: spent_usd=$recorded but cost-log sum=$recompute"
fi
```

(If `engagement-state.yaml` doesn't cache `spent_usd`, this check is trivial. If it does, sync them.)

`--fix`: update `spent_usd` to recomputed sum.

## Output

Read-only mode (default):

```
=== /comp doctor [report for <id> or all] ===

Check 1 (org index ↔ disk):     [PASS | N drifts]
Check 2 (working_artifacts):     [PASS | N drifts]
Check 3 (schema_version):        [PASS | mismatch]
Check 4 (concurrent session):    [PASS | warn]
Check 5 (spend log):             [PASS | drift]

Summary: <N> drifts found. Run with --fix to repair (interactively).
```

`--fix` mode: walk drifts in order, prompt founder per drift with `AskUserQuestion`. Apply repair, log to `$ENG_DIR/doctor-fixes.log`.

## Idempotency

`/comp doctor` writes nothing on read-only mode (default). `--fix` writes only with founder confirmation per drift. Re-run safe in both modes.

## Limitations (known)

- Does not check git state of `$STATE_ROOT/` (uncommitted changes are NOT a drift signal here; they may be in-progress work).
- Does not validate `cost-log.jsonl` line schema — corrupt JSONL surfaces as `jq` error, treat as drift.
- Does not check archived engagements (`_archive/` is read-only by convention).

## Acceptance

- The 5 checks listed in SPEC § 10 are implemented above.
- `/comp doctor` exits 0 if no drifts, non-zero count of drifts otherwise.
- `--fix` is interactive — never auto-fixes without founder confirm.
