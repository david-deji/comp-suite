# Engagement Create Primitive

Extracts engagement-creation logic from `v2/.claude/skills/comp/SKILL.md` Step 5 prose into a primitive. Mirrors `engagement-loader.md` shape. Resolves: org exists, generates engagement_id, writes `engagement-state.yaml` skeleton with `industry_outsider` per perspectives.yaml selection rule, scaffolds `engagements/<id>/` directory tree, writes empty `cost-log.jsonl`. Validates against `engagement-state.schema.json` before write.

This primitive resolves Run 2 finding M5 (engagement creation flow lived only in SKILL.md prose; no testable contract). It is a v2-only artifact (no v1 equivalent).

## Inputs

- `org_slug` — required, must exist as `$STATE_ROOT/_orgs/<org_slug>/`
- `engagement_id` — required, slug-formatted (e.g., `2026-Q2-comp-review`)
- `mode` — required, identifies the active mode (validates against `$ASSET_ROOT/_modes/*/`)
- `industry_outsider` — optional; if absent, prompts the user via the orchestrator's AskUserQuestion shape (selection rule in `$ASSET_ROOT/_core/council/perspectives.yaml`)
- `budget_usd` — optional; defaults to `5.00` per spec § 6.1

## Outputs

- Path to created `engagement-state.yaml`
- Engagement context dict ready for the rest of the primitive DAG (engagement-loader → master-yaml-ops → cycle-awareness → persona/brand-kit → mode-dispatcher → budget-check)

## Pre-conditions

1. **Org exists**: `$STATE_ROOT/_orgs/<org_slug>/` must be a directory. If not, error and direct caller to use `find_or_create_org` first.
2. **Engagement does not exist**: `$STATE_ROOT/_orgs/<org_slug>/engagements/<engagement_id>/` must NOT exist. If it does, error with "engagement already exists; use /comp resume to load it" — do NOT silently overwrite.
3. **Mode exists**: `$ASSET_ROOT/_modes/<mode>/mode.yaml` must exist.
4. **`industry_outsider` valid**: must be one of the values in `$ASSET_ROOT/_core/council/perspectives.yaml.industry_outsider.options`.

## Creation flow

1. **Validate inputs** per pre-conditions above. On any failure: error and return.
2. **Determine industry_outsider** if not passed:
   - Read `$STATE_ROOT/_orgs/<org_slug>/master.yaml` `header.industry` field if present.
   - Apply `$ASSET_ROOT/_core/council/perspectives.yaml.industry_outsider.selection_rule`: "pick the option closest-but-not-equal to the engagement's primary industry."
   - If `header.industry` is absent: prompt user via AskUserQuestion shape with the 8 options.
3. **Build proposed engagement-state.yaml** in memory:

   ```yaml
   schema_version: "2.1.0"
   engagement_id: <engagement_id>
   org_slug: <org_slug>
   mode: <mode>
   phase: intake                                # default first phase
   started_at: <iso-utc-now>
   last_active: <iso-utc-now>
   budget_usd: <budget_usd or 5.00>
   industry_outsider: <industry_outsider>
   working_artifacts: []
   checkpoints: []
   council_topics: []
   pending_decisions: []
   ```

4. **Validate** against `$ASSET_ROOT/_core/schemas/engagement-state.schema.json` using the same `python3 -c "...jsonschema..."` shape as master-yaml-ops:

   ```bash
   python3 -c "
   import sys, json, yaml
   try:
       import jsonschema
   except ImportError:
       sys.stderr.write('FATAL: jsonschema not installed — see v2/README.md § Setup\n')
       sys.exit(2)
   ...
   "
   ```

5. **On validation failure**: write a `engagement-state-validation-errors.md` to a temp location, surface errors to the user, exit non-zero. Do NOT create the engagement folder.
6. **On validation success**:
   - a. `mkdir -p $STATE_ROOT/_orgs/<slug>/engagements/<id>/{inputs,deliverables,advisor,comms,training,transformer,council}` (the mode directories are seeded for the 4 base modes; new modes are auto-created on first write per `master-yaml-ops:walk_sibling_assets` discovery)
   - b. Write `engagement-state.yaml` to disk (atomic: write to `engagement-state.yaml.new`, rename)
   - c. Touch empty `cost-log.jsonl`
   - d. If the org has no `personas.yaml` yet, the persona primitive will create the skeleton on first persona resolution (lazy init, not done here)
7. **Return** the engagement context dict for the next primitive in the DAG.

## Idempotency

This primitive is **NOT idempotent** by design — re-running with the same `engagement_id` should error per pre-condition 2. This prevents accidental overwrites of in-flight engagements. Use `/comp resume <id>` to re-enter an existing engagement.

The atomic write (step 6b — write to `.new` then rename) means a crash mid-flight leaves either the old state (no engagement) or the new state (complete engagement), never a partial one.

## Concurrent-session caveat

Two `/comp` sessions creating engagements in the same org concurrently could race on `master.yaml.next_engagement_id` if that field is used. v2 does NOT auto-generate engagement IDs from a counter — the user provides the ID at creation time. So no race surface here. Per spec § 10 concurrent-session caveat, single-operator project with no locking — operator discipline applies.

## Acceptance

- Test scenario 02 (advisor cold-start) verifies: cold engagement creation populates `engagement-state.yaml` with all required fields, writes empty `cost-log.jsonl`, scaffolds the 7-subdir tree (inputs, deliverables, 4 mode dirs, council).
- Test scenario 14 (mode-not-found) verifies: invalid `mode` errors before any state mutation.
- Test scenario 11 (close-idempotency) verifies: `/comp close` is idempotent BUT `engagement-create` is NOT (re-running on same ID errors loudly).

## Why this is a primitive (not inlined)

Run 2 friction log Step 4 finding M5: "Engagement creation flow lives only in SKILL.md prose. There is no primitive named `create_engagement` — the orchestrator inlines field assembly. This means: (a) test bench can't unit-test creation; (b) any field schema drift requires editing both schema AND SKILL.md prose."

Extraction to a primitive enables:
1. Test scenario coverage (scenarios 02, 11, 14 reference `engagement-create` directly)
2. Schema-coupled validation in one place (only this primitive validates against `engagement-state.schema.json` at creation time)
3. The orchestrator's SKILL.md Step 5 reduces to "invoke engagement-create primitive with collected args"
