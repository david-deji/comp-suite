# engagement-loader

Comp-suite v2 primitive. Reads and validates an org + engagement from the local filesystem.
The orchestrator calls this at position 1 in the startup DAG before any other primitive.

## Contract

| | |
|---|---|
| **Inputs** | `org_slug: str`, `engagement_id: str` |
| **Outputs** | `{master_yaml_path, engagement_state_path, org_slug, engagement_id}` |
| **DAG position** | 1 — root. No dependencies. |
| **Calls** | `master-yaml-ops.find_or_create_org` (when org is new), `master-yaml-ops.read_master` (delegated) |

## `load_engagement(org_slug, engagement_id)`

Run this procedure in sequence. Stop and escalate on any hard failure.

### Step 1 — Resolve paths

```python
import os, yaml

# STATE_ROOT is injected by the orchestrator (SKILL.md Step 0); assume it is in scope.

master_path   = f"{STATE_ROOT}/_orgs/{org_slug}/master.yaml"
state_path    = f"{STATE_ROOT}/_orgs/{org_slug}/engagements/{engagement_id}/engagement-state.yaml"
cost_log_path = f"{STATE_ROOT}/_orgs/{org_slug}/engagements/{engagement_id}/cost-log.jsonl"
```

### Step 2 — Validate org exists

```python
index_path = f"{STATE_ROOT}/_orgs/index.yaml"

if not os.path.exists(index_path):
    # Bootstrap case — no orgs yet
    escalate("no orgs index found; call master-yaml-ops.find_or_create_org first")

with open(index_path) as f:
    index = yaml.safe_load(f)

known_slugs = [o["org_slug"] for o in index.get("orgs", [])]
if org_slug not in known_slugs:
    escalate(f"org '{org_slug}' not in index.yaml; call master-yaml-ops.find_or_create_org")
```

### Step 3 — Validate master.yaml exists

```python
if not os.path.exists(master_path):
    escalate(f"master.yaml missing for org '{org_slug}'; re-run find_or_create_org")
```

### Step 4 — Validate engagement-state.yaml exists

```python
if not os.path.exists(state_path):
    escalate(f"engagement '{engagement_id}' not found under org '{org_slug}'; "
             "use orchestrator engagement-creation flow to create it")
```

### Step 5 — Parse engagement-state.yaml

```python
with open(state_path) as f:
    try:
        engagement_state = yaml.safe_load(f)
    except yaml.YAMLError as e:
        escalate(f"YAML parse error in engagement-state.yaml: {e}")
```

### Step 6 — Surface drift warnings (non-fatal)

```python
for artifact in engagement_state.get("working_artifacts", []):
    artifact_path = f"{STATE_ROOT}/_orgs/{org_slug}/engagements/{engagement_id}/{artifact['path']}"
    if not os.path.exists(artifact_path):
        warn(f"working artifact not on disk: {artifact['path']} (status: {artifact.get('status')})")
        # Do not fail — /comp doctor is the repair tool
```

### Step 7 — Return context

```python
return {
    "org_slug":              org_slug,
    "engagement_id":         engagement_id,
    "master_yaml_path":      master_path,
    "engagement_state_path": state_path,
    "cost_log_path":         cost_log_path,
    "engagement_state":      engagement_state,
}
```

This dict is passed as-is to `master-yaml-ops.read_master` and downstream primitives.

## Engagement ID format

Canonical format: `YYYY-Q[1-4]-<slug>` (e.g., `2026-Q2-comp-review`).
Alternative accepted: `YYYY-MM-DD-<slug>` (e.g., `2026-05-07-market-refresh`).
Enforced by `engagement-state.schema.json` `engagement_id` pattern field.

## Error shapes

| Error | Type | Message pattern |
|---|---|---|
| Org not in index | Hard — escalate | `"org '<slug>' not in index.yaml; ..."` |
| master.yaml missing | Hard — escalate | `"master.yaml missing for org '<slug>'; ..."` |
| Engagement not found | Hard — escalate | `"engagement '<id>' not found under org '<slug>'; ..."` |
| YAML parse failure | Hard — escalate | `"YAML parse error in engagement-state.yaml: <detail>"` |
| Working artifact not on disk | Soft — warn | `"working artifact not on disk: <path> (status: <status>)"` |

## Constraints

- Read-only. Never writes files, never creates directories.
- Engagement creation is orchestrator-driven; escalate to it, do not inline-create.
- Returns paths alongside data so downstream writers know where to land changes without re-computing paths.
- Atomic load: either fully loaded or escalated. Never returns partial context.
- Schema validation of master.yaml content is delegated to `master-yaml-ops.read_master` (called next in DAG).
