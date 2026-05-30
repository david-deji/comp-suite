# /draft Protocol

`/draft <artifact-type>` renders a single comms artifact for the active engagement. This is the core render engine — `/cascade` calls this pipeline for each artifact in the bundle.

Loaded by SKILL.md when intent-router classifies as `/draft`. Also loaded by `/cascade` per-artifact step. Loads: `meta-protocol.md` (mirrored), `draft-protocol.md` (this file), `artifact-catalog.md`, `valid-combinations-rules.md`, `bilingual-rules.md`, `compensation-advisor-input-contract.md`, `production-and-qa.md` (mirrored), `template-master.md` (mirrored), `brand-kit-protocol.md` (mirrored).

---

## Mode-keyed step routing

This protocol's full 10-step sequence assumes `engagement_mode: full-cascade`
or `engagement_mode: single-artifact` (the defaults for /draft). When the
engagement-comms-config declares a different mode, skip steps marked SKIPPED
and run only steps marked RUN or PARTIAL.

**Mode resolution at session start:**

1. Read `engagement_mode` from the active `engagement-comms-config.yaml`.
2. Look up the mode's step routing from `references/engagement-modes.md`.
3. Apply the routing for this session.
4. Write the mode declaration into every artifact's frontmatter so future
   sessions resume with the same routing.

**Per-mode routing for /draft:**

| Mode | Step routing |
|---|---|
| `full-cascade` | Run all 10 steps. |
| `single-artifact` | Run all 10 steps for the requested artifact only. |
| `bilingual-co-draft` | Run all 10 steps; Step 8 (render) runs FR first, EN immediately after in the same session — not sequentially across sessions. |
| `revision-only` | Steps 1-3 (config + register load); Step 4 (read source recommendation for drift check only); Step 9 (diff + targeted edits); Step 10 (write). Steps 5-8 SKIPPED. |
| `voice-extraction-only` | SKIPPED — /draft does not run in voice-extraction-only mode. Route to /ingest. |
| `glossary-merge` | SKIPPED — /draft does not run in glossary-merge mode. Route to /glossary add. |

If the mode declares a step as PARTIAL, apply the partial-mode cut documented
in the mode's `steps_partial` entry in `engagement-modes.md`.

If `engagement_mode` is missing from the config, default to `single-artifact`
for /draft and log `decision_type: mode_defaulted_silently` before proceeding.

---

## 1. Artifact-type resolution

If `/draft` was called without an artifact type, prompt:

> "Which artifact? (`all-hands-announcement` | `manager-faq` | `hrbp-enablement-memo` | `exec-one-pager`)"

Wait for explicit choice. Do not default.

Look up the artifact type in `artifact-catalog.md` to confirm v1 validity. If the requested type is not in the v1 catalog, surface:

> "That artifact type is not in the v1 catalog. Valid types: `all-hands-announcement`, `manager-faq`, `hrbp-enablement-memo`, `exec-one-pager`."

---

## 2. 10-step render sequence

### 2.1 Step 1 — Read engagement config + org profile

1. Load `engagement-comms-configs/<engagement-slug>.yaml` from Drive.
2. Load `org-comms-profiles/<client-slug>.yaml` from Drive. If absent, note: "No org-comms-profile found — using bundled defaults from `template_assets/`. Run `/ingest` to specialize."
3. Load `template_assets/valid-combinations.yaml`.
4. Identify the matching artifact entry in `engagement-comms-config.artifacts[]` for this artifact type + language combination.

### 2.2 Step 2 — Validate combination

Check the requested (artifact_type × speaker × audience × channel × format) against `template_assets/valid-combinations.yaml` and `references/valid-combinations-rules.md`. If not valid, surface:

> "That combination is not in the registry. Valid options for `<artifact_type>`:
> Speakers: <list>
> Channels: <list>
> Formats: <list>
>
> To enable a new combination, edit `engagement-comms-config.yaml` `valid_combinations_overrides:`."

Abort draft if operator does not confirm an override.

### 2.3 Step 3 — Resolve speaker register (4-layer inheritance)

Apply in order, later layers overriding earlier:

1. **Bundled default:** load `template_assets/speaker-registers/<speaker>.yaml`
2. **Org layer:** if `org-comms-profiles/<client-slug>.yaml` exists, read `speaker_registers.<speaker>` fields and overlay
3. **Engagement layer:** if `engagement-comms-config.yaml` has `speaker_overrides.<speaker>` (optional field), overlay
4. **CLI override:** if operator passed `speaker=<role>` on the command line, override the speaker assignment

Full inheritance rules: `references/speaker-register-rules.md`.

Resolved register fields used in render: `tone_descriptors`, `do_words`, `dont_words`, `sample_paragraph` (for register calibration, not for verbatim reuse), `signature_line`, `sign_off_convention`.

### 2.4 Step 4 — Read source recommendation

Two paths per `recommendation_source.type`:

**Path A — `compensation-advisor`:**

1. Check for `engagements/<engagement-slug>/checkpoint.yaml` (mid-flight state). If found and `scenario_locked: false`, prefer it.
2. If checkpoint absent or `engagement_status: closed`, read `engagements/<engagement-slug>/engagement-state.yaml`.
3. Read required fields per `compensation-advisor-input-contract.md`: `scenario_chosen`, `audience`, `key_objections_anticipated`, `narrative_frame`, `cycle.effective_date`, `org.name`.
4. If any required field is missing, surface: "Missing required field `<field>` in source recommendation. Cannot proceed without it. Update the compensation-advisor engagement-state and retry."

**Path B — `manual-paste`:**

1. Read `recommendation_source.pasted_summary` from the engagement config.
2. If null, surface: "No pasted recommendation summary found. Either paste a summary now or switch `recommendation_source.type` to `compensation-advisor`."

### 2.5 Step 5 — Drift check

Hash the current source recommendation YAML content. Compare against `engagement-comms-config.artifacts[<this-artifact>].last_drift_check_against_recommendation_revision`.

If hash differs (or if `last_drift_check` is null — first draft):
- If hash differs: surface drift warning and require acknowledgment:

  > "Source recommendation has changed since v(N-1) of `<artifact-slug>` was drafted.
  > Diff: <key changed fields>
  > Options: `refresh` (incorporate changes) | `proceed-anyway` (draft without incorporating) | `abort`"

  Wait for explicit choice. Do not draft until resolved.
- If null (first draft): no drift warning. Record hash after draft completes.

### 2.6 Step 6 — Pre-draft anti-pattern checklist

Surface anti-patterns before rendering. Merge:
- `org-comms-profiles/<client-slug>.yaml` `anti_patterns[]` (if profile exists)
- `template_assets/anti-patterns.yaml` bundled common patterns

Filter to patterns `applies_to_audiences` matching this artifact's audience + `applies_to_speakers` matching this artifact's speaker. Surface:

```
Drafting `<artifact-type>` v<N> for `<engagement-slug>`. Anti-patterns to avoid:
  - "<phrase>" → use "<use_instead>" instead (<reason>, first seen: <cycle>)
  - "<phrase>" → use "<use_instead>" instead (...)
Acknowledge and proceed? (y / n / show all anti-patterns)
```

Wait for explicit `y` or `n`. If `n`, abort. If "show all", display full anti-pattern list for the engagement and re-ask. Do NOT proceed without acknowledgment.

### 2.7 Step 7 — Render primary language

Render the artifact in `languages.primary` (default `fr-ca`):

1. Load artifact spec from `artifact-catalog.md` for this artifact type: sections, length caps, format rules, brand template slots.
2. Load channel rules from `org-comms-profile.yaml` `channel_rules.<channel>` (or bundled `template_assets/channel-rules.yaml` if absent).
3. Apply speaker register: use resolved `tone_descriptors`, `do_words`, `dont_words` to calibrate the draft voice. Do not copy `sample_paragraph` verbatim — use it to calibrate register only.
4. Apply source recommendation: incorporate `scenario_chosen`, `narrative_frame`, `key_objections_anticipated`, `cycle.effective_date`, `org.name` into artifact content.
5. Apply language rules per `bilingual-rules.md` — correct FR-CA grammar, Quebec-specific glossary terms from `vocabulary/fr-ca-glossary.yaml`, channel-appropriate formatting.
6. Enforce channel-length caps: abort and truncate if artifact exceeds channel limits.
7. Inject anti-pattern guard — scan rendered output for banned phrases before proceeding. If found, flag and re-render the offending section.

### 2.8 Step 8 — Render secondary language co-draft

If `languages.secondary` is non-null and this artifact's `languages[]` list includes the secondary:

1. Render the artifact INDEPENDENTLY in the secondary language — do NOT translate the primary draft.
2. Both drafts originate from the same source recommendation (the intent), not from each other.
3. Apply the secondary language's register and channel rules (same speaker role, different language calibration).
4. Apply `bilingual-rules.md` § Secondary language rules.
5. Run the same anti-pattern guard on the secondary draft.

Rationale: co-draft from intent avoids the "translated-from-English" register tell that reads as inauthentic to Quebec employees. Full mechanics: `references/bilingual-rules.md`.

### 2.9 Step 9 — Apply brand template

Per `branding.regenerate_at_draft: true` (default), read brand template fresh from Drive on every `/draft` call:

1. Check `branding/<org-slug>/comms-templates/` in Drive. If absent, auto-seed from `template_assets/branding/_default/comms-templates/` with a warning.
2. Apply the brand template slot for this artifact type + format (per `template_assets/valid-combinations.yaml` `brand_templates:` field):
   - HTML email: inject `email-header.html` at top + `email-signature/<speaker>.txt` at bottom
   - PDF: apply `pdf-master.yaml` configuration
   - DOCX: apply `docx-master.docx` branded template via `/mnt/skills/public/docx` skill
   - PPTX: use `branding/<org-slug>/masters/` + `comms-templates/pptx-master/` overrides via `/mnt/skills/public/pptx` skill per `template-master.md` (mirrored)

**PDF path note:** PDF generation path is verified at runtime. If DOCX→PDF conversion is available via the bundled DOCX skill, use it. If not, the artifact ships DOCX-only and the operator manually exports to PDF. PPTX-only exec-one-pager is unaffected. See `references/artifact-catalog.md` per-artifact notes for the fallback behavior per artifact type.

### 2.10 Step 10 — Write files + update config

For each (language × format) combination enabled for this artifact:

1. Determine next version number: read `engagement-comms-config.artifacts[].current_version` and increment.
2. Write to `engagements/<slug>/comms/<artifact-slug>-<lang>-v<N>.{ext}`.
3. Also write to `engagements/<slug>/comms/_drafts/<artifact-slug>-<lang>-wip.{ext}` (working copy; cleared on approval to `shipped`).
4. Multi-file write ordering per `persistence-and-ledger.md`: write primary language first, then secondary.

After all writes succeed:

5. Update `engagement-comms-config.artifacts[<this-artifact>]`:
   - `current_version: <N>` (incremented)
   - `last_drafted: <ISO date>`
   - `approval_stage: drafted` (reset to drafted on new version)
   - `last_drift_check_against_recommendation_revision: <new-hash>`

6. Write updated `engagement-comms-config.yaml` back to Drive.

---

## 3. Post-draft surface

After all writes confirm:

```
Draft complete: `<artifact-slug>-<lang>-v<N>.<ext>` (+ secondary if applicable)

Written to: engagements/<slug>/comms/
Approval stage: drafted

Run `/review <artifact-slug>` to see the diff vs v(N-1) and re-surface the anti-pattern checklist.
```

---

## 4. Failure handling

- **Source recommendation missing required field** — abort at Step 4. Surface field name. Do not substitute.
- **Invalid combination** — abort at Step 2. Surface valid options.
- **Anti-pattern acknowledgment timeout** — if operator does not respond, do not proceed. Surface: "Anti-pattern acknowledgment required before drafting."
- **Brand template not found, auto-seed attempted** — continue after warning. Log auto-seed action in post-draft summary.
- **Drive write failure on artifact** — surface the failure with the path that failed. Roll back the config version increment. Do not leave config in an inconsistent state.
- **Word/page count exceeds channel cap** — truncate, surface the truncation notice, invite operator to /review and trim.

---

## 5. What this protocol does NOT contain

- Artifact-specific content sections, length caps, and format specs — those live in `artifact-catalog.md`.
- Valid speaker × audience × channel × format registry — that lives in `valid-combinations-rules.md` + `template_assets/valid-combinations.yaml`.
- Speaker register schema and 4-layer inheritance logic — those live in `speaker-register-rules.md`.
- Bilingual co-draft mechanics, glossary-promote integration — those live in `bilingual-rules.md`.
- Compensation-advisor required fields, hash/drift mechanics — those live in `compensation-advisor-input-contract.md`.
- Brand template regeneration discipline — that lives in `brand-kit-protocol.md` (mirrored).
- PPTX master slot construction — that lives in `template-master.md` (mirrored).
- Multi-file write ordering — that lives in `persistence-and-ledger.md` (mirrored).
- Production QA gates — those live in `production-and-qa.md` (mirrored).
- Full cascade dependency order — that lives in `cascade-protocol.md`.
