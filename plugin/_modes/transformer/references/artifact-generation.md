# Artifact Generation

Catalog of every v1 artifact this skill produces, where it lives, which protocol owns it, and the write discipline applied.

Loaded by SKILL.md at any track entry that produces a file artifact. Provides the canonical naming, location, and frontmatter rules so individual protocols don't duplicate them.

---

## Artifact catalog

| Track | END artifact | Location (under `$STATE_ROOT`) | Owning protocol | Format |
|-------|--------------|------------------------------------|-----------------|--------|
| `/init` | `team-config.yaml` | `team-configs/<slug>.yaml` | `init-mode-protocol.md` | YAML |
| `/discover` (raw capture) | `discovery-<date>-<process>-<mode>.md` | `discovery/<slug>/YYYY-MM-DD-<process-slug>-<mode>.md` | `discovery-protocol.md` | Markdown (append-only) |
| `/discover` (synthesized) | `current-state.md` | `processes/<slug>/<process-slug>/current-state.md` | `discovery-protocol.md` | Markdown |
| `/discover` (cycle update) | Updated `team-config.yaml` | `team-configs/<slug>.yaml` (same as `/init`) | `cycle-discovery-and-gating.md` | YAML |
| `/diagnose` | `diagnosis.md` | `processes/<slug>/<process-slug>/diagnosis.md` | `diagnose-protocol.md` | Markdown |
| `/diagnose` (optional PPTX) | `diagnosis-<date>.pptx` | `processes/<slug>/<process-slug>/pptx/diagnosis-<YYYY-MM-DD>.pptx` | `diagnose-protocol.md` + `production-and-qa.md` | PPTX |
| `/transform` | `transformation-brief.md` | `processes/<slug>/<process-slug>/transformation-brief.md` | `transform-protocol.md` | Markdown |
| `/transform` (PPTX, required) | `transformation-brief-<date>.pptx` | `processes/<slug>/<process-slug>/pptx/transformation-brief-<YYYY-MM-DD>.pptx` | `transform-protocol.md` + `production-and-qa.md` | PPTX |
| `/transform` (council state) | `<date>-<process>-transform.yaml` | `council-states/<slug>/<date>-<process-slug>-transform.yaml` | `council-mode.md` | YAML |
| `/roadmap` | `roadmap-<Qx>.md` | `roadmap/<slug>/roadmap-<YYYY-Qx>.md` | `roadmap-protocol.md` | Markdown |
| `/roadmap` (PPTX, required) | `roadmap-<Qx>.pptx` | `roadmap/<slug>/pptx/roadmap-<YYYY-Qx>.pptx` | `roadmap-protocol.md` + `production-and-qa.md` | PPTX |
| `/roadmap` (council state) | `<date>-roadmap.yaml` | `council-states/<slug>/<date>-roadmap.yaml` | `council-mode.md` | YAML |
| `/council` (standalone) | `<date>-<topic>.yaml` | `council-states/<slug>/<date>-<topic>.yaml` | `council-mode.md` | YAML |
| `/council` (optional memo) | `council-memo-<date>.md` | `council-memos/<slug>/<date>-<topic>.md` | `council-mode.md` | Markdown |
| `/checkpoint` | `checkpoint.yaml` | `checkpoints/comp-team-transformer/<slug>/<process-slug>/checkpoint.yaml` | `persistence-and-ledger.md` | YAML |
| `/ledger update` | Updated `interventions-history.yaml` | `process-ledger/<slug>/interventions-history.yaml` | `persistence-and-ledger.md` | YAML |
| `/help` | (chat-only) | n/a | `help-mode-protocol.md` | n/a |

---

## Frontmatter discipline

Every markdown artifact carries YAML frontmatter at the top. Required keys per artifact type:

### `current-state.md`

```yaml
---
process_slug: <slug>
team_slug: <slug>
last_interview: YYYY-MM-DD
mode: self
discovered_cycle:
  anchor: <event>
  current_stage: <stage>
audience: comp-team-internal
engagement_mode: <mode_id>         # required — matches a v1 mode in engagement-modes.md
diagnosis_pending: true | false    # true when mode is discovery-only; false otherwise
---
```

### `diagnosis.md`

```yaml
---
process_slug: <slug>
team_slug: <slug>
date: YYYY-MM-DD
source_current_state: processes/<slug>/<process-slug>/current-state.md
audience: comp-team-internal | vp-people | external
engagement_mode: <mode_id>         # required — matches a v1 mode in engagement-modes.md
---
```

### `transformation-brief.md`

```yaml
---
process_slug: <slug>
team_slug: <slug>
date: YYYY-MM-DD
source_diagnosis: processes/<slug>/<process-slug>/diagnosis.md
council_state: council-states/<slug>/<date>-<process-slug>-transform.yaml
audience: comp-team-internal | vp-people | external
engagement_mode: <mode_id>         # required — matches a v1 mode in engagement-modes.md
---
```

### `roadmap-<Qx>.md`

```yaml
---
team_slug: <slug>
quarter: <YYYY-Qx>
date: YYYY-MM-DD
council_state: council-states/<slug>/<date>-roadmap.yaml
audience: vp-people  # default; override to comp-team-internal or external
cycle_anchor: <event>
---
```

### `council-memo-<date>.md`

```yaml
---
team_slug: <slug>
date: YYYY-MM-DD
topic: <free text>
council_state: council-states/<slug>/<date>-<topic>.yaml
audience: vp-people | external
length_cap_words: 800
---
```

**Hard rule:** every artifact write runs the redaction pre-write scan. The scan checks the body AND validates the `audience` tag is present in frontmatter. Missing audience tag → refuse to write.

---

## Naming conventions

- **Slugs:** kebab-case, lowercase, alphanumeric + hyphen. Match `^[a-z][a-z0-9-]*$`.
- **Dates in filenames:** ISO format (YYYY-MM-DD). Always 4-digit year, 2-digit month, 2-digit day.
- **Quarters:** `YYYY-Qx` (e.g., `2026-Q3`). Always 4-digit year.
- **No spaces in filenames.** Use hyphens.
- **No personal information in filenames.** Slugs are organizational scope, not personal identifiers.

---

## Write discipline

### Atomicity

Co-dependent artifacts use the **batched-folder-write** pattern (per `persistence-and-ledger.md`):

1. Write all artifacts in a session to a `_pending/` subfolder of the target location.
2. After all writes succeed, move from `_pending/<filename>` to `<filename>`.
3. On failure, surface to user — leave the partial state in `_pending/` for recovery rather than half-applied across the canonical paths.

Single-file artifacts can write directly without `_pending/`.

### Redaction pass

Runs before every write. Per `redaction-rules.md`. Banned-pattern detection → hard refuse, surface to user, no fallback.

### Visibility check

Runs before every write. Per `persistence-and-ledger.md`. Non-schema artifacts under `$STATE_ROOT` are local to the operator's machine and not shared externally.

### Audience tag check

Frontmatter must contain a valid `audience` tag (`comp-team-internal`, `vp-people`, or `external`). Missing or invalid → refuse to write.

---

## Chat-render fallback

When the `market` backend is unreachable and no local cache is available, the skill renders every artifact body in chat with explicit save instructions:

> "Backend unreachable. Save the following as `<full path under $STATE_ROOT>`:
>
> ```markdown
> <artifact body>
> ```
>
> Confirm when saved, or say 'skip' to leave it un-persisted."

The chat-render fallback does NOT skip the redaction pass — banned patterns still hard-refuse. The user cannot bypass redaction this way.

---

## What this protocol does NOT contain

- Output schemas (those live in the per-template files: `current-state.md`, `diagnosis_template.md`, `transform_spec_template.md`, `roadmap_template.md`).
- Track-specific generation logic (those live in the per-protocol files: `discovery-protocol.md`, `diagnose-protocol.md`, `transform-protocol.md`, `roadmap-protocol.md`).
- Backend / ledger specifics (those live in `persistence-and-ledger.md`).

This file is the cross-cutting catalog of artifacts and the write discipline that applies to all of them.
