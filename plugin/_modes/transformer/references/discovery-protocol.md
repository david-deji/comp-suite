# Discovery Protocol

## Mode-keyed step routing

At session start, read `engagement_mode` from team-config (or the session-level
declaration if team-config is not yet initialized).

Look up step routing in `references/engagement-modes.md`:

| Mode | This protocol runs | Frontmatter flag |
|---|---|---|
| `full-discovery-to-roadmap` | RUN — full interview + current-state synthesis | `engagement_mode: full-discovery-to-roadmap` |
| `discovery-only` | RUN — full interview + current-state synthesis; set `diagnosis_pending: true` | `engagement_mode: discovery-only` |
| `diagnose-only` | SKIPPED — exit with "current-state required; run /discover first" if no current-state exists | — |
| `transform-only` | SKIPPED | — |
| `roadmap-refresh` | SKIPPED | — |
| `council-deliberation` | SKIPPED | — |

Write `engagement_mode` and `diagnosis_pending` into `current-state.md` frontmatter
before the first content section. `discovery-only` emits `diagnosis_pending: true`;
`full-discovery-to-roadmap` emits `diagnosis_pending: false`.

---

The `/discover` track maps a comp process: identity, steps, handoffs, tools, pain points, and (when needed) the cycle anchor. Output is a structured `current-state.md` per process.

Loaded by SKILL.md when the Intent Router classifies the request as `/discover`. Loads `meta-protocol.md` first (universal techniques), then this file (comp-domain flow), plus `cycle-discovery-and-gating.md` if `team-config.cycle.stages == []`, plus `redaction-rules.md` for the input scan.

Question banks live in `template_assets/discovery_interview_block.json` — the canonical source for scripted_opening, intake, cycle_mapping, process_walkthrough, handoffs, tools, pain_points, and scripted_close blocks.

---

## Conversational interview

`/discover` is a single continuous interview in one Claude.ai conversation. The skill is the interviewer; the operator is both the person running the session and the SME being interviewed. There is no separate Prep briefing, no live-call copilot mode, no Workshop phase — one arc, start to finish.

The skill drives with the question banks from `template_assets/discovery_interview_block.json`, using:

- **Pros/cons option tables** (per `meta-protocol.md` § "The default question format") for structured-choice questions — SIPOC framing, cycle-mapping, handoff patterns, tool integration types, pain-point quantification.
- **Mom Test behavioral questions** for narrative answers — process steps, owner roles, failure modes.
- **One question per turn** — never stacks a table with a follow-up open question in the same response.

---

### Sub-phase sequence

Auto-checkpoint at each sub-phase transition (write to session-state file silently). The arc runs ~45-75 min depending on process complexity.

#### 1. scripted_opening (0-3 min)

Run the scripted_opening block from `discovery_interview_block.json`. Scope the session, set expectations, name the output artifact.

#### 2. Intake — SIPOC framing (3-8 min)

Each of the five SIPOC dimensions is a candidate for a pros/cons table. Present the table when common patterns exist; ask conversationally when the answer is free-form.

Example — Suppliers question:

```
**Q1. Who provides the inputs to this process?**

| Option | Pros | Cons |
|---|---|---|
| **A. Internal only (HRIS + payroll)** | Tight control; no vendor mgmt overhead | Limited external market view |
| **B. Internal + survey vendor (Mercer / Willis / etc.)** | Market benchmarks; sector comparables | Vendor cycle dependency; annual cost |
| **C. Internal + survey + regulators (CCQ, CBA, etc.)** | Full compliance footprint | Regulatory data lag; rigid format |
| **D. Internal + survey + business-unit HRBPs** | Distributed sourcing; faster field updates | Coordination overhead; version drift |
| **E. Other** | (describe in your own words) | |

Pick a letter. If "Other" or you want to combine, describe.
```

Example — Outputs question (free-form where outputs vary widely):

> "What comes out of this process — what artifact or data does it produce for downstream consumers?"

#### 3. Cycle-mapping (conditional, 8-15 min)

Only runs when `team-config.cycle.stages == []`. Inserts between Intake and Process Walkthrough. Load `cycle-discovery-and-gating.md` for the 6-prompt sequence. Present each prompt conversationally (not as a table — each answer depends on the prior one).

When `cycle.stages` is already populated, skip this block entirely.

#### 4. Process walkthrough (15-50 min)

Step-by-step narration. Each step captured as: inputs / outputs / owner role / tools / time estimate.

For structured patterns (e.g., how data flows between steps), use a pros/cons table. For narrative steps ("walk me through what happens after you get the market data file"), use the Mom Test.

Example — data handoff pattern question:

```
**How does market data reach the scale model?**

| Option | Pros | Cons |
|---|---|---|
| **A. Direct export match (columns align)** | Zero manual work; fully repeatable | Requires vendor export configured correctly |
| **B. Manual column mapping per cycle** | Flexible to vendor changes | Hours of manual work; error-prone each cycle |
| **C. Intermediate cleaning script** | Repeatable after setup; faster than manual | Script maintenance; breaks on format changes |
| **D. Analyst re-enters key fields manually** | No tooling dependency | Slowest; highest error rate; knowledge bottleneck |
| **E. Other** | (describe) | |

Pick a letter.
```

Apply pattern triggers from `meta-protocol.md` § "Pattern-trigger table" as they appear in the operator's answers. Fire one trigger per turn.

Pacing checkpoints (every 3-4 questions):

- "Want me to summarize what we have so far?"
- "Anything we should slow down on?"
- "Still on the part you wanted to focus on?"

#### 5. Handoffs (handoffs questions)

List every cross-person/team boundary. Capture: who hands off to whom, what format, what the failure modes are.

Example — handoff format question:

```
**How does the handoff from payroll to the comp analyst typically happen?**

| Option | Pros | Cons |
|---|---|---|
| **A. Automated HRIS extract (scheduled)** | No manual step; consistent timing | Requires HRIS configuration; field mapping fixed |
| **B. Payroll analyst emails a file** | Flexible; no config needed | Timing varies; format can drift; email dependency |
| **C. Shared folder (both parties update)** | No email chain; both sides can see | Version conflict risk; no clear "ready" signal |
| **D. Verbal / ad-hoc** | Fast for small teams | Not repeatable; knowledge stays with individuals |
| **E. Other** | (describe) | |

Pick a letter.
```

#### 6. Tools (tools questions)

List every system in the process. For each tool: integration type (manual export, API, shared folder, direct read), bottleneck flag.

Example — tool integration question:

```
**How does the comp model connect to the HRIS for employee data?**

| Option | Pros | Cons |
|---|---|---|
| **A. Live API / direct sync** | Always current; no manual pull | Requires integration build; API change risk |
| **B. Scheduled automated export** | Predictable; low-touch | Lag between HRIS state and model |
| **C. Manual export on demand** | No config needed; analyst-controlled | Hours of manual pull per cycle |
| **D. Copy-paste / re-entry** | No tooling dependency | Highest error rate; slowest |
| **E. Other** | (describe) | |

Pick a letter.
```

#### 7. Pain points (50-60 min)

Drive toward measurable units — hours/cycle, $/cycle, error rate, days of delay. Use SPIN cost-of-inaction: "What happens if this stays as-is another year?"

For quantification, use a banded pros/cons table when the operator is unsure of the exact number:

```
**How many hours does this absorb per cycle, across the team?**

| Option | Signal |
|---|---|
| **A. < 5 hours** | Low priority for transformation; cheap to live with |
| **B. 5-50 hours** | Real but bounded; quick-win territory |
| **C. 50-500 hours** | Strong transformation candidate; payback is visible |
| **D. 500+ hours** | Top priority; likely hides 2-3 sub-processes |
| **E. I know the number** | (tell me) |

Pick a letter.
```

If the operator picks E or gives a direct number, use it verbatim.

#### 8. Reflect-and-verify + gap check (60-65 min)

Paraphrase back using the operator's own words. Per `meta-protocol.md` § "Reflect-and-verify".

Before scripted_close, run a gap check:

> "We didn't get into `<sub-phase>` — is that intentional or worth a follow-up?"

Capture deferred sub-phases in `current-state.md § Coverage Gaps`.

#### 9. Synthesis

After the operator confirms the reflect-and-verify is accurate:

1. **Capture summary.** Present running notes for review:

   ```
   Captured during this session:
   - Process steps: <N steps captured>
   - Cycle stages: <N stages / "complete" / "not yet covered">
   - Tools mentioned: <list>
   - Handoffs: <N identified>
   - Pain points (raw): <verbatim list with topic tags>
   - Gaps flagged: <sub-phases with thin or missing data>
   ```

2. **Review gate.** "Here's what I captured. Anything to correct or add before I write the current-state map?" Wait for confirmation.

3. **Produce `current-state.md`** per the §9 schema. Run redaction pass per `redaction-rules.md`.

4. **Cycle update** (if cycle-mapping ran). Write `team-config.cycle.*` to the team-config YAML. Surface: "Cycle stages added to `team-configs/<slug>.yaml` — `<N>` stages, anchor `<event>`."

5. **Flag thin sections.** "The handoffs section has 1 entry — is that complete or worth a follow-up?"

Output: `discovery/<slug>/YYYY-MM-DD-<process-slug>-self.md` (raw capture, append-only) + `processes/<slug>/<process-slug>/current-state.md` (synthesized).

---

## Session-state-as-running-notes (per IE directive D9)

Three sections only — no 12-section YAML schema. Lives in working-state file, overwritten on each checkpoint.

```markdown
# Session State: <process-slug>
# Last checkpoint: <ISO timestamp>

## Current position
- Sub-phase: scripted_opening | intake | cycle-mapping | process-walkthrough | handoffs | tools | pain-points | reflect-and-verify | synthesis
- Active flow: <process slug>

## Key data points collected
- Process steps: [N captured]
- Cycle stages: [N captured / "complete" / "not yet covered"]
- Tools mentioned: [list]
- Handoffs identified: [N]
- Verbatim quotes (high-value): [list with topic tags]

## Questions remaining
- [ ] Cycle-mapping (if cycle.stages == [])
- [ ] Process walkthrough
- [ ] Handoffs
- [ ] Tools
- [ ] Pain points
- [ ] Close (reflect-and-verify + gap check)
```

**Checkpoint triggers:**
- On every sub-phase transition (Intake → Cycle-mapping, etc.)
- At midpoint of any sub-phase running beyond the expected time window

Auto-checkpoint writes are silent — surface only on write failure. User can also invoke `/checkpoint` manually to capture state mid-track.

---

## Output files (every `/discover` run)

- **Raw capture:** `discovery/<slug>/YYYY-MM-DD-<process-slug>-self.md` — append-only record of the session. Contains scripted_opening, full Q&A, scripted_close. Useful for re-discovery and audit trail.
- **Synthesized current-state:** `processes/<slug>/<process-slug>/current-state.md` — structured per the `current-state.md` schema. This is the input to `/diagnose`.
- **Team-config update** (if cycle-mapping ran): `team-configs/<slug>.yaml` — `cycle.*` fields populated.

All writes go through the persistence backend per `persistence-and-ledger.md`. Redaction pass runs before every write — banned patterns trigger hard-refuse.
