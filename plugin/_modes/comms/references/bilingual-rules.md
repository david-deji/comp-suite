# Bilingual Rules — FR-First Co-Draft

Defines the bilingual co-draft mechanics for this skill. Loaded by `draft-protocol.md` and `cascade-protocol.md` before any multi-language render. Loaded by `review-protocol.md` for the FR-CA glossary check step.

---

## Governing context

Quebec employers are subject to the Charter of the French Language (Bill 96). All organization-wide communications distributed to Quebec employees must be available in French. For most Quebec comp cycles:
- `languages.primary: fr-ca` — FR-CA is the primary, legally required language
- `languages.secondary: en` — EN is the secondary, produced in parallel

For organizations outside Quebec or board-level artifacts (where EN is the working language), `languages.primary` may be `en`. Per-artifact language overrides are respected.

---

### 5.1 Co-draft, not translation

Both language versions are produced from the same source: the compensation-advisor recommendation, the resolved speaker register, and the resolved audience profile. Neither language version is produced by translating the other.

**Why this matters.** A message written in English and translated to French reads as translated-to-Quebec-employees. Common tells:
- Sentence structure following English syntax (subject-verb-object rigidity)
- Anglicisms in places where a Quebec French equivalent exists (`performatif` for "performative", `compétitif` for "competitive" rather than the more natural `concurrentiel`)
- Formal register that does not match Quebec workplace norms (Quebec French is less formal than European French in professional contexts)
- Compensation terms rendered as false cognates (`bénéfices marginaux` instead of `avantages sociaux`, `évaluation de performance` instead of `évaluation du rendement`)

**The co-draft approach.** For each artifact:
1. Draft in `languages.primary` using the source recommendation directly.
2. Draft in `languages.secondary` using the same source recommendation — not as a rendering of the primary-language draft.
3. Both drafts go through the same speaker register and audience profile calibration.

---

### 5.2 FR-CA version file naming

Separate files per language per version:

```
<artifact-slug>-fr-ca-v<N>.<ext>
<artifact-slug>-en-v<N>.<ext>
```

Both files stored in `engagements/<slug>/comms/`. Version numbers increment independently per language (FR-CA may be at v3 while EN is at v1 if FR was revised more heavily).

---

### 5.3 Per-language approval tracking

Approval stages are tracked independently per language. FR-CA and EN can be in different stages simultaneously. Example from `/status`:

```
| all-hands-announcement  | fr-ca | v3 | ceo_approved | 2026-04-29 |
| all-hands-announcement  | en    | v2 | chro_review  | 2026-04-28 |
```

Advancement of one language's stage does not advance the other. Operator edits `engagement-comms-config.yaml` to advance each language's `approval_stage` independently.

---

### 5.4 Glossary integration

**FR-CA glossary.** The shared `vocabulary/fr-ca-glossary.yaml` (maintained by compensation-advisor's `/glossary promote` mechanism) is the canonical source for FR-CA compensation terminology.

**At draft time:**
1. Load `vocabulary/fr-ca-glossary.yaml` from Drive.
2. For every compensation term in the FR-CA draft, check whether a canonical FR-CA term exists in the glossary. If yes, use the canonical term — do not improvise.
3. If an appropriate FR-CA term does not exist in the glossary and the skill must choose one, flag it in the chat after drafting: "The following FR-CA terms were used without a glossary entry — consider adding via `/glossary add`: [list]."

**Engagement-level additions.** When operator identifies a new FR-CA term via `/glossary add`:
1. Append to `engagements/<slug>/comms/fr-ca-additions.yaml` with `usage_tag: comms`.
2. The term is immediately available for subsequent drafts in the same engagement.
3. Promotion to canonical (`vocabulary/fr-ca-glossary.yaml`) is performed by compensation-advisor's `/glossary promote` command — comp-comms-builder does not write to the canonical glossary directly.

Format for `fr-ca-additions.yaml`:

```yaml
schema_version: 1
engagement_slug: <slug>
additions:
  - en_term: <English term>
    fr_ca_term: <Quebec French term>
    usage_tag: comms
    added_date: YYYY-MM-DD
    notes: <optional context>
```

---

### 5.5 Quebec-specific terminology conventions

The following conventions apply to all FR-CA comms drafts. They are a subset of the canonical glossary conventions for comms-specific usage:

| English term | Use in FR-CA | Avoid in FR-CA |
|---|---|---|
| wage scale | échelle salariale | grille de salaires |
| compensation | rémunération | compensation (anglicism) |
| benefits | avantages sociaux | bénéfices |
| performance review | évaluation du rendement | revue de performance |
| all-hands meeting | rencontre tous-employés | all-hands |
| effective date | date d'entrée en vigueur | date effective |
| merit increase | augmentation au mérite | merit increase |
| HR business partner | partenaire d'affaires RH | HRBP (acceptable in internal docs; spell out in all-hands) |
| executive | dirigeant(e) / cadre supérieur(e) | exécutif(ve) (Anglicism in this context) |

This table is indicative, not exhaustive. The canonical glossary is the authoritative source. When in doubt, prefer the term already in the glossary over inventing a new one.

---

### 5.6 The "translated-from-English" tell — detection and prevention

At draft time, after producing the FR-CA version, the skill runs a basic tell-detection pass before surfacing the draft to the operator:

**Checks:**
1. Sentence structure: flag sentences following English SVO rigidity where French would use a different construction.
2. Anglicisms: compare against a bundled list of common English-sourced false cognates in comp vocabulary.
3. Register mismatch: FR-CA comms in Quebec workplaces use `tu` (informal) or `vous` (formal) — both are valid, but must be consistent throughout the artifact. Flag if mixed.
4. Courtesy-language clichés: flag phrases like "Veuillez noter que" or "Il est important de noter" — these are translation clichés not used by native Quebec business writers.

Findings surface in the chat after draft, before the operator approves. They are soft warnings, not hard stops.

---

### 5.7 FR-only cycles

If `languages.secondary: null` is set in `engagement-comms-config.yaml`, the skill produces only the primary language. No secondary draft is attempted. The `/status` table shows one row per artifact per enabled language.

When `languages.secondary: null` and `languages.primary: fr-ca`: all artifacts are FR-CA only. This is the correct configuration for Quebec-only cycles where EN is not required.

---

### 5.8 Artifact-level language overrides

Some artifacts default to a different language than the cycle primary. The `exec-one-pager` is typically EN even in FR-CA-primary cycles (board working language). This is configured per-artifact in `engagement-comms-configs/<slug>.yaml`:

```yaml
artifacts:
  - artifact_type: exec-one-pager
    languages: [en]               # overrides cycle languages for this artifact
```

When an artifact-level language list is set, it takes precedence over the cycle-level `languages.primary/secondary`. The cycle-level languages still apply to all other artifacts.

---

### 5.9 What this file does NOT contain

- Glossary promotion mechanics — those are owned by compensation-advisor's `/glossary promote`. This skill only writes to `engagements/<slug>/comms/fr-ca-additions.yaml`.
- Full FR-CA glossary content — that lives in `vocabulary/fr-ca-glossary.yaml` (shared Drive folder).
- Approval-stage transitions — those live in `approval-stage-tracking.md`.
- Per-artifact language defaults — those live in `artifact-catalog.md`.
