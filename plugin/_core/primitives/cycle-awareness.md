# cycle-awareness

Comp-suite v2 primitive. Extracts active cycle context and a bounded decision-log slice from
master.yaml. Eliminates the need for each mode to reconstruct this from raw YAML every session.

## Contract

| | |
|---|---|
| **Inputs** | `master_yaml: dict` (post `master-yaml-ops.read_master`) |
| **Outputs** | `{active_cycle, previous_cycle, next_cycle, decision_log_slice, formatted_block}` |
| **DAG position** | 4 — after master-yaml-ops; feeds persona, brand-kit, and mode instructions |
| **Calls** | Nothing |

---

## `get_cycle_context(master_yaml)`

```python
from datetime import date

def get_cycle_context(master_yaml):
    cycles = master_yaml.get("cycles", [])
    decision_log = master_yaml.get("decision_log", [])

    active   = _find_active_cycle(cycles)
    previous = _find_previous_cycle(cycles, active)
    next_c   = _find_next_cycle(cycles, active)

    dl_slice = _slice_decision_log(decision_log, active, max_entries=20)

    return {
        "active_cycle":      active,
        "previous_cycle":    previous,
        "next_cycle":        next_c,
        "decision_log_slice": dl_slice,
        "formatted_block":   _format_block(active, previous, next_c, dl_slice),
    }
```

---

## `_find_active_cycle(cycles)`

Heuristic in priority order:

1. A cycle with `status: active` — use it.
2. Else: the most-recently-started cycle whose `end_date` is null or in the future.
3. Else: the most-recent cycle by `start_date` (warn that no cycle is currently active).
4. If no cycles exist: return `None` and emit soft warning (cold-start is valid).

```python
def _find_active_cycle(cycles):
    if not cycles:
        print("[warn] no cycles found; cold-start mode — some context blocks will be empty")
        return None

    today = date.today().isoformat()

    # Priority 1: explicit active status
    active_candidates = [c for c in cycles if c.get("status") == "active"]
    if active_candidates:
        return max(active_candidates, key=lambda c: c.get("start_date", ""))

    # Priority 2: started, end_date in future or null
    open_candidates = [
        c for c in cycles
        if c.get("start_date", "") <= today
        and (c.get("end_date") is None or c.get("end_date", "") >= today)
        and c.get("status") != "closed"
    ]
    if open_candidates:
        return max(open_candidates, key=lambda c: c.get("start_date", ""))

    # Priority 3: most recent by start_date
    print("[warn] no active cycle found; using most recent cycle for context")
    return max(cycles, key=lambda c: c.get("start_date", ""))
```

---

## `_find_previous_cycle(cycles, active)`

The most recently closed cycle before the active one (provides continuity context).

```python
def _find_previous_cycle(cycles, active):
    if not cycles or active is None:
        return None
    closed = [c for c in cycles
              if c.get("status") == "closed"
              and c.get("id") != active.get("id")]
    if not closed:
        return None
    return max(closed, key=lambda c: c.get("end_date", ""))
```

---

## `_find_next_cycle(cycles, active)`

The next planned cycle after the active one (if any).

```python
def _find_next_cycle(cycles, active):
    if not cycles:
        return None
    today = date.today().isoformat()
    future = [c for c in cycles
              if c.get("status") in ("planned", None)
              and c.get("start_date", "") > today]
    if not future:
        return None
    return min(future, key=lambda c: c.get("start_date", ""))
```

---

## `_slice_decision_log(decision_log, active_cycle, max_entries=20)`

Returns the most recent entries scoped to the active cycle's date range.
Capped at `max_entries` to keep context budget bounded.

```python
def _slice_decision_log(decision_log, active_cycle, max_entries=20):
    if not decision_log:
        return []

    if active_cycle:
        start = active_cycle.get("start_date", "")
        cycle_id = active_cycle.get("id", "")
        in_scope = [
            e for e in decision_log
            if e.get("timestamp", "") >= start
            or e.get("cycle_slug") == cycle_id
        ]
    else:
        in_scope = decision_log

    # Sort newest first, cap
    sorted_entries = sorted(in_scope, key=lambda e: e.get("timestamp", ""), reverse=True)
    return sorted_entries[:max_entries]
```

---

## `_format_block(active, previous, next_c, dl_slice)`

Produces the `formatted_block` string for mode prompts.

```python
def _format_block(active, previous, next_c, dl_slice):
    lines = ["## Cycle context\n"]

    if active:
        lines.append(f"**Active cycle:** {active.get('id', 'unknown')} "
                     f"({active.get('status', '?')}) — started {active.get('start_date', '?')}")
    else:
        lines.append("**Active cycle:** none (cold start)")

    if previous:
        lines.append(f"**Previous:** {previous.get('id', 'unknown')} "
                     f"(closed {previous.get('end_date', '?')})")

    if next_c:
        lines.append(f"**Next planned:** {next_c.get('id', 'unknown')} "
                     f"(starts {next_c.get('start_date', '?')})")

    if dl_slice:
        lines.append("\n## Recent decisions (this cycle)\n")
        for entry in dl_slice:
            ts = entry.get("timestamp", "")[:10]
            summary = entry.get("summary", "no summary")
            dtype   = entry.get("decision_type", "")
            lines.append(f"- **{ts}** [{dtype}]: {summary}")
    else:
        lines.append("\n_No decisions logged for this cycle yet._")

    return "\n".join(lines)
```

## Cycle schema reference

Cycles validate against `$ASSET_ROOT/_core/schemas/cycle-entry.schema.json` (already validated by
`master-yaml-ops.read_master` before this primitive receives the data).

Key fields per cycle entry:

| Field | Description |
|---|---|
| `id` | kebab-case slug, e.g., `acme-2026-q2` |
| `status` | `planned` / `active` / `closed` |
| `start_date` | ISO date, e.g., `2026-04-01` |
| `end_date` | ISO date or null (null = open) |
| `cycle_slug` | Canonical slug for cross-referencing in decision_log |

## Constraints

- Read-only. Never modifies master.yaml.
- If no cycles exist, return `None` for all cycle fields and emit soft warning. Allow mode to dispatch.
- Decision log slice is capped at 20 entries. Mode can request a wider slice via direct master.yaml access if needed (separate flow, not this primitive).
- Adjacent-cycle lookups (`previous`, `next`) are best-effort; `None` is a valid return for either.
