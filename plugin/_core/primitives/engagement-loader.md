# engagement-loader

Comp-suite v2 primitive. Reads and validates an org + engagement. **MCP-primary** (the deployed
`market` server is the source of truth for schema-shaped state) and **fail-closed on outage** — an
unreachable server is a hard read-fail, not a degraded local read (MIM-0041 P4b). The orchestrator
calls this at position 1 in the startup DAG before any other primitive.

## Contract

| | |
|---|---|
| **Inputs** | `org_slug: str`, `engagement_id: str` |
| **Outputs** | `{master, engagement_state, org_slug, engagement_id, local_engagement_dir}` |
| **DAG position** | 1 — root. No dependencies. |
| **Calls** | MCP tools `engagement_get_master`, `engagement_get`. Schema state is MCP-only — there is no local read fallback |

## Source-of-truth posture (P4b)

- **Schema state** (master header / cycles / decision_log / sections, engagement body) is read from the
  `market` MCP server. The org is resolved from the caller's OAuth identity → `colleague_org_membership`
  → `org_id`; pass `org_slug` explicitly (`empire-co`) or omit it to use the default org.
- **There is no local read fallback for schema state.** No plugin write path ever populates
  `$STATE_ROOT` `master.yaml` / `index.yaml` / `engagement-state.yaml` — under P4b all schema-state
  writes go to the MCP backend. Those files exist only as frozen P4a import snapshots on machines that
  ran the one-time importer, and not at all on a fresh install; they are never refreshed. An unreachable
  server (connection refused, timeout, 5xx) is therefore a **hard read-fail**: escalate, never serve a
  stale on-disk read. A tool returning *not-found* is authoritative — the entity does not exist in the
  backend, NOT "look on disk."
- **A first tool-call 401 is `UNAUTHENTICATED`, not "unreachable"** — OAuth sign-in is not completed or
  has expired. Complete sign-in via `/mcp`, then resubmit (see § Error recovery). No token or header is
  involved; the `.mcp.json` registration is headerless by design.
- **Non-schema artifacts** (deliverables, inputs, rendered decks, cost-log) remain on local disk and are
  surfaced from `$STATE_ROOT` as before (Step 3).

## `load_engagement(org_slug, engagement_id)`

Run in sequence. Stop and escalate on any hard failure.

### Step 1 — Load the master (MCP-primary)

Call the **`engagement_get_master`** MCP tool with `{org_slug}`.

- **Success** → returns `{header, sections, cycles, decision_log}`. Membership resolved, so the org
  exists. Keep the `header.version` for any later section write. `header` may be `null` (see below).
- **`header: null` on a successful call** → the org is **provisioned but fresh**: a member org whose
  `master_header` row has not been seeded yet. This is common (no over-the-wire tool seeds the header;
  only the admin importer does), and it is NOT "org not provisioned". **Continue normally** — this
  matches `init-mode-protocol`. Empty `cycles` / `decision_log` are the same provisioned-but-fresh
  signal. Reserve escalation for the `NOT_A_MEMBER` wire error (§ Error recovery) — that is the only
  "org not provisioned" signal.
- **Error** → branch on `data.error_code` per § Error recovery. `NOT_A_MEMBER` / `NO_DEFAULT_ORG` /
  `ORG_UNAVAILABLE` escalate; `UNAUTHENTICATED` completes OAuth sign-in and resubmits. Do NOT create an
  org locally on any of these — new-org creation is an admin step, not a comp-suite operation (P4b D4).
- **Server unreachable** (connection refused / timeout / 5xx) → **hard read-fail**. There is no local
  cache to fall back to (§ Source-of-truth posture). Escalate:

  ```
  escalate(f"market MCP unreachable — cannot load master for org '{org_slug}'. "
           "Schema state is MCP-only under P4b; there is no local read fallback. "
           "Retry when the server is reachable.")
  ```

### Step 2 — Load the engagement body (MCP-primary)

Call **`engagement_get`** with `{org_slug, engagement_id}`.

- **`found: true`** → the engagement body (schema_version, mode, phase, budget_usd[str], working_artifacts,
  checkpoints, council_topics, pending_decisions, …). Keep its `version` for later optimistic writes.
- **`found: false`** → authoritative: the engagement does not exist in the backend. Escalate
  (`engagement '<id>' not found under org '<slug>'; use the engagement-create primitive`). Do NOT read local.
- **Error** → branch on `data.error_code` per § Error recovery.
- **Server unreachable** (connection refused / timeout / 5xx) → **hard read-fail**; there is no local
  cache. Escalate (`market MCP unreachable — cannot load engagement '<id>' under org '<slug>'`).

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
    "master":            master,              # from engagement_get_master (header may be null for a fresh org)
    "engagement_state":  engagement_state,    # from engagement_get
    "local_engagement_dir": local_dir,        # for downstream LOCAL-artifact primitives only
    "cost_log_path":     f"{local_dir}/cost-log.jsonl",   # local artifact (budget-check)
    "source":            "mcp",               # schema state is always MCP; no local read fallback
}
```

This dict is passed as-is to `master-yaml-ops` (which operates on `master`) and downstream primitives.
Schema state comes from MCP; `local_engagement_dir` / `cost_log_path` are for the stays-local primitives
(budget-check, production-gates, visual-qa) only.

## Engagement ID format

Canonical: `YYYY-Q[1-4]-<slug>` (e.g., `2026-Q2-comp-review`). Alternative: `YYYY-MM-DD-<slug>`.
Enforced server-side and by `engagement-state.schema.json`.

## Error recovery — branch on `data.error_code`, never on message text

Every private/org-scoped market tool error now arrives as a JSON-RPC error whose `data` object carries a
stable `error_code` (string) plus a derived `retryable` (bool). Branch on `data.error_code` /
`data.retryable`, NEVER on message text. The same JSON-RPC code (`-32602`) covers both retryable and
non-retryable cases, so keying on prose (as the old error-shapes table did) mis-routes escalate-vs-retry
on the exact branch where correctness matters. `-32602` is retained for JSON-RPC compatibility; the
plugin branches on the CODE.

| error_code | JSON-RPC | retryable | Recovery action |
|---|---|---|---|
| UNAUTHENTICATED | -32001 | false | Complete OAuth sign-in (/mcp), then resubmit |
| NOT_A_MEMBER | -32602 | false | Escalate — caller is not a member of the named org; do not retry |
| NO_DEFAULT_ORG | -32602 | false | Escalate — no org_slug + no default. `data.available_orgs[]` enumerates the caller's membership slugs; surface them, ask which, resubmit with --org |
| INVALID_ARGS | -32602 | false | Fix the arguments, resubmit |
| VERSION_CONFLICT | -32602 | true | Re-read the entity, re-apply the change onto the fresh version, retry ONCE; escalate if it conflicts again |
| ORG_UNAVAILABLE | -32601 | false | Escalate — private plane not configured |
| INTERNAL | (isError:true) | false | Escalate — generic handler failure |

`RETRYABLE_CODES = {VERSION_CONFLICT}`. All four backend families (engagement / brand / costing /
payequity) now RAISE on conflict → uniform `error_code` envelope; payequity no longer returns a
success-shaped `{error: version_conflict}` body, so a stale write can no longer be mis-read as success.

Notes on the codes this primitive acts on:

- **NOT_A_MEMBER** is the authoritative "org not provisioned for this caller" signal — the only one.
  New-org creation is an admin step (`colleague_org_membership` + `private.orgs` bridge), not a
  comp-suite operation, and there is no over-the-wire org-creation tool (P4b D4). Escalate; do NOT
  create anything locally. A successful call with `header: null` is NOT this error — it is a
  provisioned-but-fresh member org (continue; see Step 1).
- **NO_DEFAULT_ORG** now enumerates the caller's membership slugs in `data.available_orgs[]`. Surface
  those slugs, ask which org, and resubmit with `--org <slug>`.
- **VERSION_CONFLICT** applies to later section/body writes (via `master-yaml-ops`), not to the reads in
  Steps 1–2; re-read the entity, re-apply, and retry once.

Non-`error_code` conditions this primitive handles directly:

| Condition | Type | Recovery |
|---|---|---|
| `engagement_get` returns `found: false` | Hard — escalate | Engagement does not exist in the backend; `use the engagement-create primitive`. Do NOT read local. |
| `header: null` on a successful `engagement_get_master` | Continue | Provisioned-but-fresh member org — continue normally (Step 1), do NOT escalate. |
| Server unreachable (connection refused / timeout / 5xx) | Hard — escalate | Schema state is MCP-only; no local read cache exists to fall back to. Escalate and retry when reachable. |
| Working artifact not on disk | Soft — warn | `"working artifact not on disk: <path> (status: <status>)"` (Step 3). |

## Constraints

- Read-only. Never writes. Never creates an org or engagement locally (P4b D4 / D2).
- MCP-primary and fail-closed: a tool *not-found* is authoritative; a *server-unreachable* transport
  failure is a hard read-fail — no local read fallback exists (no plugin path populates `$STATE_ROOT`
  schema files under P4b).
- Schema state (master, engagement body) comes only from MCP; local disk is neither read nor written for
  schema state here.
- Atomic load: either fully loaded from MCP or escalated.
- Recovery branches on `data.error_code` / `data.retryable` (§ Error recovery), never on message text.
- master schema validation is delegated to `master-yaml-ops.read_master` (next in DAG); the server already
  validated on write, so client-side validation is a defensive check, not the gate.
