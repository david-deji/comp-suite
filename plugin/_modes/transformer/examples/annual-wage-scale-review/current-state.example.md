---
process_slug: annual-wage-scale-review
team_slug: example-comp-team
last_interview: 2026-04-15
mode: directed-interview
discovered_cycle:
  anchor: "effective date 2026-09-01"
  current_stage: "Market analysis"
audience: comp-team-internal
---

# Current State: Annual Wage Scale Review

> Process slug: annual-wage-scale-review
> Last interview: 2026-04-15
> Mode: directed-interview
> Discovered cycle: anchor "effective date 2026-09-01" — current stage "Market analysis", week offset -20

## Process Identity

- **Name:** Annual wage scale review
- **Frequency:** Once per year, anchored to a September 1 effective date
- **Trigger:** Comp Manager schedules cycle kickoff in late March (week -22)
- **Completion signal:** New scale ships to payroll on August 15 (week -2 from anchor); payroll runs first on-scale paycheck mid-September
- **End-to-end duration:** ~22 weeks active work (March kickoff → August payroll handoff)

## Actors & Roles

| Role | Function in process | Effort per run |
|------|---------------------|---------------|
| Comp Analyst (Operator) | Pulls market data, models scenarios, builds deck, runs roster reconciliation | ~280 hours |
| Comp Manager | Owns budget envelope, approves recommended scenarios, presents to VP | ~60 hours |
| HRBP | Translates VP feedback, manages stakeholder narrative, coordinates cascade comms | ~40 hours |
| HRIS Owner | Provides quarterly roster export, fixes data quality issues post-hoc | ~20 hours |
| VP People | Final approver of scale, owns budget signoff to CFO | ~12 hours |

## Steps

| # | Step | Inputs | Outputs | Owner role | Tool(s) | Time | Notes |
|---|------|--------|---------|-----------|---------|------|-------|
| 1 | Cycle kickoff & scope | Last year's outcomes, business context | Scope memo | Comp Manager | Outlook, OneNote | 4h | Often slips by 1-2 weeks |
| 2 | Roster export | Quarterly pull from HRIS | Roster CSV | HRIS Owner | HRIS, Excel | 2h | Format changes year to year — caught at step 5 |
| 3 | Market data pull | Survey vendor downloads, StatCan refresh | Vendor exports + internal mapping | Comp Analyst | Mercer / WTW / StatCan | 16h | Each vendor's format differs |
| 4 | Market data normalization | Vendor exports | Aligned wage table per role-province | Comp Analyst | Excel + Power Query | 24h | Manual VLOOKUP-heavy |
| 5 | Roster reconciliation | Roster CSV + market table | Reconciled roster with role mappings | Comp Analyst | Excel | 12h | Format mismatches discovered here |
| 6 | Scenario modeling | Reconciled roster + market table + budget envelope | 3-5 scenarios with cost roll-ups | Comp Analyst | Excel scenario manager | 32h | Re-run on every late VP feedback |
| 7 | Deck build (initial) | Top 2 scenarios | Draft deck | Comp Analyst | PowerPoint, internal template | 28h | Template lives in 4 personal OneDrive copies |
| 8 | Comp Manager review | Draft deck | Reviewed deck + feedback | Comp Manager | PowerPoint | 6h | Usually 2 review rounds |
| 9 | VP approval pitch | Reviewed deck | Approved scenario | Comp Manager + VP | PowerPoint, Teams | 8h | Often 1-2 follow-up sessions for clarifications |
| 10 | Final scale build | Approved scenario | Finalized scale | Comp Analyst | Excel | 16h | Re-run if VP requests scenario tweaks |
| 11 | HRBP cascade brief | Finalized scale + VP narrative | Cascade memo + manager script | HRBP | Word, Outlook | 12h | |
| 12 | Manager cascade | Cascade memo | Manager 1:1s with reports | All people managers | Outlook, in-person | (cross-org) | Outside comp-team scope but tracked |
| 13 | Payroll handoff | Finalized scale | Scale uploaded to payroll system | Comp Analyst → Payroll Owner | HRIS payroll module | 8h | Cross-system manual upload |
| 14 | Post-payroll QA | First-paycheck audit | Variance report | Comp Analyst | Excel | 16h | Catches errors mid-September; rework if needed |

## Handoffs

| From → To | Contract | Format | Failure modes |
|-----------|----------|--------|---------------|
| HRIS Owner → Comp Analyst (step 2 → 3) | Quarterly roster export | CSV | Format changes year to year; columns rename without notice; missing fields caught at step 5, requiring re-export |
| Survey vendor → Comp Analyst (step 3) | Annual market data | Vendor-specific (Excel, CSV, PDF) | Each vendor's format differs; PDF requires manual extraction; year-over-year format drift |
| Comp Analyst → Comp Manager (step 7 → 8) | Draft deck for review | PowerPoint | Reviews always come back with structural changes; "fix the narrative" requires partial rebuild |
| Comp Manager → VP (step 9) | Reviewed deck | PowerPoint | VP often requests new scenario combinations not in the initial 3-5 — requires step 6 re-run |
| Comp Analyst → Payroll Owner (step 13) | Final scale | Scale upload format (CSV per HRIS spec) | Format spec drifts; payroll catches errors during first-cycle import |

## Tools & Systems

| Tool | Used in steps | Integration type | Bottleneck? |
|------|---------------|------------------|-------------|
| HRIS (Workday) | 2, 13 | Manual export / upload | Yes — quarterly export delay (step 2); upload format drift (step 13) |
| Excel | 4, 5, 6, 10, 14 | Heavy use, multiple workbooks per cycle | Yes — manual re-format and VLOOKUP-heavy work in steps 4-5 |
| Power Query | 4 | Used inconsistently — only one analyst uses it | No, but adoption is uneven |
| Survey vendor portals | 3 | Manual download per vendor | Yes — 3-4 vendors, each format differs |
| StatCan public data | 3 | Manual web fetch | No — small portion of data |
| PowerPoint | 7-9 | Manual deck build | Yes — template lives in 4 personal OneDrive copies (drift) |
| Outlook + Teams | 9, 11 | Communication only | No |

## Pain Points (raw)

> "Roster reconciliation is the worst week of every cycle. The HRIS export changes columns every year and we don't catch it until step 5. We've lost 2-3 days every cycle for the last 4 cycles." — Comp Analyst Operator

> "Late VP feedback at step 9 means re-running scenarios. Last cycle we re-ran 4 times. Each re-run is ~8 hours. So one VP question costs me a day and a half." — Comp Analyst Operator

> "The deck template lives in 4 different personal OneDrive copies. We picked the 'best' version this cycle by sending screenshots in Teams. That's a Quick Win waiting to happen." — Comp Manager

> "I have no idea how the carry-over logic works. Marie [previous analyst, now departed] knew it. Now we figure it out from prior decks each cycle. Calibration drift, big time." — Current Comp Analyst

> "Payroll catches errors in first-cycle import. We've had a 3-day rework window every cycle since 2023. The format spec drift is silent until the import fails." — Comp Analyst Operator

> "If we didn't do this for one cycle? Employees would notice. Managers wouldn't know what to do at merit conversations. The cycle has to ship." — SPIN cost-of-inaction response from Comp Manager

## Cycle Anchoring

- **This process runs in:** Stages "Intake" (week -22), "Market analysis" (-20 to -10), "Options modeling" (-10 to -7), "Approval" (-7 to -4), "Cascade" (-4 to -2), "Payroll" (-2 to 0), "Effective" (0 to +4)
- **Gating:** Intake = `prep`, Market analysis = `prep`, Options modeling = `prep`, Approval = `prep`, Cascade = `live`, Payroll = `live`, Effective = `live`. Slack windows = (+4 to +22 next-cycle Intake), i.e., Sept 28 → following March
- **Last run:** 2025-09-01 (effective date)

## Coverage Gaps (from interview)

- Step 12 (manager cascade) is partially covered — comp team's view ends at handoff to HRBP. The actual manager 1:1s happen outside comp scope. Worth a follow-up `/discover` extension for the HRBP-cascade-comms sub-process if the team wants to optimize that part of the timeline.
- Step 14 (post-payroll QA) was thin — analyst said "we do an audit" but didn't walk through the audit's structure. Worth a 15-min follow-up to map the audit checklist.
