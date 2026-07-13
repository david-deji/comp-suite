<!-- Source: telos-machina/.claude/rules/model-registry.md @ commit af3787cb91fa793e6fcacad7fd8a7b438d9b62ee. Ported to comp-suite v2 2026-05-07 with INDEPENDENT pinning header (see below). -->

> **Comp-suite v2 model registry — INDEPENDENT pin**
>
> This file is a copy of TM's model registry, but comp-suite reviews bumps INDEPENDENTLY. TM bumps quarterly on bake-offs; comp-suite reviews the same cadence with a one-week lag to avoid silent staleness drift.
>
> Initial values (2026-05-07):
> - opus → `claude-opus-4-6`
> - sonnet → `claude-sonnet-4-6`
> - haiku → `claude-haiku-4-5-20251001`
>
> **Bump procedure**: David reviews this registry quarterly and validates against representative comp-suite tasks (one council deliberation + one mode dispatch per series) before bumping.
>
> --- TM source content below ---

# Model Registry — Latest Validated Version per Claude Series

> **Single source of truth.** All other rules and skill SKILL.md *body text* reference Claude models by *series name only* (`latest opus`, `latest sonnet`, `latest haiku`) — never by pinned version number. This file is the only place that maps series → version.
>
> **YAML frontmatter exception.** The harness parses SKILL.md frontmatter `model:` as a literal model identifier and only accepts harness-native values: `sonnet`, `opus`, `haiku`, `inherit`, or specific model IDs (`claude-sonnet-4-6`, `claude-opus-4-6`). Writing `model: latest sonnet` in frontmatter produces an invalid identifier when the parent session has a context-window flag (e.g. `[1m]`) — the harness concatenates and tries to launch `latest sonnet[1m]`, which does not exist. Use the bare series alias (`sonnet`/`opus`/`haiku`) in `model:` frontmatter; reserve `latest <series>` for body text and rule prose.
>
> **Bump procedure.** A model gets promoted to "latest validated" only after a real-work bake-off win on a comp-suite-internal bake-off bench. Bumping the table below is the gate; never edit a SKILL.md or rule file to pin a new version directly.
>
> **Owner:** David (comp-suite is a solo-operator pet project).

---

## Latest validated per series

| Series | Latest validated | Model ID | Pinned at | Notes |
|---|---|---|---|---|
| opus    | Opus 4.6    | `claude-opus-4-6`    | 2026-05-07 | Default Opus. Pinned independently from TM with one-week lag. Anthropic-scheduled retirement: 2026-06-15 — bake-off vs Opus 4.7 (or successor) required before that date. |
| sonnet  | Sonnet 4.6  | `claude-sonnet-4-6`  | 2026-05-07 | Workhorse default for synthesis and standard mode dispatch. |
| haiku   | Haiku 4.5   | `claude-haiku-4-5-20251001` | 2026-05-07 | Deterministic retrieval, classification, short-answer (extraction/validation tasks). |

> **When a new model in a series ships:** do NOT bump the table immediately. Run the new candidate against representative comp-suite tasks (one council deliberation + one mode dispatch per series) and only update the row above on a clear win. Until then, "latest validated" remains the prior version even if a newer one is technically available.

## Opus 4.7 — named exceptions only

Opus 4.7 (`claude-opus-4-7`) is **NOT** the default Opus. Use 4.7 explicitly (override at dispatch time with `model: "claude-opus-4-7"`) only when one of these named triggers fires:

| Trigger | Comp-suite relevance |
|---|---|
| Vision/multimodal heavy work | If a deck includes image-heavy interpretation (org charts, comp band visuals) |
| Long agentic tool-use loops with high error sensitivity | A council with > 6 thinkers + research dispatch loop |
| Legal contract analysis (BigLaw-shape) | Pay-equity legal review where exact contract clause distinctions matter |

For **everything else**, including default mode dispatches and default councils, `latest opus` resolves to 4.6.

**Migration constraint:** Anthropic deprecates `claude-opus-4-6` on 2026-06-15. Before that date, run a bake-off (one council on a representative comp deliberation + one advisor mode dispatch on a representative engagement) against Opus 4.7 (or whatever successor exists). If the successor wins on cost-per-outcome, bump.

---

## Bump log

| Date | Series | From → To | Bumper | Bake-off reference |
|---|---|---|---|---|
| 2026-05-07 | (initial) | — → Opus 4.6 / Sonnet 4.6 / Haiku 4.5 | David | Initialized at registry creation, ported from TM after TM's 2026-05-02 cost-driven revert |

---

## Why this file exists

Before this registry, model versions would be pinned across many places (mode.yaml `model.default`, routing.yaml `tasks.*`, ad-hoc dispatch templates). Bumping a model would mean grepping the codebase and editing many locations. Now: bump one row.

## Related

- `$ASSET_ROOT/_core/routing.yaml` — per-task model routing; references this file via `latest opus` / `latest sonnet` / `latest haiku` for body text and resolves to specific model IDs at dispatch time
- `$ASSET_ROOT/_core/primitives/mode-dispatcher.md` — the primitive that resolves series alias → model ID at dispatch time using this registry
