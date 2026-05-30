# Transform Protocol

## Mode-keyed step routing

At session start, read `engagement_mode` from team-config or the session-level
declaration.

Look up step routing in `references/engagement-modes.md`:

| Mode | This protocol runs | Pre-condition |
|---|---|---|
| `full-discovery-to-roadmap` | RUN — full 8-step work-decomposer pass + council auto-fire | `diagnosis.md` must exist (C05) |
| `discovery-only` | SKIPPED | — |
| `diagnose-only` | SKIPPED | — |
| `transform-only` | RUN — full 8-step pass + council auto-fire | `diagnosis.md` must exist (C05) |
| `roadmap-refresh` | SKIPPED — existing transformation-briefs are reused | — |
| `council-deliberation` | SKIPPED | — |

Write `engagement_mode` into `transformation-brief.md` frontmatter before the
Band Summary section. If `diagnosis.md` is absent and the mode requires it,
apply C05: refuse, surface the missing path, offer `/diagnose <process-slug>`.

---

The `/transform` track converts a diagnosis into per-candidate buildable specs for AI/automation augmentation. Each candidate gets a categorical band (no weighted scoring in v1, per IE directive D5). Council auto-fires on band locks. Strong Candidates get full work-decomposer specs.

Loaded by SKILL.md when the Intent Router classifies the request as `/transform`. Loads `transform-protocol.md` (this file), `council-mode.md` (auto-fire), `persona-library.md`, `production-and-qa.md`, `template-master.md`, `brand-kit-protocol.md`. Loads `template_assets/transform_spec_template.md` as the output scaffold.

Pattern adapted from the open-source `merllinsbeard-work-decomposer` (Input + Context + Process + Output 4-tuple decomposition; agent architecture taxonomy: simple / orchestrated / complex).

---

## Pre-flight

`/transform <process-slug>` requires a `diagnosis.md` for that process. If `processes/<slug>/<process-slug>/diagnosis.md` does not exist, surface:

> "No diagnosis for `<process-slug>`. Run `/diagnose <process-slug>` first."

and exit. Do not synthesize a transformation brief without a diagnosis input.

---

## The 8 steps

### Step 1 — Load diagnosis.md

Read the full diagnosis. Extract:
- Quick Wins (already P0 — link to them; do not duplicate as `/transform` candidates)
- Leverage points tagged `tools/automation` or `information flows`
- Loops with feedback dynamics that automation could break
- Waste ledger entries flagged `manual-when-automatable` or `over-processing`

These are the candidate-generation source.

### Step 2 — Candidate enumeration

For each candidate (one per leverage point worth specifying), capture the **work-decomposer 4-tuple**:

- **Input** — what data/signal triggers the work?
- **Context** — what does the work need to know? (policy, prior decisions, role context, audience)
- **Process** — what does the work do? (transform, classify, route, decide, generate)
- **Output** — what does the work produce? (artifact, decision, signal, escalation)

Each tuple is a one-paragraph sketch, not a full spec — the spec comes in step 6 for Strong Candidates only.

Naming: each candidate gets a kebab-case slug (e.g., `auto-roster-reconciliation`, `survey-export-format-adapter`). Slugs appear in the brief, the council state, and (eventually) the build issue.

### Step 3 — Categorical band assignment

Each candidate gets exactly one band:

| Band | When | What `/transform` produces |
|------|------|----------------------------|
| **Quick Win** | Already in diagnosis Quick Wins (P0). | One-line link to diagnosis Quick Win — no separate spec |
| **Strong Candidate** | Clear ROI, integration path known, fits in next slack window per `cycle-discovery-and-gating.md` | Full work-decomposer spec (step 6) |
| **Needs Groundwork** | Promising but blocked by data quality, tooling gap, or change-readiness deficit | Dependency note: what blocks it, who owns the unblocking, what would move it to Strong Candidate |
| **Not Ready** | Speculative, integration cost unclear, or against current cycle gating with no near-term slack window | One-liner: why parked, condition that would un-park it |

**Heuristics for band assignment** (orchestrator-side, before council):

- Quick Win: already covered in diagnosis Quick Wins.
- Strong Candidate: candidate's 4-tuple has all four fields populated, the integration path is named (which tool, which API or interface), and the next 2 quarters contain a slack window per the discovered cycle.
- Needs Groundwork: 4-tuple has at least one "(unknown)" field, OR a dependency on data quality / tooling / change readiness is named, OR the integration path is hand-waved.
- Not Ready: speculative ("could we use AI for X?") with no concrete path, OR against cycle gating with no slack window in next 2 quarters.

The orchestrator's pre-council band is a starting point. Council may re-band.

### Step 4 — Council auto-fire

Required. Per `council-mode.md` § Auto-fire matrix.

Fire trigger: pre-council band assignments are complete. Fire prompt:

> "Council auto-fire: review band assignments for `<process-slug>` transformation candidates. 5 personas (HRBP, comp-manager, comp-analyst-operator, hris-tooling, change-management). Per-candidate vote table per persona. Synthesis follows."

Council output: `council-states/<slug>/<date>-<process-slug>-transform.yaml` per the schema in `council-mode.md`.

Each persona votes one band per candidate. Synthesis surfaces:

- **Consensus bands** (≥3 personas aligned) — adopt unless user overrides.
- **Split bands** — surface tension; user picks.
- **Dissents** — preserved verbatim in council-state.

### Step 5 — User approval of band assignments

Surface the council synthesis with per-candidate consensus / split status. Use AskUserQuestion to walk through any split bands one at a time.

User may override any band — bundled or council-recommended. Override reason captured in `council-state.user_decision.decided_band[].override_reason`.

After user closes review, locked band assignments feed into step 6.

### Step 6 — Buildable spec — Strong Candidates only

For each Strong Candidate, produce a full spec per the `transform_spec_template.md` schema:

```markdown
### <Candidate name>

#### Work components (work-decomposer 4-tuple)
- Input: <full description>
- Context: <full description>
- Process: <full description>
- Output: <full description>

#### Architecture
- Type: simple | orchestrated | complex
- Diagram: (mermaid)

#### Agent roles
For each role:
- Role name:
- Input:
- Task:
- Output:
- Context/Constraints:
- Prompt template:

#### Quality gates
- Self-critique:
- Validation checks:
- Human review points:

#### Cycle-fit
- Earliest viable rollout: <Qx YYYY> (slack window in <stage>)

#### Test scenario
<one full end-to-end test scenario the user could run on day 1>
```

**Architecture taxonomy** (from work-decomposer):

- **Simple** — one agent, one prompt, one input → one output. (e.g., reformat survey CSV into model-input columns.)
- **Orchestrated** — one orchestrator + N specialist agents in fixed sequence. (e.g., agent A pulls market data, agent B aligns to internal scale, agent C drafts the comms paragraph.)
- **Complex** — orchestrator + dynamic dispatch + memory across runs. (e.g., agentic benchmarking pipeline that learns from prior cycles.)

**Default to simple.** Most comp-team automation is simple. Escalate only when the 4-tuple genuinely requires orchestration.

### Step 7 — Cycle-fit annotation

For each Strong Candidate spec, compute earliest viable rollout window per `cycle-discovery-and-gating.md`:

1. Walk forward from `team-config.cycle.current_week_offset` through cycle stages.
2. Find the next `slack` stage.
3. Compute the calendar quarter that stage starts in.
4. Annotate: `Earliest viable rollout: <Qx YYYY> (slack window in <stage name>)`.

If no slack window exists in next 2 quarters, surface warning to user and offer:
- Re-band as Needs Groundwork (adjust ETA outside the cycle gating constraint), or
- Override gating with explicit reason (captured in roadmap exceptions).

### Step 8 — Client-language filter (per IE directive D6)

The transformation-brief.md uses **narrative language with $/hour figures**. Internal scoring artifacts (council vote tables, dimension weights) do NOT appear in any artifact destined for an external audience.

Audience tag in frontmatter determines render branching:

- `audience: comp-team-internal` — full brief, council vote tables visible, dissents preserved
- `audience: vp-people` — narrative summary, council split surfaced as "the team weighed two paths", no vote tables, dissents redacted to "alternative views considered"
- `audience: external` — narrative only, no council references at all, redaction pass strips all internal terminology

Redaction pass per `redaction-rules.md` runs before every write — banned patterns trigger hard-refuse.

---

## Output

`processes/<slug>/<process-slug>/transformation-brief.md` — markdown working artifact (schema in `transform_spec_template.md`).

`processes/<slug>/<process-slug>/pptx/transformation-brief-<YYYY-MM-DD>.pptx` — required executive deck. Three production checks before write (per `production-and-qa.md`): brand kit applied, redaction pass complete, audience tag present in frontmatter.

`council-states/<slug>/<date>-<process-slug>-transform.yaml` — council state YAML capturing per-persona votes, synthesis, and user decisions.

---

## Edge cases

- **No Strong Candidates** — every candidate banded as Needs Groundwork or Not Ready. Surface to user: "No Strong Candidates for `<process-slug>` this cycle. The brief still ships with the band table and dependency notes — the path forward is to unblock Needs Groundwork items. Continue?"
- **All candidates Quick Wins** — surface: "All candidates are already Quick Wins from `/diagnose`. No `/transform` brief needed — the diagnosis already covers them. Skip and run `/roadmap` directly?"
- **Council unanimity on Not Ready for everything** — surface: "Council unanimous on Not Ready across all candidates. The transformation isn't ripe. The brief documents why and what would change the status. Generate it for the record?"
- **User overrides every council band** — fine, captured. But surface: "You overrode 4 of 5 council bands. That's a strong signal the council pool isn't covering your decision dimensions — consider registering a custom persona for next time."
