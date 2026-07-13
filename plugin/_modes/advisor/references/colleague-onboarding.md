# Compensation Advisor — Skill Overview

This is a personal-project compensation advisor skill built for Canadian comp work — multi-province wage benchmarking, costed scenario modeling, decision-deck production, and strategic deliberation. It assumes Canadian context (provincial minimum wages, CPP/QPP, CNESST, UFCW/TUAC, Loi sur l'équité salariale) but is org-agnostic — configure it for your scope via `/init`.

Loaded by SKILL.md when someone asks "how do I get started" or pastes content suggesting they're new to the skill.

---

## What this skill does, in one paragraph

The skill is a peer compensation consultant in Claude. It runs structured engagements end-to-end: discovery interview, market data pulls (Market MCP for wages — StatCan-published wage tables and live posting rates returned in one bundled call at all five percentiles P10/P25/P50/P75/P90; Indeed MCP secondary for company intel and posting validation; StatCan MCP for econometric context only — CPI, unemployment, never wages), Excel parsing, costed scenario modeling, narrative workshopping, and section-by-section interactive deck production. It also offers four utility commands (`/init`, `/update`, `/intake`, `/quickbench`) and a Council mode for multi-perspective deliberation on strategic comp trade-offs. The skill is cycle-aware (knows where you are in your annual wage review workback — neutral 7-stage default that you override in your config) and scope-aware (one engagement = one budget owner).

---

## First-time setup (15 minutes)

### Step 1: Install the skill

Install the `compensation-advisor.skill` bundle via the Claude.ai skills interface (or in Claude Code via the standard skill installation flow). Once installed, the skill triggers automatically when you ask a compensation question — you don't need to invoke it explicitly.

### Step 2: Run `/init` to build your engagement config

In a new Claude conversation, type `/init`. The skill walks you through 8 sections:

| Section | What it captures | Time |
|---|---|---|
| 0 — Engagement scope | Budget owner, banner/region, in/out scope | 3 min |
| 1 — Cycle | Cycle name, cohort, effective date, current stage, last cycle's outcome, this cycle's goals | 5 min |
| 2 — Org | Company context: banners, union landscape, governance, pay philosophy | 3 min |
| 3 — Audience | Your typical audiences (board comp committee, CHRO, HR ops, etc.) | 5 min |
| 4 — Costing | Roll-up factors, payroll burdens, replacement multipliers per province | 3 min |
| 5 — Benchmark | Default percentiles, peer companies, role aliases, provincial minimum wages | 3 min |
| 6 — Deck | Slide counts by audience, voice, decision-ask pattern | 2 min |
| 7 — Persistence | Automatic via your OAuth identity — nothing to configure (confirm sign-in) | 1 min |

Sections 0 and 1 are pushed hard — they're what makes the skill useful across multiple sessions. Sections 2-7 are skippable. Persistence (Section 7) is now automatic: once you sign in (OAuth), your configs, state, and ledger persist to the `market` MCP backend under your identity for year-over-year continuity — there is no Drive folder to wire and no paste-mode to fall back to.

At the end you get a YAML block. Save it personally — note app, password manager, wherever you keep reference material. Once you're signed in (see `references/persistence-and-ledger.md`), the skill reads your config from the `market` MCP backend at session start instead of asking for a paste.

### Step 3: Use the skill

For your first real engagement, paste your saved config + ask your question:

```
[paste your engagement-config YAML here]

I need to look at pharmacy assistant pay across QC and ON. We're seeing
turnover spike. Can you help me think through whether we should adjust
the scale or look at retention bonuses first?
```

The skill loads your config (Phase 0), then enters Track C (Consulting flow) since this is exploratory. It runs 5-beat discovery, pulls market data, models scenarios, workshops narrative, and produces an interactive deck section-by-section.

---

## What a typical session feels like

A standard end-to-end engagement at the Discovery / Market Analysis stage (week ≈ −10):

**Minute 0-5 — Paste your config and your ask.**
You paste the engagement-config YAML and write something like "We need a market review for the sponsor. Pharmacy assistant turnover is up. I think we're 6-8% behind market in QC and ON. Need scenarios for the next review in 3 weeks." Skill loads config, surfaces context (last cycle, this cycle's goals, envelope ceiling), and classifies as Track C with cycle awareness.

**Minute 5-15 — Phase 1 Discovery (5 beats, compressed).**
Skill walks the 5 beats: trigger, audience, hypothesis, constraints, then synthesizes a 3-5 sentence engagement brief and asks you to confirm. Wait for the brief — don't rush. It's the contract for the rest of the engagement.

**Minute 15-25 — Phase 2 Data Gathering (autonomous).**
Skill pulls from Market MCP, Indeed, StatCan; parses any Excel you uploaded; classifies pay structures; computes derived metrics. You see a validation summary at the end ("14 roles classified, 3 step / 11 merit, multi-province pull complete") but you don't drive this phase. This phase is silent — that's normal.

**Minute 25-35 — Phase 3 Interpretation (conversational).**
Skill leads with last-cycle drift detection (if `cycle.last_cycle` is populated), then 2-3 headline findings, then asks for organizational context. Push back if anything looks off — this is when you correct course cheaply.

**Minute 35-50 — Phase 4 Option Modeling.**
Do-nothing baseline + 2-3 costed scenarios. You see envelope totals, per-province breakdowns, replacement-cost-of-turnover assumptions. Skill respects `this_cycle_goals.envelope_ceiling` from config. You pick a direction (or a blend).

**Minute 50-65 — Phase 5 Narrative Workshop.**
Skill builds the Situation → Tension → Resolution arc, layers audience psychology (drawing on the audience archetype from your config and `judgment-notes.md` if populated), and produces a NARRATIVE FRAME block. You confirm the argument arc.

**Minute 65-95 — Phase 6 Production (interactive).**
This is the longest phase if you're in interactive mode. Skill walks 6 sections; for each, presents two framing options with pros/cons (one recommended), you pick (or describe a third), skill builds, shows preview, moves on. If you trust the skill, switch `deck.production_mode` to `hybrid` in your config — it'll prompt only on Findings, Options, Recommendation; build the rest silently. Cuts this phase to ~15 min.

**Minute 95-105 — Phase 7 QA + delivery.**
8-dimension QA runs autonomously. You see the QA summary, the deck is delivered. If anything's off, route a revision back to the appropriate phase (layout fix → Phase 6; costing change → Phase 4; audience reframe → Phase 5). Engagement state file produced for institutional memory.

**Total: 90-110 minutes for a fresh engagement, 30-50 for a refresh from a prior deck.** First engagement might run longer because you're learning the rhythm; by the third one you're moving fast.

What you don't want to do: bail at Phase 2 because nothing's happening. Or skip the brief confirmation in Phase 1. Or treat the A/B prompts in Phase 6 as ceremony — the framing choices actually matter.

---

## Common workflows

### "I'm at the Discovery stage and need a market review"

Paste config (with `cycle.current_stage: "Discovery"`) and ask. Track C/D depending on how specific your hypothesis is. End-to-end takes 30-60 minutes. **Artifacts:** `.pptx` deck (always) + `engagement-state.yaml` (Phase 7 close) + optional `cost-scenarios.xlsx` / `market-data.csv` per `deck.artifacts`.

### "I'm sending an intake form to the sponsor — who do I trigger?"

`/intake`. Skill generates a fillable PDF with scope-parameterized questions (worry roles, recruiting pain, competitor moves, poaching) tailored to the provinces and banner you specify. One-at-a-time approval on each question variant before the PDF builds. **Artifacts:** `intake-form-{cycle-slug}-{date}.pdf` + `intake-form-meta-{cycle-slug}-{date}.yaml` (variant choices + validation grounding sources).

### "Last year's deck — just refresh the numbers for this year"

Upload the prior `.pptx` and say "just update the numbers." Skill detects R-lite track, refreshes data, rebuilds with same narrative. **Artifacts:** refreshed `.pptx` + `engagement-state.yaml`.

### "I need a quick market check on bakery managers in BC"

`/quickbench bakery managers BC`. ~2 min, single-role market pull, mini-report. No engagement. **Artifacts:** `quickbench-{role-slug}-{province}-{YYYY-MM-DD}.md` (markdown body with YAML frontmatter capturing `tool_calls[]`); optionally mirrored to a local `quickbench-archive/`.

### "Should we move from P50 to P60 on hard-to-fill roles?"

`/council on whether to move from P50 to P60 for hard-to-fill grocery roles`. Skill runs a multi-persona deliberation drawn from the bundled 7-persona pool (`employment-lawyer`, `total-rewards-strategist`, `cfo-finance`, `hr-business-partner`, `dei-pay-equity`, `employee-union`, `ceo-board`) — defaults to 4-6 personas, configurable per engagement. Custom personas registered in your repo's `personas/` folder are additive (see `references/persona-library.md`). **Artifacts:** `council-state-{date}-{slug}.yaml` (always) + `council-memo-{date}-{slug}.md` (when in `memo` mode).

---

## Things to know before you start

**Workforce data — use the CSV templates, never raw HRIS exports.** When the skill needs workforce data for cost modeling, use `template_assets/wage_data_template_step.csv` (for step roles) or `template_assets/wage_data_template_merit.csv` (for salaried merit roles). These contain the minimum columns the skill needs and intentionally exclude every PII field (employee names, IDs, DOBs, addresses, performance comments, salary history). The skill will refuse to proceed if it detects PII columns in your upload — but by then the data is already in the conversation context. The right time to filter is before export, not after upload. Read `template_assets/wage_data_template_README.md` once, then build a saved HRIS query that exports those columns only.

**One engagement = one budget owner.** If you find yourself wanting to cover two budget areas in the same session, the skill will push back. Each budget owner has their own envelope, and bundling creates compromise scenarios neither one wants. The fix is two configs and two sessions.

**Cycle awareness changes skill behavior.** At week −12 the skill emphasizes scope and intake; at week −7 it's the approval pitch; at week ≥ 0 it'll decline new strategy work for that cohort and route you to the next cohort or to payroll execution support. Keep `cycle.current_stage` and `cycle.current_week_offset` updated as you progress (use `/update` between engagements).

**Stage names are configurable.** The skill ships a neutral 7-stage default (Discovery, Market Analysis, Scenario Modeling, Approval, Cascade, Implementation, Live). Override the `cycle.stages` list in your config to use your org's actual stage names + RACI. The skill keys behavior on the canonical neutral names; your overrides drive the labels in the deliverable.

**Deck production is interactive.** Phase 6 walks each of the 6 deck sections individually — for each section, you see two framing options with pros/cons, pick one (or describe a third), and the skill builds that section before moving on. Much cheaper than QA-ing a finished deck. If you want it one-shot, frame your request as Track D ("just build a [X] for the [audience] showing [Y]") and the skill auto-picks the recommended option for each section silently.

**Branding is configurable per engagement.** `deck.brand` defaults to a built-in palette; switch to `neutral` for external-audience decks (acquirers, regulators, arbitrators) via your config or by asking at Phase 5.

**The skill pushes back on data.** If you state something the data contradicts, it presents both interpretations and asks which direction you want to take. It does not silently comply with a narrative the data doesn't support. Treat this as a feature.

**The skill calls out staleness.** Provincial minimum wages, costing parameters, audience archetypes — all have `last_verified` dates and warn when stale. Re-run `/update` between cycles to keep them fresh.

---

## Quick reference card

```
/init        Build engagement config (7 sections, ~25 min one-time)
/update      Refresh existing config (3-10 min between engagements)
/intake      Strategic intake PDF for the sponsor
/quickbench  Single-role market pull, no deck (~2 min)
/council     Multi-perspective deliberation on a strategic decision
/help        Two-tier menu of all commands
```

For substantive engagements, just describe what you need — the skill classifies into Track C (consulting), Track D (direct build), Track R (refresh from prior deck), or Track R-lite (just update numbers) based on your phrasing and any uploaded files.

---

## When the skill won't be helpful

- **You're outside an annual wage cycle and need ad-hoc analysis.** The cycle-stage awareness is built in — if you're between cohorts and need a one-off check, use `/quickbench` or just paste a config without a `cycle` section.
- **You're doing executive comp (LTI design, performance share units, board-pay benchmarking).** The skill handles base salary and total cash but is not built for LTI plan design or executive comp committee work specifically.
- **You need real-time HRIS extraction.** The skill takes Excel/CSV uploads but does not directly query SuccessFactors/SAP. Pull your data first, then upload.

---

## Getting help

- **`/help`** in the skill itself — two-tier menu of all commands.
- **YAML config questions** — see `references/engagement-config-template.md` for the full schema.
- **Persistence & ledger questions** — see `references/persistence-and-ledger.md`.
