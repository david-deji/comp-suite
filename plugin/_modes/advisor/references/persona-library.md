# Persona Library

Loaded by SKILL.md when council-mode runs (`/council` and integrated council). Defines the schema for custom personas, the load order at council entry, and the collision rules between bundled defaults and repo-resident customs.

For council mechanics (dispatch, grounding, synthesis, anti-patterns), see `references/council-mode.md`. For the cross-asset resolution principle (repo-first / bundled-fallback), see `references/library-resolution.md`. This file covers persona-specific structure only.

---

## Ground truth: bundled personas

The bundled 7 personas live as a markdown table in `references/council-mode.md` § Perspective pool. Each row has exactly **three columns**: `ID`, `Persona` (display label), `Lens` (one-paragraph description of the lens, scope, and grounding tendencies). Voice characteristics are implied by the lens — they are not separate schema fields.

Each persona also has a `default_grounding_source` assigned in `council-mode.md` § Step 4 — Per-persona grounding (the grounding table). This is what tells the council what kind of source to fetch for that persona during the asymmetric-grounding step.

So the **complete bundled persona shape** is:

| Field | Source | Example |
|-------|--------|---------|
| `id` | Perspective-pool table column 1 | `employment-lawyer` |
| `label` | Perspective-pool table column 2 | `Employment Lawyer` |
| `lens` | Perspective-pool table column 3 | `CBA interpretation, pay equity maintenance exposure, ...` |
| `default_grounding_source` | Step 4 grounding table | `The actual statute / CBA article being cited (web_fetch against legisquebec.gouv.qc.ca / laws-lois.justice.gc.ca / canlii.org)` |
| `selection_heuristic` (optional) | § Persona selection heuristics line item | `Unionized scope → always include employment-lawyer` |

Custom persona schema mirrors this shape — same fields, no invented extras.

---

## Custom persona schema

Each custom persona lives in its own file at `personas/<persona_id>.yaml` in the persistence folder:

```yaml
persona:
  id: "pension-specialist"                    # required, kebab-case, must not collide with bundled IDs
  label: "Pension Specialist"                 # required, human-readable label shown in roster declaration
  lens: |                                     # required, one paragraph — same shape as bundled lens
    Focuses on retirement-benefit cost convergence with wage decisions. Probes whether
    a wage lift triggers downstream pension cost amplification (DB plans price wage as
    final-average earnings; a lift compounds for the duration of the employee's tenure).
    Surfaces actuarial assumptions the comp team typically doesn't model.
  default_grounding_source_type: "actuarial-valuation-report"
                                              # required, used by council-mode.md § Step 4
                                              # see § Grounding source types below
  selection_heuristic: |                      # optional, mirrors council-mode.md § Persona selection heuristics
    DB pension plan in scope → always include
    Compression-fix lift exceeding 4% across all steps → consider including
  added_at: 2026-04-21
  added_by: "user"
```

**Required fields** (4): `id`, `label`, `lens`, `default_grounding_source_type`. Anything missing causes a load failure surfaced as: "Custom persona `<id>` failed to load: missing required field `<field>`. Skipping."

**Optional fields**: `selection_heuristic` (used at roster-declaration time to surface auto-include logic), `added_at`, `added_by` (provenance only — not consumed by the council).

**Not in schema** (deliberately omitted to mirror bundled persona shape):
- No `voice_profile` — the bundled 7 don't have one. The persona's voice is inferred from the lens. A voice that needs separate specification probably needs a different persona.
- No `banned_phrases` — anti-pattern enforcement runs at the council-output level (council-mode.md § Anti-patterns), not per-persona.
- No `example_opening` — would be a UI nicety with no protocol consumer.
- No `required_grounding_per_response` — council-mode.md § Step 4 already mandates one live fetch per persona. Per-persona override would fragment the rule.

If you find yourself wanting one of the omitted fields, file it as a Batch F+ extension issue rather than adding it ad-hoc — the symmetry with bundled personas is load-bearing for the collision rule.

---

## Grounding source types

`default_grounding_source_type` tells `council-mode.md § Step 4` what kind of source to assign this persona during the per-persona asymmetric grounding step. The skill maps the source type to specific files/queries at council time.

Source types are aligned with the bundled persona grounding patterns:

| Source type | What it means | Tool used at council time |
|-------------|--------------|--------------------------|
| `statute-text` | Statute or CBA article — must be fetched verbatim | `web_fetch` against `legisquebec.gouv.qc.ca` / `laws-lois.justice.gc.ca` / `canlii.org` (mandatory verbatim quote per `council-mode.md` § Statutory discipline) |
| `market-mcp-role-data` | Market MCP wage-by-occupation + live-posting data | `mcp__market__get_role_intelligence` (all five percentiles default) or `mcp__market__compare_roles` |
| `cba-text` | Collective agreement scale | `mcp__market__get_cba_wage_scale` OR (for user-CBA) the parsed `user_provided_cba` block |
| `survey-house-cut` | Survey-house cut for the role/geo | `survey-archive/<vendor>/<year>/<cut>.yaml` from repo (or fresh ingestion) |
| `competitor-careers-page` | Named competitor's published wages | `web_fetch` against the competitor's careers URL |
| `econometric-table` | StatCan econometric series (CPI, unemployment, GDP) — **NOT wages** | StatCan MCP (when available) OR `web_fetch` against `statcan.gc.ca` table page |
| `internal-hris-data` | User-provided internal data | Engagement-config `current_pay` block + uploaded workforce CSV |
| `union-bulletin` | Local union news / bargaining communications | `web_fetch` against the local's news page |
| `government-budget` | Federal/provincial budget documents | `web_fetch` against `canada.ca`, `finances.gouv.qc.ca`, etc. |
| `actuarial-valuation-report` | Pension/benefit plan actuarial document | User-uploaded plan valuation |
| `indeed-company-data` | Competitor employer ratings + employer-reported salaries | `mcp__indeed__get_company_data` |

If a custom persona's `default_grounding_source_type` is none of the above, the skill treats it as `web-fetch-other` and prompts the user at council time for the specific URL/file to ground that persona.

**Asymmetric-grounding rule still applies**: council-mode.md § Step 4 mandates that no two personas in the same council hit the same source. If two custom personas (or one custom + one bundled) declare the same `default_grounding_source_type` AND the same target source resolves for both, the orchestrator reassigns one — typically the lower-priority persona to `web-fetch-other`.

---

## `personas/_index.yaml` schema

```yaml
custom_personas:
  - id: "pension-specialist"
    file: "personas/pension-specialist.yaml"
    added_at: 2026-04-21
  - id: "quebec-only-labour-counsel"
    file: "personas/quebec-only-labour-counsel.yaml"
    added_at: 2026-04-22
  - id: "union-organizer-tactical"
    file: "personas/union-organizer-tactical.yaml"
    added_at: 2026-04-25
```

The index is what `library-resolution.md` § Persona library scans at Phase 0. Without an index entry, a persona file in `personas/` is ignored (this is intentional — orphan files don't surprise the user).

---

## Loading procedure (council entry)

When council-mode dispatches the per-persona blocks:

1. Read `personas/_index.yaml` from the persistence folder (skip if paste-mode).
2. For each entry, read the referenced `personas/<id>.yaml` file. Validate the 4 required fields. Surface any validation failure as: "Custom persona `<id>` failed to load: <reason>. Skipping this persona for this council."
3. Build the union pool: bundled-7 (read from `council-mode.md` § Perspective pool table) + valid customs.
4. Detect ID collisions between custom and bundled: if any, surface "Custom persona `<id>` collides with bundled `<id>`. Bundled wins; skipping custom." and exclude the custom one from the pool.
5. When declaring the roster (council-mode.md § Step 2), list all available personas with a `(bundled)` or `(custom)` tag so the user knows what's available.
6. When the user selects a custom persona, the council Step 4 grounding assignment uses the persona's `default_grounding_source_type` instead of the council-mode default mapping.
7. If the custom has a `selection_heuristic`, surface it alongside the bundled selection heuristics during roster declaration when its trigger condition matches the engagement scope.

---

## Adding and removing custom personas

**Add** via direct file edit + index update — there is no `/persona init` command in v1 (deferred to Batch F). The user creates `personas/<id>.yaml` manually following the schema, then adds an entry to `personas/_index.yaml`. Both writes commit at close time.

**Remove** by deleting the index entry. The persona file may stay on disk (recoverable) — the absence from the index is what excludes it from the council pool.

**Modify** by editing the persona file directly. Changes take effect on the next council session (no caching).

---

## Done criteria

- [ ] A custom persona at `personas/pension-specialist.yaml` with the 4 required fields appears in the council roster declaration tagged `(custom)` alongside the bundled 7
- [ ] Selecting it for a council session causes Step 4 grounding to assign it the persona's `default_grounding_source_type`, mapped to a real tool/source per the table above
- [ ] An ID collision (custom persona `id: cfo-finance` when bundled `cfo-finance` exists) is surfaced as a warning and the custom is skipped
- [ ] A persona file in `personas/` without an index entry is silently ignored (no warning, no roster appearance)
- [ ] A persona file with a missing required field surfaces a validation error and is excluded from the pool
- [ ] When a custom persona's `default_grounding_source_type` matches a bundled persona's grounding source for the same fetched target, asymmetric reassignment fires (lower-priority persona moves to `web-fetch-other`)
- [ ] A custom persona's `selection_heuristic` text appears at roster-declaration time when its trigger matches the engagement scope

---

## Anti-patterns

1. **Custom persona that duplicates a bundled lens.** If your custom is "another finance perspective," use the bundled `cfo-finance` with a different grounding rather than creating a near-duplicate. Council strength comes from lens diversity, not lens count.
2. **Custom persona with no grounding source type.** The asymmetric grounding rule (council-mode.md § Step 4) is load-bearing for council quality. A persona that grounds in "general knowledge" produces sycophantic agreement.
3. **Editing bundled personas via the custom path.** The bundled 7 are versioned with the skill release; editing them via `personas/cfo-finance.yaml` won't take effect (collision rule). To customize the bundled finance persona, file a Batch-F-or-later issue to extend the bundled persona schema with override hooks.
4. **Persona file with `lens` content longer than ~150 words.** Long lens descriptions degrade persona dispatch — the model spends budget re-reading the lens instead of reasoning. Keep lens to one paragraph; if you need more depth, the persona is probably two personas in one.
5. **Adding personas mid-engagement.** Custom persona additions take effect on the next council session, not the active one. To use a new persona in the current council, add it BEFORE invoking `/council`. Adding mid-council confuses the synthesis step.
6. **Adding fields beyond the schema (e.g., `voice_profile`, `banned_phrases`, `confidence_score`).** The schema deliberately mirrors the bundled persona shape. Extending it asymmetrically breaks the collision rule and creates two classes of persona where there should be one. File a Batch-F+ issue to extend the schema for bundled AND custom together.
7. **Using `econometric-table` as a grounding source type for a wage claim.** Econometric tables are CPI, unemployment, GDP — never wages. Wage grounding goes through `market-mcp-role-data`. This mirrors the StatCan-MCP-vs-Market-MCP boundary in `tools-available.md`.
