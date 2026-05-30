# budget-check

Comp-suite v2 primitive. Pre-call gate that prevents tool dispatches from exceeding the
per-engagement cost budget. Runs before every tool call with `est_call_cost_usd > 0`.

> Discipline source: `$ASSET_ROOT/_core/policies/cost-discipline.md`. The "cap experiments before
> starting" musts and "never run open-ended retry loops against a paid API" must-nots
> are operationalized here; the policy file is the rationale.

## Contract

| | |
|---|---|
| **Inputs** | `engagement_state: dict`, `tool_name: str`, `est_cost: float` |
| **Outputs** | `{allow: bool, reason: str}` or `{allow: bool, reason: str, requires_user_confirm: bool}` |
| **DAG position** | 7 — last in startup DAG; then re-runs before every paid tool dispatch |
| **Calls** | Reads `cost-log.jsonl` (local FS), reads tool entry from `$ASSET_ROOT/_core/tools/registry.yaml` |

The primitive is a read-only gate. It never writes to cost-log.
The orchestrator owns the cost-log append after a successful tool call.

---

## `check_budget(engagement_state, tool_name, est_cost)`

```python
import json, os, yaml

COST_LOG_DIR_TEMPLATE = f"{STATE_ROOT}/_orgs/{{org_slug}}/engagements/{{engagement_id}}"
DEFAULT_BUDGET_USD    = 5.00

def check_budget(engagement_state, tool_name, est_cost):
    # Step 1 — Look up tool registry entry
    tool_entry = _get_tool_entry(tool_name)
    if tool_entry is None:
        return {"allow": False, "reason": f"tool '{tool_name}' not found in registry"}

    # Step 2 — Free-tier short-circuit (est_call_cost_usd == 0)
    if tool_entry.get("est_call_cost_usd", 0.0) == 0.0:
        return {"allow": True, "reason": "free tier"}

    # Step 3 — Read engagement budget
    budget = float(engagement_state.get("budget_usd", DEFAULT_BUDGET_USD))

    # Step 4 — Sum existing spend from cost-log.jsonl
    org_slug      = engagement_state.get("org_slug", "")
    engagement_id = engagement_state.get("engagement_id", "")
    spent = _sum_cost_log(org_slug, engagement_id)

    # Step 5 — Budget check
    would_be_total = spent + est_cost
    if would_be_total > budget:
        return {
            "allow":  False,
            "reason": (
                f"budget exceeded: spent ${spent:.2f} of ${budget:.2f} budget; "
                f"this call would add ${est_cost:.2f} (total ${would_be_total:.2f})"
            ),
        }

    # Step 6 — Within budget; check requires_user_confirm
    if tool_entry.get("requires_user_confirm", False):
        return {
            "allow":                True,
            "reason":               f"within budget (${spent:.2f} / ${budget:.2f}); user confirmation required",
            "requires_user_confirm": True,
            "spent":                spent,
            "budget":               budget,
            "est_cost":             est_cost,
        }

    return {"allow": True, "reason": f"within budget (${spent:.2f} / ${budget:.2f})"}
```

---

## Cost-log reading: `_sum_cost_log(org_slug, engagement_id)`

```python
def _sum_cost_log(org_slug, engagement_id):
    cost_log_path = (
        f"{STATE_ROOT}/_orgs/{org_slug}/engagements/{engagement_id}/cost-log.jsonl"
    )

    if not os.path.exists(cost_log_path):
        return 0.0

    total = 0.0
    with open(cost_log_path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                total += float(entry.get("est_cost", 0.0))
            except (json.JSONDecodeError, ValueError) as e:
                # Malformed line: warn, skip, continue — do not lock out the engagement
                print(f"[warn] cost-log.jsonl line {line_num} malformed, skipping: {e}")

    return total
```

---

## Tool registry lookup: `_get_tool_entry(tool_name)`

```python
def _get_tool_entry(tool_name):
    with open(f"{ASSET_ROOT}/_core/tools/registry.yaml") as f:
        registry = yaml.safe_load(f)
    return registry.get("tools", {}).get(tool_name)
```

---

## Orchestrator responsibilities (not this primitive)

After a tool call completes, the orchestrator (not budget-check) appends one line to `cost-log.jsonl`:

```json
{"ts": "2026-05-07T15:42:18Z", "tool": "perplexity-research", "est_cost": 0.30, "mode": "advisor", "task": "research", "rationale": "market benchmarks for sector X"}
```

The append happens as the **last step** of the tool dispatch — never before the call, never on refusal.
JSONL is append-safe: one JSON object per line, `open(path, "a")` for appends.

---

## User confirmation prompt (when `requires_user_confirm: true`)

When this primitive returns `requires_user_confirm: true`, the orchestrator surfaces:

```
Tool: <tool_name>
Estimated cost: $<est_cost>
Spent so far: $<spent> / $<budget>
Reason: <rationale provided by mode>

Proceed? [y/N]
```

A **YES** response: orchestrator proceeds with the tool call, then appends the standard cost-log line.

A **NO** response: orchestrator logs a declined-dispatch entry in cost-log.jsonl:

```json
{"ts": "...", "tool": "<name>", "est_cost": 0.00, "mode": "...", "task": "...", "rationale": "user declined"}
```

`est_cost: 0.00` on declined entries so the declined call does not inflate the spend total.

---

## Atomicity guarantee (scenario 10)

A refused dispatch writes **zero bytes** to `cost-log.jsonl`. Specifically:

- `allow: false` (budget exceeded) → primitive returns immediately, no I/O.
- `requires_user_confirm: true` + user says NO → orchestrator writes the 0.00 declined entry, which does not affect the budget calculation (since `_sum_cost_log` sums `est_cost`, not entry count).

The holdout-C acceptance test verifies: engagement with `budget_usd: 0.50`, $0.40 already logged, `perplexity-research` ($0.30 est) is refused. Cost-log unchanged after refusal.

---

## Engagement cost summary (surfaced by orchestrator)

At `/comp resume` and `/comp doctor`, the orchestrator calls `_sum_cost_log` directly and formats:

```
Engagement: <org_slug>/<engagement_id>
Spent: $<spent> / $<budget> (<pct>% of budget)
Last activity: <last ts from cost-log.jsonl>
```

## Constraints

- Pre-call gate only. Read-only on engagement-state, registry, and cost-log.
- `_sum_cost_log` is tolerant of malformed lines (warn + skip); a corrupted log line must not lock out the engagement.
- `budget_usd` defaults to `5.00` if not set in engagement-state.yaml.
- This primitive does not write; the orchestrator owns all cost-log appends.
