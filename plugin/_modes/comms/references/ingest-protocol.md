# /ingest Protocol

`/ingest` extracts voice, audience, channel, and anti-pattern intelligence from a client's prior organizational communications into a long-lived `org-comms-profile.yaml`. Output drives all downstream `/draft` and `/cascade` runs with org-specific speaker registers, audience profiles, and anti-patterns.

Loaded by SKILL.md when intent-router classifies as `/ingest`. Loads `meta-protocol.md` first (universal interview techniques, mirrored), then this file (comms-domain flow), plus `speaker-register-rules.md` for the register schema and inheritance constraints, plus `audience-profile-rules.md` for profile schema, plus `redaction-rules.md` for the input scan.

The skill interviews the operator directly in a single Claude.ai conversation. The operator is the SME being interviewed — there is no third-party interviewee, no "read this to them and paste back what they say." Every Q&A turn is between operator and skill. Structured-choice questions use pros/cons option tables per `meta-protocol.md § "The default question format"`.

Question banks live in `template_assets/ingest_question_block.json` — the canonical source for `scripted_opening_ingest`, `source_identity`, `voice_extraction`, `audience_profile_inference`, `channel_rules_detection`, `anti_pattern_surfacing`, `brand_discovery`, `scripted_close_ingest` blocks.

---

## 1. Session opening

If no org-slug is known, prompt: "Which org? (e.g., `acme`, `rona`, `metro-qc`)"

Confirm sources available, then open with the scripted opening from `ingest_question_block.json`:

> "Starting `/ingest` for `<org-slug>`. I'll walk through seven sub-phases: source identity, voice extraction per speaker, audience profile inference, channel rules detection, anti-pattern surfacing, brand discovery, and synthesis into `org-comms-profiles/<org-slug>.yaml`.
>
> I'll ask one question at a time. For choices with common patterns I'll present options with pros and cons — pick a letter or describe your own. You can pause at any point.
>
> Estimated time: 45-60 minutes depending on the source set. Ready?"

Wait for the operator's ready signal before proceeding.

---

## 2. Sources accepted (v1)

| Source type | How to ingest |
|---|---|
| PDF — past announcements, memos, FAQs | Claude.ai reads natively. Tag each by speaker + audience + cycle. |
| Pasted text — prior emails, intranet posts | Operator pastes inline. Tag same as PDF. |
| Prior PPTX decks — exec one-pagers, board summaries | Skill extracts text content from slide titles, bullets, speaker notes via `/mnt/skills/public/pptx`. Layout and images NOT preserved. |

Sources deferred to v2: URL-fetch (intranet pages by URL), `.eml` files.

Before extracting any source: run redaction scan per `redaction-rules.md`. Refuse to process a source with banned patterns (employee names, raw salary figures, personal contact info). Instruct re-paste with required transformations.

---

## 3. Sub-phase sequence

Seven sub-phases in order. The skill drives with question banks from `template_assets/ingest_question_block.json`; operator types responses. Use the Mom Test (past behavior, not hypotheticals) and pros/cons option tables for structured-choice questions. One question per turn.

### Sub-phase 1: Source identity (~3 min)

For each source supplied, use the `source_identity` block.

**Q1. How would you classify this source?**

| Option | Pros | Cons |
|---|---|---|
| **A. All-employees announcement (full org)** | Broadest voice sample; shows how CEO/CHRO address everyone | May be pitched up — omits manager-level register |
| **B. Manager-only communication (people managers)** | Captures HRBP-to-manager register and FAQ tone | Narrower audience; may not reflect exec voice |
| **C. Executive / board summary** | Captures formal, concise exec register | Very short sample; register may be consultant-edited |
| **D. HRBP enablement memo** | Captures operational, process-heavy HRBP register | Internal only; unlikely to show CEO/CHRO voice |
| **E. Other** | (describe the source type and intended audience) | |

After classifying, confirm:
- Which speaker produced this communication?
- Which cycle / year is it from?
- Is this typical of how that speaker communicates, or was it an exception?

Assign a source ID (`src-001`, `src-002`, ...) for cross-referencing.

---

### Sub-phase 2: Voice extraction per speaker (~15-25 min)

For each speaker present in the source set (ceo, chro, vp-ops, hrbp-manager):

Walk through `voice_extraction` block per speaker. For each, ask:

**Q2a. Tone descriptors: how would you describe this speaker in 3 adjectives?**

(Open prose — no table. Example prompts if the operator is stuck: "Warm or formal? Specific or general? Operational or strategic?")

**Q2b. What's the reading-level register this speaker uses?**

| Option | Pros | Cons |
|---|---|---|
| **A. Grade 7 (very plain, short sentences, no jargon)** | Accessible to all employees; no comprehension risk | May feel condescending to managers or senior staff |
| **B. Grade 9 (plain, some compound sentences, minimal jargon)** | Widely accessible; works for mixed audiences | Occasional jargon still slips through |
| **C. Grade 12 (standard professional)** | Appropriate for manager and HRBP communications | Less accessible for front-line hourly employees |
| **D. Post-secondary (technical, policy-dense, acronym-heavy)** | Appropriate for exec/board or regulatory-facing comms | Alienates non-expert audiences; risks misinterpretation |
| **E. Other** | (describe the level you observe in the source) | |

Then collect:
- **Do-words:** 3-5 words or phrases this speaker uses naturally
- **Don't-words:** 3-5 words or phrases this speaker NEVER uses or that feel inauthentic
- **Sample paragraph:** extract the best representative paragraph from the source (verbatim or lightly edited)
- **Signature line:** how does this speaker sign off?
- **Sign-off convention:** closing phrase before the signature (e.g., "Reach out to your HRBP with questions.")
- **Ingest source(s) that contributed:** `[src-001, src-002]`

If a speaker has no source material: note `sample_paragraph: null`, `inferred_from: []` in the profile.

---

### Sub-phase 3: Audience profile inference (~10-15 min)

For each audience represented in the source set (all_employees, people_managers, hrbps, exec_board):

**Q3a. What vocabulary style do the materials targeted at this audience use?**

| Option | Pros | Cons |
|---|---|---|
| **A. Concrete and literal (plain-language standards)** | No ambiguity; accessible to front-line employees | May feel flat for managers who want context |
| **B. Mixed (professional but plain)** | Versatile; works across most audiences | Risks being "too technical for some, too plain for others" |
| **C. Technical / policy-dense** | Appropriate for HRBPs and compliance-facing audiences | Creates comprehension risk for non-specialist employees |
| **D. Strategic / high-level** | Right for exec and board audiences | Lacks operational specifics that managers need |
| **E. Other** | (describe the vocabulary style you observe) | |

Then collect:
- **Reading level implied by the source:** grade-7 | grade-9 | grade-12 | college
- **Key concerns the audience demonstrated in reactions or follow-up** (if known)
- **Channel preference observed** (email / intranet / DOCX distributable / verbal)

---

### Sub-phase 4: Channel rules detection (~5-10 min)

For each channel observed in the source set:

**Q4a. What email length convention does this org use for all-employees announcements?**

| Option | Pros | Cons |
|---|---|---|
| **A. Short-form (≤250 words, no sub-headers)** | Fast to read; mobile-friendly | Lacks detail; forces follow-up questions |
| **B. Standard (250-500 words, 2-3 sub-headers)** | Balanced; covers context and action items | Longer than some employees read on first pass |
| **C. Long-form (500+ words, full narrative)** | Complete; reduces follow-up questions | Risk of non-readership; front-line employees skip |
| **D. Variable (depends on message complexity)** | Flexible | Inconsistent; employees can't predict format |
| **E. Other** | (describe the email length convention you observe) | |

Then walk through `channel_rules_detection` block for each channel:
- **Intranet:** headline conventions? Use of callout boxes? Bullet usage?
- **DOCX distributable:** cover-page used or not? Page-count norms?
- **PPTX:** slide-count norms? Headline-only or bullets-per-slide?

If the operator is uncertain about a channel, note `null` and accept bundled channel-rules defaults from `template_assets/channel-rules.yaml`.

---

### Sub-phase 5: Anti-pattern surfacing (~5-10 min)

Walk through `anti_pattern_surfacing` block conversationally:

- What phrases have caused confusion, complaints, or misinterpretation in prior cycles?
- For each: what's the phrase, why was it a problem, what cycle, which audience reacted, and what's the preferred alternative?
- The operator may also proactively flag phrases to avoid even without a prior incident.

For each anti-pattern captured, write:

```yaml
- phrase: "<term>"
  reason: "<why it caused issues or why to avoid>"
  use_instead: "<preferred phrase>"
  first_encountered_cycle: <cycle-slug or null>
  applies_to_speakers: [<speaker-list>]
  applies_to_audiences: [<audience-list>]
```

This sub-phase is conversational (5 Whys style), not a pros/cons table — each anti-pattern is an operator narrative, not a structured choice.

---

### Sub-phase 6: Brand discovery (~5-10 min)

Walk through `brand_discovery` block:

**Q6a. Does this org have a consistent visual convention in their comms materials?**

| Option | Pros | Cons |
|---|---|---|
| **A. Full brand kit (colors, logo, signature block, email banner, DOCX template)** | Rich brand data; strong comms-templates seed | Requires sourcing the actual files, not just screenshots |
| **B. Partial brand (colors + logo only; no email/DOCX templates)** | Easy to seed palette and logo; comms templates approximate | Channel-specific templates may still need manual refinement |
| **C. Signature block + formatting conventions only (no colors)** | Captures sign-off and typography norms | No color data; skill falls back to bundled palette defaults |
| **D. No consistent brand in prior comms** | Operator starts fresh; clean slate for comms-templates | No prior-comms brand data to anchor from |
| **E. Other** | (describe what brand assets are available) | |

Then collect:
- What palette colors appear in email headers / banners from prior sources?
- What signature styling (bold/plain, job title format, org name format)?
- Any standard disclaimer or legal footer in comms artifacts?
- Is there an existing DOCX master or email template the operator can share?

If viable comms-brand data surfaces and `branding/<org-slug>/comms-templates/` does not yet exist, offer: "I can seed `comms-templates/` from this brand data. Run now or defer to `/brand init <org-slug>` after ingest?" If operator says now, proceed to auto-seed (mirrors `/brand init` Step 4 with operator-supplied color overrides).

---

### Sub-phase 7: Workshop synthesis

8. Present capture summary:

```
Captured during ingest:
- Sources processed: <N> (<list of source IDs>)
- Speakers with data: <list>  |  Speakers with no source: <list>
- Audiences with data: <list>
- Anti-patterns flagged: <N>
- Channel rules: <list of channels with data>
- Brand data: <found / not found>
```

9. Review gate. Surface:

> "Here's the org-comms-profile draft. Anything to correct, add, or remove before I write it?"

Present the full profile as YAML in chat. Wait for operator input. Accept corrections; do not write until operator confirms.

10. Run redaction pass per `redaction-rules.md`. Refuse write on banned-pattern detection.
11. Write `org-comms-profiles/<org-slug>.yaml` to Drive.
12. Append `ingest_history[]` entry:

```yaml
- date: YYYY-MM-DD
  sources_count: <N>
  sources_summary: "<brief description>"
```

---

## 4. Re-ingest handling

`/ingest` is rerunnable. New sources are additive:

- Load existing `org-comms-profiles/<org-slug>.yaml` at the start of a new ingest run.
- Present: "Existing profile has `<N>` ingest runs. I'll show you diffs between the current profile and what I'm about to extract."
- Operator reviews each proposed change: accept | reject | merge.
- `ingest_history[]` gets a new entry appended — history is never overwritten.
- If the operator rejects a proposed change, the existing value is preserved.

---

## 5. Source-type-specific notes

### 5.1 PDFs (past announcements, memos)

Claude.ai reads PDFs natively. Text content is available; figures and decorative elements are referenced by page but not extracted as register data. If the PDF contains multiple artifacts (e.g., a combined Q&A booklet), tag each section separately.

### 5.2 Pasted text (prior emails, intranet posts)

Exact paste preferred — do not paraphrase. Pasted text is processed as-is. Redaction scan runs on paste.

### 5.3 Prior PPTX (exec one-pagers, board summaries)

Skill extracts text from slide titles, body bullets, and speaker notes via `/mnt/skills/public/pptx`. Layout and images are NOT extracted as brand data — brand extraction from PPTX uses the text content only. Operator must separately provide palette/logo data if they want brand data from a prior PPTX.

---

## 6. Session-state-as-running-notes

Three sections only. Lives in working-state file, overwritten on each checkpoint.

```markdown
# Ingest Session State: <org-slug>
# Last checkpoint: <ISO timestamp>

## Current position
- Sub-phase: source-identity | voice-extraction | audience-profile-inference |
              channel-rules-detection | anti-pattern-surfacing | brand-discovery | workshop
- Active source: <source-id>
- Active speaker: <speaker or null>

## Data collected
- Sources processed: <N of <total>>
- Speakers with data: <list>
- Anti-patterns flagged: <N>
- Channel rules: <list>

## Questions remaining
- [ ] Source identity (any sources still pending)
- [ ] Voice extraction (which speakers still outstanding)
- [ ] Audience profile inference (which audiences still outstanding)
- [ ] Channel rules detection
- [ ] Anti-pattern surfacing
- [ ] Brand discovery
- [ ] Workshop synthesis
```

**Checkpoint triggers:**
- On every sub-phase transition
- At midpoint of any sub-phase running >15 minutes

Auto-checkpoint writes are silent — surface only on write failure.

---

## 7. Output files (every `/ingest` run)

- **Synthesized profile:** `org-comms-profiles/<org-slug>.yaml` — long-lived; updated additively on each run. This is the primary END artifact.
- **Raw capture:** `org-comms-profiles/_raw-capture/<org-slug>-YYYY-MM-DD.md` — append-only record. Contains scripted_opening, full Q&A, scripted_close.
- **Optional brand seed:** `branding/<org-slug>/comms-templates/` — seeded during Sub-phase 6 if brand data surfaced and operator confirmed. Only `comms-templates/` subdirectory; never sibling-owned files.

All writes go through the persistence backend per `persistence-and-ledger.md` (mirrored). Redaction pass runs before every write per `redaction-rules.md`.

---

## 8. What this protocol does NOT contain

- Universal interview techniques (Mom Test, SIPOC, 5 Whys, pros/cons tables, reflect-and-verify) — those live in `meta-protocol.md` (mirrored).
- Speaker register schema and 4-layer inheritance logic — those live in `speaker-register-rules.md`.
- Audience profile schema — that lives in `audience-profile-rules.md`.
- Redaction patterns — those live in `redaction-rules.md`.
- Question banks — those live in `template_assets/ingest_question_block.json`.
- org-comms-profile.yaml schema — that lives in `engagement-comms-config-template.md` (schema reference) and SPEC.md § 5.2.
- Brand kit scaffolding — that lives in `brand-mode-protocol.md`.
