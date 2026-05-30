---
process_slug: annual-wage-scale-review
team_slug: example-comp-team
date: 2026-04-22
source_current_state: processes/example-comp-team/annual-wage-scale-review/current-state.md
audience: comp-team-internal
---

# Diagnosis: Annual Wage Scale Review

## Quick Wins (P0 — do these this week)

1. **Consolidate the deck template** — owner: Comp Manager, effort: 2h, expected outcome: single source of truth in shared folder, eliminating year-over-year template drift. The four personal OneDrive copies become one canonical version checked into the comp-team shared folder.

2. **Document the carryover logic** — owner: current Comp Analyst, effort: 4h, expected outcome: 1-page wiki entry capturing the historical carryover rules so they no longer rely on archaeological reconstruction from prior decks. Calibration drift shrinks.

3. **Tighten the HRIS roster export contract** — owner: HRIS Owner + Comp Analyst, effort: 3h shared, expected outcome: documented column-name contract for the roster export. HRIS Owner agrees to surface column changes ≥30 days before export. Step 5 reconciliation surprises drop.

---

## 1. Context + System Boundary

**Goal:** Deliver an approved annual wage scale to payroll by August 15 (week -2 from effective date) such that first-cycle paychecks ship on the new scale with zero post-payroll variance.

**In-scope:** Steps 1-13 (kickoff through payroll handoff). Comp team work, HRIS Owner roster export, HRBP cascade prep.

**Non-scope:** Manager 1:1 cascade (step 12 — outside comp scope), executive comp design (separate process), pay equity exercise (separate Quebec-mandated process every 5 years).

**Time horizon:** 1 cycle (this annual review). Roadmap will sequence multi-cycle improvements.

**Outcome metrics:**
- Cycle-time end-to-end: 22 weeks → target 18 weeks (4-week saving primarily from steps 4-5 and step 6 re-runs)
- Post-payroll variance count: ~6 corrections per cycle → target 0
- Number of step-6 scenario re-runs caused by late VP feedback: 4 last cycle → target ≤1

**Leading indicators:**
- Step 5 reconciliation surprises (column mismatches caught) per cycle
- Days lost to step-4 manual VLOOKUP work
- Step-13 payroll-import errors at first attempt
- Step-7 deck template version drift (which OneDrive copy was canonical this cycle)
- Number of cycles in a row that the same Quick Win has gone unfixed

---

## 2. Actors & Incentives Map

| Role | Function in process | Incentive | Constraint |
|------|---------------------|-----------|------------|
| Comp Analyst (Operator) | Does the work — data, modeling, deck, payroll handoff | Cycle ships on time, no post-payroll fires | Single-threaded; absorbs all cycle slips |
| Comp Manager | Budget envelope, VP-facing decisions | Approved scale within budget; defensible to VP | Must defend any over-budget recommendation |
| HRBP | Cascade narrative, manager comms | Smooth cascade; manager confidence | Late in cycle — limited influence on upstream design |
| HRIS Owner | Roster export, payroll spec | System integrity; uptime; minimize ad-hoc requests | Roster changes happen all year; comp team is one of many consumers |
| VP People | Final approval, CFO defense | Defensible scale within budget; minimize political risk | Limited cycle bandwidth — reviews late, requests changes that re-trigger step 6 |

---

## 3. System Map

10 high-signal causal links:

- HRIS roster format drift increases Step 5 reconciliation surprises (delay: caught only at step 5, ~12-14 weeks after format changed)
- Step 5 reconciliation surprises increase Step 6 modeling delay (immediate)
- Late VP feedback at Step 9 increases Step 6 re-runs (no delay; each re-run = 8h)
- Step 6 re-runs increase total cycle hours (~32h per cycle from re-runs alone)
- Manual Power Query usage in Step 4 decreases Step-4 hours by ~50% (immediate)
- Power Query adoption is uneven — only one analyst uses it; cycle bus-factor 1
- Deck template version drift increases Step 7 build hours (~6h per cycle picking the right version)
- Carryover logic tribal-knowledge increases Step 6 modeling errors (intermittent, ~1 catch per 2 cycles)
- Late VP feedback decreases approval-timeline buffer (cumulative — step 9 slips push cascade window into `live` weeks)
- Tight cycle deadline decreases benchmarking depth in Step 3 (analyst skips slow vendors; hidden quality cost)

---

## 4. Feedback Loops (R/B)

### Loop 1 — VP late-feedback compounding (R, harmful)

VP reviews late at step 9 → analyst re-runs step 6 → cycle slips → less time for step 11 cascade prep → HRBP rushes → manager cascade lands shaky → next year VP wants more detail → reviews more thoroughly → reviews even later.

**So what:** Late VP feedback compounds across cycles. The fix is upstream — getting VP into a structured pre-review at step 7 (deck draft) rather than step 9 (formal pitch).

### Loop 2 — Bus-factor on Power Query (R, fragile)

One analyst uses Power Query → step 4 takes 12h instead of 24h → that analyst becomes the cycle bottleneck → no time to teach others → if they're out, cycle slips by 12h+ → the other analysts revert to manual VLOOKUP → Power Query usage doesn't spread.

**So what:** Power Query is a hidden dependency on one person. Spreading it = bus-factor mitigation + cycle-time saving.

### Loop 3 — Template drift (R, cosmetic but persistent)

Each cycle picks the "best" of 4 personal OneDrive copies → "best" subtly changes → next cycle picks slightly different "best" → template never converges → year-over-year deck format drifts → VPs notice and ask "is this a new format?" → analyst spends ~2h per cycle explaining template choice.

**So what:** Quick Win — consolidate to one canonical template. The drift is small per cycle but compounds; it's also a credibility tax with the VP.

### Loop 4 — Carryover-logic archaeology (R, calibration risk)

Carryover logic lives in prior-cycle decks → analyst re-derives each cycle → derivation has small errors → next cycle uses prior cycle as ground truth → errors compound → eventually carryover logic in cycle N has nothing to do with carryover logic in cycle N-5.

**So what:** Documentation Quick Win. 4 hours of writing prevents 5+ years of calibration drift.

---

## 5. Waste Ledger

| Category | Description | Frequency | Severity (hours-cost) |
|----------|-------------|-----------|----------------------|
| Waiting | Quarterly HRIS roster export — comp team waits for HRIS owner schedule | Per-cycle | 1-5h |
| Waiting | VP review at step 9 — average 5-day turnaround, blocks downstream | Per-cycle | 5-20h |
| Rework | Step 6 scenario re-runs after late VP feedback | Per-cycle | 5-20h (8h × ~4 re-runs last cycle = 32h) |
| Rework | Step 5 reconciliation surprises — re-export from HRIS | Per-cycle | 5-20h |
| Rework | First-cycle payroll variance — step-14 corrections | Per-cycle | 5-20h |
| Handoffs | Survey vendor → analyst (3 vendors, 3 formats) | Per-cycle | 5-20h (16h step 3) |
| Handoffs | Comp analyst → payroll owner — format spec drift | Per-cycle | 1-5h (8h handoff + corrections) |
| Over-processing | 5-scenario modeling when only 2 reach VP review | Per-cycle | 5-20h |
| Manual-when-automatable | VLOOKUP-heavy step 4 (24h) when Power Query brings it to 12h | Per-cycle | 5-20h |
| Manual-when-automatable | Manual scale-to-payroll upload (step 13) | Per-cycle | 1-5h |

---

## 6. Leverage Points + Intervention Plan

| # | Category | Description | Owner | Sequencing |
|---|----------|-------------|-------|-----------|
| 1 | Tools / automation | Consolidate deck template — one canonical version in shared folder | Comp Manager | Now (Quick Win) |
| 2 | Information flows | Document carryover logic on a wiki | Comp Analyst | Now (Quick Win) |
| 3 | Interfaces | Roster export contract — column-name spec + 30-day change notice | HRIS Owner + Comp Analyst | Now (Quick Win) |
| 4 | Tools / automation | Spread Power Query usage across all analysts (training + shared workbook) | Comp Manager | Next |
| 5 | Information flows | VP pre-review at step 7 (draft deck) instead of step 9 (formal pitch) | Comp Manager + VP | Next |
| 6 | Interfaces | Survey vendor format adapters (one per vendor — Mercer, WTW, StatCan) | Comp Analyst (build) + HRIS Owner (review) | Next |
| 7 | Tools / automation | Roster reconciliation auto-check — Power Query workbook that flags column drift before step 5 | Comp Analyst | Later |

---

## 7. Risks / Open Questions / Next Steps

**Risks:**
- VP pre-review at step 7 (leverage point #5) requires VP buy-in. If VP refuses, late-feedback loop continues.
- Power Query adoption (leverage point #4) requires training time the team doesn't have during prep weeks. Best landed in slack window (Sept-March).
- Survey vendor adapters (leverage point #6) depend on vendor format stability. Vendors change formats unpredictably; adapter maintenance is recurring.

**Open questions:**
- Does step-12 manager cascade reveal any pain that should re-feed into earlier steps? Worth a follow-up `/discover` on the HRBP-cascade-comms sub-process.
- Is post-payroll variance dominated by format drift (step 13) or roster errors (step 5)? Step-14 audit didn't get full coverage in `/discover`.

**Next steps:**
- Ship Quick Wins this week (action: Comp Manager kicks off all 3).
- Run `/transform` on leverage points 4-7 to produce buildable specs.
- Run `/roadmap` after `/transform` to sequence into 2026-Q4 / 2027-Q1 (first slack window post next cycle).
