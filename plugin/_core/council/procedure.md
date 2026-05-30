<!-- Source: telos-machina/.claude/rules/council-procedure.md @ commit af3787cb91fa793e6fcacad7fd8a7b438d9b62ee. Copied verbatim 2026-05-07. -->
# Council Procedure

Reusable procedure for all council and deliberation patterns. Skills reference this
file instead of inlining dispatch mechanics. The procedure handles the shared 80%;
each skill provides the 20% that varies via parameters.

Full operational reference (dispatch template, perspective pool, gap aggregation, tag propagation): `internal-ops-bureau/knowledge/council-procedure-reference.md`

See also:
- `.claude/agents/thinker.md` — agent definition (gap-first output structure)
- `.claude/rules/council-output-pattern.md` — per-thinker unique files, dual-return
- `internal-ops-bureau/knowledge/worker-comms.md` — 8-section XML template, comms blocks

## Parameters (set by the calling skill)

| Parameter | Description | Examples |
|---|---|---|
| `perspective_pool` | List of {name, persona, focus} | See reference file |
| `perspective_count` | Number or range of thinkers | 3-7, 5, 3-5 |
| `task_framing` | What thinkers are doing | "deliberate on [topic]", "evaluate specs adversarially" |
| `output_structure` | Thinker output sections | Per-decision votes, file:line findings |
| `synthesis_style` | How orchestrator synthesizes | `consensus-tensions` / `vote-count` / `severity-triage` |
| `gap_flavor` | Domain-specific gap question | See reference file |
| `post_council_routing` | What happens after synthesis | `founder-review` / `fix-dispatch` / `verdict` |
| `confidence_tags` | Whether to tag findings | true (default) / false (vote-based) |
| `quality_gate` | Per-skill checklist items | See per-skill definitions |
| `output_dir` | Where files go | Per-skill path pattern |

## Mandatory NBJ Perspective

Every council includes one NBJ thinker (does NOT count against `perspective_count`). NBJ persona, episode selection procedure, and knowledge base layout in the reference file.

Applies to: Deliberation (/research, /specify) — always. Decision (/brand) — always. Review (/build) — only for strategic dimensions.

## Synthesis Styles

- **consensus-tensions** (default — /research, /specify): consensus, tensions, single-source, unverified, unresearched, path forward, unresolved concerns
- **vote-count** (/brand): per-decision vote tallies, DECIDED/SPLIT/OVERRIDE
- **severity-triage** (/build): CRITICAL > HIGH > MEDIUM > LOW, cross-reviewer consistency

The orchestrator synthesizes — NEVER delegate synthesis to another agent.

## Quality Gate

- [ ] Each thinker produced at least one actionable finding
- [ ] Each thinker references specific input sections
- [ ] At least 2/N thinkers produced knowledge gap entries (all-zero = anomalous)
- [ ] Gaps aggregated and presented to founder
- [ ] Synthesis covers all perspectives (none dropped)
- [ ] No placeholder text in assembly file
- [ ] NBJ dispatched with context pack from `research-bureau/knowledge/nate-b-jones/`
- [ ] NBJ grounds claims in named files, not generic commentary

## Council Archetypes

| Archetype | Used by | Synthesis | When to use |
|---|---|---|---|
| **Deliberation** | /research, /specify | consensus-tensions | Open questions, strategy |
| **Decision** | /brand | vote-count | Picking option A vs B vs C |
| **Review** | /build | severity-triage | Adversarial code evaluation |

Review uses `general-purpose` agents, not `thinker`. Gap identification via `Unverified Assumptions` section.
