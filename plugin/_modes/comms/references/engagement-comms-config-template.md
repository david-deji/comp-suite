# engagement-comms-config.yaml — Schema & Field Documentation

Full annotated schema for `engagement-comms-configs/<engagement-slug>.yaml`. Loaded by `init-mode-protocol.md` to drive the interview and validate operator-edited configs. Loaded by `draft-protocol.md` and `cascade-protocol.md` to resolve artifacts, languages, and approval stages.

Schema version: 1.

---

## Full schema

```yaml
# engagement-comms-configs/<engagement-slug>.yaml
# Created by: /init
# Persisted to: market MCP backend via engagement_put_section (comms section)

schema_version: 1                          # required; must be 1

engagement_mode: full-cascade              # required; mode_id from engagement-modes.md
                                           # Default: full-cascade (runs the full /cascade chain)
                                           # Other values: single-artifact | bilingual-co-draft |
                                           #   revision-only | voice-extraction-only | glossary-merge
                                           # See references/engagement-modes.md for taxonomy.
                                           # Declare before any /draft or /cascade call.
                                           # If absent at /draft time, defaults to full-cascade and
                                           # logs decision_type: mode_defaulted_silently.

engagement_slug: <kebab-case>              # required; immutable after creation
                                           # MUST match compensation-advisor's slug if type=compensation-advisor
                                           # Format: ^[a-z][a-z0-9-]*$
                                           # Example: pharmacy-fy26

client_slug: <kebab-case>                  # required; resolves org-comms-profiles/<client_slug>.yaml
                                           # Example: acme

cycle_name: "<free text>"                  # required; human-readable cycle name
                                           # Example: "FY26 Annual Wage Review"

created: YYYY-MM-DD                        # required; ISO date; set by /init; do not edit

# ─── Source recommendation ────────────────────────────────────────────────────

recommendation_source:
  type: compensation-advisor               # required
                                           # compensation-advisor — reads checkpoint.yaml or engagement-state.yaml
                                           # manual-paste — reads pasted_summary field below

  engagement_slug: <kebab-case>            # required if type=compensation-advisor
                                           # The compensation-advisor engagement slug
                                           # Reads: engagements/<slug>/checkpoint.yaml (preferred)
                                           #     or engagements/<slug>/engagement-state.yaml (if closed)
                                           # null if type=manual-paste

  scenario_locked: false                   # required; boolean
                                           # false = scenario may still change (soft warning at each draft)
                                           # true = set after compensation-advisor Phase 7 acceptance
                                           # Operator sets this manually; skill does not auto-toggle

  pasted_summary: null                     # required if type=manual-paste; null otherwise
                                           # See compensation-advisor-input-contract.md § 7.4 for schema
                                           # Inline YAML block:
                                           #   schema_version: 1
                                           #   org_name: "<name>"
                                           #   cycle_name: "<name>"
                                           #   effective_date: YYYY-MM-DD
                                           #   cohort: "<description>"
                                           #   scenario_summary: |
                                           #     <multi-line>
                                           #   narrative_frame: "<frame>"
                                           #   key_objections_anticipated: [<list>]
                                           #   budget_envelope: null
                                           #   selection_rationale: null

# ─── Languages ────────────────────────────────────────────────────────────────

languages:
  primary: fr-ca                           # required
                                           # fr-ca — Quebec French (default; Bill 96)
                                           # en — English primary (non-Quebec employer or board-only cycle)
                                           # ISO 639-1 + country; lowercase

  secondary: en                            # nullable
                                           # null — single-language cycle; no secondary draft
                                           # en — English secondary (most Quebec cycles)
                                           # fr-ca — French secondary (rare; EN-primary employer with QC operations)

  glossary_source: vocabulary/fr-ca-glossary.yaml
                                           # path within the local $STATE_ROOT library; LOCAL — not backend
                                           # default shown; do not modify unless maintaining a fork

# ─── Artifacts ────────────────────────────────────────────────────────────────

artifacts:                                 # required; list of 1-4 entries from v1 catalog
                                           # At least one entry required; all 4 is the typical /cascade setup

  - artifact_type: all-hands-announcement  # required; one of the 4 v1 slugs:
                                           #   all-hands-announcement
                                           #   manager-faq
                                           #   hrbp-enablement-memo
                                           #   exec-one-pager

    speaker: chro                          # required; must be valid for this artifact_type
                                           # See valid-combinations-rules.md for valid speaker per artifact

    audience: [all_employees]              # required; list
                                           # Valid values per artifact: see artifact-catalog.md
                                           # Slugs: all_employees, people_managers, hrbps, exec_board

    channel: [email, intranet]             # required; list
                                           # Valid values: email, intranet, docx_distributable, pptx_distributable

    formats: [html, pdf]                   # required; list
                                           # Valid values: html, pdf, docx, pptx, txt
                                           # Must be consistent with channel and artifact_type

    languages: [fr-ca, en]                 # nullable; overrides cycle-level languages for this artifact
                                           # null — inherits from cycle languages.primary + languages.secondary
                                           # Example override: exec-one-pager often [en] even in fr-ca-primary cycles

    current_version: 1                     # required; integer; auto-incremented by /draft
                                           # Starts at 1; incremented on each /draft write

    approval_stage:                        # required; scalar or map (see below)
                                           # Scalar (single language): "drafted"
                                           # Map (multiple languages):
      fr-ca: drafted                       #   fr-ca: <stage>
      en: drafted                          #   en: <stage>
                                           # Valid stages: drafted, chro_review, legal_review, ceo_approved, shipped

    last_drafted:                          # set by /draft; null until first draft
                                           # Scalar or map matching approval_stage structure
      fr-ca: null
      en: null

    last_drift_check_against_recommendation_revision: null
                                           # hash of source recommendation YAML at last draft
                                           # null until first draft
                                           # String (SHA-256 or MD5); compared at next /draft to detect drift

  - artifact_type: manager-faq
    speaker: chro
    audience: [people_managers]
    channel: [docx_distributable]
    formats: [docx]
    languages: [fr-ca]
    current_version: 1
    approval_stage: drafted                # scalar: single language
    last_drafted: null
    last_drift_check_against_recommendation_revision: null

  - artifact_type: hrbp-enablement-memo
    speaker: chro
    audience: [hrbps]
    channel: [docx_distributable]
    formats: [docx]
    languages: [fr-ca, en]
    current_version: 1
    approval_stage:
      fr-ca: drafted
      en: drafted
    last_drafted:
      fr-ca: null
      en: null
    last_drift_check_against_recommendation_revision: null

  - artifact_type: exec-one-pager
    speaker: chro
    audience: [exec_board]
    channel: [pptx_distributable]
    formats: [pptx]
    languages: [en]
    current_version: 1
    approval_stage: drafted
    last_drafted: null
    last_drift_check_against_recommendation_revision: null

# ─── Approval chain ──────────────────────────────────────────────────────────

approval_stages:                           # required; ordered list of stage strings
                                           # Default shown; operator may customize per-engagement
                                           # Custom stages are opaque labels; skill does not validate names
  - drafted
  - chro_review
  - legal_review
  - ceo_approved
  - shipped

# ─── Valid combinations overrides ────────────────────────────────────────────

valid_combinations_overrides: []           # optional; empty list = no overrides
                                           # Per-engagement extensions or restrictions to the bundled registry
                                           # See valid-combinations-rules.md § 2.4 for schema
                                           # Example:
                                           # - artifact_type: all-hands-announcement
                                           #   add_speakers: [vp-ops]
                                           # - artifact_type: manager-faq
                                           #   restrict_formats: [docx]

# ─── Speaker register overrides ──────────────────────────────────────────────

speaker_register_overrides: {}             # optional; empty map = no overrides
                                           # Per-engagement overrides to org-level speaker registers
                                           # See speaker-register-rules.md § 3.6 for schema
                                           # Example:
                                           # chro:
                                           #   sign_off_convention: "Questions? Email your HRBP directly."

# ─── Branding ────────────────────────────────────────────────────────────────

branding:
  org_slug: <client_slug>                  # required
                                           # Resolves branding/<org_slug>/comms-templates/ under $STATE_ROOT
                                           # Typically same as client_slug

  regenerate_at_draft: true                # required; boolean
                                           # true — read fresh branding from $STATE_ROOT on every /draft (default)
                                           # false — use cached brand templates within the session

# ─── Optional: training-designer handoff ────────────────────────────────────

training_handoff:
  enabled: false                           # required; boolean
                                           # true — read message-map.yaml from comp-training-designer
                                           # false — no handoff; standard /ingest interview

  message_map_path: null                   # required if enabled=true; null otherwise
                                           # Path relative to $STATE_ROOT
                                           # Example: cycles/pharmacy-fy26/year-end-2026/message-map.yaml
                                           # See training-designer-handoff.md for details
```

---

## Field validation at `/init`

The `/init` walkthrough validates the following before persisting the config via `engagement_put_section`:

| Check | Rule |
|---|---|
| `engagement_slug` format | Must match `^[a-z][a-z0-9-]*$` |
| `client_slug` format | Must match `^[a-z][a-z0-9-]*$` |
| `languages.primary` | Must be `fr-ca` or `en` |
| `languages.secondary` | Must be `fr-ca`, `en`, or null |
| `artifacts[].artifact_type` | Must be one of 4 v1 slugs |
| `artifacts[].speaker` | Must be valid for the artifact_type per `valid-combinations-rules.md` |
| `artifacts[].channel` | Must be valid for the artifact_type |
| `artifacts[].formats` | Must be valid for the artifact_type and channel |
| `approval_stages` | Must be a list of at least 2 strings including `drafted` and `shipped` |
| `training_handoff.message_map_path` | Must be set (non-null) if `enabled: true` |

Validation failures surface to operator inline during `/init` with the corrected value suggested. The config file is not written until all validations pass.

---

## What this file does NOT contain

- Per-artifact render flow — that lives in `draft-protocol.md` and `cascade-protocol.md`.
- Speaker register schema — that lives in `speaker-register-rules.md`.
- Audience profile schema — that lives in `audience-profile-rules.md`.
- `org-comms-profile.yaml` schema — that lives in SPEC.md § 5.2 and is populated by `/ingest`.
- Valid-combinations registry schema — that lives in `valid-combinations-rules.md`.
