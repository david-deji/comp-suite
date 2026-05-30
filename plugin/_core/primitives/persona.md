# Persona Primitive

Resolves persona context for the active mode and engagement, then formats a render block for prompt injection.

This is **CC-harness glue**. The persona shape (id, label, lens, default_grounding_source, selection_heuristic) and the comp-domain persona library (segment × role × level matrix) live in **mode-specific** reference files — not here. Per spec § 6 (port-from-v1), the v1 persona shape is restored to mode references; this primitive describes how the orchestrator reads them.

## Why this is glue, not a port

v1 had a single `advisor/references/persona-library.md` (the library content) and embedded resolution logic across multiple files. v2 separates them:

| Concern | v1 location | v2 location |
|---|---|---|
| Persona library content | `advisor/references/persona-library.md` | `$ASSET_ROOT/_modes/<mode>/references/persona-library.md` (verbatim port; mode-scoped) |
| Per-org persona instances | (state — outside v1) | `$STATE_ROOT/_orgs/<slug>/personas.yaml` (validated against `$ASSET_ROOT/_core/schemas/personas.schema.json`) |
| Resolution logic (this file) | (embedded across SKILL.md + library) | `_core/primitives/persona.md` (NEW — orchestrator contract) |

## Inputs

- `org_slug` — required, identifies which org's personas.yaml to load
- `mode` — required, identifies which mode's persona-library.md to consult for taxonomy
- `engagement_id` — optional, for engagement-specific persona overrides if any

## Outputs

A dict with these keys:

- `personas` — list of persona dicts from `$STATE_ROOT/_orgs/<slug>/personas.yaml`
- `library_taxonomy` — segment/role/level matrix loaded from `$ASSET_ROOT/_modes/<mode>/references/persona-library.md`
- `render_block` — formatted markdown string for prompt injection, listing each persona's id, label, lens, and grounding source per v1 shape

## Resolution flow

1. Read `$STATE_ROOT/_orgs/<org_slug>/personas.yaml`.
   - If missing: create empty skeleton (no personas defined yet) and emit a warning. Do NOT crash; some engagements don't need personas at first.
   - If present: validate against `$ASSET_ROOT/_core/schemas/personas.schema.json`. On schema failure, write `$STATE_ROOT/_orgs/<org_slug>/personas-validation-errors.md` and return `personas: []` with a warning.
2. Read `$ASSET_ROOT/_modes/<mode>/references/persona-library.md` for taxonomy. The library is the canonical mode-specific persona catalog (segment × role × level matrix per v1 shape).
3. Cross-reference each persona in `personas.yaml` against the library taxonomy. Personas that reference a `segment`, `role`, or `level` not present in the library get a `[unverified]` tag in the render block.
4. For each persona, format the render block using the v1 shape:

   ```
   ### Persona: {label} ({id})
   - Lens: {lens}
   - Grounding source: {default_grounding_source}
   - Selection heuristic: {selection_heuristic}
   ```

5. Concatenate all render blocks under a `## Personas` heading.

## Asserts and edge cases

- `org_slug` must exist as a directory under `$STATE_ROOT/_orgs/`. If not, this primitive errors (engagement-loader should have caught it earlier).
- `mode` must have a directory under `$ASSET_ROOT/_modes/<mode>/`. If `persona-library.md` is missing in that mode, return an empty taxonomy and warn (not all modes use personas — billing modes wouldn't, for example).
- An empty `personas.yaml` (no personas defined) is valid. Return `personas: []` with no warning. The mode decides whether to prompt the user to define personas at engagement entry.
- Persona schema violations are non-fatal: the primitive returns the partial-valid set plus a validation-errors file. Hard failure would block engagement load.

## Validation against schema

Per spec § 7.4, validates `$STATE_ROOT/_orgs/<slug>/personas.yaml` against `$ASSET_ROOT/_core/schemas/personas.schema.json`. The schema enforces the v1 shape: each persona has `{id, label, lens, default_grounding_source, selection_heuristic}` plus optional fields.

```bash
python3 -c "
import sys, json, yaml
try:
    import jsonschema
except ImportError:
    sys.stderr.write('FATAL: jsonschema not installed — see $ASSET_ROOT/README.md § Setup\n')
    sys.exit(2)
with open('$ASSET_ROOT/_core/schemas/personas.schema.json') as f:
    schema = json.load(f)
with open('$STATE_ROOT/_orgs/<slug>/personas.yaml') as f:
    data = yaml.safe_load(f)
errors = list(jsonschema.Draft202012Validator(schema).iter_errors(data))
print(json.dumps([str(e.message) for e in errors]))
"
```

## Empty-state initialization

When `personas.yaml` doesn't exist for a new org, the primitive creates this skeleton:

```yaml
schema_version: "2.1.0"
org_slug: <slug>
personas: []
```

Empty `personas: []` is the correct default; users define personas as engagements demand them. The mode-dispatcher does not auto-populate from the library taxonomy.

## Persona-library cross-ref

Each mode's `persona-library.md` is the source of taxonomy. The orchestrator reads it lazily (only when a persona references a category from it). For modes without persona-library.md (e.g., a future billing mode), the primitive returns `library_taxonomy: null` and skips cross-validation.

## Acceptance

- Test scenario 02 (advisor cold-start) verifies: a fresh org gets `personas.yaml` skeleton on first engagement, render block returns empty under `## Personas` heading without crashing.
- Test scenario 09 (mode-plugin-add-fifth) verifies: a new mode without `persona-library.md` does not crash this primitive.
