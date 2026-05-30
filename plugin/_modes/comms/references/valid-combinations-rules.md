# Valid-Combinations Rules

Registry semantics for the `template_assets/valid-combinations.yaml` file. Loaded by `draft-protocol.md` and `cascade-protocol.md` before any render. Defines how the skill loads the registry, validates a requested tuple, surfaces errors, and applies per-engagement overrides.

---

## Registry overview

The registry file `template_assets/valid-combinations.yaml` defines which tuples of (artifact_type × speaker × audience × channel × format × brand_template) are valid in v1. It ships with the skill bundle. One entry per artifact type.

The registry is the gating mechanism: the skill refuses to render any combination not present in it unless an explicit per-engagement override is configured.

---

### 2.1 Registry schema

```yaml
schema_version: 1

combinations:
  - artifact_type: <slug>               # kebab-case artifact slug
    valid_speakers: [<speaker-slug>, …] # subset of: ceo, chro, vp-ops, hrbp-manager
    valid_audiences: [<audience-slug>, …] # subset of: all_employees, people_managers, hrbps, exec_board
    valid_channels: [<channel-slug>, …] # subset of: email, intranet, docx_distributable, pptx_distributable
    valid_formats: [<format-slug>, …]   # subset of: html, pdf, docx, pptx, txt
    brand_templates:                    # map of format → template path(s)
      <format>: <relative-path-or-expression>
    typical_length_words: <int>         # informational; not a gate
    typical_length_pages: <int>         # informational; not a gate
    typical_length_slides: <int>        # informational; not a gate
    notes: "<free text>"                # render notes for the skill
```

Valid slug sets:

| Field | Valid values |
|---|---|
| `artifact_type` | `all-hands-announcement`, `manager-faq`, `hrbp-enablement-memo`, `exec-one-pager` |
| Speaker | `ceo`, `chro`, `vp-ops`, `hrbp-manager` |
| Audience | `all_employees`, `people_managers`, `hrbps`, `exec_board` |
| Channel | `email`, `intranet`, `docx_distributable`, `pptx_distributable` |
| Format | `html`, `pdf`, `docx`, `pptx`, `txt` |

---

### 2.2 How the skill loads the registry

At the start of any `/draft` or `/cascade` run:

1. Read `template_assets/valid-combinations.yaml` from the skill bundle.
2. Read `engagement-comms-configs/<engagement-slug>.yaml` from Drive.
3. If `valid_combinations_overrides:` is present in the engagement config, merge the overrides into the in-memory registry (see § 2.4 for override semantics).
4. Cache the merged registry for the duration of the render session. Re-read at the next `/draft` invocation.

If `template_assets/valid-combinations.yaml` is missing or unparseable: surface error, abort render. Do not proceed with defaults.

---

### 2.3 Validation at draft time

Before rendering any artifact, the skill validates the requested tuple against the merged registry.

**Validation steps (in order):**

1. Locate the registry entry where `artifact_type` matches the requested artifact slug. If no entry found → invalid combination (see § 2.5).
2. Check that the requested `speaker` is in `valid_speakers`. If not → invalid combination.
3. Check that the requested `audience` is a subset of `valid_audiences`. If not → invalid combination.
4. Check that the requested `channel` is a subset of `valid_channels`. If not → invalid combination.
5. Check that the requested `format` is a subset of `valid_formats`. If not → invalid combination.
6. Resolve `brand_templates` for each requested format. If a format is in `valid_formats` but has no corresponding entry in `brand_templates`, surface a warning (not a hard stop): "No brand template registered for format `<format>`. Rendering with `_default` template."
7. If all checks pass: proceed to render.

---

### 2.4 Per-engagement overrides

Operator may extend or restrict the registry for a single engagement via `valid_combinations_overrides:` in `engagement-comms-config.yaml`.

```yaml
valid_combinations_overrides:
  - artifact_type: all-hands-announcement
    add_speakers: [vp-ops]            # adds to valid_speakers for this engagement only
  - artifact_type: manager-faq
    restrict_formats: [docx]          # removes pdf from valid_formats for this engagement
```

Supported override keys:
- `add_speakers` — appends to `valid_speakers`
- `restrict_speakers` — intersects with `valid_speakers` (narrows, not replaces)
- `add_audiences` — appends to `valid_audiences`
- `restrict_audiences` — intersects with `valid_audiences`
- `add_channels` — appends to `valid_channels`
- `restrict_channels` — intersects with `valid_channels`
- `add_formats` — appends to `valid_formats`
- `restrict_formats` — intersects with `valid_formats`

Override keys that add values expand the registry for this engagement. Override keys that restrict values narrow it. Restrictions take precedence over additions for the same field when both are present.

Overrides are engagement-scoped only. They do not modify the bundled `template_assets/valid-combinations.yaml`.

---

### 2.5 Refusal protocol

When the requested combination is invalid and no override permits it:

**Surface this exact message pattern:**

```
That combination is not in the registry.

Requested: artifact_type=<slug>, speaker=<slug>, audience=<slug>, channel=<slug>, format=<slug>

Valid options for `<artifact_type>`:
  speakers:   <list from registry>
  audiences:  <list from registry>
  channels:   <list from registry>
  formats:    <list from registry>

To enable a new combination for this engagement only, edit `engagement-comms-configs/<slug>.yaml`
and add a `valid_combinations_overrides:` entry. Changes to the bundled registry require
a skill update.
```

Do not attempt a "best-guess" fallback render with a different speaker or channel. Hard stop + refusal message.

If the operator explicitly acknowledges the refusal and says to proceed anyway, refuse a second time. The valid-combinations registry is a hard gate, not a soft warning.

---

### 2.6 v1 registry summary (mirrored from template_assets/valid-combinations.yaml)

| Artifact | Valid speakers | Valid audiences | Valid channels | Valid formats |
|---|---|---|---|---|
| `all-hands-announcement` | `ceo`, `chro` | `all_employees` | `email`, `intranet` | `html`, `pdf` |
| `manager-faq` | `chro`, `vp-ops` | `people_managers` | `docx_distributable` | `docx`, `pdf` |
| `hrbp-enablement-memo` | `chro` | `hrbps` | `docx_distributable` | `docx`, `pdf` |
| `exec-one-pager` | `chro` | `exec_board` | `pptx_distributable` | `pptx` |

The actual registry data lives in `template_assets/valid-combinations.yaml` (owned by Worker C). This table is a read-only summary for quick reference. In case of discrepancy, the YAML file is authoritative.

---

### 2.7 What this file does NOT contain

- The actual registry YAML data — that lives in `template_assets/valid-combinations.yaml`.
- Per-artifact length caps and section requirements — those live in `artifact-catalog.md`.
- Speaker register content — that lives in `speaker-register-rules.md`.
- Render flow — that lives in `draft-protocol.md` and `cascade-protocol.md`.
