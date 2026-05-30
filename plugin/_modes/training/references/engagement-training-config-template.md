# engagement-training-config.yaml — Schema & Field Documentation

The full schema for `engagement-training-configs/<slug>.yaml`. Loaded by `/init` walkthrough and by every mode that parses pasted YAML.

Schema version: 1.

---

## Full schema

```yaml
# engagement-training-configs/<engagement-slug>.yaml

schema_version: 1

engagement_mode: full-bundle          # required; mode_id from references/engagement-modes.md
                                      # default: full-bundle. Other v1 values: single-audience,
                                      # cascade-only, ingest-only, audience-design-only,
                                      # council-deliberation. Drives step routing in generate-,
                                      # cascade-, and ingest-protocol.md.

engagement:
  slug: <kebab-case-stable-id>      # required, immutable; SHARED with comp-team-transformer team.slug if same engagement
  name: <free text>                 # required
  domain: compensation              # constant
  language: en                      # constant for v1

audiences:
  enabled:                          # required, ≥1 entry; subset of v1 audiences
    - employees                     # broad workforce, lowest comp-literacy
    - managers                      # people managers, cascade-eligible
    - hrbps                         # HR business partners
    - execs                         # executives / leadership
  default_posture: broadcast-with-checkpoints  # only valid value in v1

depth_layers:
  # Per audience, max depth that may be rendered.
  # Depth = 1 (headline only) → 4 (headline + mechanics + tradeoffs + governance).
  employees: 1
  managers: 2
  hrbps: 3
  execs: 4

cycle:
  stages: []                        # populated: [{name, week_offset, anchor_date, gating: live|prep|slack}]
  current_stage: null               # auto-computed from anchor_event + today's date
  current_week_offset: null         # auto-computed
  anchor_event: null                # e.g. "effective date YYYY-MM-DD"
  last_inherited: null              # ISO date — when cycle was last inherited from sibling skill

sources:
  transformation_briefs: []         # paths/IDs to comp-team-transformer transformation-brief.md (preferred)
  process_docs: []                  # paths/IDs to markdown/PDF policy / guideline / FAQ docs
  prior_pptx: []                    # paths/IDs to prior training decks

voice:
  tone: consulting-peer             # default; mirrors siblings
  audience_voice:
    employees: clear-reassuring
    managers: direct-decisive
    hrbps: technical-collaborative
    execs: strategic-brief
  brand:
    org_slug: <slug>                # resolves brand kit per the shared library-resolution
    # OR
    # brand: neutral

redaction:
  names: titles-and-functions       # required, hard rule
  salary: banded                    # required
  vendors: kept                     # required
  company_name: kept-private        # required
  whitelist: []                     # operator-approved exceptions to person-name regex (optional)

personas:
  bundled_pack: comp-training-v1    # default (5 personas — see persona-library.md)
  custom: []                        # additional per-engagement personas (paths under personas/)

interactive_blocks:
  embedded_or_separate: embedded    # embedded (in deck slides) | separate (standalone cards)
  block_types_enabled:
    - poll
    - quiz
    - scenario_card
    - retrieval_prompt

persistence:
  drive_folder_id: <folder-id>      # SHARED with comp-advisor + comp-team-transformer
  visibility: private               # enforced
  enabled: true                     # if false, paste-mode

cycles_trained:
  # Index of training runs. Updated by /generate.
  - cycle_slug: <e.g., year-end-2026>
    state: ingested | message-mapped | rendered | cascaded
    audiences_rendered: [employees, managers, hrbps, execs]
    last_render: <ISO date>
    sources_used: [list of source IDs]
    delivery_targets:
      employees: "Week +1 / Effective / target date YYYY-MM-DD"
      managers: "Week 0 / Cascade / target date YYYY-MM-DD"
      hrbps: "Week -2 / Prep / target date YYYY-MM-DD"
      execs: "Week -4 / Approval / target date YYYY-MM-DD"
```

---

## Field documentation

### `engagement.*`

- **`slug`** — Stable kebab-case ID. Immutable after creation. Matches `^[a-z][a-z0-9-]*$`. SHARED with comp-team-transformer's `team.slug` if the same engagement is also under transformation.
- **`name`** — Human-readable engagement name. Used in deck cover slides ("Comp Training: <name>").
- **`domain`** — Constant `compensation` in v1. Reserved for future expansion.
- **`language`** — Constant `en` in v1. FR-CA deferred to v2 (`/translate` mode).

### `audiences.*`

- **`enabled`** — Subset of {employees, managers, hrbps, execs}. At least one required. Determines which audiences `/generate batch` will render.
- **`default_posture`** — Only valid value in v1: `broadcast-with-checkpoints`. v2 will add `knowles-80-20` per-audience.

### `depth_layers.*`

Per audience in `audiences.enabled`, an integer 1-4:
- **1** — headline + 1 example. Suitable for employees.
- **2** — headline + mechanics + objection-handling + cascade prompts. Suitable for managers.
- **3** — headline + mechanics + edge cases + escalation paths. Suitable for HRBPs.
- **4** — headline + tradeoffs + budget + governance. Suitable for execs.

Constraint enforced at `/ingest` Workshop synthesis: HRBP depth ≥ manager depth ≥ employee depth on the same fact (when all three are non-null). Execs see different cuts — depth-4 framing, not deeper-of-the-same.

### `cycle.*`

Inherited from sibling `comp-team-transformer/team-configs/<slug>.yaml` if engagement-slug matches. Otherwise populated manually or via cross-skill cycle-discovery.

- **`stages`** — List of `{name, week_offset, anchor_date, gating}`. `gating` ∈ {live, prep, slack}.
- **`current_stage`** — Computed at Phase 0 from `anchor_event` + today's date.
- **`current_week_offset`** — Computed at Phase 0 from `anchor_event` + today's date.
- **`anchor_event`** — Free-text reference, typically "effective date YYYY-MM-DD".
- **`last_inherited`** — ISO date of last sync from sibling skill. Manual operation in v1 (re-run `/init` or edit YAML directly).

### `sources.*`

Loose-coupled. Three categories, all optional:

- **`transformation_briefs`** — Preferred. Direct handoff from comp-team-transformer's `/transform` output. Schema-aware ingestion possible.
- **`process_docs`** — Markdown or PDF policy / guideline / FAQ documents. Generic parsing.
- **`prior_pptx`** — Prior training decks for repurposing/reskinning. PPTX text content extracted; layouts ignored.

Empty arrays are valid — `/ingest` accepts ad-hoc source paste at runtime.

### `voice.*`

- **`tone`** — Engagement-wide tone default. `consulting-peer` is the trilogy default.
- **`audience_voice`** — Per-audience overrides. Drives copy style in PPTX text and facilitator guides.
- **`brand.org_slug`** — Engagement brand kit identifier. Resolves to `branding/<org_slug>/` in shared persistence. `_default` fallback always available.
- **`brand: neutral`** — Skip default-kit branding (rare; for external-audience artifacts).

### `redaction.*`

All keys required. Defaults match the trilogy hard rules:
- **`names: titles-and-functions`** — No person names anywhere on disk.
- **`salary: banded`** — Salary → band/percentile.
- **`vendors: kept`** — HRIS / tool / survey vendor names retained.
- **`company_name: kept-private`** — Company name kept in private folder; replaced with `<COMPANY>` only when artifact tagged `audience_tag: external`.
- **`whitelist`** — Optional operator-approved exceptions to the person-name regex (e.g., a vendor name that matches name-pattern). Each entry is reviewed at first appearance.

### `personas.*`

- **`bundled_pack`** — Only valid value in v1: `comp-training-v1` (5 personas). v2 will add `+nbj` opt-in.
- **`custom`** — Additional per-engagement personas. Each entry is a path under `personas/` in shared persistence (e.g., `personas/comp-team-acme-finance-partner.yaml`).

### `interactive_blocks.*`

- **`embedded_or_separate`** — `embedded` (interactive blocks rendered as PPTX slides inline) or `separate` (rendered as standalone markdown cards alongside the deck).
- **`block_types_enabled`** — Subset of {poll, quiz, scenario_card, retrieval_prompt}. Defaults to all four.

### `persistence.*`

- **`drive_folder_id`** — Drive folder ID. Must be the same as comp-advisor and comp-team-transformer for the trilogy to share brand kits and persona libraries.
- **`visibility`** — Must be `private`. Skill verifies before any write.
- **`enabled`** — `true` (default) or `false` (paste-mode fallback).

### `cycles_trained` (auto-managed)

Index of training runs for this engagement. Updated by `/generate` after each successful render. Operator does not edit directly.

- **`cycle_slug`** — Identifier for the training cycle (e.g., `year-end-2026`).
- **`state`** — `ingested` (message-map exists) → `message-mapped` (council reviewed) → `rendered` (decks produced) → `cascaded` (cascade kit produced).
- **`audiences_rendered`** — Subset of `audiences.enabled` that has produced decks for this cycle.
- **`last_render`** — ISO date of last `/generate` call for this cycle.
- **`sources_used`** — IDs from `sources.*` consumed during this cycle's `/ingest`.
- **`delivery_targets`** — Per audience, the `delivery_target` metadata stamped on that audience's deck. Read for warning at next `/generate` if target is in the past.

---

## Field documentation

### `engagement_mode`

Controls which steps run in this engagement. Must match a `mode_id` in
`references/engagement-modes.md`. Default is `full-bundle` when absent (and
`decision_type: mode_defaulted_silently` is logged). The field drives step routing
in `generate-protocol.md`, `cascade-protocol.md`, and `ingest-protocol.md` via the
"## Mode-keyed step routing" section at the top of each protocol.

---

## Validation rules

Enforced at parse time (every mode that loads the config):

- `engagement_mode` ∈ {`full-bundle`, `single-audience`, `cascade-only`, `ingest-only`, `audience-design-only`, `council-deliberation`} when present
- `engagement.slug` matches `^[a-z][a-z0-9-]*$`
- `audiences.enabled` non-empty, all values ∈ {employees, managers, hrbps, execs}
- `depth_layers.<audience>` ∈ {1, 2, 3, 4} for every audience in `audiences.enabled`
- `redaction.*` keys all present (no missing — hard fail)
- `persistence.visibility == private` if `persistence.enabled == true`
- `personas.bundled_pack == comp-training-v1` (only valid value in v1)
- `cycle.stages[].gating` ∈ {`live`, `prep`, `slack`} when populated
- `interactive_blocks.embedded_or_separate` ∈ {`embedded`, `separate`}
- `interactive_blocks.block_types_enabled` subset of {poll, quiz, scenario_card, retrieval_prompt}

Validation failure → refuse to proceed with the calling mode. Surface specific field + reason.

---

## v2 schema additions (not present in v1)

- `discovery_modes` block (async-form mode added)
- `staleness` block (6-month re-ingest threshold)
- `personas.bundled_pack: comp-training-v1+nbj` option
- `audiences.enabled` extends with `external` (client-facing training)
- `posture: knowles-80-20` per-audience override
- `language: fr-ca` for FR-CA pass

---

## Example (filled config)

See `examples/year-end-cycle/` (not embedded here — examples directory carries the example config alongside the rendered bundle).
