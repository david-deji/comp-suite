# friction-aggregator

Comp-suite v2 primitive. Reads `$STATE_ROOT/harness/friction.jsonl`, groups events by
target, scores each group, and produces a list of concrete-diff `Proposal`s for
founder ratification via `/comp learn`.

> Spec source: `$ASSET_ROOT/SPEC-learn.md` § 7-9. The action-class taxonomy (§ 8) defines the
> diff shapes; the meta-tracking logic (§ 9) defines `would_prevent_signatures`.

## Contract

| | |
|---|---|
| **Inputs** | `since_iso: str` (default = last synthesis ts, or epoch) |
| **Outputs** | `{proposals: List[Proposal], events_read: int, events_skipped: int, meta_findings: List[MetaFinding]}` |
| **DAG position** | Standalone — runs only inside `/comp learn`; never in the per-mode startup DAG |
| **Calls** | Reads `$STATE_ROOT/harness/friction.jsonl`, `$STATE_ROOT/harness/rejected.yaml`, `$STATE_ROOT/harness/applied/*.md`, `$STATE_ROOT/harness/synthesis/*.md` |

Read-only on `friction.jsonl`. No paid tool calls. No subagent dispatch. The aggregator
runs inline in the orchestrator session.

---

## `aggregate(since_iso=None)`

```python
import json, os, hashlib, glob, yaml
from datetime import datetime, timezone

HARNESS_DIR     = f"{STATE_ROOT}/harness"
JSONL           = f"{HARNESS_DIR}/friction.jsonl"
REJECTED_YAML   = f"{HARNESS_DIR}/rejected.yaml"
SYNTHESIS_GLOB  = f"{HARNESS_DIR}/synthesis/*.md"
APPLIED_GLOB    = f"{HARNESS_DIR}/applied/*.md"

# Action-class priority (higher = surfaced first in synthesis).
TARGET_CLASS_PRIORITY = {
    "schema":         100,
    "primitive":       90,
    "hook":            70,
    "reference":       60,
    "intent-router":   55,
    "prompt":          50,
    "perspective":     40,
    "persona":         35,
    "glossary":        30,
    "unspecified":     10,
}

def aggregate(since_iso=None):
    # Step 1 — Resolve since_iso default
    if since_iso is None:
        since_iso = _last_synthesis_ts() or "1970-01-01T00:00:00Z"

    # Step 2 — Read events, validate, filter
    events_read    = 0
    events_skipped = 0
    events         = []
    if not os.path.exists(JSONL):
        return {"proposals": [], "events_read": 0, "events_skipped": 0, "meta_findings": []}
    with open(JSONL) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if not _validate_event_shape(event):
                    events_skipped += 1
                    print(f"[warn] friction.jsonl line {line_num} fails shape check, skipping")
                    continue
                if event["ts"] < since_iso:
                    continue
                events_read += 1
                events.append(event)
            except (json.JSONDecodeError, ValueError) as e:
                events_skipped += 1
                print(f"[warn] friction.jsonl line {line_num} malformed, skipping: {e}")

    # Step 3 — Drop rejected-pattern events
    rejected_sigs = _load_rejected_signatures()
    events = [e for e in events if _event_signature(e) not in rejected_sigs]

    # Step 4 — Group by (target_class, target_path)
    groups = {}
    for e in events:
        key = (e["target_class"], e.get("target_path") or "<unspecified>")
        groups.setdefault(key, []).append(e)

    # Step 5 — Build proposals (only groups with >=2 events, OR single high-impact)
    proposals = []
    for (tcls, tpath), group_events in groups.items():
        if len(group_events) < 2:
            # LOW-confidence single-event proposal only in high-impact areas
            high_impact = (
                tcls in {"primitive", "schema"}
                or any(e.get("severity") == "high" for e in group_events)
            )
            if not high_impact:
                continue
            confidence = "LOW"
        elif len(group_events) >= 3 and _same_signal(group_events):
            confidence = "HIGH"
        else:
            confidence = "MEDIUM"

        # Most common signal type in the group (pattern anchor)
        signal_pattern = _most_common([e["signal_type"] for e in group_events])
        action_class   = _classify_action(tcls, signal_pattern)
        proposal_sig   = _proposal_signature(tcls, tpath, signal_pattern)

        proposals.append({
            "target_class":              tcls,
            "target_path":               tpath if tpath != "<unspecified>" else None,
            "evidence":                  group_events,
            "signal_pattern":            signal_pattern,
            "confidence":                confidence,
            "action_class":              action_class,
            "proposed_diff":             _generate_diff(tcls, tpath, group_events, action_class),
            "signature":                 proposal_sig,
            "would_prevent_signatures":  sorted({_event_signature(e) for e in group_events}),
        })

    # Step 6 — Sort: target_class priority desc, confidence desc, evidence count desc
    confidence_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    proposals.sort(key=lambda p: (
        -TARGET_CLASS_PRIORITY.get(p["target_class"], 0),
        -confidence_rank[p["confidence"]],
        -len(p["evidence"]),
    ))

    # Step 7 — Run meta-tracking pass (closed-loop check on prior applied changes)
    meta_findings = _meta_track(events, since_iso)

    return {
        "proposals":      proposals,
        "events_read":    events_read,
        "events_skipped": events_skipped,
        "meta_findings":  meta_findings,
    }
```

---

## Helpers

### `_validate_event_shape(event) -> bool`

Permissive shape check (full schema validation requires `jsonschema` which is optional):
verify required keys exist, `ts` parses as ISO-8601, `severity` ∈ {low,medium,high},
`source` ∈ {manual,auto,post-session}, `target_class` is a known string, `signal_type`
is non-empty. Returns `False` on any failure (caller skips with warning).

### `_event_signature(event) -> str`

Stable hash of `(signal_type, target_class, target_path)`. Used to:
1. Look up rejected patterns in `rejected.yaml`.
2. Compute `would_prevent_signatures` for each proposal.
3. Detect recurrence in meta-tracking.

```python
def _event_signature(event):
    key = f"{event['signal_type']}|{event['target_class']}|{event.get('target_path') or ''}"
    return hashlib.sha256(key.encode()).hexdigest()[:12]
```

### `_proposal_signature(tcls, tpath, signal_pattern) -> str`

Same shape as event signature but at the group level. Stored in `applied/*.md` and
`rejected.yaml`. The pair `(event_signature, proposal_signature)` powers meta-tracking.

```python
def _proposal_signature(tcls, tpath, signal_pattern):
    key = f"{signal_pattern}|{tcls}|{tpath or ''}"
    return hashlib.sha256(key.encode()).hexdigest()[:12]
```

### `_load_rejected_signatures() -> set[str]`

Reads `rejected.yaml`, returns a set of proposal signatures the founder previously
rejected. Returns empty set if file missing.

```python
def _load_rejected_signatures():
    if not os.path.exists(REJECTED_YAML):
        return set()
    with open(REJECTED_YAML) as f:
        try:
            data = yaml.safe_load(f) or []
        except yaml.YAMLError:
            return set()
    return {entry["signature"] for entry in data if "signature" in entry}
```

### `_last_synthesis_ts() -> str | None`

Reads the most recent `synthesis/*.md` file, parses its frontmatter `next_since_ts:`
field. Returns None if no prior synthesis run.

### `_same_signal(events) -> bool`

Returns True if ≥3 events share the same `signal_type`. Used for HIGH-confidence gating.

### `_most_common(values) -> str`

Standard mode (statistical). Tie-broken by first occurrence.

---

## Action-class classification

`_classify_action(target_class, signal_pattern)` maps the (target_class, signal_pattern)
tuple to one of eight action classes (per SPEC-learn.md § 8):

| target_class | signal_pattern | action_class |
|---|---|---|
| `prompt` | `repeated-clarification` | `PROMPT_EDITS` |
| `prompt` | `askuserquestion-other-longform` | `PROMPT_EDITS` |
| `hook` | `hook-fired-warn` | `HOOK_TUNING` |
| `hook` | `post-session-hook-overridden` | `HOOK_TUNING` |
| `glossary` | (any) | `GLOSSARY_ADDITIONS` |
| `schema` | `post-session-unused-schema-field` | `SCHEMA_DRIFT` |
| `schema` | `schema-validation-failure` | `SCHEMA_DRIFT` |
| `primitive` | `primitive-runtime-error` | `PRIMITIVE_CONTRACT` |
| `primitive` | (other) | `PRIMITIVE_CONTRACT` |
| `intent-router` | `intent-router-low-confidence` | `INTENT_ROUTER_TUNING` |
| `perspective` | `post-session-council-redundancy` | `PERSPECTIVE_REFINEMENT` |
| `persona` | (any) | `PERSPECTIVE_REFINEMENT` |
| `reference` | `post-session-broken-cite` | `REFERENCE_CROSS_LINK` |
| `reference` | (other) | `REFERENCE_CROSS_LINK` |
| `unspecified` | (any) | `PROMPT_EDITS` (default — operator did not classify) |

```python
ACTION_TABLE = {
    ("prompt",        "repeated-clarification"):           "PROMPT_EDITS",
    ("prompt",        "askuserquestion-other-longform"):   "PROMPT_EDITS",
    ("hook",          "hook-fired-warn"):                  "HOOK_TUNING",
    ("hook",          "post-session-hook-overridden"):     "HOOK_TUNING",
    ("schema",        "post-session-unused-schema-field"): "SCHEMA_DRIFT",
    ("schema",        "schema-validation-failure"):        "SCHEMA_DRIFT",
    ("primitive",     "primitive-runtime-error"):          "PRIMITIVE_CONTRACT",
    ("intent-router", "intent-router-low-confidence"):     "INTENT_ROUTER_TUNING",
    ("perspective",   "post-session-council-redundancy"):  "PERSPECTIVE_REFINEMENT",
    ("reference",     "post-session-broken-cite"):         "REFERENCE_CROSS_LINK",
}
CLASS_FALLBACK = {
    "prompt":         "PROMPT_EDITS",
    "hook":           "HOOK_TUNING",
    "glossary":       "GLOSSARY_ADDITIONS",
    "schema":         "SCHEMA_DRIFT",
    "primitive":      "PRIMITIVE_CONTRACT",
    "intent-router":  "INTENT_ROUTER_TUNING",
    "perspective":    "PERSPECTIVE_REFINEMENT",
    "persona":        "PERSPECTIVE_REFINEMENT",
    "reference":      "REFERENCE_CROSS_LINK",
    "unspecified":    "PROMPT_EDITS",
}

def _classify_action(target_class, signal_pattern):
    return ACTION_TABLE.get((target_class, signal_pattern),
                            CLASS_FALLBACK.get(target_class, "PROMPT_EDITS"))
```

---

## Diff generation

`_generate_diff(target_class, target_path, evidence, action_class)` produces a
**concrete-edit description**, not generative prose. The aggregator does not have
the agent-tier authority to apply the edit during synthesis — it writes the
description, the operator ratifies, the orchestrator applies it via `Edit` tool
during `/comp learn` (per SPEC-learn.md § 10).

The function does NOT call any LLM. It assembles a structured edit suggestion from
template strings keyed by action_class. The proposed edit text reads as a
unified-diff-style block:

```
File: <target_path or "(unspecified — operator must locate)">
Edit type: <action_class>
Evidence count: <N> events
Most common signal: <signal_pattern>

Concerns surfaced by evidence:
  - <event 1 description first 80 chars>
  - <event 2 description first 80 chars>
  ...

Suggested edit:
  <action-class-specific template>

Manual step required: review the file at the target path and apply the smallest
edit that addresses ALL evidence events. The operator (during /comp learn
ratification) reviews this proposal and either Accept / Modify / Reject / Defer.
```

Per SPEC-learn.md § 8, action-class-specific templates:

| action_class | Template hint |
|---|---|
| `PROMPT_EDITS` | "Add or sharpen an option in the prompt; quote operator feedback as evidence." |
| `HOOK_TUNING` | "Remove or qualify a never-list term; add an exception path in lib.sh." |
| `GLOSSARY_ADDITIONS` | "Add term + canonical translation; cite where the gap surfaced." |
| `SCHEMA_DRIFT` | "Remove unused field, OR add documentation note explaining when required." |
| `PRIMITIVE_CONTRACT` | "Edit Inputs/Outputs table; add validation; address the surfaced runtime error." |
| `INTENT_ROUTER_TUNING` | "Add a mode-keyword example pattern in intent-router.md." |
| `PERSPECTIVE_REFINEMENT` | "Merge redundant perspectives, OR sharpen each persona's focus field." |
| `REFERENCE_CROSS_LINK` | "Update or remove broken reference; cite file:line." |

```python
TEMPLATE_HINTS = {
    "PROMPT_EDITS":          "Add or sharpen an option in the prompt; quote operator feedback as evidence.",
    "HOOK_TUNING":           "Remove or qualify a never-list term; add an exception path in lib.sh.",
    "GLOSSARY_ADDITIONS":    "Add term + canonical translation; cite where the gap surfaced.",
    "SCHEMA_DRIFT":          "Remove unused field, OR add documentation note explaining when required.",
    "PRIMITIVE_CONTRACT":    "Edit Inputs/Outputs table; add validation; address the surfaced runtime error.",
    "INTENT_ROUTER_TUNING":  "Add a mode-keyword example pattern in intent-router.md.",
    "PERSPECTIVE_REFINEMENT":"Merge redundant perspectives, OR sharpen each persona's focus field.",
    "REFERENCE_CROSS_LINK":  "Update or remove broken reference; cite file:line.",
}

def _generate_diff(tcls, tpath, evidence, action_class):
    lines = []
    lines.append(f"File: {tpath or '(unspecified — operator must locate)'}")
    lines.append(f"Edit type: {action_class}")
    lines.append(f"Evidence count: {len(evidence)} events")
    if evidence:
        sig = evidence[0]['signal_type']
        lines.append(f"Most common signal: {sig}")
    lines.append("")
    lines.append("Concerns surfaced by evidence:")
    for e in evidence[:5]:  # cap at 5 for readability
        d = e["description"][:80]
        lines.append(f"  - [{e['ts']}] {d}")
    if len(evidence) > 5:
        lines.append(f"  - ... ({len(evidence) - 5} more events not shown)")
    lines.append("")
    lines.append("Suggested edit:")
    lines.append(f"  {TEMPLATE_HINTS.get(action_class, 'Apply minimal edit addressing all evidence.')}")
    lines.append("")
    lines.append("Manual step required: review the file at the target path and apply the smallest")
    lines.append("edit that addresses ALL evidence events.")
    return "\n".join(lines)
```

---

## Meta-tracking pass

`_meta_track(new_events, since_iso)` reads previous applied/*.md records, looks for
recurrence of `would_prevent_signatures`, returns findings.

```python
def _meta_track(new_events, since_iso):
    findings = []
    new_event_sigs = {_event_signature(e) for e in new_events}
    for applied_file in sorted(glob.glob(APPLIED_GLOB)):
        applied_records = _parse_applied_file(applied_file)
        for record in applied_records:
            applied_at = record.get("applied_at", "")
            if applied_at < since_iso:
                # Predates this run's window — already surfaced (or won't be)
                continue
            recurred = set(record.get("would_prevent_signatures", [])) & new_event_sigs
            if recurred:
                findings.append({
                    "applied_at":          applied_at,
                    "target_path":         record.get("target_path"),
                    "diff_summary":        record.get("diff_summary"),
                    "recurred_signatures": sorted(recurred),
                    "severity":            "MEDIUM",
                    "message": (
                        f"Applied change at {record.get('target_path')} ({applied_at}) "
                        f"claimed to prevent {len(record.get('would_prevent_signatures', []))} "
                        f"signature(s). {len(recurred)} recurred. Revisit the diff."
                    ),
                })
    return findings
```

---

## Output shape

On success:

```python
{
  "proposals": [
    {
      "target_class": "primitive",
      "target_path":  "_core/primitives/mode-dispatcher.md",
      "evidence":     [<3 events>],
      "signal_pattern": "primitive-runtime-error",
      "confidence":   "HIGH",
      "action_class": "PRIMITIVE_CONTRACT",
      "proposed_diff": "<concrete edit block>",
      "signature":    "a1b2c3d4e5f6",
      "would_prevent_signatures": ["xyz...", "abc..."],
    },
    # ...
  ],
  "events_read":    14,
  "events_skipped": 0,
  "meta_findings": [
    {
      "applied_at": "2026-05-08T16:00:00Z",
      "target_path": "_core/primitives/mode-dispatcher.md",
      "diff_summary": "Add MCP liveness probe with 3s timeout",
      "recurred_signatures": ["xyz..."],
      "severity": "MEDIUM",
      "message": "Applied change ... 1 recurred. Revisit the diff.",
    },
  ],
}
```

On no events / threshold-fail (caller `/comp learn` enforces threshold; aggregator
just returns empty proposals):

```python
{"proposals": [], "events_read": 0, "events_skipped": 0, "meta_findings": []}
```

---

## Constraints

- Read-only on `friction.jsonl`. Never mutates or rotates.
- No paid tool calls. No subagent dispatch.
- Malformed lines are warn-skipped (same tolerance as `budget-check._sum_cost_log`).
  A corrupted line must not lock out the loop.
- Diff generation is deterministic templating, NOT generative LLM rewriting (per
  SPEC-learn.md § 8 founder direction: "proposed edits are concrete diffs from
  operator feedback, not generative 'improve this prompt' calls").
- Cross-session caching is not acceptable; aggregation runs fresh on every
  `/comp learn` invocation.
