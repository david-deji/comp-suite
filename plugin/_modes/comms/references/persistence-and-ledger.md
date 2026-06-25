# Persistence & Ledger (v2 — MCP backend)

> Canonical for compensation-advisor; mirrored verbatim into `comms/`, `training/`,
> `transformer/` references on build. **Supersedes the v1 Google-Drive persistence
> backend, retired in MIM-0041 P4b.** If any mode still describes a `google_drive_*`
> probe or "write master.yaml to Drive", that prose is dead — this file is the contract.

## The v2 model in one paragraph

Schema-shaped state — orgs, the per-org `master` header, engagement bodies, cycles,
the decision log, brand kits, and costing configs/scenarios — lives in the **`market`
MCP backend** (the deployed comp-backend, `https://mcp.dallaire-jette.com/mcp/rpc`).
The backend is the **source of truth**. Identity is OAuth (Google login); the verified
email resolves to an org via membership (`colleague → org`). Local `$STATE_ROOT` is no
longer a persistence backend — it holds **non-schema artifacts** (deliverables, council
scratch, rendered decks, `cost-log.jsonl`, `harness/*`) plus a **read cache** of schema
state for transport-failure fallback. There is no Google Drive, no paste-mode backend,
no `persistence.backend` toggle.

## Where each thing lives

| State | Home (v2) | Tool / path |
|---|---|---|
| Org existence + membership | backend | `engagement_get_master` (read); create = admin-path (D4) |
| `master` header + federated sections | backend | `engagement_get_master` / `engagement_put_section` |
| Engagement body (`engagement-state`) | backend | `engagement_get` / `engagement_put` |
| Cycles (status, primary pointer) | backend | `engagement_put_cycle` (upsert; `primary=true` demotes prior atomically) |
| Decision log | backend | `engagement_append_decision` (append-only, idempotent on `id`) |
| Brand kit + files + logos | backend | `brand_get_kit` / `brand_list_files` / `brand_get_file` / `brand_put_*` |
| Costing config + scenarios | backend | `costing_get_config` / `costing_put_config` / `costing_*_scenario` |
| Deliverables, council scratch, decks | local | `$STATE_ROOT/_orgs/<slug>/...` (non-schema, D3) |
| Spend ledger | local | `$STATE_ROOT/.../cost-log.jsonl` (no backend entity) |
| Schema read cache | local | `$STATE_ROOT/_orgs/...` — refreshed from the backend; never a write target for schema |

## Read / write contract (the four decisions)

- **D1 — Fallback.** Read schema state via the MCP tool first. Fall back to the local
  `$STATE_ROOT` cache **only on transport failure** (connection error, timeout, 5xx,
  not-yet-authenticated). A tool returning *not-found / empty* is **authoritative** — do
  not fall back to local on not-found (that resurrects the stale state the import replaced).
- **D2 — Writes are MCP-only.** Schema-state writes go through the MCP tool and nowhere
  else. On write failure, **escalate/halt** — never write-local-and-reconcile. Local schema
  files are a read cache, not a write target.
- **D4 — Org / master-header creation is admin-path.** No `create-org` / `put-master-header`
  tool exists. `find_or_create_org` reads existing orgs via `engagement_get_master`; a *new*
  org or first master-header escalates to the admin bridge (membership + `private.orgs`),
  not over the wire. comp-suite never silently creates an org the backend doesn't know.
- **Optimistic concurrency.** `engagement_put` / `engagement_put_section` / `brand_put_*`
  read a `version`; pass it as `expected_version` (`0` to create). On stale-reject, **re-read
  and retry** the read-modify-write loop — never force. Money (`budget_usd`) is a decimal
  STRING, never float.

## Command mapping (checkpoint / resume / ledger / cycle-ops)

| Command | v2 behavior |
|---|---|
| `/checkpoint` | Engagement body → `engagement_put` (with `expected_version`); decisions → `engagement_append_decision`. Local `cost-log.jsonl` flushed. No Drive write. |
| `/resume [<slug>]` | `engagement_get {org_slug, engagement_id}` for the body; `engagement_get_master` for cycles + decision log. Local cache only on transport failure (D1). |
| `/ledger` | Read prior cycles + outcomes from `engagement_get_master.cycles[]` + the decision log; local `cost-log.jsonl` for spend. |
| `/close-cycle` | `engagement_put_cycle {cycle_slug, status: closed, closed_date}` + `engagement_append_decision {decision_type: cycle_closed}`. No local `master.yaml` write. |
| `/reopen-cycle` | `engagement_put_cycle {cycle_slug, status: drafting}` + `engagement_append_decision {decision_type: cycle_reopened, refs.related_decision_ids}`. |
| `/switch-cycle` | `engagement_put_cycle {cycle_slug, primary: true}` (server demotes prior primary atomically) + `engagement_append_decision {decision_type: cycle_primary_switched}`. |

## Binary deliverables (unchanged)

Rendered PDF / DOCX / PPTX are **never** written to any backend — they deliver as
chat-download artifacts; the operator files them into their own storage. The skill records
the intended path in metadata for provenance; bytes never round-trip through an LLM context.
This rule predates v2 and is unaffected by the backend change.

## What is retired

- The Google-Drive (Claude.ai connector) persistence backend and every `google_drive_search`
  / `google_drive_fetch` call.
- "Phase 0 — Persistence Backend Detection" (the session-start Drive probe). The backend is
  always reachable via OAuth; transport failure is handled by the D1 local-cache fallback,
  not by a paste-mode branch.
- The `persistence.backend` / `persistence.drive_folder_id` config block as a *backend
  selector*. Engagement config may still carry operator preferences, but it no longer
  chooses where schema state is persisted — that is always the `market` backend.
