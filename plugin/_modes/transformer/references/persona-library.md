# Persona Library

Comp-team-transformer ships a bundled-5 persona pack (`comp-team-v1`) for council deliberation. Custom personas registered in `team-config.personas.custom: []` load alongside the bundled pack at council entry.

Loaded by SKILL.md at `/council` entry (standalone or auto-fired from `/transform` / `/roadmap`). Loaded alongside `council-mode.md`.

The bundled pack is at `template_assets/persona_pack_comp-team-v1.yaml` (see for full voice_prompt definitions).

---

## Bundled pack: `comp-team-v1` (5 personas)

| Slug | Name | Lens | Grounding |
|------|------|------|-----------|
| `hrbp` | HR Business Partner | Translation between business and comp; fairness narrative; stakeholder management | qualitative |
| `comp-manager` | Compensation Manager | Budget owner, decision-maker, risk-bearer, defender to leadership | qualitative + quantitative |
| `comp-analyst-operator` | Comp Analyst (Operator) | Does the work — data pulls, modeling, deck-building, benchmarking | operator-experience |
| `hris-tooling` | HRIS / Tooling Lens | System constraints, integration cost, data quality | technical |
| `change-management` | Change Management Lens | Rollout sequencing, adoption risk, resistance, comms | strategic |

Why these five (per IE directive D2): they cover the load-bearing decision dimensions for `/transform` (band assignment) and `/roadmap` (sequencing). Every other persona considered for v1 (finance-partner, payroll-partner, ta-liaison, employee-recipient, NBJ thinker) folds into one of these or is deferred to v2.

**Cuts vs first draft (9 → 5):**

- `finance-partner` → folded into `comp-manager` (both speak in $ impact and risk).
- `payroll-partner` → folded into `hris-tooling` (both speak in integration / data quality).
- `ta-liaison` → folded into `hrbp` (both speak in stakeholder management).
- `employee-recipient` → folded into `change-management` (both speak in adoption / fairness narrative).
- `nbj-thinker` → deferred to v2 (`personas.bundled_pack: comp-team-v1+nbj`).

---

## Custom persona protocol

A team may register custom personas in their team-config:

```yaml
personas:
  bundled_pack: comp-team-v1
  custom:
    - personas/finance-partner.yaml
    - personas/cba-negotiator.yaml
```

### Custom persona schema

Each custom persona file is YAML matching the `persona_pack_comp-team-v1.yaml` persona schema:

```yaml
slug: <kebab-case>
name: <free text>
lens: <one-line description of the perspective>
grounding: qualitative | quantitative | qualitative + quantitative | operator-experience | technical | strategic
voice_prompt: |
  <multi-line system prompt for this persona's voice block during council>
```

### Loading discipline

At `/council` entry:

1. Load the bundled pack from `template_assets/persona_pack_comp-team-v1.yaml`.
2. For each path in `team-config.personas.custom`, attempt to load the persona file from `$STATE_ROOT/_orgs/<slug>/personas/<filename>`.
3. **Collision rule:** if a custom persona has the same `slug` as a bundled persona, **the custom overrides**. Surface to user: "Custom persona `<slug>` overrides bundled persona — using custom voice_prompt."
4. **Validation:** every loaded persona must have all five fields (`slug`, `name`, `lens`, `grounding`, `voice_prompt`). Reject malformed personas with a specific error; do not silently skip.

### Slug uniqueness

Slugs must be unique within a council session. If two custom personas have the same slug (other than overriding a bundled), reject with: "Slug collision in custom personas: `<slug>` appears in `<file1>` and `<file2>`. Pick one."

---

## Council pool size

V1 default council pool: bundled-5 + any custom registered.

For council-mode mechanics (when each persona speaks, synthesis discipline, auto-fire matrix), see `council-mode.md`. This file is the persona registry; `council-mode.md` is the conversation flow.

---

## v2 expansions (not in v1)

- **NBJ thinker pack** — `personas.bundled_pack: comp-team-v1+nbj`. Adds Nate B. Jones thinker as a meta-perspective ("what would NBJ say about this transformation?"). Grounded in the Nate B. Jones research corpus.
- **Industry-specific persona packs** — `comp-team-grocery-v1`, `comp-team-public-sector-v1`, etc. Default pack still v1; teams can opt into industry packs that ship with industry-specific lenses (e.g., grocery's seasonal labor lens, public-sector's CBA-negotiator lens).
- **Adversarial pack** — `comp-team-v1+adversarial`. Adds a deliberate disagreer ("VP-skeptic", "auditor-mindset", "burnt-by-prior-rollout") for stress-testing.
- **Per-team override of bundled pack** — pin a subset of bundled personas (e.g., team only ever wants HRBP + comp-manager + change-management for council).
