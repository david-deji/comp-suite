# Compensation-Advisor Input Contract

Defines exactly which fields comp-comms-builder reads from compensation-advisor's output files, in what priority order, how drift is detected, and the manual-paste fallback schema when no compensation-advisor engagement-state is present.

Loaded by `draft-protocol.md` and `cascade-protocol.md` before reading the source recommendation.

---

## Source files

Two possible source files, read in this priority order:

1. `engagements/<engagement-slug>/checkpoint.yaml` — preferred if the compensation-advisor engagement is mid-flight (not yet closed). Contains the working state at the last `/checkpoint` call.
2. `engagements/<engagement-slug>/engagement-state.yaml` — used if `engagement_status: closed` or if `checkpoint.yaml` is absent.

Path is resolved using `engagement-comms-config.yaml recommendation_source.engagement_slug`. If `recommendation_source.type == manual-paste`, skip file reads entirely and read `pasted_summary` field instead (see § 7.4).

---

### 7.1 Required fields

These fields must be present in the source file. If any required field is missing or null, surface an error and abort the draft:

```
Source recommendation is missing required field: <field_name>
Path checked: engagements/<slug>/checkpoint.yaml and engagements/<slug>/engagement-state.yaml
Cannot draft without this field. Options:
  1. Return to compensation-advisor and complete the relevant phase.
  2. Use manual-paste fallback: set recommendation_source.type = manual-paste and populate pasted_summary.
```

| Field | Location in source YAML | Used for |
|---|---|---|
| `scenario_chosen` | top-level dict or nested | The approved comp decision: envelope type, path, cohort |
| `audience` | list of archetype strings | Which employee populations are affected; aligns to artifact audience |
| `key_objections_anticipated` | list of strings | Populates manager-faq Top 5 and HRBP edge-case sections |
| `cycle.effective_date` | nested under `cycle:` | Effective date line in all-hands announcement and exec one-pager |
| `cycle.cohort` | nested under `cycle:` | Which employees are in scope; informs hrbp-enablement-memo calculation example |
| `org.name` | nested under `org:` | Organization name used in artifact headers and signatures |
| `narrative_frame` | top-level string | The communication philosophy (e.g., "market-alignment story") used to frame the all-hands announcement |

---

### 7.2 Optional fields

Used if present; skipped gracefully if absent. Do not abort if missing.

| Field | Location | Used for |
|---|---|---|
| `selection_log[]` | list of decision log entries | Informs which framings were considered and rejected (prevents contradicting prior decisions) |
| `prior_engagement_refs[]` | list of engagement slugs | Informs continuity language in multi-year cycles (e.g., "as we did last year...") |
| `scenario_chosen.budget_envelope` | nested | Populates exec one-pager cost impact section |
| `scenario_chosen.rationale` | nested | Optional exec one-pager governance narrative |
| `cycle.anchor_event` | nested | Anchor event for timing context in all-hands |
| `cycle.current_stage` | nested | Whether the comp cycle is in prep, live, or post-distribution |

---

### 7.3 Drift detection

At every `/draft` run, the skill checks whether the source recommendation has changed since the last draft:

**Algorithm:**
1. Hash the full content of the source file (`checkpoint.yaml` or `engagement-state.yaml`) at draft time.
2. Compare against `engagement-comms-config.artifacts[<this-artifact>].last_drift_check_against_recommendation_revision`.
3. If hashes match: no drift. Proceed silently.
4. If hashes differ: drift detected.

**On drift detected:**
```
Source recommendation has changed since v<N-1> was drafted.

Changed file: engagements/<slug>/checkpoint.yaml
Prior check: <ISO date of last draft>

Options:
  refresh         — re-read the source and draft using updated recommendation
  proceed-anyway  — draft using updated source but acknowledge the prior version may be inconsistent
  abort           — stop; review source changes before drafting
```

Wait for operator response. Do not proceed until operator chooses.

**After draft completes (any option):** update `last_drift_check_against_recommendation_revision` with the new hash and update `last_drafted` to today's date.

If `last_drift_check_against_recommendation_revision` is null (first draft): skip drift check, proceed, then set the hash.

---

### 7.4 Manual-paste fallback schema

When `recommendation_source.type == manual-paste`, operator populates `pasted_summary` in `engagement-comms-config.yaml` with a structured block. The skill reads this instead of Drive file lookups.

Required structure for `pasted_summary`:

```yaml
pasted_summary:
  schema_version: 1
  org_name: "<Organization name>"
  cycle_name: "<Cycle name, e.g., FY26 Annual Wage Review>"
  effective_date: "YYYY-MM-DD"
  cohort: "<Description of in-scope employees, e.g., Pharmacy hourly workers>"
  scenario_summary: |
    <Free text describing the approved compensation decision. Should include:
    - What changed (band movement, merit pool, market adjustment)
    - Magnitude (percentage or dollar)
    - Which population is affected
    - Any phasing>
  narrative_frame: "<Communication framing, e.g., market-alignment story | equity-restoration story | merit-emphasis story>"
  key_objections_anticipated:
    - "<First anticipated objection or employee question>"
    - "<Second anticipated objection or employee question>"
    # minimum 3; recommended 5-8
  budget_envelope: null               # optional; used for exec one-pager cost impact
  selection_rationale: null           # optional; used for exec one-pager governance narrative
```

If `pasted_summary` is present but missing required fields, surface the same error as § 7.1 with field names.

Drift detection does not apply to manual-paste (no hash to track against). `last_drift_check_against_recommendation_revision` remains null.

---

### 7.5 Scenario lock behavior

`engagement-comms-config.yaml recommendation_source.scenario_locked` signals whether the compensation-advisor decision is final:

- `scenario_locked: false` — scenario may still change. The skill proceeds but surface a soft warning at the start of each draft: "Note: compensation-advisor scenario is not yet locked. Drafts may need to be revised if the recommendation changes."
- `scenario_locked: true` — scenario is accepted. No warning.

Operator sets `scenario_locked: true` manually after compensation-advisor Phase 7 acceptance. The skill does not toggle this field automatically.

---

### 7.6 What this file does NOT contain

- The compensation-advisor's own data schema — that lives in compensation-advisor's specification.
- Approval-stage tracking mechanics — those live in `approval-stage-tracking.md`.
- Drift detection for speaker registers — speaker register drift is handled in `/ingest` re-run protocol, not here.
- Training-designer handoff mechanics — those live in `training-designer-handoff.md`.
