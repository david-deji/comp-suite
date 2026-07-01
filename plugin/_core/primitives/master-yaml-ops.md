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
current version, write with `expected_version`, and on `data.error_code == VERSION_CONFLICT` **re-read,
re-apply the change onto the fresh version, and retry once** — never force, never write a local copy.
See § Error-code recovery contract.

```
1. (defensive) validate section_data client-side against the mode's declared schema; on failure raise
   ValueError with the errors. The server re-validates.
2. Read the current version:
     m = engagement_get_master(org_slug)
     current = m.sections[section_name]                 # may be absent
     expected_version = current.version if present else 0
3. Call engagement_put_section with {org_slug, section_name, body: section_data, expected_version}.
   - Success → done.
   - `data.error_code == VERSION_CONFLICT` (retryable) → re-read (step 2), re-apply the change onto the
     fresh version, and retry ONCE; if it conflicts again, escalate
     "concurrent writer on section '<name>'; re-run after the other session finishes".
   - transport failure → ESCALATE (do NOT write local):
       "MCP unreachable — cannot write section '<name>'. Schema writes require the backend (P4b D2).
        Retry when the market server is reachable."
```

There is no `$STATE_ROOT/_orgs/<slug>/master.yaml` write here anymore. The server owns the master;
local schema writes are forbidden (they would diverge from the backend).

---

## `append_decision_log(org_slug, entry)` — MCP-only, idempotent on an explicit `id`

The decision log is an **append-only** table (`GRANT SELECT, INSERT` only — rows can never be updated or
deleted). Crash-safety therefore hinges entirely on the `id`, and it splits by path:

- **Explicit-id path (crash-safe):** the server keys the insert `ON CONFLICT (org_id, id) DO NOTHING`, so
  re-submitting the same `id` after an ambiguous timeout is an idempotent no-op.
- **Default omit-id path (NOT crash-safe):** the server mints a fresh `dl-NNN` and runs an unconditional
  INSERT with no ON CONFLICT. A retry after a timeout that hid a successful commit double-logs a second
  identical decision that can never be cleaned up.

So the write path MUST mint a deterministic `id` (or pass a client idempotency key) BEFORE the append, and
reuse that same `id` on every retry — do not let a retryable append omit `id`.

```
1. (defensive) validate entry client-side against decision-log-entry.schema.json.
2. Mint a deterministic id for this decision BEFORE the call (e.g. a UUIDv5/hash over
   {org_slug, cycle_slug, skill, decision_type, summary} + the logical event, or read the current max
   dl-NNN and pick the next) so every retry of THIS decision carries the same id.
3. Call engagement_append_decision with:
     {org_slug, timestamp, skill, decision_type, summary,
      cycle_slug (or null), tags (list), id (the minted id), refs (optional)}.
   - Success → done. A retry with the same id hits `ON CONFLICT (org_id, id) DO NOTHING` and is a no-op.
   - transport failure → ESCALATE (do NOT write local): same message as write_master_section.
     Retry with the SAME minted id; the ON CONFLICT branch makes that retry idempotent.
```

Only the explicit-id path is crash-safe. Omitting `id` lets the server assign the next `dl-NNN` via an
unconditional INSERT — acceptable only for a guaranteed-single call that will never be retried; an
ambiguous-timeout retry on the omit-id path double-logs permanently. Pass a minted `id` on any path that
may be retried.

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

## Error-code recovery contract (server P3 taxonomy)

Every private/org-scoped market tool error arrives as a JSON-RPC error whose `data` object carries a
stable `error_code` (string) + a derived `retryable` (bool). Branch on `data.error_code` /
`data.retryable`, NEVER on message text.

| error_code | JSON-RPC | retryable | Recovery action |
|---|---|---|---|
| UNAUTHENTICATED | -32001 | false | Complete OAuth sign-in (/mcp), then resubmit |
| NOT_A_MEMBER | -32602 | false | Escalate — caller is not a member of the named org; do not retry |
| NO_DEFAULT_ORG | -32602 | false | Escalate — no org_slug + no default. `data.available_orgs[]` enumerates the caller's membership slugs; surface them, ask which, resubmit with --org |
| INVALID_ARGS | -32602 | false | Fix the arguments, resubmit |
| VERSION_CONFLICT | -32602 | true | Re-read the entity, re-apply the change onto the fresh version, retry ONCE; escalate if it conflicts again |
| ORG_UNAVAILABLE | -32601 | false | Escalate — private plane not configured |
| INTERNAL | (isError:true) | false | Escalate — generic handler failure |

`RETRYABLE_CODES = {VERSION_CONFLICT}`. All four backend families (engagement/brand/costing/payequity)
raise on conflict → uniform error_code envelope; payequity no longer returns a success-shaped
`{error:version_conflict}` body.

## Constraints

- **No schema-state write touches `$STATE_ROOT`** (P4b D2). Master, sections, decisions, cycles, brand,
  costing are MCP-only. Local schema files are a read cache (transport-failure fallback) only.
- MCP-primary reads: a tool *not-found* is authoritative; only a *transport* failure falls back to cache.
- Optimistic writes thread `version → expected_version`; on `data.error_code == VERSION_CONFLICT`
  (retryable) re-read, re-apply onto the fresh version, retry once, then escalate. Branch on
  `data.error_code` / `data.retryable`, never on message text (§ Error-code recovery contract).
- `append_decision_log` is idempotent only on an **explicit** `id` server-side (`ON CONFLICT (org_id, id)
  DO NOTHING`). Mint a deterministic id before the append so a retry is a no-op; the default omit-id path
  runs an unconditional INSERT and is NOT crash-safe.
- `walk_sibling_assets` / `render_tree_view` are LOCAL and unchanged — they list non-schema artifacts.
