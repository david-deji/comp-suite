# Engagement Modes — comp-comms-builder

Named taxonomy of work-shape modes within the existing commands. Closes the
friction where the agent has to invent partial-flow shapes mid-session because
the skill has no name for them. Read this file when the engagement-comms-config
`engagement_mode` field is not `full-cascade`, or when the user's request does
not match the canonical cascade shape.

**File length target:** 150-200 lines (taxonomy table + per-mode detail + rules
+ uniform mode declaration syntax).

---

## Mode taxonomy (v1, 6 modes)

| Mode | Steps run | Steps skipped | Typical artifact | Example trigger |
|---|---|---|---|---|
| `full-cascade` | full /cascade chain (exec one-pager → all-hands → manager FAQ → HRBP memo) | none | All 4 artifacts in dependency order | "/cascade pharmacy-fy26" |
| `single-artifact` | one /draft only | other artifacts in catalog | One artifact (e.g., manager-faq DOCX) | "/draft manager-faq" |
| `bilingual-co-draft` | FR-first co-draft + parallel EN | translation-style EN-from-FR | Bilingual artifact pair (FR + EN) | "/draft all-hands-announcement" with bilingual config |
| `revision-only` | /review diff against prior version + targeted edits | full /draft regen | Diff report + targeted edits | "/review all-hands-announcement" on existing draft |
| `voice-extraction-only` | /ingest speaker registers only | audience profiles, anti-pattern surfacing, channel rules detection | org-comms-profile.yaml `speaker_registers.*` only | "/ingest" with `extract: voice-only` flag |
| `glossary-merge` | /glossary promote workflow | full ingest, all draft work | Updated `vocabulary/fr-ca-glossary.yaml` | "/glossary promote" |

---

## Per-mode detail

### `full-cascade`

- **mode_id**: `full-cascade`
- **steps_run**: exec-one-pager → all-hands-announcement → manager-faq → hrbp-enablement-memo (dependency order enforced)
- **steps_partial**: none
- **steps_skipped**: none
- **state_shape**: `full` — all engagement-comms-config fields populated
- **artifact_shape**: up to 4 artifacts, up to 16 file writes (accounting for bilingual variants and multiple formats)
- **trigger_examples**: "/cascade pharmacy-fy26", "full cascade", "render the bundle", "produce the full comms package"
- **pre_engagement_only**: false
- **state_shape_variant**: `full`

### `single-artifact`

- **mode_id**: `single-artifact`
- **steps_run**: one /draft call for the specified artifact type
- **steps_partial**: none
- **steps_skipped**: all other artifacts in the cascade catalog
- **state_shape**: `partial` — only the matching artifact entry in `artifacts[]` is active; others null-out rules pending v1.1
- **artifact_shape**: one artifact (HTML, DOCX, or PPTX depending on artifact type)
- **trigger_examples**: "/draft manager-faq", "/draft exec-one-pager", "write the memo", "draft the announcement"
- **pre_engagement_only**: false
- **state_shape_variant**: `partial`
- **decision_log**: `null_out_rules_pending_v1_1` for sibling artifacts not produced in this mode

### `bilingual-co-draft`

- **mode_id**: `bilingual-co-draft`
- **steps_run**: FR-first render + EN co-draft in same session for one artifact
- **steps_partial**: none
- **steps_skipped**: cascade to other artifacts (unless combined with full-cascade)
- **state_shape**: `full` — bilingual variant; both language entries in artifact `approval_stage` map populated
- **artifact_shape**: bilingual artifact pair — FR-CA primary + EN secondary (same artifact type, two language renders)
- **trigger_examples**: "/draft all-hands-announcement" with `languages: [fr-ca, en]` in config, "bilingual draft", "FR and EN together"
- **pre_engagement_only**: false
- **state_shape_variant**: `full`
- **constraint**: FR MUST be drafted first. EN derived from FR source content, not from translation. See C04 (contracts.md).

### `revision-only`

- **mode_id**: `revision-only`
- **steps_run**: /review diff against prior version (v(N) vs v(N-1)), targeted edits, anti-pattern re-check, glossary check
- **steps_partial**: /draft (edits applied to existing content only — no full regen)
- **steps_skipped**: full /draft regen pipeline, brand-template re-application unless structural change
- **state_shape**: `partial` — `current_version` incremented; diff tracked; no fresh recommendation read unless drift detected
- **artifact_shape**: diff report (chat-only) + edited artifact file at v(N)
- **trigger_examples**: "/review manager-faq", "diff this", "anti-pattern check", "show what changed"
- **pre_engagement_only**: false
- **state_shape_variant**: `partial`

### `voice-extraction-only`

- **mode_id**: `voice-extraction-only`
- **steps_run**: /ingest speaker registers sub-phase only
- **steps_partial**: none
- **steps_skipped**: audience profile inference, channel rules detection, anti-pattern surfacing, brand discovery, workshop synthesis
- **state_shape**: `standalone` — only `speaker_registers.*` block of org-comms-profile.yaml is written
- **artifact_shape**: org-comms-profile.yaml (speaker_registers section only)
- **trigger_examples**: "/ingest" with `extract: voice-only`, "just extract the voice", "only the speaker register"
- **pre_engagement_only**: false
- **state_shape_variant**: `standalone`
- **decision_log**: `null_out_rules_pending_v1_1` for omitted /ingest sub-phases

### `glossary-merge`

- **mode_id**: `glossary-merge`
- **steps_run**: /glossary promote workflow (surface pending terms, validate, merge to canonical glossary)
- **steps_partial**: none
- **steps_skipped**: all draft work, all ingest work
- **state_shape**: `standalone` — only the glossary files are touched; no engagement-comms-config writes
- **artifact_shape**: updated `vocabulary/fr-ca-glossary.yaml`
- **trigger_examples**: "/glossary promote", "merge the glossary terms", "glossary merge"
- **pre_engagement_only**: false
- **state_shape_variant**: `standalone`

---

## Uniform mode declaration syntax

Add these fields to `engagement-comms-config.yaml` at the top level:

```yaml
engagement_mode: full-cascade          # required; mode_id from v1 taxonomy above
                                       # default: full-cascade
mode_steps_run: []                     # populated from taxonomy at declaration time
mode_steps_skipped: []                 # populated from taxonomy at declaration time
mode_steps_partial: []                 # populated from taxonomy at declaration time
pre_engagement_only: false             # true only if mode produces non-cycle artifact
state_shape_variant: full              # full | partial | standalone | pre_engagement
                                       # full         = standard schema, all fields populated
                                       # partial      = mode-specific null-out applies
                                       # standalone   = mode runs outside canonical cascade chain
                                       # pre_engagement = artifact lands in pre_engagement_artifacts[]
```

---

## Null-out scope (v1)

No comms mode ships explicit field-level null-out rules in v1. Workers populating
partial-flow state for any mode MUST emit a `decision_log` entry of
`decision_type: null_out_rules_pending_v1_1` so the gap is visible. v1.1 will
add per-mode null-out rules driven by production friction.

---

## Anti-pattern (refused)

Declaring a mode mid-session without a name. If the work shape does not fit any
v1 mode, the agent surfaces:

> "This looks like a sub-shape we don't have a name for. Options:
> A. Shoehorn into the closest mode and accept the schema mismatch.
> B. Propose a v1.1 mode and document now — I'll log the gap."

Does NOT silently invent a new mode_id.

---

## How modes interact with commands

Commands (`/draft`, `/cascade`, `/ingest`, `/review`, `/glossary add`) are entry
points. Modes refine WHICH variant of the command runs. Default mode per command
is the "full" variant. Mode can be overridden by an explicit user signal or by a
config-vs-request mismatch surfaced at opening-sequence pre-flight check 4.
