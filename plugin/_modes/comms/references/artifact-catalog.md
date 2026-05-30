# Artifact Catalog — v1 (4 Artifacts)

Full catalog of every artifact this skill produces in v1. Loaded by `draft-protocol.md` and `cascade-protocol.md` at the start of any render. Provides the canonical format, length, section, brand template, and special rules so individual protocols do not duplicate them.

---

## Quick-reference table

| Artifact slug | Channel(s) | Format(s) | Valid speakers | Audience | Languages | Length cap |
|---|---|---|---|---|---|---|
| `all-hands-announcement` | `email`, `intranet` | HTML, PDF | `ceo`, `chro` | `all_employees` | FR-CA primary; EN secondary | 400 words body; subject ≤ 70 chars |
| `manager-faq` | `docx_distributable` | DOCX; PDF via DOCX→PDF | `chro`, `vp-ops` | `people_managers` | FR-CA (EN per-engagement) | 4 pages; ≥10 Q&A pairs |
| `hrbp-enablement-memo` | `docx_distributable` | DOCX; PDF via DOCX→PDF | `chro` | `hrbps` | FR-CA + EN | 4 pages + edge-case appendix |
| `exec-one-pager` | `pptx_distributable` | PPTX | `chro` | `exec_board` | EN (board language) | 1–3 slides |

---

### 1.1 `all-hands-announcement`

**Purpose.** Organization-wide communication announcing the compensation decision to all employees. First artifact written in a cascade — the headline framing established here must be consistent with the exec one-pager and must anchor the manager FAQ.

**Channels.** `email` and `intranet`. Same body content; only the wrapper differs:
- Email: `email-header.html` wrapper + speaker signature block
- Intranet: `pdf-master.yaml` wrapper (PDF for download or inline view)

Skill generates both wrappers from the same prose body. Do not write separate bodies per channel.

**Formats.**
- `html` — email body (inline HTML, compatible with standard ESP rendering)
- `pdf` — intranet version; rendered via PDF path verified at `/build` Phase 0 (see `draft-protocol.md` § PDF rendering). If PDF generation is unavailable, ship HTML only and note fallback.

**Valid speakers.** `ceo` or `chro`. Speaker must be one of these; any other value fails the valid-combinations check.

**Audience.** `all_employees`. Reading level grade 9; concrete vocabulary; concerns: paycheque impact, effective date, who to ask.

**Languages.** FR-CA primary (Quebec employer Bill 96 default). EN secondary if `languages.secondary: en` is set in `engagement-comms-config.yaml`. Both produced as parallel files — not a translation of each other (see `bilingual-rules.md`).

**File naming.**
```
all-hands-announcement-fr-ca-v<N>.html
all-hands-announcement-fr-ca-v<N>.pdf
all-hands-announcement-en-v<N>.html
all-hands-announcement-en-v<N>.pdf
```
Stored in `engagements/<slug>/comms/`.

**Length cap.**
- Subject line: ≤ 70 characters
- Body: ≤ 400 words (email/intranet cap from `channel_rules.email.max_body_words`)
- Intranet version may extend to 600 words if operator explicitly requests expanded intranet edition; default is the same 400-word body with minor lead-paragraph expansion.

**Required sections (in order).**

1. **Headline / Subject** — one sentence. Concrete and action-oriented. Avoid jargon.
2. **What changes** — 2–4 sentences. The core decision in plain language.
3. **Effective date** — explicit date. Never "soon" or "coming months."
4. **Who to ask** — 1 sentence directing employees to their manager or HRBP. No HR ticket numbers or personal emails.

Optional: **A personal word from [Speaker]** — 1 sentence in the speaker's register if CEO/CHRO sign-off is the cultural norm for the org. Pull from `speaker_registers.<speaker>.sign_off_convention`.

**Brand templates.**
```
template_assets/branding/_default/comms-templates/email-header.html
template_assets/branding/_default/comms-templates/email-signature/<speaker>.txt
template_assets/branding/_default/comms-templates/pdf-master.yaml
```
For orgs with a custom brand kit: `branding/<org-slug>/comms-templates/email-header.html`, etc. Auto-seed from `_default` if custom kit absent (per cold-start rule in `draft-protocol.md`).

**Special rules.**
- Same prose body for email and intranet — do not rewrite for channel.
- Subject line must appear before the body in the output file (needed for the email-header.html template substitution).
- Anti-pattern checklist runs before drafting, not after.
- Drift check against compensation-advisor source at every `/draft` run.

---

### 1.2 `manager-faq`

**Purpose.** Arm people managers with talking points and Q&A to handle team questions. Drafted second in a cascade (after exec one-pager). The headline and effective date from the all-hands announcement must be consistent here — do not rephrase the core decision.

**Channel.** `docx_distributable` only. Distributed as a file, not via email body or intranet page.

**Formats.**
- `docx` — primary format.
- `pdf` — secondary, produced via DOCX→PDF conversion per Phase 0 verification. If conversion unavailable, ship DOCX only.

**Valid speakers.** `chro` or `vp-ops`. CHRO is the default; VP Ops appropriate when the cycle is banner-specific (e.g., pharmacy-only wage scale).

**Audience.** `people_managers`. Reading level grade 12; mixed vocabulary; concerns: team questions, escalation triggers, talking points, timing.

**Languages.** FR-CA for Quebec manager populations. EN enabled per-engagement (set `languages.secondary: en` in artifacts config). When EN is enabled, a parallel DOCX is produced — not translated from FR-CA (per `bilingual-rules.md`).

**File naming.**
```
manager-faq-fr-ca-v<N>.docx
manager-faq-fr-ca-v<N>.pdf
manager-faq-en-v<N>.docx
manager-faq-en-v<N>.pdf
```

**Length cap.** 4 pages maximum. ≥10 Q&A pairs required. Group by topic cluster — do not present as a flat numbered list.

**Required sections (in order).**

1. **Headline** — restate the core decision in one sentence (must match all-hands-announcement headline verbatim).
2. **Top 5 questions employees will ask** — the most common questions anticipated; short direct answers. Pull from `key_objections_anticipated` in the compensation-advisor source.
3. **Talking points** — 3–5 bullet points for managers to use in team conversations. Action-oriented, not corporate.
4. **Escalation triggers** — explicit: "If an employee asks X, escalate to [HRBP/specific contact]." Never "use your judgment."
5. **FAQ index** — remaining Q&A pairs grouped by topic (e.g., "Timing," "Impact on my pay," "Special situations"). Minimum 10 total pairs including the Top 5.

Optional: **Consultation script** — a short opening script for managers to use when raising the topic with their team. 3–5 sentences. Pull from `speaker_registers.hrbp-manager.sample_paragraph` if populated.

**Brand template.** `comms-templates/docx-master.docx` (org-specific) or `template_assets/branding/_default/comms-templates/docx-master.docx` (cold start).

**Special rules.**
- Headline in section 1 must match the all-hands-announcement headline. If they conflict, flag to operator before writing.
- Q&A groupings must be labeled as topic clusters, not numbered sections.
- Escalation paths must be specific (name a role or team) — generic "contact HR" is a violation.

---

### 1.3 `hrbp-enablement-memo`

**Purpose.** Technical enablement for HR business partners. HRBPs handle edge cases, escalations, and compliance questions from both employees and managers. This memo goes to depth 3 (edge cases + escalation paths + calculation examples) — it is NOT a simplified version of the manager FAQ.

**Channel.** `docx_distributable`.

**Formats.**
- `docx` — primary.
- `pdf` — secondary via DOCX→PDF conversion. Falls back to DOCX-only if conversion unavailable.

**Valid speakers.** `chro` only. HRBP communications come from the CPO/CHRO to their HRBP team.

**Audience.** `hrbps`. Reading level college; technical vocabulary; concerns: edge cases, escalation paths, mechanics, compliance.

**Languages.** FR-CA + EN. Both produced by default (HRBPs typically serve bilingual populations and need reference in both languages).

**File naming.**
```
hrbp-enablement-memo-fr-ca-v<N>.docx
hrbp-enablement-memo-fr-ca-v<N>.pdf
hrbp-enablement-memo-en-v<N>.docx
hrbp-enablement-memo-en-v<N>.pdf
```

**Length cap.** 4 pages + edge-case appendix. The appendix does not count toward the 4-page cap.

**Required sections (in order).**

1. **Mechanics** — how the compensation change works, technically. Formulae, band adjustments, proration rules. More detail than the manager FAQ. Pull from `scenario_chosen` fields in the compensation-advisor source.
2. **Edge cases** — specific non-standard situations HRBPs will encounter. Minimum 5 cases. Format: situation → guidance → precedent or rule citation.
3. **Escalation paths** — who handles what when an HRBP cannot resolve. Named roles, not generic "contact compensation."
4. **Calculation worked example** — at least one complete worked example: name-anonymized employee profile → calculation → resulting pay change. Pull from `cycle.cohort` if available.
5. **Consultation script** — 3–5 sentences an HRBP can use when meeting with a manager or employee who escalates. Tone: technical but peer-to-peer. Pull from `speaker_registers.hrbp-manager.sample_paragraph` if populated.

**Appendix (required).** Edge-case decision tree or table. Minimum 5 entries. Can extend beyond 4-page cap.

**Brand template.** `comms-templates/docx-master.docx`.

**Special rules.**
- This is the only artifact that requires a calculation worked example. If the compensation-advisor source does not contain enough data to compute a real example, construct a generic one and mark it `[ILLUSTRATIVE — replace with actual figures]`.
- Appendix is required, not optional. If HRBPs are the audience, there are always edge cases.
- Do not simplify to the manager FAQ level — HRBPs are technically proficient.

---

### 1.4 `exec-one-pager`

**Purpose.** Board/executive-ready governance summary of the compensation decision. Produced first in the cascade (before all-hands) because the headline framing ratified here anchors all downstream artifacts. This is NOT a condensed version of the all-hands announcement — it is a different framing at depth 4 (tradeoffs / budget / governance).

**Channel.** `pptx_distributable`.

**Format.** `pptx` only. 1–3 slides, using the org's PPTX master.

**Valid speakers.** `chro` only. The CHRO presents to the board/exec team.

**Audience.** `exec_board`. Reading level college; technical vocabulary; concerns: governance, budget impact, peer benchmark, risk.

**Languages.** EN. Board language is English by default. If the operator explicitly sets `languages.primary: fr-ca` for this artifact, produce FR-CA instead.

**File naming.**
```
exec-one-pager-en-v<N>.pptx
```

**Length cap.** 1–3 slides. Hard maximum 3 slides. Each slide has one headline + supporting bullets + source footnote.

**Required sections (across slides).**

Slide 1 — **Decision summary.** What was decided, effective when, which cohort.
Slide 2 — **Cost impact.** Budget envelope, YoY delta, cost per FTE or per banner if multi-unit.
Slide 3 (optional) — **Governance + risk.** Regulatory compliance, union contract alignment, peer-benchmark comparison, downside risks and mitigations.

Footer on all slides: **Comparison to prior year** — key metric (e.g., "3.2% envelope vs 2.8% last cycle").

**Brand templates.** Two-layer:
1. `branding/<org-slug>/masters/` — org's PPTX master (owned by compensation-advisor; DO NOT overwrite)
2. `comms-templates/pptx-master/` — comms-specific overlay (slide layouts for 1-3-slide one-pager format)

If `branding/<org-slug>/masters/` does not exist, fall back to `template_assets/branding/_default/comms-templates/pptx-master/`.

**Special rules.**
- Produced first in `/cascade` dependency order, before all-hands.
- The headline on slide 1 becomes the canonical headline. All downstream artifacts must use it without rephrasal.
- One headline per slide — do not stack two assertions on one slide.
- Footnotes required: cite the compensation-advisor source slug and revision date.
- Depth 4 framing only: tradeoffs and governance. Do not include "what this means for employees" content — that belongs in the all-hands announcement.

---

## PDF rendering (Phase 0 verification required)

**Status at spec time:** OPEN. See SPEC.md § 11 and `draft-protocol.md` for the verification procedure and fallback logic.

- If DOCX→PDF conversion is available: `manager-faq`, `hrbp-enablement-memo`, and `all-hands-announcement` (PDF variant) go through the conversion path.
- If unavailable: `manager-faq` and `hrbp-enablement-memo` ship DOCX-only; `all-hands-announcement` ships HTML-only (already its primary channel format). Operator exports to PDF manually.
- `exec-one-pager` is PPTX-only and is unaffected by the PDF verification.

---

## Cascade dependency order

`/cascade` renders artifacts in this order. Do NOT reorder.

1. `exec-one-pager` — establishes the canonical headline
2. `all-hands-announcement` — uses the canonical headline from step 1
3. `manager-faq` — references the all-hands headline and top objections
4. `hrbp-enablement-memo` — references mechanics from step 1 and FAQ from step 3

---

## What this catalog does NOT contain

- Per-mode render flow — that lives in `draft-protocol.md` and `cascade-protocol.md`.
- Valid-combination registry semantics — that lives in `valid-combinations-rules.md` + `template_assets/valid-combinations.yaml`.
- Speaker register content — that lives in `speaker-register-rules.md` + `template_assets/speaker-registers/`.
- Bilingual co-draft mechanics — that lives in `bilingual-rules.md`.
- Drive write discipline — that lives in `persistence-and-ledger.md` (mirrored).
