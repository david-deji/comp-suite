# Artifact Generation

Catalog of every v1 artifact this skill produces, where it lives, which protocol owns it, and the write discipline applied.

Loaded by SKILL.md at any mode entry that produces a file artifact. Provides the canonical naming, location, and frontmatter rules so individual protocols don't duplicate them.

---

## Artifact catalog

| Mode | END artifact | Location (in shared Drive folder) | Owning protocol | Format |
|------|--------------|------------------------------------|-----------------|--------|
| `/init` | `engagement-training-config.yaml` | `engagement-training-configs/<slug>.yaml` | `init-mode-protocol.md` | YAML |
| `/brand init <org-slug>` | brand kit scaffold | `branding/<org-slug>/` (theme/, logo placeholders, _README.md, footnotes.yaml) | `brand-mode-protocol.md` + `brand-kit-protocol.md` (mirrored) | mixed |
| `/ingest` (raw capture) | `ingest-<date>-<mode>.md` | `discovery/<engagement>/<cycle-slug>/YYYY-MM-DD-ingest-<mode>.md` | `ingest-protocol.md` | Markdown (append-only) |
| `/ingest` (synthesized) | `message-map.yaml` | `cycles/<engagement>/<cycle-slug>/message-map.yaml` | `ingest-protocol.md` | YAML |
| `/generate` (audience-design raw) | `audience-design-<audience>.md` | `discovery/<engagement>/<cycle-slug>/YYYY-MM-DD-audience-design-<audience>.md` | `generate-protocol.md` | Markdown (append-only) |
| `/generate` (deck) | `<audience>.pptx` | `cycles/<engagement>/<cycle-slug>/<audience>.pptx` | `generate-protocol.md` + `production-and-qa.md` (mirrored) | PPTX |
| `/generate` (facilitator guide) | `<audience>-facilitator.md` | `cycles/<engagement>/<cycle-slug>/<audience>-facilitator.md` | `generate-protocol.md` | Markdown |
| `/generate` (interactive blocks) | `<audience>-interactive-blocks.md` | `cycles/<engagement>/<cycle-slug>/<audience>-interactive-blocks.md` | `generate-protocol.md` + `interactive-blocks.md` | Markdown |
| `/generate` (council state) | `<cycle-slug>-<audience>-generate.yaml` | `council-states/<engagement>/<cycle-slug>-<audience>-generate.yaml` | `council-mode.md` | YAML |
| `/cascade` (deck) | `managers-cascade-kit.pptx` | `cycles/<engagement>/<cycle-slug>/managers-cascade-kit.pptx` | `cascade-protocol.md` + `production-and-qa.md` (mirrored) | PPTX |
| `/cascade` (facilitator guide) | `managers-cascade-facilitator.md` | `cycles/<engagement>/<cycle-slug>/managers-cascade-facilitator.md` | `cascade-protocol.md` | Markdown |
| `/council` (standalone) | `<date>-<topic>.yaml` | `council-states/<engagement>/<date>-<topic>.yaml` | `council-mode.md` | YAML |
| `/council` (optional memo) | `council-memo-<date>-<topic>.md` | `council-states/<engagement>/council-memo-<date>-<topic>.md` | `council-mode.md` | Markdown |
| `/checkpoint` | `checkpoint.yaml` | `checkpoints/comp-training-designer/<engagement>/<cycle-slug>/checkpoint.yaml` | `persistence-and-ledger.md` (mirrored) | YAML |
| `/help` | (chat-only) | n/a | `help-mode-protocol.md` | n/a |

---

## Frontmatter discipline

Every markdown artifact carries YAML frontmatter at the top. Required keys per artifact type:

### `<audience>-facilitator.md`

```yaml
---
engagement_slug: <slug>
cycle_slug: <e.g., year-end-2026>
audience: employees | managers | hrbps | execs
date: YYYY-MM-DD
delivery_target: "Week <N> / <stage-name> / target date YYYY-MM-DD"
source_message_map: cycles/<engagement>/<cycle-slug>/message-map.yaml
source_council_state: council-states/<engagement>/<cycle-slug>-<audience>-generate.yaml
audience_tag: <audience>-internal | shareable-internal | external
posture: broadcast-with-checkpoints
---
```

### `<audience>-interactive-blocks.md`

```yaml
---
engagement_slug: <slug>
cycle_slug: <e.g., year-end-2026>
audience: employees | managers | hrbps | execs
date: YYYY-MM-DD
slide_refs: [3, 7, 12, 18]   # which slides each block targets
audience_tag: <audience>-internal
---
```

### `managers-cascade-facilitator.md`

```yaml
---
engagement_slug: <slug>
cycle_slug: <e.g., year-end-2026>
audience: managers-cascade   # special tag — derived from managers
date: YYYY-MM-DD
delivery_target: "Week <N> / <stage-name> / target date YYYY-MM-DD"
source_manager_deck: cycles/<engagement>/<cycle-slug>/managers.pptx
audience_tag: managers-internal
target_duration_minutes: 30
---
```

### `council-memo-<date>-<topic>.md`

```yaml
---
engagement_slug: <slug>
date: YYYY-MM-DD
topic: <free text>
council_state: council-states/<engagement>/<date>-<topic>.yaml
audience_tag: comp-team-internal | shareable-internal | external
length_cap_words: 800
---
```

### `ingest-<date>-<mode>.md` (raw capture)

```yaml
---
engagement_slug: <slug>
cycle_slug: <e.g., year-end-2026>
mode: self
date: YYYY-MM-DD
sources_processed: [list of source IDs]
audience_tag: comp-team-internal
---
```

**Hard rule:** every artifact write runs the redaction pre-write scan. The scan checks the body AND validates the `audience_tag` is present in frontmatter. Missing audience tag → refuse to write.

---

## Naming conventions

- **Slugs:** kebab-case, lowercase, alphanumeric + hyphen. Match `^[a-z][a-z0-9-]*$`.
- **Dates in filenames:** ISO format (YYYY-MM-DD). Always 4-digit year, 2-digit month, 2-digit day.
- **Cycle slugs:** kebab-case, descriptive (e.g., `year-end-2026`, `mid-year-refresh-2027`, `policy-update-2026-q3`).
- **Audience names:** fixed v1 set: `employees`, `managers`, `hrbps`, `execs`. (`managers-cascade` is derived; not a primary audience.)
- **No spaces in filenames.** Use hyphens.
- **No personal information in filenames.** Slugs are organizational scope, not personal identifiers.

---

## Write discipline

### Atomicity (Drive backend)

Drive lacks atomic multi-file saves. Co-dependent artifacts use the **batched-folder-write** pattern (per `persistence-and-ledger.md` mirrored):

1. Write all artifacts in a session to a `_pending/` subfolder of the target location.
2. After all writes succeed, atomic move (Drive rename) from `_pending/<filename>` to `<filename>`.
3. On failure, surface to user — leave the partial state in `_pending/` for recovery rather than half-applied across the canonical paths.

Single-file artifacts can write directly without `_pending/`.

`/generate` per-audience produces 3 co-dependent artifacts (PPTX + facilitator guide + interactive blocks) — always batched.

### Redaction pass

Runs before every write. Per `redaction-rules.md`. Banned-pattern detection → hard refuse, surface to user, no fallback.

### Visibility check

Runs before every write. Per `persistence-and-ledger.md` (mirrored). Drive folder must be private (no "Anyone with link" or public sharing). Verified at first mode invocation in a session and on every checkpoint.

### Audience tag check

Frontmatter must contain a valid `audience_tag` (`employees-internal`, `managers-internal`, `hrbps-internal`, `execs-internal`, `shareable-internal`, or `external`). Missing or invalid → refuse to write.

### Delivery-target stamp (PPTX-producing modes only)

Every rendered deck (`/generate` per audience, `/cascade`) writes a `delivery_target` field on the cover slide AND in deck frontmatter. Computed from `cycle.current_stage` + operator-supplied `delivery_target_week_offset` per `cycle-awareness.md`. Soft warning if target date is in the past — does not block write.

---

## Paste-mode fallback

When `engagement-training-config.persistence.enabled == false` OR Drive backend is unreachable, the skill renders every artifact body in chat with explicit save instructions:

> "Persistence disabled. Save the following as `<full path in Drive folder>`:
>
> ```markdown
> <artifact body>
> ```
>
> Confirm when saved, or say 'skip' to leave it un-persisted."

Paste-mode does NOT skip the redaction pass — banned patterns still hard-refuse. The user can't bypass redaction by switching to paste-mode.

PPTX artifacts in paste-mode: skill produces a markdown spec (`<audience>.pptx-spec.md`) instead of a binary .pptx. The operator runs `node build_template.js` locally (or in Claude.ai scratch) to render. `examples/year-end-cycle/` demonstrates this format.

---

## What this protocol does NOT contain

- Per-template content schemas — those live in the per-template files (`message_map_template.yaml`, `facilitator_guide_template.md`, `interactive_block_templates.json`, `cascade_kit_template.md`).
- Mode-specific generation logic — those live in the per-protocol files (`ingest-protocol.md`, `generate-protocol.md`, `cascade-protocol.md`).
- Drive API specifics — those live in `persistence-and-ledger.md` (mirrored from compensation-advisor).

This file is the cross-cutting catalog of artifacts and the write discipline that applies to all of them.
