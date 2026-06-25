# `pay-equity-engagement.yaml` — Schema Template

Operator-authored config sibling to comp-advisor's main `engagement-config.yaml`.
Read by `references/pay-equity-qc-protocol.md` at `/init pay-equity-qc` to seed the
engagement, drive obligation routing, and configure side-deliverables.

This file is INPUT. The 22 in-skill tools own all generated state files
(`engagement.json`, `job-classes.json`, etc.). Operators do not hand-edit those.

## File location

Lives at `engagements/<client-slug>/pay-equity/pay-equity-engagement.yaml`, persisted via the
pay-equity tooling's own persistence layer (`scripts/pay_equity/persistence_gdrive.py`; migration to the v2 model tracked as MIM-0042).

## Full schema

```yaml
# pay-equity-engagement.yaml
# Operator-authored config — read at /init pay-equity-qc

engagement_kind: pay-equity-qc       # always this literal — discriminator for the protocol

# --- Client identity ---
client:
  name: "Acme Distribution inc."              # legal employer name (appears on affichages)
  neq: "0000000000"                  # Numéro d'entreprise du Québec (10 digits, optional)
  employee_count: 850                # current Québec workforce — drives size_tier auto

# --- Exercise framing ---
exercise:
  type: maintenance                  # initial | maintenance
  reference_period_start: "2025-01-01"
  reference_period_end: "2025-12-31"
  pay_period_frequency: biweekly     # weekly | biweekly | semimonthly | monthly
  has_union: true

  # Maintenance-only fields (required if type == maintenance):
  initial_had_committee: true        # was the initial exercise conducted with a comité?
  has_accredited_association: true   # at least one accredited union covering affected employees?
  intended_maintien_mode: employer_solo
    # employer_solo | committee | joint_with_union
    # If employer_solo AND (initial_had_committee OR has_accredited_association),
    # tool computes participation_required = true and rewrites mode to
    # employer_solo_with_participation. Operator cannot opt out.

# --- Multi-establishment (optional) ---
establishments:
  - name: "Centre de distribution Exemple"
    location: "Ville-Exemple, QC"
    employee_count: 320
  - name: "Magasin IGA Marché des Saveurs"
    location: "Montréal, QC"
    employee_count: 530

# --- Threshold ---
threshold_reach_year: 2025           # year the company crossed Loi threshold (10+ employees);
                                     # computes initial_exercise_deadline (4 yrs from this date
                                     # under Art. 38)

# --- Operator (single supported profile in v1) ---
operator:
  mode: expert                       # ALWAYS "expert" in v1 — guided mode collapsed
  language: fr                       # fr | en — chat language; affichages always FR
  entry_mode: paste                  # paste | csv | guided  (Phase 3 job-class entry preference)

# --- Persistence ---
# Pay-equity working data persists via the pay-equity tooling's own layer
# (scripts/pay_equity/persistence_gdrive.py). Migrating that layer to the v2 model
# (local $STATE_ROOT or backend entities) is tracked as MIM-0042 — no persistence
# block to configure here. comp-advisor schema state (master/engagement/cycle/
# decision) persists automatically to the market MCP backend, not via this file.

# --- Side deliverables (optional) ---
# When the operator wants non-statutory output (executive deck, board memo,
# workforce explainer), declare each one here. Brand kit + audience archetype
# activate per side-deliverable per references/pay-equity-render-branching.md.
side_deliverables:
  - kind: executive_deck             # any descriptive label
    audience_archetypes: [board_member, exec_team]
    brand: acme-grocery             # references one of engagement-config.deck.brand_kits
  - kind: workforce_memo
    audience_archetypes: [workforce_floor]
    language: en                     # per-deliverable language override (engagement language by default)
```

## Field reference

### `engagement_kind` (literal, required)

Always the string `pay-equity-qc`. The router uses this discriminator to load
`references/pay-equity-qc-protocol.md` and bypass the comp-advisor 0-7 phase model.

### `client.*` (required)

- `name` — appears verbatim on affichages and statutory documents
- `neq` — Quebec enterprise number, optional but recommended (10 digits)
- `employee_count` — drives auto-derivation of `size_tier`:
  - `< 10` → ValidationError (Loi does not apply, Art. 4)
  - `10–49` → SizeTier.SMALL
  - `50–99` → SizeTier.MEDIUM
  - `100+` → SizeTier.LARGE

### `exercise.*` (required)

- `type` — `initial` (first exercise) or `maintenance` (5-year audit cycle)
- `reference_period_start` / `reference_period_end` — date range (ISO 8601) used by
  compensation tools to scope wages
- `pay_period_frequency` — drives interest-engine per-pay-period computation (R3)
- `has_union` — affects committee composition rules and consultation requirements
- For maintenance only: `initial_had_committee`, `has_accredited_association`,
  `intended_maintien_mode` (drives Art. 76.2.1 participation gate)

### `establishments[]` (optional)

If multi-establishment, declare each with name, location, and employee count.
Affichages must be posted at each location separately under Art. 76.

### `threshold_reach_year` (required)

The year the company first reached 10+ employees. Used to compute the
`initial_exercise_deadline` (4 years from threshold reach under Art. 38). For
companies that have always been over the threshold, supply the founding year or
the earliest year on record.

### `operator.*`

- `mode` — must be `expert` in v1 (the only supported profile)
- `language` — `fr` or `en`. Drives chat language and the operator decision log
  language. Affichages remain French regardless. Side-deliverables follow this
  setting unless overridden per-deliverable.
- `entry_mode` — operator's preference for Phase 3 (job-class entry):
  - `paste` — paste a JSON/CSV/YAML block of all classes at once
  - `csv` — paste a CSV-only block; orchestration parses
  - `guided` — class-by-class collection (used by Path C in maintenance Phase M1 too)

### `persistence.*`

Inherits the comp-advisor `engagement-config.persistence` block (see
`references/persistence-and-ledger.md` § Backend detection). Per-engagement override
may point to a different repo, but `folder_visibility` must be `private` — the skill
refuses to write to a publicly shared folder.

### `side_deliverables[]` (optional)

Each entry triggers the brand kit + audience archetype mechanism for that one
deliverable per `references/pay-equity-render-branching.md`. May be added at /init
or appended mid-engagement when the operator asks for an additional non-statutory
output.

| Field | Required | Notes |
|-------|----------|-------|
| `kind` | yes | descriptive label (`executive_deck`, `board_memo`, `workforce_explainer`) |
| `audience_archetypes` | yes | list of archetype IDs from `references/persona-library.md` |
| `brand` | no | brand kit slug; falls back to `engagement-config.deck.brand` if absent |
| `language` | no | `fr` or `en`; falls back to `operator.language` if absent |

## Why this is separate from `engagement-config.yaml`

Comp-advisor's main `engagement-config.yaml` covers the brand-and-deck cycle
(audience archetypes, persistence backend, deck production mode). The pay equity
exercise is a parallel top-level workflow with a different shape — different
phases, different deliverables, different statutory constraints. Combining the
two would either bloat `engagement-config.yaml` with pay-equity-only fields or
strip pay-equity of clarity. They share the persistence backend and brand kit
references but otherwise stand alone.
