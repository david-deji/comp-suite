# Skill Overview

Phase map, Phase 0 detail, and core principles for `comp-training-designer`. Loaded by SKILL.md at session entry, before any mode-specific reference loads.

---

## Phase map

| Phase | Mode(s) | Purpose | Output |
|---|---|---|---|
| **Phase 0** | every mode except `/help`, `/resume` | Config loading, identity + org resolution, redaction input scan, cycle awareness load, surface state | (no artifact — readiness gate) |
| **Phase 1** | `/ingest` | Source extraction → message-map (conversational interview) | `cycles/<engagement>/<cycle-slug>/message-map.yaml` |
| **Phase 2** | `/generate` | Per-audience render (audience-design interview → council auto-fire → bundle render) | per-audience PPTX + facilitator guide + interactive blocks |
| **Phase 3** | `/cascade` | Manager deck → 30-min team-meeting variant (mechanical derivation) | `managers-cascade-kit.pptx` + `managers-cascade-facilitator.md` |
| **Phase 4** | `/brand` | Read/write engagement brand kit (shared with siblings) | brand kit for `<org-slug>` (`brand_get_kit` / `brand_put_kit`) |

`/init`, `/council`, `/checkpoint`, `/resume`, `/help` are utility/control modes — they don't sit in the phase progression.

---

## Phase 0 detail (every mode except `/help`, `/resume`)

Sequence (silent unless something fails):

1. **Identity + org resolution.** Resolve the operator's OAuth identity → org via `list_my_orgs`; read the org header via `engagement_get_master`. The `market` backend is always reachable via OAuth; transport failure (connection error, timeout, 5xx, not-yet-authenticated) falls back to the local `$STATE_ROOT` read cache (D1) — not to a paste-mode branch. A tool returning not-found/empty is authoritative.

2. **Engagement-training-config load.** If user pasted YAML, parse against schema (per `engagement-training-config-template.md`). If a `engagement.slug` was referenced, load the engagement config from the backend via `engagement_get` (local cache on transport failure, D1). If neither: prompt "No engagement-training-config — run `/init` first?" and exit.

3. **Cross-skill cycle load.** If `engagement.slug` matches a sibling `comp-team-transformer/team-configs/<slug>.yaml`, copy `cycle.stages` from there into in-memory state. Sibling skills share cycles — never duplicate cycle definitions across skills.

4. **Redaction input scan.** Scan all pasted/loaded inputs for banned patterns per `redaction-rules.md`: raw names, raw salary figures, raw headcounts, personal contact info. **On detection: refuse to proceed**, surface warning, instruct re-paste with redaction. Hard rule.

5. **Cycle awareness load.** If `cycle.stages` is non-empty, compute `current_stage` and `current_week_offset` from `anchor_event` + today's date. Cache for `delivery_target` metadata stamping in `/generate` (per `cycle-awareness.md`). Note: cycle data is metadata-only in this skill — no gating.

6. **Surface state to user.** One-line summary: which engagement, which audiences enabled, current cycle stage, last cycle trained.

Phase 0 outputs no artifact. It's a readiness gate — every subsequent phase depends on it passing.

---

## Core principles

### Artifact philosophy

Every mode produces a durable consumption artifact. Markdown for working documents; PPTX for delivered training material. Council always produces `council-state.yaml`. Only `/help` is chat-only.

### Redaction discipline

Hard rule. No raw names, no raw salary figures, no raw headcounts, no personal contact info anywhere on disk. Required transformations: salary → band/percentile, headcount → size_band, names → role + function, company name → kept private (replaced with `<COMPANY>` only when artifact tagged `audience: external`). Pre-write scan repeats at every artifact write. Does NOT relax under user pressure. Full rules in `redaction-rules.md`.

### Differentiated depth

The defining twist of this skill. On the same fact (`msg-XXX` in message-map.yaml), HRBP depth ≥ manager depth ≥ employee depth (when all three are non-null). Execs see different cuts (tradeoffs / budget / governance) — depth-4 framing, not deeper-of-the-same. Schema validation enforces this at `/ingest` Workshop synthesis. `/generate` refuses to render an audience that would violate the constraint. Full rules in `audience-depth-rules.md`.

### Conversational interview discipline

`/ingest` and `/generate` audience-design interviews run as single continuous conversations. The skill interviews the operator directly: one question at a time, using pros/cons option tables for structured choices and Mom Test follow-ups for narrative answers. No separate Prep / Whisper / Workshop modes — the arc runs from scripted opening through sub-phases to reflect-and-verify and scripted close without mode transitions. Pattern-trigger table in `meta-protocol.md` governs what the skill asks next based on the operator's answer. Inherited from `meta-protocol.md` (mirrored from comp-team-transformer).

### Delivery-target metadata, no cycle gating

Every rendered deck carries `delivery_target` metadata on the cover slide and in deck frontmatter, computed from `cycle.current_stage` + operator-supplied `delivery_target_week_offset`. **No gating** — training is often intentionally delivered in live/prep windows by design (cascade in week 0, exec ratification in prep, HRBP cycle-mechanics training in prep). Soft warning fires only if `delivery_target` is in the past. This differs deliberately from comp-team-transformer's `/transform` and `/roadmap` cycle-gating (which refuse rollouts into live/prep) — process changes during a live cycle break workflow; training delivered during a live cycle is often the whole point. Full rule in `cycle-awareness.md`.

### Council single-context

Personas are sequential voice blocks within one response, not parallel subagent dispatch. Never draft the synthesis block until every persona block is complete. Auto-fires on `/generate` per-audience message-map slice locks. `/cascade` does NOT auto-fire (mechanical derivation, no contested decisions). No weighted scoring — categorical depth votes only. Full rules in `council-mode.md`.

### Mirror discipline

Six reference files are mirror copies (not symlinks): `meta-protocol.md` (canonical at comp-team-transformer), `persistence-and-ledger.md`, `production-and-qa.md`, `template-master.md`, `brand-kit-protocol.md`, `tools-available.md` (canonical at compensation-advisor). This skill never edits them — coordinate with the canonical skill for any change, then re-copy here. The mirror header at the top of each file names the canonical source.

### Pedagogical posture

v1 default: **broadcast-with-checkpoints**. Facilitator-led explanation with periodic comprehension checks (poll / quiz / scenario card / retrieval prompt) every 3-5 content slides. Suits 200+ rooms and async/recorded delivery. Knowles 80/20 active-learning posture is deferred to v2 (config-toggle per audience). Higher facilitation overhead than broadcast-with-checkpoints; v1 deliberately doesn't impose that load on org-wide training.

---

## v1/v2 boundary

v1 ships:
- 5 production modes (`/init`, `/brand`, `/ingest`, `/generate`, `/cascade`) + 4 utility modes (`/council`, `/checkpoint`, `/resume`, `/help`)
- 4 audiences fixed (employees, managers, HRBPs, execs) with depth-layer differentiation
- broadcast-with-checkpoints posture only
- 5-persona pack (`comp-training-v1`)
- Loose-coupled source ingestion (transformation-briefs + process docs + prior PPTX)
- Manager cascade derivation
- pptxgenjs render against shared engagement brand kit
- Delivery-target metadata stamping (no gating)

v2 work begins ONLY after v1 produces a real per-audience training bundle on a real cycle (the v1 dogfood must succeed end-to-end).
