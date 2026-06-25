# engagement-loader

Comp-suite v2 primitive. Reads and validates an org + engagement. **MCP-primary** (the deployed
`market` server is the source of truth for schema-shaped state), with a **local `$STATE_ROOT`
fallback only on transport failure** (MIM-0041 P4b). The orchestrator calls this at position 1 in
the startup DAG before any other primitive.

## Contract

| | |
|---|---|
| **Inputs** | `org_slug: str`, `engagement_id: str` |
| **Outputs** | `{master, engagement_state, org_slug, engagement_id, local_engagement_dir}` |
| **DAG position** | 1 — root. No dependencies. |
| **Calls** | MCP tools `engagement_get_master`, `engagement_get` (primary); local file reads (fallback only) |

## Source-of-truth posture (P4b)

- **Schema state** (master header / cycles / decision_log / sections, engagement body) is read from the
  `market` MCP server. The org is resolved from the caller's OAuth identity → `colleague_org_membership`
  → `org_id`; pass `org_slug` explicitly (`empire-co`) or omit it to use the default org.
- **Local `$STATE_ROOT` is a read cache**, consulted ONLY when the MCP server is unreachable
  (connection refused, timeout, 5xx, not-yet-authenticated). A tool returning *not-found* is
  authoritative — it means the entity does not exist in the backend, NOT "look on disk."
- **Non-schema artifacts** (deliverables, inputs, rendered decks, cost-log) remain on local disk and are
  surfaced from `$STATE_ROOT` as before (Step 3).

## `load_engagement(org_slug, engagement_id)`

Run in sequence. Stop and escalate on any hard failure.

### Step 1 — Load the master (MCP-primary)

Call the **`engagement_get_master`** MCP tool with `{org_slug}`.

- **Success** → returns `{header, sections, cycles, decision_log}`. This both loads the master AND
  confirms the org exists (membership resolved it). Keep the `header.version` for any later section write.
- **Transport failure** (server unreachable / timeout / 5xx / not authenticated) → **FALLBACK** to the
  local cache, and warn the operator that state is read-only until MCP returns:

  ```python
  import os, yaml
  master_path = f"{STATE_ROOT}/_orgs/{org_slug}/master.yaml"
  if not os.path.exists(master_path):
      escalate(f"MCP unreachable and no local cache for org '{org_slug}'")
  with open(master_path) as f:
      master = yaml.safe_load(f)
  warn("MCP unreachable — master read from local $STATE_ROOT cache. Schema WRITES are blocked "
       "until the market server is reachable (P4b D2: no local-and-reconcile).")
  ```

- **Org not provisioned** (the tool resolves no org for the caller, or returns an empty/`found=false`
  master) → per P4b D4 there is no over-the-wire org-creation tool; escalate, do NOT create locally:

  ```
  escalate(f"org '{org_slug}' is not provisioned in the backend. New-org creation is an admin step "
           "(colleague_org_membership + private.orgs bridge), not a comp-suite operation.")
  ```

### Step 2 — Load the engagement body (MCP-primary)

Call **`engagement_get`** with `{org_slug, engagement_id}`.

- **`found: true`** → the engagement body (schema_version, mode, phase, budget_usd[str], working_artifacts,
  checkpoints, council_topics, pending_decisions, …). Keep its `version` for later optimistic writes.
- **`found: false`** → authoritative: the engagement does not exist in the backend. Escalate
  (`engagement '<id>' not found under org '<slug>'; use the engagement-create primitive`). Do NOT read local.
- **Transport failure** → FALLBACK to `{STATE_ROOT}/_orgs/{org_slug}/engagements/{engagement_id}/engagement-state.yaml`
  (read cache); same read-only warning as Step 1.

### Step 3 — Surface artifact drift (LOCAL — unchanged)

`working_artifacts` are non-schema files on local disk (deliverables, etc.). Check them on `$STATE_ROOT`
exactly as before — these never moved to the backend (P4b D3):

```python
local_dir = f"{STATE_ROOT}/_orgs/{org_slug}/engagements/{engagement_id}"
for artifact in engagement_state.get("working_artifacts", []):
    artifact_path = f"{local_dir}/{artifact['path']}"
    if not os.path.exists(artifact_path):
        warn(f"working artifact not on disk: {artifact['path']} (status: {artifact.get('status')})")
        # Do not fail — /comp doctor is the repair tool
```

### Step 4 — Return context

```python
return {
    "org_slug":          org_slug,
    "engagement_id":     engagement_id,
    "master":            master,              # from engagement_get_master (or local cache fallback)
    "engagement_state":  engagement_state,    # from engagement_get (or local cache fallback)
    "local_engagement_dir": local_dir,        # for downstream LOCAL-artifact primitives only
    "cost_log_path":     f"{local_dir}/cost-log.jsonl",   # local artifact (budget-check)
    "source":            "mcp" | "local-cache",           # which path served the read
}
```

This dict is passed as-is to `master-yaml-ops` (which operates on `master`) and downstream primitives.
Schema state comes from MCP; `local_engagement_dir` / `cost_log_path` are for the stays-local primitives
(budget-check, production-gates, visual-qa) only.

## Engagement ID format

Canonical: `YYYY-Q[1-4]-<slug>` (e.g., `2026-Q2-comp-review`). Alternative: `YYYY-MM-DD-<slug>`.
Enforced server-side and by `engagement-state.schema.json`.

## Error shapes

| Error | Type | Source | Message pattern |
|---|---|---|---|
| Org not provisioned in backend | Hard — escalate | MCP not-found | `"org '<slug>' is not provisioned in the backend. New-org creation is an admin step …"` |
| Engagement not found | Hard — escalate | MCP `found:false` | `"engagement '<id>' not found under org '<slug>'; use the engagement-create primitive"` |
| MCP unreachable, no local cache | Hard — escalate | transport + miss | `"MCP unreachable and no local cache for org '<slug>'"` |
| MCP unreachable, local cache hit | Soft — warn, read-only | transport | `"MCP unreachable — master read from local cache. Schema WRITES blocked …"` |
| Working artifact not on disk | Soft — warn | local | `"working artifact not on disk: <path> (status: <status>)"` |

## Constraints

- Read-only. Never writes. Never creates an org or engagement locally (P4b D4 / D2).
- MCP-primary: a tool *not-found* is authoritative; only a *transport* failure falls back to local cache.
- Schema state (master, engagement body) comes from MCP; local disk is a read cache, never written here.
- Atomic load: either fully loaded (from MCP or, on transport failure, from cache) or escalated.
- master schema validation is delegated to `master-yaml-ops.read_master` (next in DAG); the server already
  validated on write, so client-side validation is a defensive check, not the gate.
