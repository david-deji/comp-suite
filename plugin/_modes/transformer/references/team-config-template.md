# Team Config Template

The team-config YAML is the per-team durable state for `comp-team-transformer`. One file per team, stored at `team-configs/<team-slug>.yaml` in the shared persistence folder. Created by `/init`. Edited manually in v1 (no `/update` track).

This file documents the schema field-by-field, the validation rules enforced at parse time, and the v1/v2 boundary.

---

## Full schema

```yaml
# team-configs/<team-slug>.yaml

schema_version: 1

engagement_mode: full-discovery-to-roadmap  # default; override at session start
                                             # values: full-discovery-to-roadmap | discovery-only
                                             #         diagnose-only | transform-only
                                             #         roadmap-refresh | council-deliberation
                                             # see references/engagement-modes.md for taxonomy

team:
  slug: <kebab-case-stable-id>      # required, immutable after creation
  name: <free text>                 # required
  size_band: solo | 2-3 | 4-7 | 8+  # required, banded — never raw headcount
  domain: compensation              # constant
  language: en                      # constant for v1

org:
  industry: <industry-slug>         # optional — drives industry-context references if registered

scope:
  in_scope: [<list of process names>]    # required, ≥1 entry
  out_of_scope: [<list of process names>] # required (may be empty list, but key must exist)

cycle:
  # POPULATED VIA /discover, NOT pre-configured.
  # /init leaves these blank. /discover cycle-mapping block fills them.
  stages: []                        # populated: [{name, week_offset, anchor_date, gating: live|prep|slack, description}]
  current_stage: null               # populated post-discovery
  current_week_offset: null         # populated post-discovery
  anchor_event: null                # e.g. "effective date YYYY-MM-DD"
  last_discovered: null             # ISO date

voice:
  tone: consulting-peer             # default; may override
  audience_default: comp-team-internal
  upward_audience: vp-people        # used for shareable PPTX
  brand:
    org_slug: <slug>                # resolves brand kit per comp-advisor library-resolution
    # OR
    # brand: neutral                # for external-audience artifacts

redaction:
  names: titles-and-functions       # required, hard rule
  salary: banded                    # required
  vendors: kept                     # required
  company_name: kept-private        # required
  team_size: banded                 # required (already enforced via size_band)

personas:
  bundled_pack: comp-team-v1        # default (5 personas)
  custom: []                        # additional per-team personas (paths under personas/)

persistence:
  drive_folder_id: <folder-id>      # shared with compensation-advisor
  visibility: private               # enforced; skill verifies before any write (no "Anyone with link", no public sharing)
  enabled: true                     # if false, paste-mode

processes:
  # Index of processes under transformation. Updated by /discover and /transform.
  - slug: <process-slug>
    state: discovered | diagnosed | spec'd | shipped
    last_interview: <ISO date>
    last_diagnosis: <ISO date>
    last_transformation: <ISO date>
    discovery_mode: self
```

---

## Field reference

### `team` (required)

- `slug` — kebab-case stable identifier. Used in every artifact path (`processes/<slug>/...`, `discovery/<slug>/...`, `roadmap/<slug>/...`). Immutable after creation: changing it orphans every prior artifact. Must match `^[a-z][a-z0-9-]*$`.
- `name` — human-readable team name. Used in artifact titles and PPTX cover slides.
- `size_band` — one of `solo`, `2-3`, `4-7`, `8+`. Banded by hard rule (per redaction rules). Raw headcount is a banned input pattern.
- `domain` — constant `compensation` for v1. Reserved field for future skills sharing the same architecture.
- `language` — constant `en` for v1. French support deferred to v2.

### `org` (optional)

- `industry` — industry slug for cross-references with comp-advisor's industry-context files (e.g., `grocery`). Optional. When populated and a matching `industry-context-<slug>.md` exists in comp-advisor, that file is read at Phase 0.

### `scope` (required)

- `in_scope` — list of process names this team wants to transform. ≥1 entry required. Free-text names; slugs are derived per process during `/discover`.
- `out_of_scope` — list of process names explicitly out of scope for this engagement. Key required (may be empty list `[]`). Prevents scope drift during interviews.

### `cycle` (populated via `/discover`, not `/init`)

`/init` leaves all `cycle.*` fields blank. The `/discover` cycle-mapping block populates them when `cycle.stages == []`. This is a deliberate v1 design choice — cycle stages are too easy to mis-state without an interview. Pre-configured cycles produce wrong gating decisions.

- `stages` — list of `{name, week_offset, anchor_date, gating, description}`. Populated by `/discover` cycle-mapping.
- `current_stage` — computed at Phase 0 from `anchor_event` + today's date. Cached for session.
- `current_week_offset` — computed at Phase 0. Negative = before anchor; zero = anchor day; positive = after.
- `anchor_event` — free-text event description (e.g., `effective date 2026-09-01`).
- `last_discovered` — ISO date of the most recent `/discover` cycle-mapping run.

### `voice` (required)

- `tone` — defaults to `consulting-peer` (mirrors comp-advisor's default). May override per team.
- `audience_default` — defaults to `comp-team-internal`. Used in markdown working artifacts.
- `upward_audience` — defaults to `vp-people`. Used in shareable PPTX targeting executive readout.
- `brand.org_slug` — resolves the brand kit from `branding/<slug>/` in the persistence folder. When unset, defaults to `branding/_default/`.
- `brand: neutral` — alternative form for external-audience artifacts. Mutually exclusive with `org_slug`.

### `redaction` (required, hard rule)

All five keys must be present. Missing any key fails parse-time validation. Values are constants in v1:

- `names: titles-and-functions` — names redacted to role + function (e.g., "Comp Analyst" not "Marie").
- `salary: banded` — salary figures replaced with `Band <N> midpoint` or `P<percentile> of market`.
- `vendors: kept` — HRIS / tool / vendor names retained for transformation design.
- `company_name: kept-private` — company name kept in private folder, replaced with `<COMPANY>` only on artifacts tagged `audience: external`.
- `team_size: banded` — already enforced via `team.size_band`, declared here for completeness.

Full enforcement rules in `redaction-rules.md`.

### `personas` (required)

- `bundled_pack` — must be `comp-team-v1` in v1. Only valid value. The pack ships 5 personas: HRBP, comp-manager, comp-analyst-operator, hris-tooling, change-management.
- `custom` — list of paths to per-team custom persona YAML files. Loaded additively at council entry. See `persona-library.md` for the custom persona schema.

### `persistence` (required)

- `drive_folder_id` — Google Drive folder ID for the shared comp-advisor persistence root. Required when `enabled: true`.
- `visibility` — must be `private` when `enabled: true`. Skill verifies before any write that the folder is not shared with "Anyone with link" or made public. Hard gate.
- `enabled` — when `false`, skill operates in paste-mode (no automatic writes; user pastes/saves manually).

### `processes` (updated by `/discover` and `/transform`)

Index of processes under transformation. Updated automatically; do not edit manually unless rebuilding state.

Each entry:
- `slug` — kebab-case process identifier.
- `state` — one of `discovered`, `diagnosed`, `spec'd`, `shipped`.
- `last_interview` — ISO date of last `/discover` run.
- `last_diagnosis` — ISO date of last `/diagnose` run.
- `last_transformation` — ISO date of last `/transform` run.
- `discovery_mode` — `self` (only mode in v1). Retained for schema compatibility; v2 may add async-form mode.

---

## Validation rules (parse-time)

Enforced when team-config is loaded at Phase 0:

1. `team.slug` matches `^[a-z][a-z0-9-]*$`. Reject otherwise.
2. `scope.in_scope` is a non-empty list. Reject otherwise.
3. All five `redaction.*` keys are present. Missing any key → hard fail.
4. If `persistence.enabled == true`, then `persistence.visibility == private`. Reject otherwise.
5. `personas.bundled_pack == comp-team-v1`. Only valid value in v1; `+nbj` deferred to v2.
6. Every `cycle.stages[].gating` is one of `live`, `prep`, `slack`. Reject otherwise.
7. `team.language == en` and `team.domain == compensation` (v1 constants).

On any validation failure, surface the specific rule violated and exit. Do not attempt partial loads.

---

## v2 schema additions (not present in v1)

Reserved for v2; do not add in v1 configs:

- `discovery_modes` block — adds `async-form` mode option.
- `staleness` block — adds 6-month threshold for `current_state.md` re-discovery prompts.
- `personas.bundled_pack: comp-team-v1+nbj` — adds Nate B. Jones thinker persona.
- `team.language: fr` — French interview/output support.
- A second-team router for users running multiple teams under one Drive folder.

---

## Example: minimal team-config

```yaml
schema_version: 1
team:
  slug: comp-team-acme
  name: Acme Comp Team
  size_band: 4-7
  domain: compensation
  language: en
scope:
  in_scope:
    - annual wage scale review
    - market benchmarking refresh
  out_of_scope:
    - executive comp design
cycle:
  stages: []
  current_stage: null
  current_week_offset: null
  anchor_event: null
  last_discovered: null
voice:
  tone: consulting-peer
  audience_default: comp-team-internal
  upward_audience: vp-people
  brand:
    org_slug: acme
redaction:
  names: titles-and-functions
  salary: banded
  vendors: kept
  company_name: kept-private
  team_size: banded
personas:
  bundled_pack: comp-team-v1
  custom: []
persistence:
  drive_folder_id: 1AbCdEfGhIjKlMnOpQrStUvWxYz
  visibility: private
  enabled: true
processes: []
```
