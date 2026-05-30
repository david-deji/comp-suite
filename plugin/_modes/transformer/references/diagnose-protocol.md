# Diagnose Protocol

## Mode-keyed step routing

At session start, read `engagement_mode` from team-config or the session-level
declaration.

Look up step routing in `references/engagement-modes.md`:

| Mode | This protocol runs | Pre-condition |
|---|---|---|
| `full-discovery-to-roadmap` | RUN — 9-step systems-thinking pass | `current-state.md` must exist (C04) |
| `discovery-only` | SKIPPED | — |
| `diagnose-only` | RUN — 9-step pass; `diagnosis_pending: false` in output | `current-state.md` must exist (C04) |
| `transform-only` | SKIPPED | — |
| `roadmap-refresh` | SKIPPED | — |
| `council-deliberation` | SKIPPED | — |

Write `engagement_mode` into `diagnosis.md` frontmatter before the first content
section. If `current-state.md` is absent and the mode requires it, apply C04:
refuse, surface the missing path, offer `/discover <process-slug>`.

---

The `/diagnose` track runs a 9-step systems-thinking pass over a discovered process and produces a `diagnosis.md` artifact with Quick Wins surfaced first. Adapted from the open-source `liqiongyu-systems-thinking` workflow + `openclaw-structure-thinking` MECE issue tree + the IE research Quick-Wins-P0 directive (D8).

Loaded by SKILL.md when the Intent Router classifies the request as `/diagnose`. Loads `diagnose-protocol.md` (this file) + `template_assets/diagnosis_template.md` as the output scaffold. PPTX path also loads `production-and-qa.md`, `template-master.md`, `brand-kit-protocol.md`.

**Council auto-fire on `/diagnose`: NO** (per VISION §12). Diagnosis lock is the user's call after reviewing the systems map and Quick Wins.

---

## Pre-flight

`/diagnose <process-slug>` requires a `current-state.md` for that process. If `processes/<slug>/<process-slug>/current-state.md` does not exist, surface:

> "No current-state for `<process-slug>`. Run `/discover <process-slug>` first."

and exit. Do not synthesize a diagnosis from a missing input.

---

## The 9 steps

Run in order. Each step writes a section of `diagnosis.md`. Quick Wins (step 8) is extracted last but rendered FIRST in the artifact (per IE D8 — first thing a reader sees).

### Step 1 — Read current-state.md

Canonical input. Read every section:
- Process Identity (frequency, trigger, completion signal, end-to-end duration)
- Actors & Roles (single-actor or multi-actor)
- Steps (with inputs, outputs, owner role, tools, time)
- Handoffs (contracts, formats, failure modes)
- Tools & Systems (integration types, bottleneck flags)
- Pain Points (raw verbatim)
- Cycle Anchoring (which stage this process runs in)
- Coverage Gaps (sub-phases that didn't get full coverage in `/discover`)

If any section is empty or thin, surface to user before proceeding: "current-state.md has limited data for `<section>`. Diagnose anyway, or run a follow-up `/discover` first?"

### Step 2 — Define system boundary

Useful, not complete. Output to `diagnosis.md § 1. Context + System Boundary`.

- **Goal** — what the process is supposed to produce (e.g., "deliver an approved annual wage scale by effective date").
- **In-scope** — actors, steps, tools that the diagnosis treats as variable.
- **Non-scope** — explicitly excluded (e.g., "executive comp design — separate process").
- **Time horizon** — 1 cycle / 2 cycles / continuous.
- **Outcome metrics** — 1-3 (e.g., cycle-time end-to-end, error rate post-payroll, employee escalation count).
- **Leading indicators** — 3-7 (e.g., handoff slip count, rework count per cycle, time-from-data-pull-to-modeling-start).

### Step 3 — Actors & incentives map

Comp-flavored. Use the Persona Library (`persona-library.md`) as a reference for actor archetypes, but do not run council here — council is invoked at `/transform`, not `/diagnose`.

For each actor:
- **Role** (e.g., Comp Analyst, HRBP, Comp Manager, HRIS Owner)
- **Function in process**
- **Incentive** (what they optimize for)
- **Constraint** (what they can't do — budget, headcount, regulatory, vendor)

For solo workflows, collapse to `[operator + interfaces]`. The user is the operator; everyone else is an interface (vendor, regulator, internal partner).

### Step 4 — System map

10-20 high-signal causal links. Use concrete, observable variables only — no abstractions ("quality", "alignment").

**Comp-domain variables that work:**
- cycle-time (end-to-end and per-stage)
- error rate (post-hoc catches)
- rework count per cycle
- handoff count
- handoff slip rate
- time-to-decision (from data ready to manager approval)
- employee escalation count (post-cycle)
- manual-step count
- single-point-of-failure count

**Format:** "A increases B" or "A decreases B". Mark time delays where they matter (e.g., "manual rework increases cycle-time, with 2-week delay before downstream notices").

If a link feels load-bearing but you can't define how to observe it, surface: "Hypothesis: `<A>` affects `<B>` — no observable. Skip from system map, or accept as testable hypothesis?"

### Step 5 — Feedback loops (R/B)

Extract 2-6 loops. Each loop gets a one-line **"so what"** narrative — what behavior or pattern does it create over time?

Comp-domain loops to look for:

| Loop | Type | "So what" |
|------|------|-----------|
| Manual rework absorbs hours → less time for prevention → more rework next cycle | R (reinforcing) | Firefighting starves prevention. |
| Tight cycle deadline → less benchmarking depth → less defensible scale → more leadership pushback → more re-runs | R | Compressed timelines compound into more total time spent. |
| Handoff slip → rework → tighter window for next handoff → more slips | R | Slip cascades. |
| Excel template error → catch in QA → adopt new template → next cycle errors caught earlier | B (balancing) | QA discipline stabilizes template quality, but slowly. |
| Goodhart on competitiveness metric → optimize the metric → underlying competitiveness drifts | R, harmful | Metric becomes target; target stops measuring what it was supposed to. |

Each loop must include a "so what" — without it, the loop is decorative.

### Step 6 — Waste ledger

Process-optimization frame. Five waste categories:

| Category | What to look for | Comp examples |
|----------|------------------|---------------|
| **Waiting** | Idle time between steps | Waiting on market data delivery, waiting on VP approval signature, waiting on payroll confirmation |
| **Rework** | Re-doing a step | Re-modeling scenarios after late VP feedback, re-running benchmarks after roster correction, re-formatting deck for new audience |
| **Handoffs** | Cross-person/team transfers | Analyst → manager review, manager → VP approval, comp → payroll, comp → comms |
| **Over-processing** | More work than needed for the audience | 50-slide deck for 5-min board readout, scenario modeling beyond what VP will consider |
| **Manual when automatable** | Steps a script could do | Excel re-formatting, copy-paste between systems, manual roster reconciliation |

Tag each waste entry with frequency × severity. Frequency: per-cycle / weekly / ad-hoc. Severity: hours-cost-per-occurrence (banded: <1h / 1-5h / 5-20h / >20h).

### Step 7 — Leverage points

Categorized intervention candidates. Six categories (per `liqiongyu-systems-thinking`):

- **Incentives** — what gets rewarded/punished. (e.g., "VP rewards on-time scale, not accuracy → analyst over-engineers timeline buffer.")
- **Information flows** — who sees what, when. (e.g., "Roster updates not pushed to comp until week-of-modeling — 2-week delay.")
- **Rules / policies** — definitions, SLAs, decision rights. (e.g., "VP approval window is 5 days, but no rule on what 'approval' means — catches ambiguity in scope.")
- **Buffers / capacity** — staffing, WIP limits, throttles. (e.g., "Comp team of 3 doing 5-team scope.")
- **Tools / automation** — eliminate recurring manual work. (e.g., "Replace Excel re-format with one Power Query refresh.")
- **Interfaces** — contracts between teams, APIs, handoffs. (e.g., "Define a roster-export contract with HRIS team.")

3-7 leverage points per process. Each entry includes:
- Category
- Description
- Owner (which role would unblock it)
- Sequencing tag: now / next / later

### Step 8 — Quick Wins extraction (P0 — REQUIRED)

Per IE directive D8: 2-3 things the user can do **this week**, without `/transform`, without further engineering work, without leadership approval. **Required, not optional.**

What qualifies:

- Kill a redundant approval ("VP approval is rubber-stamped — propose removing")
- Replace an Excel template with a checked-in version ("Template lives in 4 personal OneDrive copies — consolidate")
- Automate a one-line script ("Roster reconciliation is a 30-line VLOOKUP — convert to Power Query, runs in 30 seconds")
- Document a tribal step ("Annual carryover logic lives in the analyst's head — write it down on a wiki page")
- Tighten one handoff contract ("Compensation → payroll handoff drops 1-2 fields per cycle — document the schema")

**What does NOT qualify:**

- Anything requiring leadership approval beyond a 5-min "go ahead"
- Anything requiring vendor procurement
- Anything requiring `/transform` work (build a new agent, integrate two systems)
- Anything that takes more than ~5 hours to implement

Render as the FIRST content section of `diagnosis.md` (after frontmatter):

```markdown
## Quick Wins (P0 — do these this week)
1. <action> — owner: <role>, effort: <hours>, expected outcome: <metric>
2. <action> — owner: <role>, effort: <hours>, expected outcome: <metric>
3. <action> — owner: <role>, effort: <hours>, expected outcome: <metric>
```

Each Quick Win must have all four fields populated. Missing any field disqualifies it from Quick Wins — kick to leverage points instead.

If you can't find at least 2 Quick Wins, surface to user: "No Quick Wins in this process — that's unusual. Want to extend the diagnosis with a deeper look at handoffs or tools, or accept the absence?"

### Step 9 — Quality gate

Before writing the artifact, run the checklist:

- [ ] Boundary statement is clear (Goal + In/Non-scope + horizon + metrics)
- [ ] Actors are realistic (no "the team" — specific roles)
- [ ] System map has 10-20 concrete, observable links
- [ ] At least 2 feedback loops with "so what" narratives
- [ ] Waste ledger covers at least 3 of the 5 categories
- [ ] Leverage points are categorized (no uncategorized entries)
- [ ] Quick Wins ≥2, all fields populated
- [ ] Risks / Open Questions / Next Steps section drafted

If any checklist item fails, fix before writing. Hard quality gate.

---

## Output

`processes/<slug>/<process-slug>/diagnosis.md` (markdown, schema in `diagnosis_template.md`).

Optional `processes/<slug>/<process-slug>/pptx/diagnosis-<YYYY-MM-DD>.pptx` if user requests. PPTX requires reading `production-and-qa.md` (three production checks before write: brand kit applied, redaction pass complete, audience tag present in frontmatter), `template-master.md`, `brand-kit-protocol.md`. Audience tag for `/diagnose` PPTX defaults to `comp-team-internal`; surface a confirmation if user wants `vp-people` or `external`.

---

## Council on diagnosis lock — explicit NO

`/diagnose` does NOT auto-fire `/council`. Diagnosis lock is the user's call after reviewing the systems map and Quick Wins. If the user wants council deliberation on a contested loop or leverage point interpretation, they explicitly invoke `/council`.

This is deliberate (per VISION §12). Council fires automatically on `/transform` band locks and `/roadmap` sequence locks because those are commitment points. Diagnosis is interpretation; user owns it.
