# Audience Profile Rules

Schema and bundled defaults for the 4 v1 audience profiles. Loaded by `draft-protocol.md` at render time to calibrate language level and channel selection. Loaded by `ingest-protocol.md` at Workshop synthesis to validate extracted profiles.

---

## What an audience profile is

An audience profile encodes the observable characteristics of a reader group: how they read, what vocabulary they respond to, what they care about, and how they receive communications. It is NOT a persona or stakeholder map — it is a language calibration constraint for the draft engine.

Profiles accumulate through `/ingest`. Cold-start behavior uses bundled defaults from `template_assets/audience-profiles/<audience>.yaml`. After `/ingest` with org-specific sources, the org-level profile replaces the bundled defaults for that audience.

---

### 4.1 Audience profile schema

Each audience profile entry in `org-comms-profiles/<org-slug>.yaml` under `audience_profiles.<audience>:` has the following fields:

```yaml
schema_version: 1                 # always present at top of org-comms-profile.yaml

audience_profiles:
  <audience-slug>:
    reading_level: <level>        # grade-7 | grade-9 | grade-12 | college
    vocabulary: <type>            # concrete | mixed | technical
    key_concerns: []              # 3-6 items; what this audience cares about in comp comms
    channel_preference: []        # ordered list of preferred channels for this audience
    inferred_from: []             # list of source IDs from /ingest that informed this profile
```

Field rules:
- `reading_level`: choose one of four discrete levels. Not a continuum.
  - `grade-7` — simple sentences, common words, minimal jargon. Not used for any v1 audience by default; available for override in high-hourly populations.
  - `grade-9` — accessible paragraphs, occasional technical term with inline definition, max 3-line bullets.
  - `grade-12` — can handle compound sentences, technical terms without inline definition, formatted tables.
  - `college` — full technical vocabulary, no simplification required, can process dense information.
- `vocabulary`: calibrates word choice.
  - `concrete` — physical/tangible nouns, "your paycheque" over "your compensation."
  - `mixed` — blend of concrete and abstract; technical terms OK in context.
  - `technical` — compensation mechanics vocabulary: proration, band midpoint, merit matrix, etc.
- `key_concerns`: 3–6 items. Informs which topics the draft engine foregrounds. Not a comprehensive list of concerns — the top concerns that drive engagement with the artifact.
- `channel_preference`: ordered list of channels. First channel is primary. Informs which channel format the draft engine optimizes for when multiple channels are enabled.
- `inferred_from`: source IDs from `ingest_history`. Provides traceability.

Valid audience slug values: `all_employees`, `people_managers`, `hrbps`, `exec_board`.

---

### 4.2 Bundled defaults — 4 audiences

The following defaults ship in `template_assets/audience-profiles/<audience>.yaml`. Applied when no org-level profile exists.

#### Audience: `all_employees`

```yaml
schema_version: 1
audience: all_employees
reading_level: grade-9
vocabulary: concrete
key_concerns:
  - paycheque impact
  - effective date
  - what to do
  - who to ask
channel_preference:
  - email
  - intranet
inferred_from: []
```

Draft calibration guidance: Use "your pay" not "your compensation." Lead with the effective date in the first 50 words. End with a clear single call to action (who to ask). Do not include mechanics, calculation examples, or edge cases — those belong in `hrbp-enablement-memo`. No acronyms without inline definition.

#### Audience: `people_managers`

```yaml
schema_version: 1
audience: people_managers
reading_level: grade-12
vocabulary: mixed
key_concerns:
  - team questions
  - escalation triggers
  - talking points
  - timing
channel_preference:
  - docx_distributable
  - intranet
inferred_from: []
```

Draft calibration guidance: Managers are readers between two worlds — they need enough mechanics to answer team questions, but they do not need full HRBP-depth edge cases. Foreground talking points and escalation triggers. Use Q&A format; group by topic. "Concrete" for employee-facing language, "mixed" for manager-to-HRBP language.

#### Audience: `hrbps`

```yaml
schema_version: 1
audience: hrbps
reading_level: college
vocabulary: technical
key_concerns:
  - edge cases
  - escalation paths
  - mechanics
  - compliance
channel_preference:
  - docx_distributable
inferred_from: []
```

Draft calibration guidance: HRBPs are the expert audience. Do not simplify. Use full technical vocabulary. Include formulae, proration rules, band-crossing mechanics. Structure edge cases as condition → guidance → citation. Escalation paths must name specific roles, not generic "HR."

#### Audience: `exec_board`

```yaml
schema_version: 1
audience: exec_board
reading_level: college
vocabulary: technical
key_concerns:
  - governance
  - budget impact
  - peer benchmark
  - risk
channel_preference:
  - pptx_distributable
inferred_from: []
```

Draft calibration guidance: Execs see tradeoffs and governance — not "what this means for employees." One assertion per slide. Budget impact in dollar or percentage terms with YoY delta. Risk framed as residual risk (what remains after mitigation). Peer benchmark: one comparable data point, not a full market survey.

---

### 4.3 How `/draft` uses the audience profile

At the start of any render, after resolving the speaker register, `draft-protocol.md` resolves the audience profile for the target audience:

1. Read `org-comms-profiles/<org-slug>.yaml audience_profiles.<audience>`. If null or not yet ingested: fall back to `template_assets/audience-profiles/<audience>.yaml`.
2. Apply `reading_level` calibration:
   - `grade-9`: max 20-word sentences; define any compensation term on first use; max 3-level bullet depth.
   - `grade-12`: max 30-word sentences; technical terms permitted; tables and structured lists OK.
   - `college`: no length or complexity limit; dense formatting permitted.
3. Apply `vocabulary` filter: flag any word choice inconsistent with the vocabulary type. (`concrete` + "compensation envelope" → rephrase to "total pay budget.")
4. Apply `key_concerns` ordering: ensure the top concern is addressed in the first third of the artifact, the second concern in the second third, etc. Concerns not addressed → surface warning before write (not a hard stop).
5. Use `channel_preference[0]` (primary channel) to select the default template when the engagement config enables multiple channels.

---

### 4.4 How `/ingest` updates audience profiles

During `/ingest` Workshop synthesis, for each audience represented in the ingested sources:

1. Infer `reading_level` from the vocabulary and sentence complexity of prior communications directed at that audience. Operator confirms or corrects.
2. Infer `vocabulary` type from the same sources.
3. Extract `key_concerns` from recurring topics, questions, or reaction patterns noted in the sources or described by the operator during the interview.
4. Confirm `channel_preference` from the distribution channels used in prior communications.
5. Append source IDs to `inferred_from`.
6. Merge into `org-comms-profiles/<org-slug>.yaml audience_profiles.<audience>`. If a field already exists, surface the delta and ask operator to confirm or reject the update.

Re-ingest is additive. Prior profile entries are not erased.

---

### 4.5 Per-audience language calibration quick reference

| Audience | Reading level | Vocabulary | Lead with | Avoid |
|---|---|---|---|---|
| `all_employees` | Grade-9 | Concrete | Effective date + pay impact | Mechanics, acronyms, edge cases |
| `people_managers` | Grade-12 | Mixed | Talking points + escalation triggers | Full mechanics depth, governance |
| `hrbps` | College | Technical | Edge cases + calculation mechanics | Simplification, generic "contact HR" |
| `exec_board` | College | Technical | Tradeoffs + budget impact | Employee-level details, cascade mechanics |

---

### 4.6 What this file does NOT contain

- The actual bundled default YAML data — that lives in `template_assets/audience-profiles/<audience>.yaml`.
- Speaker register rules — those live in `speaker-register-rules.md`.
- Artifact section requirements — those live in `artifact-catalog.md`.
- Channel-specific formatting rules (max length, formatting conventions) — those live in `org-comms-profiles/<org-slug>.yaml channel_rules` and `template_assets/channel-rules.yaml`.
- Bilingual co-draft mechanics — those live in `bilingual-rules.md`.
