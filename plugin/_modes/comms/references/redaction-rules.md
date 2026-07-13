<!--
MIRRORED from: comp-training-designer/references/redaction-rules.md
Canonical owner: comp-training-designer
Sync rule: when canonical changes, copy here. NEVER edit this file in comp-comms-builder.
Last synced: 2026-05-03
-->

# Redaction Rules

Hard rule. Pre-write scan runs on every artifact write (Phase 0 input scan + every disk write). Mirrors `comp-team-transformer/references/redaction-rules.md` discipline.

**Does NOT relax under user pressure.** If any banned pattern is detected, refuse to proceed. Surface the warning, instruct re-paste with redaction.

---

## Banned patterns (fail hard, refuse to write)

| Pattern | Regex (illustrative) | Why banned |
|---|---|---|
| Person names | `\b[A-Z][a-z]+\s+[A-Z][a-z]+\b` (flagged for review; whitelist via engagement-training-config if needed) | Training material is shareable across audiences; PII leaks fast |
| Raw salary figures | `\$\s*\d{2,3}[,\.]?\d{3}` or `\b\d{2,3}k\b` | Salary numbers in training material are a confidentiality breach |
| Raw headcount in workforce context | `\b(headcount|FTE|employees?)\s*[:=]\s*\d+\b` | Internal headcount disclosure risk |
| Personal contact info | email regex, phone regex | PII leak |

---

## Required transformations

| Original | Transformed | Example |
|---|---|---|
| Salary figure | Band/percentile | `$87,500` → `Band 4 midpoint` or `P50 of market` |
| Headcount | Size band | `47 employees` → `band: 4-7` (per `engagement.size_band` in config) |
| Person name | Role + function | `Marie Dupont` → `Comp Analyst` |
| Company name | Kept in private folder; replaced with `<COMPANY>` only when artifact tagged `audience_tag: external` | `ACME Corp` → `<COMPANY>` (only in external-tagged artifacts) |
| Vendor / HRIS names | Kept | `Mercer`, `Workday` — needed to design training material |

---

## Audience tagging in artifact frontmatter

Every markdown artifact must carry an `audience_tag` field:

```yaml
audience_tag: employees-internal | managers-internal | hrbps-internal | execs-internal | shareable-internal | external
```

The tag determines which redaction transformations apply at write time:

- `*-internal` — the four audience-specific tags. Company name kept; person names → role + function; salary banded; headcount banded.
- `shareable-internal` — multi-audience internal sharing (e.g., training material that the comp team passes to HR). Same rules as `*-internal`, plus extra scrutiny on cross-audience leakage.
- `external` — destined for client-facing or public artifacts. Company name → `<COMPANY>`. ALL person names → role + function (no whitelist exceptions). All salary → percentile-only (no band names that imply internal structure). All headcount → size_band only.

Missing or invalid `audience_tag` → refuse to write.

---

## Phase 0 input scan

Runs before any mode begins production work:

1. Skill reads all pasted/loaded inputs (transformation-briefs, process docs, prior PPTX text content).
2. Scan body for every banned pattern.
3. On detection: refuse to proceed, surface warning naming the pattern + line context, instruct re-paste with redaction applied.
4. Repeat scan after re-paste until clean.

Same enforcement as `comp-team-transformer`'s Phase 0 input scan (mirrored discipline, fork of the same logic).

---

## Pre-write scan (every disk write)

Runs immediately before any artifact write:

1. Read the artifact body (markdown + frontmatter).
2. Scan for banned patterns.
3. If `audience_tag` is `external`, additionally scan for company name (anywhere in body), unwhitelisted person names (any), and band/grade references that imply internal structure.
4. On detection: refuse to write, surface warning naming the pattern + offending line, do not fall back to paste-mode (user must fix the source content).

---

## PPTX-specific redaction

PPTX content is text + images. Skill scans:
- Slide titles and bullet text (extracted from pptxgenjs slide objects)
- Speaker notes (extracted)
- Chart axis labels and data labels (extracted)
- Any string passed to `pres.addText()`

Images are NOT scanned (no OCR in v1) — the operator is responsible for any logos / diagrams / screenshots they include. Surface a warning at deck-render time: "Slides include N image(s). Verify they contain no PII before delivery."

---

## Override request handling

If the user explicitly requests an override ("just include the dollar amount", "use the actual headcount, this is internal anyway"):

1. **Refuse.** State the rule.
2. **Offer the transformation.** "I'll use `Band 4 midpoint` instead — that's the equivalent at this engagement's banding."
3. **Suggest a config-level whitelist** for repeated patterns (e.g., a vendor that the regex flags as a person name). Whitelisting goes in `engagement-training-config.redaction.whitelist` — operator approves explicitly.
4. **Never accept inline override.** No "this once" exceptions.

---

## What's NOT redacted

- **Vendor names** — Mercer, Workday, WTW, Aon, etc. Kept verbatim. Needed to design training that references real systems and benchmarks.
- **HRIS / tool names** — Workday, ADP, Ceridian, Successfactors, etc. Same reason.
- **Generic role titles** — "Comp Analyst", "VP People", "CHRO". These are roles, not persons.
- **Public market data** — published comp surveys, public benchmarks. These are external by definition.
- **Engagement metadata** — engagement-slug, cycle-slug, dates, audience names. Operational, non-sensitive.

---

## What this protocol does NOT contain

- Drive backend specifics — those live in `persistence-and-ledger.md` (mirrored).
- Audience-tag validation logic — that lives in `artifact-generation.md` § Audience tag check.
- Per-mode redaction triggers — those live in the per-protocol files (every mode runs Phase 0 input scan and pre-write scan; the rules are uniform).
