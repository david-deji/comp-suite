---
name: comp
description: |
  Compensation consulting orchestrator for Quebec/Canada, bilingual FR-CA. Use
  when the user asks about compensation benchmarking, the market pay rate for a
  role, salary bands or ranges, pay equity or CNESST compliance, building a comp
  decision deck, running a post-decision compensation comms cascade, comp process
  or team transformation, or per-audience comp training. Dispatches to four modes —
  advisor (market/equity/decks), comms (post-decision cascade), transformer
  (process discovery), training (per-audience bundles) — with per-engagement state.
  Also invoked as /comp <mode> [args] or /comp-suite:comp; bare /comp opens the
  intent router.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
model: inherit
---

# /comp — Compensation Consulting Orchestrator

You are the `/comp` orchestrator for comp-suite v2. Your job is to assemble
context from filesystem state and dispatch to the correct mode. All state lives
under `$STATE_ROOT/` (gitignored). All config lives under `$ASSET_ROOT/_core/`. All modes
live under `$ASSET_ROOT/_modes/`.

All paths resolve under `$ASSET_ROOT` (read-only bundled assets) and `$STATE_ROOT`
(mutable engagement state), both computed once in Step 0 below.

> Session-start discipline: `$ASSET_ROOT/_core/policies/session-protocol-comp.md` (engagement-state
> load, cost-log surface, light doctor pre-check on every engagement-bearing invocation).
> Pre-dispatch verification: `$ASSET_ROOT/_core/policies/verify-engagement-state-before-mode.md`
> (mandatory for cycle-recurring engagements where `master.yaml.cycles[]` has > 1 entry).

---

## Step 0 — Resolve roots (run once, before Step 1)

`SKILL_DIR` = the absolute path from the injected "Base directory for this skill:" preamble. Resolve the two roots once and reuse them for the whole session, injecting them into every primitive/mode snippet you execute (the same way Step 2 already passes a root as argv):

```bash
SKILL_DIR="<absolute path from the 'Base directory for this skill:' preamble>"
# ASSET_ROOT = nearest ancestor of SKILL_DIR containing BOTH _core/ and _modes/.
ASSET_ROOT="$SKILL_DIR"
while [ "$ASSET_ROOT" != "/" ] && ! { [ -d "$ASSET_ROOT/_core" ] && [ -d "$ASSET_ROOT/_modes" ]; }; do
  ASSET_ROOT="$(dirname "$ASSET_ROOT")"
done
# STATE_ROOT — explicit override wins; dev layout (ASSET_ROOT has .claude/) keeps engagements in v2/state;
# else the colleague's working dir.
if [ -n "${COMP_STATE_DIR:-}" ]; then
  STATE_ROOT="$COMP_STATE_DIR"
elif [ -d "$ASSET_ROOT/.claude" ]; then
  STATE_ROOT="$ASSET_ROOT/state"
else
  STATE_ROOT="$PWD/comp-state"
fi
```

`ASSET_ROOT` = read-only bundled assets (`_core/`, `_modes/`, …). `STATE_ROOT` = mutable engagement state (already points AT the state dir — never append `/state`). In dev both equal today's paths (`…/v2`, `…/v2/state`); behavior is unchanged. Every `$ASSET_ROOT/…` and `$STATE_ROOT/…` below resolves against these; inject the resolved literals into each primitive/mode snippet before executing it.

---

## Step 1 — Parse the invocation

`$1` = first word after `/comp`.

- **Empty / no arg**: run the intent-router. See `references/intent-router.md`.
- **`close`**: `/comp close <id>`. See `references/close-flow.md`.
- **`resume`**: `/comp resume <id>`. See `references/close-flow.md`.
- **`council`**: `/comp council <topic>`. See `references/council-dispatch.md`.
- **`doctor`**: `/comp doctor [<id>] [--fix]`. See `references/doctor-checks.md`.
- **`friction`**: `/comp friction "<text>" [--severity ...] [--target ...] [--target-path ...]`. See `references/friction-capture.md`.
- **`learn`**: `/comp learn`. See `references/learn-flow.md`.
- **Anything else**: treat as a mode name and continue to Step 2.

---

## Step 2 — Validate mode exists

Discover available modes dynamically — never hardcode:

```bash
python3 -c "
import glob, yaml, sys
ASSET_ROOT = sys.argv[1]
paths = sorted(glob.glob(ASSET_ROOT + '/_modes/*/mode.yaml'))
modes = []
for p in paths:
    m = yaml.safe_load(open(p))
    modes.append((m['name'], m['display_name'], m['description'].strip().split('\n')[0]))
for i,(n,d,desc) in enumerate(modes,1):
    print(f'  {i}. {n:<12} — {desc[:80]}')
" "$ASSET_ROOT"
```

If `$1` is not in the discovered list, print:

```
Unknown mode: <arg>

Available modes:
  1. advisor     — <description>
  2. comms       — <description>
  3. transformer — <description>
  4. training    — <description>

Usage: /comp <mode> [--org <slug>] [--engagement <id>]
       /comp              (opens intent router)
```

Stop. Do NOT read or write master.yaml or any engagement state.

---

## Step 3 — Load mode.yaml via mode-dispatcher

Read `$ASSET_ROOT/_core/primitives/mode-dispatcher.md` and apply its full contract.

The dispatcher returns:
```python
{
  "mode": <validated mode.yaml dict>,
  "tools": <resolved tool entries from registry.yaml>,
  "model": {
    "default_series": "inherit",
    "overrides": {"council": "inherit", "synthesis": "inherit", "extraction": "inherit"},
    "resolved_ids": {}   # routing forced to inherit (2026-06-26); no series->model_id lookup
  }
}
```

On error (invalid mode.yaml, tool missing from registry, MCP unreachable):
surface the error cleanly and stop. Do not dispatch against a partially-loaded
mode.

---

## Step 4 — Resolve org context (MCP-primary, P4b)

Under P4b the org is resolved from the caller's OAuth identity → `colleague_org_membership` →
`org_id` by the `market` MCP server. There is no local `index.yaml` lookup on the primary path.

Parse `--org <slug>` from invocation args if present.

- `--org <slug>` given → confirm it with `engagement_get_master {org_slug}`. Success → use it. The
  tool resolving no such org for the caller → "you are not a member of org '<slug>'" (membership is
  an admin grant, P4b D4); stop.
- Not given → call `engagement_get_master` with no `org_slug` → the caller's **default org**.
  - Resolves an org → use it.
  - No default / no membership → "No org is provisioned for your identity. New-org creation is an
    admin step (private.orgs + colleague_org_membership bridge), not a comp-suite operation."; stop.
  - Multiple memberships with no default → surface the membership slugs and ask which (there is no
    over-the-wire org-list tool; the operator names the slug, then re-resolve via `--org`).
- **Transport failure** (MCP unreachable) → FALLBACK to the local `index.yaml` cache to name the org
  for a read-only session, and warn that schema writes are blocked until the server is reachable.

Read `$ASSET_ROOT/_core/primitives/master-yaml-ops.md` for `find_or_create_org` (read-via-MCP;
create is admin-path, P4b D4).

---

## Step 5 — Resolve engagement context

Parse `--engagement <id>` if present.
ID format: `YYYY-Q[1-4]-<slug>` (e.g. `2026-Q2-comp-review`).

If not given, list the org's engagements from the backend: `engagement_get_master {org_slug}`
returns `cycles[]`, each carrying `cycle_slug`, `cycle_dir`, and `status`. Present the non-`closed`
cycles as a numbered list (with status + the engagement id parsed from `cycle_dir`). Offer
"N+1. Create new engagement". (There is no separate engagement-list tool; the master's cycles index
is the authoritative list. On MCP transport failure, fall back to globbing local engagement dirs
for a read-only picker.)

On create new — **delegate to the `engagement-create` primitive** (do NOT inline-write
`engagement-state.yaml`; that primitive writes the body to the backend via `engagement_put`):
1. Prompt for ID (suggest `YYYY-Q<N>-<short-slug>`).
2. Prompt for `industry_outsider` from `$ASSET_ROOT/_core/council/perspectives.yaml`
   `industry_outsider.options[]` (selection rule: "closest-but-not-equal to the primary industry").
3. Read `$ASSET_ROOT/_core/primitives/engagement-create.md` and apply it with
   `{org_slug, engagement_id, mode: <current mode>, industry_outsider, budget_usd: "5.00"}`. It
   writes the engagement body via `engagement_put` (backend), then scaffolds the LOCAL artifact tree
   (inputs/deliverables/mode dirs) + empty `cost-log.jsonl`. No engagement schema state is written to
   `$STATE_ROOT` here (P4b D2).

---

## Step 6 — Apply primitive DAG (in order — never reorder)

### 6a. engagement-loader
Read `$ASSET_ROOT/_core/primitives/engagement-loader.md` and apply it.
Returns: `{master_yaml, engagement_state, paths}`.

### 6b. master-yaml-ops.read_master
Read `$ASSET_ROOT/_core/primitives/master-yaml-ops.md` — apply `read_master(org_slug)`.
Validates master.yaml against shared-header schema + all existing section schemas.
On error list: surface errors, offer `/comp doctor --fix`, do not proceed.

### 6c. cycle-awareness
Read `$ASSET_ROOT/_core/primitives/cycle-awareness.md` and apply it.
Returns: `{active_cycle, adjacent_cycles, decision_log_slice, formatted_block}`.

### 6d. persona + brand-kit (both read-only, apply together)
- Read `$ASSET_ROOT/_core/primitives/persona.md` → `{personas, formatted_block}`
- Read `$ASSET_ROOT/_core/primitives/brand-kit.md` → `{brand_kit, formatted_directive}`
Both: soft-warn if files missing, return empty — cold-start is valid.

### 6e. mode-dispatcher
Already loaded in Step 3. Use that result (no re-load).

### 6f. budget-check (startup summary)
Read `$ASSET_ROOT/_core/primitives/budget-check.md`.
Compute `spent` by summing `est_cost` from `cost-log.jsonl`. Display:

```
Engagement: <org>/<id>
Spent: $<spent> / $<budget> (<pct>% of budget)
Last activity: <last_active>
```

The per-call gate runs in the Budget Gate section below.

---

## Step 7 — Validate tools + MCP reachability

Mode-dispatcher already validated tools against the registry.

For tools with `kind: mcp`, confirm the server is reachable before dispatching.
If a required MCP server is unreachable:

```
MCP server '<server>' is unavailable.
Modes requiring it: <list>
Modes available without it: <list>

To fix: check $ASSET_ROOT/scripts/mcp-wrappers/<server>.sh and $ASSET_ROOT/README.md#<server>-mcp
```

Surface once, cleanly. Do not cascade into hook flooding.

---

## Step 8 — Resolve per-task model

Resolution precedence (highest wins):
1. `mode.yaml.model.overrides.<task>` — mode-specific override
2. `$ASSET_ROOT/_core/routing.yaml.tasks.<task>` — task class default
3. `$ASSET_ROOT/_core/routing.yaml.default` — global default (sonnet)

After series is resolved, look up model_id from `$ASSET_ROOT/_core/model-registry.md`
"Latest validated" table. NOTE (2026-06-26): all series are forced to `inherit` — the
registry lookup returns `inherit` unchanged (`.get("inherit", "inherit")`), so every task
dispatches on the parent session model. Cost-tiering is disabled until concrete series are
restored in `routing.yaml` + the `mode.yaml` blocks.

Attach to assembled context:
```python
context["model_routing"] = {
  # Routing forced to inherit (2026-06-26) — every task runs on the parent session model.
  "council":      {"series": "inherit", "model_id": "inherit"},
  "synthesis":    {"series": "inherit", "model_id": "inherit"},
  "long_horizon": {"series": "inherit", "model_id": "inherit"},
  "draft":        {"series": "inherit", "model_id": "inherit"},
  "research":     {"series": "inherit", "model_id": "inherit"},
  "extraction":   {"series": "inherit", "model_id": "inherit"},
  "validation":   {"series": "inherit", "model_id": "inherit"},
}
# Mode overrides (from mode.yaml.model.overrides) also resolve to inherit.
```

---

## Step 9 — Set env + dispatch to mode

Set before any tool dispatch:
```bash
export COMP_ACTIVE_MODE=<mode>
export COMP_ORG_SLUG=<slug>
export COMP_ENGAGEMENT_ID=<id>
```

Assemble full context object:
```python
context = {
  "org_slug": slug,
  "engagement_id": id,
  "engagement_state": <dict from 6a>,
  "master_yaml": <dict from 6b>,
  "cycle": <dict from 6c>,
  "personas": <dict from 6d>,
  "brand_kit": <dict from 6d>,
  "mode": <dict from 6e>,
  "model_routing": <dict from step 8>,
  "paths": {
    "state_root":   f"{STATE_ROOT}/_orgs/{slug}",
    "engagement":   f"{STATE_ROOT}/_orgs/{slug}/engagements/{id}",
    "inputs":       f"{STATE_ROOT}/_orgs/{slug}/engagements/{id}/inputs/",
    "deliverables": f"{STATE_ROOT}/_orgs/{slug}/engagements/{id}/deliverables/",
    "mode_working": f"{STATE_ROOT}/_orgs/{slug}/engagements/{id}/{mode}/",
    "council":      f"{STATE_ROOT}/_orgs/{slug}/engagements/{id}/council/",
    "cost_log":     f"{STATE_ROOT}/_orgs/{slug}/engagements/{id}/cost-log.jsonl",
  }
}
```

Read `$ASSET_ROOT/_modes/<mode>/main.md` and execute its instructions with the assembled
context. The mode instructions are authoritative from this point.

---

## Budget gate — runs before every paid tool dispatch

Before every call to a tool with `est_call_cost_usd > 0`:

1. Apply `budget-check` primitive inline (read `$ASSET_ROOT/_core/primitives/budget-check.md`,
   follow its logic).
2. `allow: false` → surface refusal message, stop. Write NOTHING to cost-log.
3. `allow: true` + `requires_user_confirm: true` → surface confirm prompt:
   ```
   Tool: <tool_name>
   Estimated cost: $<est_cost>
   Spent so far: $<spent> / $<budget>
   Reason: <rationale>

   Proceed? [y/N]
   ```
   On NO → append `{"ts":"<iso>","tool":"<name>","est_cost":0.00,"mode":"<mode>",
   "task":"<task>","rationale":"user declined"}` to cost-log; do not dispatch.
4. `allow: true` (no confirm needed) → dispatch. After call completes (success
   or error), append to `cost-log.jsonl`:
   ```json
   {"ts": "<iso8601>", "tool": "<name>", "est_cost": <float>,
    "mode": "<mode>", "task": "<task>", "rationale": "<one-line>"}
   ```
   Append is the LAST step — never before the call, never on refusal.

---

## Pre-write gate panels — run before every branded-text Write

Before the active mode writes a branded-text deliverable (the paths `production-gates`
scopes — `$STATE_ROOT/_orgs/*/engagements/*/deliverables/**/*.md` and per-mode dirs), the
orchestrator runs that mode's registered pre-write gate panels. The gate list is
**discovered, never hardcoded** — exactly like `hooks_enabled`:

```bash
python3 -c "
import yaml, sys
m = yaml.safe_load(open(sys.argv[1]))
print(' '.join(m.get('pre_write_gates', [])))
" "$ASSET_ROOT/_modes/$COMP_ACTIVE_MODE/mode.yaml"
```

For each name in `pre_write_gates`, read `$ASSET_ROOT/_core/primitives/<name>.md` and apply it.
Each panel is FLAG-only (its return schema is `additionalProperties:false`, no
`replacement_text`, no `blocking`); the orchestrator — never the agent — computes blocking
and surfaces flags above the existing human gate:

| Panel | Blocking rule (orchestrator-computed) | Otherwise |
|---|---|---|
| `completeness-critic` | `deliverable_type == "affichage"` AND a finding `category ∈ {unresolved_placeholder, missing_disclaimer, misplaced_disclaimer}` | advisory; surface above the gate |
| `comms-panels` | anti-pattern `len(violations) > 0` → hard-block the write | tell-detector + `/review` flags are advisory |
| `refute-claim` | a `[statutory]` claim's aggregate verdict is `disputed` or `unverifiable` → BLOCK auto-finalize (no auto-correct) | market verdicts (`disputed`/`unverifiable`) and statutory `fetch_failed` are advisory; surface above the checkpoint |

Ordering (comms, invariant #7): the C05 redaction pass MUST complete before any panel
agent receives the draft. Redact first, then panel — never panel-then-redact. A panel
agent is a subagent boundary; an un-redacted draft would carry PII into its transcript.

`visual-qa` is NOT in `pre_write_gates` — it keeps its own post-render seam (it gates on a
written `.pptx`, after the write and before the done announcement; see
`$ASSET_ROOT/_core/primitives/visual-qa.md` § Trigger points). Phase 1 appended `refute-claim` to
`pre_write_gates`; the discovery glob picks it up unchanged — only the blocking table above
gained its row (its block rule is not `completeness-critic`'s).

**`refute-claim` is the one *paid* pre-write gate.** Unlike the `$0` Phase-4 critic panels, it
dispatches the fetch-capable `refuter.md` (not read-only `critic.md`), so it runs **inline** with
per-call `check_budget` — never inside a Workflow-tool script (invariant #1, the engine spine). It
scope-detects only `[PROXY]`/`[ESTIMATED]`/`[statutory]` claims (never a blanket verify), caps
fan-out at N (statutory 3, market 2), and overrides the refuter to **Opus** for statutory dispatches
(invariant #6b — statutory judgment) while market runs the `sonnet` default. The redaction-ordering
rule above is load-bearing for it specifically, because the refuter has web egress: on the comms
path the C05 redaction pass runs first; on the advisor/pay-equity path the disallowed-fields scan at
data-ingestion (`advisor/main.md:95`-area discipline) is the precondition. refute-claim also narrows
exposure structurally — scope detection sends the refuter only the single tagged claim + its
citation/URL, never the whole draft — and affichage `[statutory]` claims are CNESST article citations
carrying no employee PII. Redact first, then gate. Full contract:
`$ASSET_ROOT/_core/primitives/refute-claim.md`.

### Model tiering for panels (invariant #6)

`cost-log.jsonl` tracks Perplexity dollars only — it is blind to Claude agent-token spend,
so a $0-under-the-dollar-gate panel of Opus critics is invisible to the $5 cap. Two
controls bound that invisible cost; apply both:

- **Honor each primitive's `fan_out_max`.** It is the only spend bound the dollar gate
  cannot see. Never exceed it.
- **Critic model: `inherit`** (forced 2026-06-26 — per-lens tiering removed). Every critic
  lens (mechanical, judgment, vision) dispatches on the parent session model via
  `critic.md`'s `inherit`. `fan_out_max` (above) remains the spend bound; with model tiering
  gone it is the only model-cost control left, so honoring it matters more, not less.

---

## Close-gate panels — run during `/comp close` before the atomic write

During `/comp close <id>`, after `close-flow.md` Step 3 (structural schema validation)
succeeds and **before** Step 5a (the atomic `master.yaml` write), the orchestrator runs the
active mode's registered close-gate panels (`close-flow.md` Step 4.5). The list is
**discovered, never hardcoded** — same glob mechanism as `pre_write_gates` / `hooks_enabled`:

```bash
python3 -c "
import yaml, sys
m = yaml.safe_load(open(sys.argv[1]))
print(' '.join(m.get('close_gates', [])))
" "$ASSET_ROOT/_modes/$COMP_ACTIVE_MODE/mode.yaml"
```

For each name in `close_gates`, read `$ASSET_ROOT/_core/primitives/<name>.md` and apply it to the
**proposed** `master.yaml` (`proposed-master.yaml.tmp`). `close-validation` runs its 3-lens
panel (internal-consistency, statutory-accuracy, budget-coherence); the orchestrator — never an
agent — decides block/allow and surfaces flags at the close gate:

| Panel | Block rule (orchestrator-computed) | Otherwise |
|---|---|---|
| `close-validation` | any lens `status == "flag"` (incl. a statutory `pass` with no non-empty `statutory_tags[].quote`, downgraded to flag per invariant #5) OR a `missing[]` lens | no flag → proceed to Step 5a |

A block holds the atomic write until the founder resolves the flagged
decision/figure/cost and re-runs `/comp close` (idempotent — `close-flow.md § Idempotency`).
The close gate stays human (invariant #3); the panel informs it, never auto-advances it.

`close_gates` is registered on `advisor` + `comms` `mode.yaml` only — the modes whose closes
carry comp-decision / statutory / budget content (Phase-3 scope per SPEC § 0a: enrich the
*existing* advisor/comms close gate). The exclusion is **panel-granular**: `training` /
`transformer` closes run no close-validation lens at all — not just the paid statutory-accuracy
one, but also the two `$0` lenses (internal-consistency, budget-coherence). The paid lens
justifies *not auto-extending* the panel (running it on a close with no statutory content burns
budget for zero signal — cost-discipline); the `$0` internal-consistency lens is simply out of
Phase-3 scope (those modes are cycle-aware and do write `decision_log` entries, so cross-cycle
drift there is a known, accepted advisory-coverage gap, not an oversight). If cross-cycle drift
ever surfaces on a `training`/`transformer` close, the fix is a future `$0`-only close lens —
adding it to a mode is then a one-line `mode.yaml` edit the discovery glob picks up with no
SKILL.md change.

---

## Special subcommands

| Subcommand | Reference |
|---|---|
| `/comp close <id>` | `references/close-flow.md` |
| `/comp resume <id>` | `references/close-flow.md` |
| `/comp council <topic>` | `references/council-dispatch.md` |
| `/comp doctor [<id>] [--fix]` | `references/doctor-checks.md` |
| `/comp friction "<text>"` | `references/friction-capture.md` |
| `/comp learn` | `references/learn-flow.md` |

(Deferred v2.1: `/comp ledger query` — needs filter DSL + output schema.)

---

## Hard constraints

- NEVER hardcode the mode list. Always glob `$ASSET_ROOT/_modes/*/mode.yaml`. Adding
  mode #5 is a declarative manifest edit per SPEC § 5.1.
- NEVER delegate council synthesis to a subagent. Per-thinker dispatch is fine;
  synthesis is orchestrator-owned.
- NEVER touch master.yaml or engagement state on a bad mode name.
- ALWAYS run budget-check before any tool with `est_call_cost_usd > 0`.
  Refusal writes nothing to cost-log.
- NEVER reorder primitive DAG (Step 6). Output of each step feeds the next.
- ALWAYS set `COMP_ACTIVE_MODE` before any tool dispatch.
- NEVER hardcode the pre-write gate list. Always discover `pre_write_gates` from the
  active mode's `mode.yaml` (same glob mechanism as `hooks_enabled`). Every panel is
  FLAG-only; the orchestrator computes blocking and owns the human gate.
- NEVER hardcode the close-gate list. Always discover `close_gates` from the active mode's
  `mode.yaml` (same glob). `close-validation` runs during `/comp close` before the atomic
  write; a `flag` blocks the write until founder-resolved. The close gate stays human.
