# mode-dispatcher

Comp-suite v2 primitive. Validates a mode manifest and resolves tools + per-task model routing.
Runs on every `/comp` invocation. Never mutates manifests or registries.

> Routing precedence + named-Opus-trigger heuristics: `$ASSET_ROOT/_core/policies/skill-routing-comp.md`.
> The taxonomy in `$ASSET_ROOT/_core/routing.yaml` is the default layer; the policy file describes
> when to escalate UP from sonnet via the named triggers, and when to route DOWN to haiku.

## Contract

| | |
|---|---|
| **Inputs** | `mode_name: str` |
| **Outputs** | `{mode: dict, tools: list[dict], model_routing: dict}` or `{error: str, available: list[str]}` |
| **DAG position** | 6 — after persona + brand-kit; feeds budget-check |
| **Calls** | Reads `$ASSET_ROOT/_modes/*/mode.yaml`, `$ASSET_ROOT/_core/tools/registry.yaml`, `$ASSET_ROOT/_core/routing.yaml`, `$ASSET_ROOT/_core/model-registry.md` |

---

## `dispatch_mode(mode_name)`

```python
import os, glob, yaml

def dispatch_mode(mode_name):
    # Step 1 — Resolve mode directory
    mode_dir = f"{ASSET_ROOT}/_modes/{mode_name}"
    if not os.path.isdir(mode_dir):
        available = [os.path.basename(d) for d in glob.glob(f"{ASSET_ROOT}/_modes/*/") if os.path.isdir(d)]
        return {
            "error":     f"mode '{mode_name}' not found",
            "available": sorted(available),
        }

    # Step 2 — Load and parse mode.yaml
    mode_yaml_path = f"{mode_dir}/mode.yaml"
    with open(mode_yaml_path) as f:
        try:
            mode = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return {"error": f"mode.yaml parse error: {e}"}

    # Step 3 — Validate required fields
    required_fields = [
        "name", "display_name", "description", "version", "model",
        "tools_required", "hooks_enabled", "master_yaml_section",
        "schema", "references", "templates",
    ]
    missing = [f for f in required_fields if f not in mode]
    if missing:
        return {"error": f"mode.yaml missing required fields: {missing}"}

    # Step 4 — Confirm name matches directory
    if mode["name"] != mode_name:
        return {
            "error": (f"mode.yaml name '{mode['name']}' does not match "
                      f"directory name '{mode_name}'")
        }

    # Step 5 — Validate master_yaml_section uniqueness
    section_collision = _check_section_collision(mode_name, mode["master_yaml_section"])
    if section_collision:
        return {"error": section_collision}

    # Step 6 — Resolve tools
    tools_result = _resolve_tools(mode.get("tools_required", []))
    if "error" in tools_result:
        return tools_result

    # Step 7 — Resolve per-task model routing
    model_routing = _resolve_model_routing(mode)

    return {
        "mode":          mode,
        "tools":         tools_result["tools"],
        "model_routing": model_routing,
    }
```

---

## Tool resolution: `_resolve_tools(tools_required)`

```python
def _resolve_tools(tools_required):
    with open(f"{ASSET_ROOT}/_core/tools/registry.yaml") as f:
        registry = yaml.safe_load(f)

    tool_defs = registry.get("tools", {})
    resolved  = []
    missing   = []

    for tool_name in tools_required:
        if tool_name not in tool_defs:
            missing.append(tool_name)
        else:
            resolved.append({"name": tool_name, **tool_defs[tool_name]})

    if missing:
        return {"error": f"tools not in registry: {missing}"}

    # Check MCP server availability for mcp-kind tools
    mcp_servers = registry.get("mcp_servers", {})
    unavailable = []
    for tool in resolved:
        if tool.get("kind") == "mcp":
            server = tool.get("server")
            if server and not _mcp_server_available(server, mcp_servers):
                unavailable.append({"tool": tool["name"], "server": server})

    if unavailable:
        # Surface clean error for scenario 13 (mcp-server-unavailable).
        # The one REQUIRED server is `market` (OAuth — Google sign-in, no token). Perplexity is
        # optional — it is not in any mode's tools_required, so it never lands here; its
        # absence degrades silently to the web-search builtin (registry: web-search).
        return {
            "error": "MCP servers unavailable",
            "unavailable_tools": unavailable,
            "message": (
                "The market MCP is not responding. It authenticates via OAuth (Google "
                "sign-in — no token); run /mcp in Claude Code to confirm the `market` server "
                "is connected and authorized, and check https://mcp.dallaire-jette.com is "
                "reachable. See INSTALL.md. Market-dependent work (benchmarks, offer "
                "comparisons, CBA scales) is unavailable until it is restored; web research "
                "still works via WebSearch."
            ),
        }

    return {"tools": resolved}


def _mcp_server_available(server_name, mcp_servers):
    # Optimistic: assume available if no liveness check is defined.
    # The orchestrator's startup validation (not this primitive) does the real ping.
    # Return True here; unavailability is surfaced at the actual dispatch call.
    return True
```

---

## Model routing: `_resolve_model_routing(mode)`

Per SPEC § 7 precedence: mode override > task default > global default.

```python
def _resolve_model_routing(mode):
    with open(f"{ASSET_ROOT}/_core/routing.yaml") as f:
        routing = yaml.safe_load(f)

    task_defaults  = routing.get("tasks", {})
    global_default = routing.get("default", "sonnet")
    mode_overrides = mode.get("model", {}).get("overrides", {})

    model_registry = _read_model_registry()

    result = {}
    all_tasks = set(list(task_defaults.keys()) + list(mode_overrides.keys()))

    for task in all_tasks:
        # Precedence: mode override > task default > global default
        if task in mode_overrides:
            series = mode_overrides[task]
        elif task in task_defaults:
            series = task_defaults[task]
        else:
            series = global_default

        model_id = model_registry.get(series, series)
        result[task] = {"series": series, "model_id": model_id}

    # Always include default resolution
    default_series = mode.get("model", {}).get("default", global_default)
    result["_default"] = {
        "series":   default_series,
        "model_id": model_registry.get(default_series, default_series),
    }

    return result


def _read_model_registry():
    """
    Reads $ASSET_ROOT/_core/model-registry.md and returns {series: model_id}.
    Parses the 'Latest validated per series' table.
    Initial values per SPEC § 7:
      opus   → claude-opus-4-6
      sonnet → claude-sonnet-4-6
      haiku  → claude-haiku-4-5-20251001
    """
    HARDCODED_INITIAL = {
        "opus":   "claude-opus-4-6",
        "sonnet": "claude-sonnet-4-6",
        "haiku":  "claude-haiku-4-5-20251001",
    }
    # Parse the registry markdown table if it exists; fall back to initial values
    registry_path = f"{ASSET_ROOT}/_core/model-registry.md"
    if not os.path.exists(registry_path):
        return HARDCODED_INITIAL

    with open(registry_path) as f:
        content = f.read()

    result = dict(HARDCODED_INITIAL)
    for line in content.splitlines():
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 3 and parts[0].lower() in ("opus", "sonnet", "haiku"):
            series   = parts[0].lower()
            model_id = parts[2].strip("`")
            if model_id.startswith("claude-"):
                result[series] = model_id

    return result
```

---

## Section collision check: `_check_section_collision(mode_name, section_name)`

No two modes may write the same master.yaml section. This would corrupt the federated write model.

```python
def _check_section_collision(mode_name, section_name):
    for path in glob.glob(f"{ASSET_ROOT}/_modes/*/mode.yaml"):
        other_name = os.path.basename(os.path.dirname(path))
        if other_name == mode_name:
            continue
        with open(path) as f:
            other = yaml.safe_load(f)
        if other.get("master_yaml_section") == section_name:
            return (
                f"master_yaml_section '{section_name}' is already claimed by mode '{other_name}'. "
                "Each mode must declare a unique section."
            )
    return None
```

---

## Output shape

On success:

```python
{
  "mode": {
    "name": "advisor",
    "display_name": "Compensation Advisor",
    # ... full mode.yaml content
  },
  "tools": [
    {"name": "web-search", "kind": "builtin", "est_call_cost_usd": 0.00, ...},
    {"name": "market-data", "kind": "mcp", "server": "market",
     "est_call_cost_usd": 0.00, "requires_user_confirm": False, ...},
    # ...
  ],
  "model_routing": {
    "council":      {"series": "opus",   "model_id": "claude-opus-4-6"},
    "synthesis":    {"series": "opus",   "model_id": "claude-opus-4-6"},
    "extraction":   {"series": "haiku",  "model_id": "claude-haiku-4-5-20251001"},
    "draft":        {"series": "sonnet", "model_id": "claude-sonnet-4-6"},
    "_default":     {"series": "sonnet", "model_id": "claude-sonnet-4-6"},
  }
}
```

On mode not found (scenario 14):

```python
{
  "error": "mode 'totallybogus' not found",
  "available": ["advisor", "comms", "training", "transformer"]
}
```

## Constraints

- Read-only. Never mutates mode.yaml, routing.yaml, or registry.yaml.
- Validation runs on every dispatch; session-level caching is acceptable, cross-session caching is not.
- Glob discovery for section collision check uses `glob.glob(f"{ASSET_ROOT}/_modes/*/mode.yaml")` — same pattern as master-yaml-ops. No hardcoded list.
- Model series → model_id resolution reads `$ASSET_ROOT/_core/model-registry.md` as the source of truth; initial fallbacks are hardcoded only as bootstrap guard.
- Returns both `series` (alias) and `model_id` (resolved version) so callers can audit model selection.
