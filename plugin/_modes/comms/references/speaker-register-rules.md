# Speaker Register Rules

Four-layer inheritance model for per-speaker registers. Loaded by `draft-protocol.md` at the start of any `/draft` or `/cascade` run. Defines the schema, resolution algorithm, default characteristics for the 4 v1 speakers, update protocol, and where registers read from and write to.

---

## What a speaker register is

A speaker register is the set of language norms and conventions that distinguish how a specific organizational role communicates. It is NOT a persona or a writing sample library — it is a constraint set for the draft engine: which words to use, which words to avoid, what the opening and closing conventions are, and what the voice sounds like at sentence level.

"Register" is used deliberately over "voice" to set accurate expectations: it encodes observable surface patterns, not deep authorial intent.

---

### 3.1 Register entry schema

Each register entry in `org-comms-profiles/<org-slug>.yaml` under `speaker_registers.<speaker>:` has the following fields:

```yaml
schema_version: 1                 # always present at the top of org-comms-profile.yaml

speaker_registers:
  <speaker-slug>:
    tone_descriptors: []          # list of 2-5 adjectives; e.g. [formal, vision-flavored, broad]
    do_words: []                  # words/phrases the speaker uses; pulled from ingested sources
    dont_words: []                # words/phrases the speaker avoids; sourced from anti-patterns or /ingest
    sample_paragraph: null        # verbatim paragraph extracted from ingested source; null if not yet ingested
    signature_line: null          # e.g. "— [Name], President & CEO, Acme Inc."
    sign_off_convention: null     # closing line the speaker uses; e.g. "Together, we move forward."
    inferred_from: []             # list of ingest source IDs that contributed to this register
```

Field rules:
- `tone_descriptors`: 2–5 adjectives. Do not use more than 5 — specificity degrades beyond that.
- `do_words`: flat list of strings. Can be single words or short phrases (max 4 words).
- `dont_words`: same format as `do_words`. Sourced from `/ingest` anti-pattern surfacing or explicit operator input.
- `sample_paragraph`: verbatim text from an ingested prior communication, attributed to this speaker. Null until `/ingest` populates it. The draft engine uses this as a calibration exemplar.
- `signature_line`: the speaker's full sign-off line including role. Use `[Name]` as a placeholder for the individual's name (PII redaction per `redaction-rules.md`).
- `sign_off_convention`: the closing phrase before the signature. Can be a complete sentence or a fragment. Null until ingested.
- `inferred_from`: list of source IDs (matching the `ingest_history` source tagging in `org-comms-profile.yaml`). Provides traceability.

---

### 3.2 Four-layer inheritance

At draft time, the skill resolves the active register for the requested speaker by merging four layers in priority order (highest to lowest):

```
Layer 4: Artifact-level override (CLI flag or engagement-comms-config artifact entry)
Layer 3: Engagement-level override (engagement-comms-config.yaml speaker_register_overrides)
Layer 2: Org-level register (org-comms-profiles/<org-slug>.yaml speaker_registers.<speaker>)
Layer 1: Bundled default (template_assets/speaker-registers/<speaker>.yaml)
```

Higher layers override lower layers field-by-field (not wholesale replacement). Example: if the bundled default has `tone_descriptors: [formal, broad]` and the org-level register has `tone_descriptors: [warm, mechanical, specific]`, the org-level value wins. If the org-level register has `sample_paragraph: null` (not yet ingested), the bundled default's `sample_paragraph` applies.

**Merge algorithm:**

For each field in the register schema:
1. Start with the bundled default value.
2. Apply org-level value if non-null and non-empty.
3. Apply engagement-level value if non-null and non-empty.
4. Apply artifact-level override if explicitly set.

A `null` value at any layer means "not set at this layer" — fall through to the layer below. An empty list `[]` at any layer means "explicitly cleared at this layer" — do not fall through.

---

### 3.3 Where registers read from and write to

**Read paths (resolution order):**

```
template_assets/speaker-registers/<speaker>.yaml           # Layer 1: bundled defaults (read-only)
org-comms-profiles/<org-slug>.yaml                         # Layer 2: org-level (local $STATE_ROOT cache)
engagement-comms-configs/<engagement-slug>.yaml            # Layer 3: engagement-level overrides
<CLI flag or per-artifact config in engagement-comms-config>  # Layer 4: artifact-level
```

**Write paths:**

| Source of update | Writes to |
|---|---|
| `/ingest` run | `org-comms-profiles/<org-slug>.yaml` (Layer 2) |
| Operator edits engagement config directly | `engagement-comms-configs/<engagement-slug>.yaml` (Layer 3) |
| Bundled default changes | Requires skill bundle update; NOT edited at runtime |

`/ingest` is the primary mechanism for populating org-level registers. Operators do not manually edit `org-comms-profiles/` — they run `/ingest` with new source material.

---

### 3.4 The 4 v1 speakers and their bundled defaults

The following defaults ship in `template_assets/speaker-registers/<speaker>.yaml`. They apply when no org-level register exists (cold start).

#### Speaker: `ceo`

```yaml
schema_version: 1
speaker: ceo
tone_descriptors: [formal, vision-flavored, broad]
do_words:
  - we believe
  - our journey
  - together
  - commitment
  - our team
dont_words:
  - must
  - cannot
  - employees should
  - mandate
  - will be required
sample_paragraph: null
signature_line: "— [Name], President & CEO"
sign_off_convention: "Together, we move forward."
inferred_from: []
```

Context: CEO communications set the cultural tone. Vision-flavored and broad; they do not go into mechanics. They convey commitment and stability. The CEO voice does NOT drill into specifics — that is the CHRO's role.

Typical use: `all-hands-announcement` speaker when the cycle is org-wide and high-stakes (e.g., first year of a new comp philosophy).

#### Speaker: `chro`

```yaml
schema_version: 1
speaker: chro
tone_descriptors: [warm, mechanical, specific]
do_words:
  - here is how
  - what this means for you
  - the steps are
  - effective
  - specifically
dont_words:
  - strategic
  - transformational
  - leverage
  - synergy
  - journey
sample_paragraph: null
signature_line: "— [Name], Chief People Officer"
sign_off_convention: "Reach out to your HRBP with questions."
inferred_from: []
```

Context: CHRO is the workhorse voice for most comms. Warm but specific — mechanics are their domain. They do not hide behind vision language. They give employees clear answers.

Typical use: `all-hands-announcement` (most cycles), `manager-faq`, `hrbp-enablement-memo`, `exec-one-pager`.

#### Speaker: `vp-ops`

```yaml
schema_version: 1
speaker: vp-ops
tone_descriptors: [direct, banner-specific, operations-anchored]
do_words:
  - for our team
  - in our stores
  - what we are doing
  - on the floor
  - our operations
dont_words:
  - enterprise-wide
  - corporate
  - governance
  - transformation
  - strategic initiative
sample_paragraph: null
signature_line: "— [Name], VP Operations"
sign_off_convention: null
inferred_from: []
```

Context: VP Ops speaks to a specific operational unit (pharmacy, distribution, retail banner). Concrete and operations-anchored. Does not use corporate or enterprise language. Appropriate for banner-specific FAQ or memo where the CHRO's broader framing would feel distant.

Typical use: `manager-faq` when the cycle is banner-specific.

#### Speaker: `hrbp-manager`

```yaml
schema_version: 1
speaker: hrbp-manager
tone_descriptors: [actionable, escalation-aware, peer-to-peer]
do_words:
  - escalate to
  - the talking points are
  - your team will likely ask
  - here is what to say
  - refer to
dont_words:
  - tell your team
  - push back
  - defer
  - just say
  - figure it out
sample_paragraph: null
signature_line: null
sign_off_convention: null
inferred_from: []
```

Context: This is the HRBP/manager register — the peer-to-peer voice for the HRBP enablement memo consultation script section and for manager-FAQ consultation scripts. It is NOT a speaker for artifacts — `hrbp-manager` is not a valid speaker in `valid-combinations.yaml`. It provides the consultation script register used within artifacts authored by other speakers.

Note: `hrbp-manager` appears as `valid_speakers` only within the `inferred_from` tracking in the org-comms-profile. It is not directly registered as a valid speaker in `template_assets/valid-combinations.yaml`.

---

### 3.5 Update protocol from `/ingest`

When `/ingest` completes its Workshop synthesis, it updates `speaker_registers` in `org-comms-profiles/<org-slug>.yaml` as follows:

1. For each speaker present in the ingested sources:
   a. Merge new `tone_descriptors` with existing (deduplicate; cap at 5).
   b. Merge new `do_words` and `dont_words` (deduplicate).
   c. If a higher-quality `sample_paragraph` is extracted, replace the existing one. Higher quality = longer, more representative of full register.
   d. Update `signature_line` and `sign_off_convention` if present in sources.
   e. Append new source IDs to `inferred_from` (do not remove prior source IDs).
2. Append the ingest run to `org-comms-profiles/<org-slug>.yaml ingest_history[]`.
3. Write the updated `org-comms-profiles/<org-slug>.yaml` to Drive.

Re-ingest is additive. Prior register entries are NOT erased by a re-run — new evidence merges into existing. Operator is prompted to confirm or reject drift from prior profile before write.

---

### 3.6 Engagement-level overrides

If the operator needs to adjust a speaker register for a specific cycle (without changing the org-level profile), they add `speaker_register_overrides:` to `engagement-comms-configs/<engagement-slug>.yaml`:

```yaml
speaker_register_overrides:
  chro:
    tone_descriptors: [warm, decisive, frank]   # overrides org-level for this cycle
    sign_off_convention: "Questions? Email your HRBP directly."
```

These overrides apply for all artifacts in this engagement. They do not modify `org-comms-profiles/<org-slug>.yaml`.

---

### 3.7 What this file does NOT contain

- The actual bundled default YAML content — that lives in `template_assets/speaker-registers/<speaker>.yaml`.
- Per-artifact section requirements — those live in `artifact-catalog.md`.
- Anti-pattern entries — those live in `org-comms-profiles/<org-slug>.yaml anti_patterns[]` and `template_assets/anti-patterns.yaml`.
- Audience profile rules — those live in `audience-profile-rules.md`.
