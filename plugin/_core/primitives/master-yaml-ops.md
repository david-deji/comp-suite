# master-yaml-ops

Comp-suite v2 primitive. All access to the org **master** flows through these functions. Under P4b the
master is **backend state served by the `market` MCP server** — `read_master` reads it via
`engagement_get_master`; section and decision writes go through `engagement_put_section` /
`engagement_append_decision`. No primitive writes `master.yaml` on disk anymore; local `master.yaml` is a
read cache used only when the MCP server is unreachable (MIM-0041 P4b D1/D2).

## Contract

| | |
|---|---|
| **Inputs** | Varies per function — see signatures below |
| **Outputs** | Validated dict, void, or error list |
| **DAG position** | 2 — consumes engagement-loader output; feeds all other primitives |
| **Functions** | `find_or_create_org`, `read_master`, `write_master_section`, `append_decision_log`, `walk_sibling_assets`, `render_tree_view` |

Schema files remain at `$ASSET_ROOT/_core/schemas/` for client-side defensive validation; the server is
the authoritative validator on write.

---

## `find_or_create_org(slug)` — READ via MCP; CREATE is admin-path (P4b D4)

There is no over-the-wire org-creation tool. `engagement_get_master` resolves an existing org (the caller's
OAuth identity → `colleague_org_membership` → `org_id`). A new org is provisioned by an admin bridge
(`private.orgs` + a membership row), NOT by comp-suite.

```
1. Call engagement_get_master with {org_slug: slug}.
   - Success → the org exists; return its header (slug, display_name, industry, …).
   - not-found / no org resolved → escalate:
       "org '<slug>' is not provisioned in the backend. New-org creation is an admin step
        (private.orgs + colleague_org_membership bridge), not a comp-suite operation.
        Provision the org and a membership row, then retry."
   - transport failure → FALLBACK: read $STATE_ROOT/_orgs/index.yaml + master.yaml (read cache);
     warn that the org view is from local cache and writes are blocked until MCP returns.
```

Do NOT create `index.yaml`, the org dir, or a `master.yaml` skeleton locally — that would create an org
the backend does not know about (divergence, the exact failure P4a's import ended).

---

## `read_master(org_slug)` — MCP-primary

Returns `{data}` (header + sections + cycles + decision_log) or `{data, validation_errors, read_only}`.

```
1. Call engagement_get_master with {org_slug}.
   - Success → assemble {data: {header, <sections>, cycles, decision_log}}.
     Keep header.version and each section's version for later optimistic writes.
   - transport failure → FALLBACK to local cache:
```

```python
import yaml, os
def _read_master_local(org_slug):
    master_path = f"{STATE_ROOT}/_orgs/{org_slug}/master.yaml"
    if not os.path.exists(master_path):
        return {"error": f"MCP unreachable and no local cache for org '{org_slug}'"}
    with open(master_path) as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return {"error": f"local cache YAML parse failure: {e}"}
    if data is None:
        return {"error": "local master cache is empty"}
    return {"data": data, "source": "local-cache", "read_only": True}
```

Client-side schema validation (`_validate` against `$ASSET_ROOT/_core/schemas/*.json`) is OPTIONAL and
defensive — the server validated on write. Run it only when debugging suspected drift; never block a read
on it.

---

## `write_master_section(org_slug, section_name, section_data)` — MCP-only (P4b D2)

Sections are one of `advisor / comms / training / transformer`. Optimistic concurrency: read the section's
current version, write with `expected_version`, and on a stale-reject **re-read and retry** — never force,
never write a local copy.

```
1. (defensive) validate section_data client-side against the mode's declared schema; on failure raise
   ValueError with the errors. The server re-validates.
2. Read the current version:
     m = engagement_get_master(org_slug)
     current = m.sections[section_name]                 # may be absent
     expected_version = current.version if present else 0
3. Call engagement_put_section with {org_slug, section_name, body: section_data, expected_version}.
   - Success → done.
   - stale-version reject → re-read (step 2) and retry ONCE; if it rejects again, escalate
     "concurrent writer on section '<name>'; re-run after the other session finishes".
   - transport failure → ESCALATE (do NOT write local):
       "MCP unreachable — cannot write section '<name>'. Schema writes require the backend (P4b D2).
        Retry when the market server is reachable."
```

There is no `$STATE_ROOT/_orgs/<slug>/master.yaml` write here anymore. The server owns the master;
local schema writes are forbidden (they would diverge from the backend).

---

## `append_decision_log(org_slug, entry)` — MCP-only, idempotent

```
1. (defensive) validate entry client-side against decision-log-entry.schema.json.
2. Call engagement_append_decision with:
     {org_slug, timestamp, skill, decision_type, summary,
      cycle_slug (or null), tags (list), id (optional), refs (optional)}.
   - The server is append-only and idempotent on id (assigns the next monotonic dl-NNN per org when id
     is omitted). Re-running after a crash is safe — a duplicate id is a no-op server-side.
   - transport failure → ESCALATE (do NOT write local): same message as write_master_section.
```

Omit `id` to let the server assign the next `dl-NNN`; pass an explicit `id` only when re-driving a known
entry idempotently.

---

## `walk_sibling_assets(org_slug, engagement_id)` — LOCAL (unchanged, P4b D3)

Walks the engagement directory tree for **non-schema artifacts** (inputs, deliverables, per-mode scratch).
These never moved to the backend — they stay on `$STATE_ROOT`. Verbatim from pre-P4b.

```python
import os
import glob as _glob
from datetime import datetime

def _discover_asset_dirs():
    static = ["inputs", "deliverables"]
    mode_dirs = sorted(
        os.path.basename(p.rstrip("/"))
        for p in _glob.glob(f"{ASSET_ROOT}/_modes/*/")
        if os.path.isfile(os.path.join(p, "mode.yaml"))
    )
    return static + mode_dirs

def walk_sibling_assets(org_slug, engagement_id):
    base = f"{STATE_ROOT}/_orgs/{org_slug}/engagements/{engagement_id}"
    results = []
    for dir_name in _discover_asset_dirs():
        dir_path = os.path.join(base, dir_name)
        if not os.path.isdir(dir_path):
            continue
        for root, _, files in os.walk(dir_path):
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                rel   = os.path.relpath(fpath, base)
                mtime = os.path.getmtime(fpath)
                results.append({
                    "path":          rel,
                    "kind":          dir_name,
                    "last_modified": datetime.utcfromtimestamp(mtime).strftime("%Y-%m-%dT%H:%M:%SZ"),
                })
    return results
```

---

## `render_tree_view(asset_walk_result)` — LOCAL (unchanged)

Produces a human-readable markdown block from `walk_sibling_assets` output.

```python
def render_tree_view(asset_walk_result):
    from collections import defaultdict
    import os
    by_kind = defaultdict(list)
    for asset in asset_walk_result:
        by_kind[asset["kind"]].append(asset)
    lines = ["### Engagement assets\n"]
    for kind, items in sorted(by_kind.items()):
        if not items:
            lines.append(f"  {kind}/  (empty)")
        else:
            lines.append(f"  {kind}/")
            for item in items:
                fname = os.path.basename(item["path"])
                lines.append(f"    ├── {fname}  ({item['last_modified'][:10]})")
    return "\n".join(lines)
```

## Constraints

- **No schema-state write touches `$STATE_ROOT`** (P4b D2). Master, sections, decisions, cycles, brand,
  costing are MCP-only. Local schema files are a read cache (transport-failure fallback) only.
- MCP-primary reads: a tool *not-found* is authoritative; only a *transport* failure falls back to cache.
- Optimistic writes thread `version → expected_version`; stale-reject → re-read-retry once, then escalate.
- `append_decision_log` is idempotent on `id` server-side — safe to re-run after a crash.
- `walk_sibling_assets` / `render_tree_view` are LOCAL and unchanged — they list non-schema artifacts.
