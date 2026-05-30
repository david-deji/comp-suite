# Skill Overview

Phase map, Phase 0 detail, and core principles. Loaded by SKILL.md alongside `team-config-template.md` at every track entry that runs Phase 0 (which is every track except `/help`, `/resume`, and `/ledger` read paths).

---

## Phase map

```
Phase 0 — Config Loading        (every track: persistence test, team-config load, redaction scan, cycle compute, surface state)
   │
   ├─→ /init        → team-config walkthrough (no production work)
   ├─→ /discover    → Phase 1 (conversational interview: skill asks, operator answers)
   ├─→ /diagnose    → Phase 2 (9-step systems-thinking pass)
   ├─→ /transform   → Phase 3 (work-decomposer + categorical bands + council auto-fire)
   └─→ /roadmap     → Phase 4 (sequencing + cycle-fit gating + council auto-fire)

   /council         → reasoning only, can fire standalone or auto-fire from Phase 3 / Phase 4
   /checkpoint      → mid-track state save (any phase)
   /resume          → restore from saved checkpoint
   /ledger          → outcome update on shipped intervention
   /help            → list of tracks (chat-only)
```

Typical first-cycle workflow: `/init` → `/discover` → `/diagnose` → `/transform` → `/roadmap`.

---

## Phase 0 detail (Config Loading)

Runs at every track entry except `/help`, `/resume`, `/ledger` read paths. Five steps in order:

### 1. Persistence backend test

Run a Drive folder-list against `team-config.persistence.drive_folder_id`. Three outcomes:

- **Success + visibility check passes** (folder is private, not "Anyone with link") → proceed.
- **Success + visibility check fails** (folder shared with anyone, or public) → refuse all writes. Surface: "Persistence folder is `<visibility>`. Skill writes only to private folders. Restrict the folder to specific people or run paste-mode."
- **Unreachable / permission denied** → fall back to paste-mode. Surface: "Drive backend unreachable. Operating in paste-mode for this session."

Runs once per session. Cache result for the session.

### 2. Team-config load

Three paths:

- User pasted YAML at session start → parse against `team-config-template.md` schema. Validate. If validation fails, surface specific rule violated and exit.
- User referenced a `team.slug` (e.g., "/discover for `comp-team-acme`") → auto-load `team-configs/<slug>.yaml` from persistence.
- Neither → prompt: "No team config — run `/init` first?" and exit.

After load: `team-config.cycle.current_stage` and `team-config.cycle.current_week_offset` are computed from `cycle.anchor_event` + today's date. Cached for session.

### 3. Redaction input scan

Scan all pasted inputs for banned patterns per `redaction-rules.md`:

- Person names
- Raw salary figures
- Raw headcount in workforce context
- Personal email
- Personal phone

On detection: refuse to proceed, surface warning naming the pattern category, instruct re-paste with required transformation. Hard rule.

### 4. Cycle awareness load

If `cycle.stages` is non-empty, compute `current_stage` and `current_week_offset` from `cycle.anchor_event` + today's date. Cache for cycle-gating decisions in `/transform` and `/roadmap`.

If `cycle.stages == []`:
- For `/discover`: route through `cycle-discovery-and-gating.md` mapping block (mandatory mid-Intake).
- For `/transform` / `/roadmap`: surface warning that gating is disabled, accept user choice to proceed without gating.

### 5. Surface state to user

One-line summary:

> "Loaded team `<name>` (`<slug>`). `<N>` processes tracked. Current cycle stage: `<stage>` (week `<offset>` from anchor). Persistence: `<enabled/paste-mode>`."

Then proceed to track-specific protocol.

---

## Core principles

### Artifact philosophy

Every track produces a durable consumption artifact. Markdown for working documents (`current-state.md`, `diagnosis.md`, `transformation-brief.md`, `roadmap-<Qx>.md`). PPTX for executive readouts on `/diagnose` (optional), `/transform` (required), `/roadmap` (required). Council always produces `council-state.yaml`. Only `/help` is chat-only.

No PPTX during interview phases. PPTX is the END artifact for shareable readouts, not for working iteration.

### Redaction discipline

Hard rules per `redaction-rules.md`. Phase 0 input scan + every-write pre-write scan. Never relaxes under user pressure. Detection → refuse, instruct, wait. The skill operates with no PII on disk.

### Cycle awareness

When `cycle.stages` is populated, every transformation rollout is gated against the discovered cycle. `/transform` annotates earliest viable rollout per spec. `/roadmap` rejects placements into `live` or `prep` windows without explicit override. The user explicitly acknowledges any override.

Cycle stages are discovered, never pre-configured (per VISION lock and IE research).

### Conversational interview discipline

`/discover` runs a single continuous interview in one Claude.ai conversation. The skill is the interviewer; the operator is the SME being interviewed. No three-mode pipeline, no live-call copilot. The skill uses pros/cons option tables (3-5 options + "Other") for structured choices and Mom Test behavioral questions for narrative answers. One question per turn — never stacks a table with a follow-up question. See `references/meta-protocol.md` for the full interview contract.

### Council single-context

Personas are sequential voice blocks within ONE response. Never parallel subagents. Synthesis follows after every persona block is complete. Auto-fires on `/transform` (band locks) and `/roadmap` (sequence locks). No weighted scoring in v1 — categorical bands only.

### Checkpoint blocking

`/checkpoint` writes are synchronous. The next phase blocks until the user explicitly confirms.

### Quick Wins are P0

Every `/diagnose` produces ≥2 Quick Wins as the FIRST content section after frontmatter. Quick Wins are actions the user can take this week without further engineering, leadership approval, or `/transform` work. P0 means it's the first thing a reader sees — even before the systems map.

### Mirrored references are read-only

`persistence-and-ledger.md`, `production-and-qa.md`, `template-master.md`, `brand-kit-protocol.md`, `tools-available.md` are manual copies of source files in [github.com/david-deji/compensation-advisor](https://github.com/david-deji/compensation-advisor). Each file has a mirror header at the top naming its canonical URL. This skill never edits them — coordinate with compensation-advisor for any change, then re-copy here.

### Paste-mode fallback

When persistence is disabled or unreachable, the skill renders every artifact body in chat with explicit save instructions. Paste-mode does NOT skip redaction — banned patterns still hard-refuse.

---

## Glossary

| Term | Meaning |
|------|---------|
| Quick Win | P0 action a user can take this week without further engineering, leadership approval, or `/transform` work. ≥2 required per diagnosis. |
| Strong Candidate | Transformation candidate with clear ROI, integration path known, fits in next slack window. Gets a full work-decomposer spec in `/transform`. |
| Needs Groundwork | Promising candidate blocked by data quality, tooling gap, or change-readiness deficit. Dependency notes only — no spec in v1. |
| Not Ready | Candidate parked — speculative, integration cost unclear, or against current cycle gating with no slack window in next 2 quarters. |
| Cycle stage | Named phase of the comp cycle relative to the anchor event (effective date or scale-ship date). Tagged `live` / `prep` / `slack`. |
| Slack window | A `slack`-tagged stage where transformation rollouts may ship. Pre-cycle calm or post-cycle calm. |
| Live window | A `live`-tagged stage during active cycle execution. No transformations may ship — hard refuse. |
| Prep window | A `prep`-tagged stage during cycle preparation. No disruptive change — hard refuse. |
| Auto-fire | Council fires automatically on `/transform` band lock and `/roadmap` sequence lock. User does not invoke. |
| Categorical band | One of {Quick Win, Strong Candidate, Needs Groundwork, Not Ready}. No numeric scoring in v1. |
| Gap detection | Pre-close check that surfaces any sub-phase that didn't get full coverage during `/discover`. |
| Cycle anchor | Event the comp cycle hangs on (e.g., effective date YYYY-MM-DD). Used to compute `current_week_offset` for every other stage. |
| Audience tag | `comp-team-internal` / `vp-people` / `external`. In artifact frontmatter. Determines render branching and redaction strictness. |

---

## Where things live (cheat sheet)

| Question | Answer |
|----------|--------|
| Where is the team config? | `team-configs/<slug>.yaml` in shared Drive folder |
| Where is the current state of process X? | `processes/<slug>/<process-slug>/current-state.md` |
| Where are diagnoses? | `processes/<slug>/<process-slug>/diagnosis.md` (optional PPTX in `pptx/`) |
| Where are transformation briefs? | `processes/<slug>/<process-slug>/transformation-brief.md` + required PPTX in `pptx/` |
| Where are roadmaps? | `roadmap/<slug>/roadmap-<YYYY-Qx>.md` + required PPTX in `pptx/` |
| Where are council states? | `council-states/<slug>/<date>-<topic-or-process>.yaml` |
| Where are checkpoints? | `checkpoints/comp-team-transformer/<slug>/<process-slug>/checkpoint.yaml` |
| Where is the outcome ledger? | `process-ledger/<slug>/interventions-history.yaml` |
| Where is the persistence contract? | `references/persistence-and-ledger.md` (mirrored from `david-deji/compensation-advisor`) |
| Where is the brand kit? | `branding/<org_slug>/` in shared Drive folder (per `brand-kit-protocol.md`, mirrored from `david-deji/compensation-advisor`) |
