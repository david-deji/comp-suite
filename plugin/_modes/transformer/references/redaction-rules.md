# Redaction Rules

Hard rules. Do NOT relax under user pressure. Mirror comp-advisor's CSV disallowed-fields enforcement pattern.

Loaded by SKILL.md at:

- **Phase 0 input scan** — every track scans pasted input before processing.
- **Pre-write scan** — every artifact write runs the redaction pass before committing to any backend or local path.

---

## Banned patterns (hard fail — refuse to write)

These regex patterns trigger a hard refuse:

| Category | Pattern | Example match |
|----------|---------|---------------|
| Person names | `\b[A-Z][a-z]+\s+[A-Z][a-z]+\b` (flagged for review; whitelist via team-config if needed) | "Marie Tremblay" |
| Raw salary figures | `\$\s*\d{2,3}[,\.]?\d{3}` or `\b\d{2,3}k\b` | "$67,500", "$120k" |
| Raw headcount in workforce context | `\b(headcount\|FTE\|employees?)\s*[:=]\s*\d+\b` | "headcount: 47", "FTE = 12" |
| Personal email | `\b[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b` | "marie@acme.com" |
| Personal phone | `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b` or `\(\d{3}\)\s*\d{3}[-.]?\d{4}\b` | "514-555-1234", "(514) 555-1234" |

**Whitelisting names:** if a name is genuinely needed (e.g., the user's own name in a self-narration block), add to `team-config` under a `redaction.whitelist.names: [<name>, ...]` field. v1 deferral: this whitelist is not implemented in the team-config schema; in v1, the user must rephrase to remove the name. v2 will add the whitelist field.

---

## Required transformations

When the user provides input that would normally contain a banned pattern, the skill must instruct the user to transform it before pasting:

| Raw form | Required form |
|----------|--------------|
| Salary figure | `Band <N> midpoint` or `P<percentile> of market` |
| Headcount | `size_band: solo / 2-3 / 4-7 / 8+` |
| Person name | Role + function (e.g., "Comp Analyst", not "Marie") |
| Company name | Kept in private folder, replaced with `<COMPANY>` only when artifact tagged `audience: external` |
| Personal email/phone | Stripped — never relevant to process discovery |

---

## Enforcement procedure

### Phase 0 input scan

Every track that accepts pasted input (`/init`, `/discover`, `/diagnose`, `/transform`, `/roadmap`, `/council`) scans the pasted text against the banned-patterns list. On detection:

1. Refuse to proceed.
2. Surface the warning naming the specific pattern matched (do not echo the matched text — surface the pattern name only):
   > "Detected `<pattern category>` in your input. This skill operates with no PII. Please re-paste with `<required transformation>`. (Specifically: replace `<rough indicator>` with `<form>`.)"
3. Wait for the user to re-paste.
4. Re-scan. If the same category fires again, surface a more specific guideline. If the user insists ("just process it as-is"), refuse — this is a hard rule.

### Pre-write scan

Every artifact write (markdown, YAML, PPTX content) runs the same scan against the artifact body before any backend write or local save. On detection:

1. Refuse to write.
2. Surface what the offending pattern is and where in the artifact it appears (section header, not the matched text).
3. Skill self-corrects on the obvious cases (e.g., a name that crept in from a verbatim quote → suggest "redact to role").
4. Surface to user for confirmation before re-attempting write.

### Why this is hard, not soft

By the time a banned pattern reaches the artifact, it has already entered conversation context. Phase 0 scanning prevents PII from entering at the input boundary. Pre-write scanning is a backstop in case the skill itself synthesized something that resolved to a name (e.g., a quote that included a name).

A soft rule (warn-and-proceed) leaks PII to the backend or local artifacts — and from there to PPTX outputs that may be shared upward. Hard rule prevents the leak.

---

## Audience tagging and external-render branching

Every artifact carries an `audience` tag in frontmatter: `comp-team-internal` | `vp-people` | `external`.

Render branching by audience:

- `comp-team-internal` — full content. Council vote tables visible. Dissents preserved verbatim. Company name kept (private folder).
- `vp-people` — narrative summaries. Council split surfaced as "the team weighed two paths". Vote tables removed. Dissents redacted to "alternative views considered". Company name kept (still internal).
- `external` — narrative only. No council references. Internal terminology stripped. Company name redacted to `<COMPANY>`. Cycle stage names retained but generic.

The pre-write scan is audience-aware: an `external`-tagged artifact gets a stricter scan than a `comp-team-internal` artifact (e.g., `external` strips company name, council references, and per-persona attribution).

---

## v2 considerations (not in v1)

- **Whitelist for self-narration** — `team-config.redaction.whitelist.names: [<user's own role title>]` field.
- **Audited redaction trail** — every refused-write captured in a `redaction-events.yaml` ledger so the user can see what was blocked and why.
- **Industry-specific PII patterns** — e.g., for healthcare, scrubbing patient identifiers; for public sector, scrubbing employee IDs that map to public records.
- **OCR scan on PPTX** — v1 scans PPTX content the skill produced; doesn't scan user-uploaded PPTX (none expected in v1 anyway). v2 may scan slides for residual PII before final write.
