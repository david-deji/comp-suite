# Friction Capture

> Loaded from `SKILL.md` for `/comp friction "<text>" [flags]`.
> Implements SPEC-learn.md § 3 (manual capture) and § 5.1 (manual path).

## Purpose

Append one event to `$STATE_ROOT/harness/friction.jsonl` so the next `/comp learn`
synthesis run can group it with similar events and propose concrete harness changes.

Capture is fast, fail-soft, and never blocks. The operator should run this
the moment friction surfaces — do not defer to "later."

## Invocation

```
/comp friction "<text>" [--severity low|medium|high] [--target <class>] [--target-path <path>]
```

Where:
- `<text>` (required, non-empty) — one-line operator description of the friction.
- `--severity` (optional, default `medium`) — operator's gut-feel severity.
- `--target` (optional, default `unspecified`) — target class. Choose from
  `primitive`, `reference`, `hook`, `prompt`, `schema`, `intent-router`, `persona`,
  `perspective`, `glossary`, `unspecified`.
- `--target-path` (optional) — repo-relative path hint for grouping by file.

## Procedure

1. **Validate `<text>`** — non-empty, ≤ 1000 chars. Reject with one-line error
   otherwise. Do NOT echo the text back unredacted to stderr (it may contain
   operator language that would be noise in transcripts).

2. **Validate flag values:**
   - `--severity` must be `low | medium | high`. Default `medium` if absent.
   - `--target` must match the schema enum at `$ASSET_ROOT/_core/schemas/friction-event.schema.json`.
     Default `unspecified` if absent or unrecognized.
   - `--target-path` is free-text; trim leading `./` if present.

3. **Read environment:**
   ```bash
   COMP_ACTIVE_MODE="${COMP_ACTIVE_MODE:-}"
   COMP_ENGAGEMENT_ID="${COMP_ENGAGEMENT_ID:-}"
   ```
   Empty values become null fields in the JSON event (not empty strings).

4. **Append event** via inline python3 (do NOT use the lib.sh helper — that
   helper is for `source: auto`; manual capture is `source: manual`):

   ```bash
   HARNESS_DIR="$STATE_ROOT/harness"
   mkdir -p "$HARNESS_DIR"
   # First-event-ever: stamp install date for hook gate
   [ ! -f "$HARNESS_DIR/.install-date" ] && date -u +%Y-%m-%d > "$HARNESS_DIR/.install-date"

   python3 - "$severity" "$target_class" "$target_path" "$text" \
            "$COMP_ENGAGEMENT_ID" "$COMP_ACTIVE_MODE" "$HARNESS_DIR/friction.jsonl" \
            <<'PYEOF'
   import sys, json
   from datetime import datetime, timezone
   sev, tcls, tpath, desc, eng, mode, out = sys.argv[1:8]
   event = {
     "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
     "source": "manual",
     "severity": sev,
     "target_class": tcls,
     "target_path": tpath if tpath else None,
     "description": desc,
     "context_engagement_id": eng if eng else None,
     "context_mode": mode if mode else None,
     "signal_type": "operator-flagged",
   }
   with open(out, "a") as f:
       f.write(json.dumps(event, ensure_ascii=False) + "\n")
   PYEOF
   ```

5. **Echo confirmation** to stdout:
   ```
   Friction logged: <severity> | <target_class> | <description first 60 chars>...
   ```
   Exit 0.

## Auto-capture paths (reference for callers)

The orchestrator and hook scripts also write events with `source: auto` via
`$ASSET_ROOT/_core/hooks/lib.sh:emit_friction_event`. Callsites and signal types per
SPEC-learn.md § 5.2:

| Trigger | signal_type | Where |
|---|---|---|
| AskUserQuestion "Other" with > 50 chars | `askuserquestion-other-longform` | Orchestrator (SKILL.md and references that call AskUserQuestion) |
| Hook script exit 1 (warn) — first 30 days only | `hook-fired-warn` | `lib.sh` `emit_friction_event` from each hook |
| Primitive RuntimeError surfaced to operator | `primitive-runtime-error` | Each primitive's validator path |
| Intent-router classifier returns `confidence: low` | `intent-router-low-confidence` | `intent-router.md` step 3 |
| Schema validation surfaces to operator | `schema-validation-failure` | `master-yaml-ops` validators |
| Same clarification asked twice in one session | `repeated-clarification` | Orchestrator session-bound counter |

Auto callers always go through `emit_friction_event` so the JSON-encoding,
first-30-days gate, and fail-soft semantics are centralized.

## Post-session capture (reference for callers)

`/comp close <id>` runs scans before the close-progress.yaml deletion (per
close-flow.md § "Post-session friction scan"). Scans write events with
`source: post-session`. See close-flow.md for the four scanners
(broken-cite, unused-schema-field, hook-overridden, council-redundancy).

## Edge cases

- **Outside an engagement**: `COMP_ACTIVE_MODE` and `COMP_ENGAGEMENT_ID` may be
  empty. JSON event produces `null` (not empty string) for `context_*` fields.
  No primitive DAG runs — `/comp friction` is a state-light subcommand.
- **Disk full / write fails**: capture path silently no-ops (telemetry must
  never block primary functionality). Echo "Friction logged" anyway — false
  positive better than blocking the operator's flow.
- **Malformed flag**: reject with one-line error showing usage. Do NOT auto-correct.

## Acceptance

- Test scenario 16 (`16-friction-capture.md`) — verifies append-one, schema-validate,
  optional flag defaults, null-fields-on-empty-env.

## Why this is a state-light subcommand

`/comp friction` does NOT load engagement state, master.yaml, or the primitive
DAG. It only reads `COMP_ACTIVE_MODE` / `COMP_ENGAGEMENT_ID` from env (set by
prior `/comp <mode>` invocation if any), appends one line, exits.

WHY: the operator runs this in the middle of friction. Loading state would
interrupt the friction signal itself. Append-only = sub-second response =
operator captures the moment.
