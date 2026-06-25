# Engagement Create Primitive

Creates a new engagement. Under P4b the engagement **body** is written to the backend via
`engagement_put` (the `market` MCP server is the source of truth); the local engagement **directory
tree** and empty `cost-log.jsonl` are still scaffolded on `$STATE_ROOT` because they hold non-schema
artifacts (inputs, deliverables, per-mode scratch, the spend log) that have no backend home (MIM-0041
P4b D3). Mirrors `engagement-loader.md` shape.

## Inputs

- `org_slug` — required; the org must already be provisioned in the backend (resolved by membership)
- `engagement_id` — required, slug-formatted (e.g., `2026-Q2-comp-review`)
- `mode` — required, validates against `$ASSET_ROOT/_modes/*/`
- `industry_outsider` — optional; selection rule in `$ASSET_ROOT/_core/council/perspectives.yaml`
- `budget_usd` — optional; defaults to `"5.00"` (decimal STRING, numeric(18,2) — never float)

## Outputs

- The created engagement body (as returned/confirmed by `engagement_put`)
- The local engagement dir path (for downstream local-artifact primitives)
- Engagement context dict for the rest of the DAG (engagement-loader → master-yaml-ops → cycle-awareness →
  persona/brand-kit → mode-dispatcher → budget-check)

## Pre-conditions (MCP-primary)

1. **Org provisioned**: call `engagement_get_master {org_slug}`. If it resolves no org → escalate
   (new-org creation is an admin step, P4b D4); do NOT create locally. On transport failure → escalate
   "MCP unreachable — cannot create an engagement while the backend is down (P4b D2)."
2. **Engagement does not exist**: call `engagement_get {org_slug, engagement_id}`. If `found: true` →
   error "engagement already exists; use /comp resume to load it" — do NOT overwrite. `found: false` is
   the required state to proceed.
3. **Mode exists**: `$ASSET_ROOT/_modes/<mode>/mode.yaml` must exist (local — modes are bundled assets).
4. **`industry_outsider` valid**: one of `perspectives.yaml.industry_outsider.options`.

## Creation flow

1. **Validate inputs** per pre-conditions. On any failure: error and return (no state mutation).
2. **Determine `industry_outsider`** if not passed:
   - Read `header.industry` from `engagement_get_master {org_slug}`.
   - Apply `perspectives.yaml.industry_outsider.selection_rule` ("closest-but-not-equal to the primary
     industry").
   - If `header.industry` absent → prompt via the orchestrator's AskUserQuestion shape (8 options).
3. **Build the engagement body** in memory (decimal-string money):

   ```yaml
   schema_version: "2.1.0"
   engagement_id: <engagement_id>
   body_org_slug: <org_slug>          # advisory; tenancy is enforced by org_id (RLS), not this field
   mode: <mode>
   phase: intake
   started_at: <iso-utc-now>
   last_active: <iso-utc-now>
   budget_usd: "<budget_usd or 5.00>" # STRING
   industry_outsider: <industry_outsider>
   working_artifacts: []
   checkpoints: []
   council_topics: []
   pending_decisions: []
   ```

4. **Write the body via MCP** (create = `expected_version: 0`):

   ```
   engagement_put {
     org_slug, engagement_id, schema_version: "2.1.0", body_org_slug: org_slug,
     mode, phase: "intake", started_at, last_active, budget_usd: "<...>",
     industry_outsider, working_artifacts: [], checkpoints: [], council_topics: [],
     pending_decisions: [], expected_version: 0
   }
   ```
   - Success → the engagement exists in the backend.
   - stale/exists reject (a row already exists at version >0) → the engagement already exists; surface
     "engagement already exists; use /comp resume" (matches pre-condition 2 under a race).
   - transport failure → ESCALATE; do NOT write a local `engagement-state.yaml` (P4b D2). No partial state.
5. **Scaffold the LOCAL artifact tree** (non-schema; stays on `$STATE_ROOT`, P4b D3) only AFTER the MCP
   body write succeeds:
   - `mkdir -p $STATE_ROOT/_orgs/<slug>/engagements/<id>/{inputs,deliverables,advisor,comms,training,transformer,council}`
   - `touch $STATE_ROOT/_orgs/<slug>/engagements/<id>/cost-log.jsonl`  (local spend log — budget-check)
   - Personas are lazy-initialized by the persona primitive on first use (persona stays local under P4b).
6. **Return** the engagement context dict for the next primitive in the DAG.

> Cycle creation is NOT part of engagement-create. When a comp cycle is opened, write it with
> `engagement_put_cycle` (upsert by `cycle_slug`; `primary=true` atomically demotes the prior primary) —
> never to a local `master.yaml`.

## Idempotency

NOT idempotent by design — re-running with the same `engagement_id` must error (pre-condition 2 /
the `engagement_put` exists-reject). This prevents overwriting an in-flight engagement. The MCP write is
the create gate (a row at version >0 means it exists); the local dir scaffold runs only after a successful
create, so a crash leaves either no engagement (backend rejected/unreached) or a complete one.

## Concurrent-session caveat

The backend `engagement_put` optimistic write (`expected_version: 0`) is the race guard: two sessions
creating the same `engagement_id` — the second gets an exists-reject. The user provides the ID (no counter
race). Single-operator project; operator discipline applies.

## Acceptance

- Scenario 02 (advisor cold-start): cold creation writes the body via `engagement_put` (verifiable with
  `engagement_get`), scaffolds the local 7-subdir tree + empty `cost-log.jsonl`.
- Scenario 14 (mode-not-found): invalid `mode` errors before any MCP write or local mutation.
- Scenario 11 (close-idempotency): `/comp close` idempotent; `engagement-create` is NOT (re-running on the
  same ID errors loudly via the exists-reject).

## Why this is a primitive (not inlined)

Run 2 finding M5: engagement creation lived only in SKILL.md prose with no testable contract. Extraction
gives test coverage (scenarios 02/11/14), one schema-coupled validation point, and a backend-write contract
the orchestrator invokes instead of inlining field assembly.
