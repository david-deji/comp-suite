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

1. The cycle with `primary: true` — the server's active-cycle pointer (exactly one per org, § 4.3 C3). Use it.
2. Else: the most-recently-opened in-flight cycle (any `status` other than `closed`).
3. Else: the most-recent cycle by `opened_date` (warn that no cycle is currently active).
4. If no cycles exist: return `None` and emit soft warning (cold-start is valid).

```python
def _find_active_cycle(cycles):
    if not cycles:
        print("[warn] no cycles found; cold-start mode — some context blocks will be empty")
        return None

    # Priority 1: the primary cycle — the server's active-cycle pointer (exactly one per org)
    primary_candidates = [c for c in cycles if c.get("primary") is True]
    if primary_candidates:
        return max(primary_candidates, key=lambda c: c.get("opened_date", ""))

    # Priority 2: most-recently-opened in-flight cycle (status not closed)
    open_candidates = [c for c in cycles if c.get("status") != "closed"]
    if open_candidates:
        return max(open_candidates, key=lambda c: c.get("opened_date", ""))

    # Priority 3: most recent by opened_date
    print("[warn] no primary or in-flight cycle found; using most recent cycle for context")
    return max(cycles, key=lambda c: c.get("opened_date", ""))
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
              and c.get("cycle_slug") != active.get("cycle_slug")]
    if not closed:
        return None
    return max(closed, key=lambda c: c.get("closed_date") or "")
```

---

## `_find_next_cycle(cycles, active)`

The next in-flight cycle opened after the active one (if any). There is no `planned` status in
the real state machine (`open → drafting → shipped → closed`), so "next" is the earliest-opened
non-closed cycle whose `opened_date` is after the active cycle's.

```python
def _find_next_cycle(cycles, active):
    if not cycles or active is None:
        return None
    active_opened = active.get("opened_date", "")
    later = [c for c in cycles
             if c.get("status") != "closed"
             and c.get("cycle_slug") != active.get("cycle_slug")
             and c.get("opened_date", "") > active_opened]
    if not later:
        return None
    return min(later, key=lambda c: c.get("opened_date", ""))
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
        start      = active_cycle.get("opened_date", "")
        cycle_slug = active_cycle.get("cycle_slug", "")
        in_scope = [
            e for e in decision_log
            if e.get("cycle_slug") == cycle_slug
            or (start and e.get("timestamp", "") >= start)
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
        lines.append(f"**Active cycle:** {active.get('cycle_slug', 'unknown')} "
                     f"({active.get('status', '?')}) — opened {active.get('opened_date', '?')}")
    else:
        lines.append("**Active cycle:** none (cold start)")

    if previous:
        lines.append(f"**Previous:** {previous.get('cycle_slug', 'unknown')} "
                     f"(closed {previous.get('closed_date', '?')})")

    if next_c:
        lines.append(f"**Next:** {next_c.get('cycle_slug', 'unknown')} "
                     f"(opened {next_c.get('opened_date', '?')})")

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
| `cycle_slug` | kebab-case slug, e.g., `pharmacy-qc-fy26`; unique per org; the join key against `decision_log[].cycle_slug` |
| `status` | `open` / `drafting` / `shipped` / `closed` (§ 4.3 state machine) |
| `opened_date` | ISO date the cycle was created, e.g., `2026-04-01` |
| `closed_date` | ISO date, or null when the cycle is not yet closed |
| `primary` | Boolean — exactly one cycle per org is `primary: true`; the active-cycle pointer |

## Constraints

- Read-only. Never modifies master.yaml.
- If no cycles exist, return `None` for all cycle fields and emit soft warning. Allow mode to dispatch.
- Decision log slice is capped at 20 entries. Mode can request a wider slice via direct master.yaml access if needed (separate flow, not this primitive).
- Adjacent-cycle lookups (`previous`, `next`) are best-effort; `None` is a valid return for either.
