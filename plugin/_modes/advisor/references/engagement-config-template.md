# Engagement Config — Unified Template

The engagement config is a single YAML block users paste at session start (or build via Init mode). It captures durable inputs the skill reuses across phases — org context, audience archetypes, costing parameters, benchmark defaults, deck preferences, and council defaults.

All eight sections (`engagement_scope`, `cycle`, `org`, `audience`, `costing`, `benchmark`, `deck`, `council`) are **optional**. Skill prompts for any section's data only when its phase needs that data and no config was provided. Persistence is **not** a config section in v2 — schema state persists automatically to the `market` backend (keyed to your authenticated login via org membership); there is no backend to select and no folder to name. See `references/persistence-and-ledger.md`.

### `engagement_mode` — Entry-time work-shape declaration

The engagement config accepts an optional `engagement_mode` field at the top level (alongside the eight sections). Setting it at `/init` time declares the intended work shape upfront so partial-flow engagements do not have to retrofit their mode at Phase 5 or later.

```yaml
engagement_mode: full-engagement   # default when absent
# Allowed values: full-engagement | narrative-frame-only | data-light-decision |
#                 costing-only | council-deliberation-only | r-lite-refresh
```

Default value when absent: `full-engagement`. The skill applies `full-engagement` behavior unless this field is present and set to a different value.

This is the **entry-time declaration**. The `engagement-state.yaml` produced at Phase 7 carries the full expansion — `mode_phases_run`, `mode_phases_partial`, `mode_phases_skipped`, `state_shape_variant`, and `pre_engagement_only` — derived from `references/engagement-modes.md`'s mode taxonomy. The config field is the user's intent; the state file fields are the system's resolved record.

Add a `last_verified: YYYY-MM-DD` field per section. Skill warns when a section is >180 days stale.

---

## Full template (paste-ready)

Copy this block, fill the sections you want, paste at session start. Delete sections you don't have — they're optional.

```yaml
# engagement-config — paste at session start
# (persistence is automatic via the `market` backend in v2 — there is no persistence
#  block to configure; see references/persistence-and-ledger.md)

# engagement_scope defines the boundary of THIS engagement.
# Rule of thumb: one engagement = one budget owner = one VP Ops (or equivalent).
# Pharmacy, Atlantic retail, Ontario retail, Western retail, Discount, etc. each
# have their own VP and their own budget envelope, so each is its own engagement.
# If you find yourself trying to cover two budget owners in one engagement, split it.
engagement_scope:
  last_verified: 2026-04-21
  budget_owner_role: "VP Ops, [Banner / Region]"   # e.g., "VP Ops, Pharmacy" or "VP Ops, Atlantic Retail"
  budget_owner_name: "[Person's name]"
  scope_label: "[Short label — 'Pharmacy FY26', 'Atlantic Retail May cohort']"
  banner_or_region: "[Pharmacy / Atlantic / Ontario / Western / Discount / etc.]"
  in_scope_role_families: ["[role family 1]", "[role family 2]"]   # what's covered
  out_of_scope: "[explicit list of what's NOT in this engagement — e.g., 'flagship-banner stores, Western retail, corporate HQ']"
  hr_lead: "[HRD or HRBP name owning the analyst-side relationship]"

# cycle tracks where we are in the end-to-end annual wage scale review.
# stage names are the canonical 7-stage workback (neutral defaults). Override the stage
# list in your personal config to use your org's actual stage names + RACI.
# anchor is "Wage Scale Effective Date" = day 0; all other offsets are weeks before/after.
cycle:
  last_verified: 2026-04-21
  cycle_name: "FY26 Annual Wage Review"
  cohort: "[Apr / May / Jun / Oct — whichever effective-date cohort this engagement belongs to]"
  effective_date: 2026-05-01            # the day-0 anchor for this cohort
  current_stage: "[stage name from stages list below]"
  current_week_offset: -10              # weeks relative to effective_date (negative = before)
  stages:
    # Neutral 7-stage default. Override with your org's actual stage names + RACI in your
    # personal config. Examples of how a real cycle might rename these:
    #   Discovery         → "Strategy Kickoff & Market Review" (retailer-style)
    #   Market Analysis   → "Market Analysis & Scale Design" / "Initial Data Audit & Validation"
    #   Scenario Modeling → "Options Review"
    #   Approval          → "Final Approval"
    #   Cascade           → "VP Ops Messaging Cascade" / "Store Guide & Wage Scale Posting"
    #   Implementation    → "System & Payroll Configuration" / "Final Pay Preview & Sign-Off"
    #   Live              → "Wage Scale Effective Date" / "Payout Date"
    # The skill keys behavior on the canonical neutral names below; your overrides drive the labels.
    - name: "Discovery"
      description: "Intake, scope alignment, last-cycle context, this-cycle goals."
      raci: { R: "Comp Lead", C: "HR Lead, Sponsor" }
      weeks_offset: [-12, -10]
    - name: "Market Analysis"
      description: "External benchmarks, internal data audit, scale design baseline."
      raci: { R: "Comp Analyst", C: "Comp Lead, HR Partners" }
      weeks_offset: [-14, -10]
    - name: "Scenario Modeling"
      description: "Cost-out 2-3 options against envelope; present financial models to leaders."
      raci: { R: "Comp Lead", C: "Sponsor, HR Lead" }
      weeks_offset: [-9, -8]
    - name: "Approval"
      description: "Decision-ask to budget owner. If > envelope, escalate per governance."
      raci: { R: "Comp Lead", A: "Sponsor" }
      weeks_offset: [-7, -7]
    - name: "Cascade"
      description: "Sponsor owns messaging and cascades changes through their org."
      raci: { R: "Sponsor", I: "HR Partners, Leaders" }
      weeks_offset: [-6, 0]
    - name: "Implementation"
      description: "Payroll instructions, system configuration, site posting, exception sign-off."
      raci: { R: "Comp Lead", I: "Payroll, HR Systems" }
      weeks_offset: [-6, -1]
    - name: "Live"
      description: "Effective date, retro pay, audit and exception reports."
      raci: { R: "Payroll", C: "HR Partners" }
      weeks_offset: [0, 2]
  last_cycle:
    # What was decided and done in the previous wage review for this same scope.
    # Skill uses this to ground "what's changed" framing in Phase 1 and to detect drift.
    cycle_name: "FY25 Annual Wage Review"
    effective_date: 2025-05-01
    headline_decision: "[1-2 sentence summary — e.g., '3% ATB + step compression fix on meat cutters in QC']"
    cost_to_company: "[$ amount or %]"
    scope_changed: "[what's different about this year's scope vs last — fewer roles, new banner, etc.]"
    known_outcomes: "[turnover trend, manager pushback, retention wins / losses observed since]"
    deferred_items: "[anything explicitly deferred from last cycle to this one]"
  this_cycle_goals:
    # User provides skeleton at engagement creation; intake form responses fill in detail later.
    # 'source' field tags where each goal came from for traceability.
    primary_objective: "[what success looks like — e.g., 'close meat-cutter gap to P50, hold envelope under $4M']"
    must_address: ["[non-negotiable item 1]", "[non-negotiable item 2]"]
    nice_to_have: ["[stretch item 1]"]
    envelope_ceiling: "[$ cap if known]"
    intake_inputs:                 # populated after intake forms come back
      worry_roles: []              # from intake Q4
      recruiting_pain: []          # from intake Q5
      competitor_moves: []         # from intake Q8
      poaching_signals: []         # from intake Q9
      source: "intake-form-{cycle-slug}-{date}.pdf"

org:
  last_verified: 2026-04-21
  name: "[Company name]"
  industry: "[grocery / manufacturing / healthcare / etc.]"
  banner: ["[Banner 1]", "[Banner 2]"]
  union_landscape:
    ON: "[union local or 'non-union']"
    QC: "[union local or 'non-union']"
  governance: "[who signs off on what]"
  pay_philosophy: "[stated philosophy — P50, P50+retention, P75 lead, etc.]"
  scale: "[approx headcount / revenue tier]"
  prior_recommendations: "[1-2 line summary of last cycle's outcome]"

audience:
  last_verified: 2026-04-21
  archetypes:
    - id: comp-committee
      who: "Board comp committee — 3 external directors + CEO"
      beliefs: "We pay competitively for retail; corporate is generous"
      typical_objection: "What's the ROI on each dollar?"
      preferred_framing: risk-first
      slide_count_target: 8
    - id: chro
      who: "CHRO + VP HR"
      beliefs: "We're behind market on hourly, fine on salary"
      typical_objection: "Where's the budget coming from?"
      preferred_framing: strategy-with-options
      slide_count_target: 15
    - id: hr-ops
      who: "Comp team and HR business partners"
      beliefs: "Manager pushback on individual comp decisions"
      typical_objection: "How do we explain this to managers?"
      preferred_framing: implementation-detail
      slide_count_target: 25

costing:
  last_verified: 2026-04-21
  # Roll-up factor can be national OR per-province (QC benefit costs include QPP/QPIP, differ from CPP-only provinces).
  # Use per-province map when accuracy matters. Use single national value when approximating.
  roll_up_factor:
    QC: 1.38   # incl. QPP, QPIP, CNESST, vacation, pension
    ON: 1.32   # incl. CPP, EI, EHT, vacation, pension
    AB: 1.30
    BC: 1.32
    NS: 1.30
    default: 1.35
  pay_attribution_pct: 0.35
  voluntary_turnover_pct:
    # Per-province if you have actuals — labour markets differ. Single value if approximating.
    QC: 0.22
    ON: 0.18
    AB: 0.20
    BC: 0.21
    NS: 0.16
    default: 0.15
  replacement_multipliers:
    hourly: 0.18
    professional: 0.55
    management: 1.25
    executive: 1.80
    unknown: 0.50
  payroll_burden_pct:
    QC: 0.142   # CPP/QPP, EI, QPIP, HSF, CNESST
    ON: 0.115   # CPP, EI, EHT, WSIB
    AB: 0.105
    BC: 0.118
    NS: 0.110
    other: 0.12
  # When provincial minimum wage forces step 1 up, do we cascade the increase
  # up the scale (every step shifts) or lift step 1 only (and accept compression)?
  # cascade: maintain scale spread; higher mandatory floor cost
  # step_1_only: only lift step 1; lower floor cost but creates compression at the bottom
  # ask_per_engagement: skill prompts at Phase 4 entry every time (default if unset)
  minimum_wage_treatment: cascade
  target_percentile: 50
  rounding:
    per_role: 100
    aggregate: 1000
    percentage_decimals: 1
    compa_ratio_decimals: 2
  effective_date_default: "next-fiscal-year-start"

benchmark:
  last_verified: 2026-04-21
  default_percentiles: [10, 25, 50, 75, 90]
  default_province: QC
  scope_provinces: [QC, ON, AB, BC, NS]  # all provinces this engagement covers; drives multi-province calculation
  include_economic_regions: true
  source_priority: [market_mcp, cba, indeed, web]
  peer_companies: ["Loblaws", "Metro", "Walmart Canada", "Costco"]
  role_aliases:
    "Cake Decorator": NOC 63202
    "Deli Associate": NOC 65201
    "Meat Cutter": NOC 63201
  cba_lookup_required_for: ["UFCW grocery", "construction", "healthcare", "public-sector"]
  aging_rule: "only when source predates Market MCP window_months OR external survey >12 months old"
  provincial_minimum_wages:
    # Update annually — provincial labour ministries change rates regularly. Verify before citing.
    ON: { rate: 17.20, effective: 2025-10-01, next_review: 2026-10-01 }
    QC: { rate: 16.10, effective: 2025-05-01, next_review: 2026-05-01 }
    BC: { rate: 17.85, effective: 2025-06-01, next_review: 2026-06-01 }
    AB: { rate: 15.00, effective: 2024-10-01, next_review: 2025-10-01 }
    NS: { rate: 15.70, effective: 2025-04-01, next_review: 2026-04-01 }

deck:
  last_verified: 2026-04-21
  brand: acme  # <org-slug> | neutral
  language: en   # en | fr-ca — fr-ca activates references/fr-ca-glossary.md (closed glossary;
                 # unapproved terms get surfaced to user mid-engagement, never silently translated)
  production_mode: interactive  # interactive | silent | hybrid
  # interactive: 6a section plan + 6b per-section A/B choice + 6c assembly. Best for high-stakes
  #              decks (board, CHRO, contested recommendations).
  # silent:      6a section plan still confirmed, 6b auto-picks Option A, 6c assembles. Best for
  #              routine refreshes, deliverables you've shipped many times before.
  # hybrid:      6a section plan, 6b interactive only on high-stakes sections (Findings,
  #              Recommendation), silent on routine sections (Cover, Market Context, Appendix).
  #              Default for most analyst workflows once you trust the skill.
  slide_count_by_audience:
    board: 8
    chro: 15
    hr_ops: 25
    employees: 6
  required_appendix: [methodology, assumptions, glossary, data-sources]
  voice: practitioner, peer-tone, no jargon-explanations
  decision_ask_pattern: "Approve $X over Y months for Z scope"
  default_chart_types:
    gap_analysis: waterfall
    compa_ratio: histogram
    scale_comparison: side-by-side-bar
    yoy_delta: line-with-callouts
  callout_size_pt: 60
  artifacts: [pptx]  # always include pptx; add xlsx (cost scenarios) or csv (raw market data) for client self-service

council:
  last_verified: 2026-04-21
  default_mode: reasoning                # reasoning | memo | integrated
  default_perspectives:                  # 4-6 recommended; 7 max
    - employment-lawyer
    - total-rewards-strategist
    - cfo-finance
    - hr-business-partner
    - dei-pay-equity
  perspective_overrides:
    # Per-persona context tweaks. Useful when a client's context shifts emphasis.
    # jurisdiction_focus defaults to benchmark.scope_provinces if unset.
    employment-lawyer:
      jurisdiction_focus: [QC]
      emphasis: "CBA interpretation, pay equity maintenance exposure (Loi sur l'équité salariale)"
    cfo-finance:
      emphasis: "Multi-year roll-up; envelope ceiling ~$5M"
    dei-pay-equity:
      emphasis: "QC Pay Equity Act predominance logic; maintenance cycle"
  confidence_tags:
    required: true
    # Canonical 11-tag vocabulary per references/tools-available.md § Verified-source discipline.
    # Fine-grained tags enable per-source-class auto-downgrade. Do NOT use the legacy 4-tag shorthand.
    vocabulary: [statcan-wage, live-postings, cba, indeed-company, econometric, statutory, market-data, survey-house, user-provided-cba, professional-judgment, assumption]
  synthesis_style: consensus-tensions    # consensus-tensions | vote-count | severity-triage
  memo_format:
    sections: [situation, options, recommendation, risks, unresolved]
    length_cap_words: 800
    audience_inherits_from: audience.archetypes   # reuses main config's audience archetype
  persona_voice_profiles:
    # Optional framing overrides per persona
    employment-lawyer: "Cite CCQ / CNESST articles where relevant; conservative posture"
    dei-pay-equity: "QC Pay Equity Act lens; centers systemic fairness"
  artifacts: [council-state-yaml, council-memo-md]   # memo-md only in memo mode; state-yaml always
```

---

## Section schemas

### `engagement_scope` — Engagement boundary

Defines who owns the budget for this engagement and what's in/out of scope. The skill uses this to gate Phase 1 ("does this engagement actually have a single budget owner?") and to prevent scope creep in Phase 4 costing.

**The rule:** one engagement = one budget owner = one VP Ops (or equivalent). Pharmacy, Atlantic retail, Ontario retail, Western retail, Discount each have their own VP and their own budget envelope. If a request seems to span two budget owners, the skill will surface that and recommend splitting.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `budget_owner_role` | string | yes | The VP-level role accountable for the budget (e.g., "VP Ops, Pharmacy"). If you can't name one, the engagement isn't scoped tightly enough. |
| `budget_owner_name` | string | recommended | The actual person in the role today. Drives Phase 5 decision-ask phrasing. |
| `scope_label` | string | yes | Short engagement label used in deck headers and filenames. |
| `banner_or_region` | string | recommended | Maps to the slice of the business this covers (Pharmacy, Atlantic, Ontario, Western, Discount, etc.). |
| `in_scope_role_families` | list of strings | recommended | What's covered. Drives Phase 2 data pull and Phase 4 costing scope. |
| `out_of_scope` | string | recommended | Explicit list of what's NOT in this engagement. Cited on the deck's scope slide. Reduces ambiguity when the user later asks "should we include corporate?" |
| `hr_lead` | string | optional | The HRD or HRBP managing the analyst-side relationship. |

### `cycle` — End-to-end annual wage scale review tracking

Tracks where the engagement sits in the multi-month cycle, what was decided last cycle, and what this cycle is trying to accomplish. The skill uses `cycle.current_stage` and `cycle.current_week_offset` to calibrate every phase — at week −12 we're still framing scope; at week −7 we're building the approval pitch; at week +2 we're past the door and into payroll execution support.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `cycle_name` | string | yes | E.g., "FY26 Annual Wage Review". Appears in deck headers and intake forms. |
| `cohort` | string | recommended | Which effective-date cohort: Apr / May / Jun / Oct (or your equivalent). Multi-cohort engagements should be split. |
| `effective_date` | date | yes | The day-0 anchor. Wage scale goes live on this date. All other stage dates compute as offsets from this. |
| `current_stage` | string | yes | Stage name from the `stages` list. Drives skill behavior (e.g., during "Strategic Intake & Budgeting" the skill nudges toward `/intake`; during "Options Review" it goes to Phase 4 costing). |
| `current_week_offset` | int | recommended | Weeks before/after `effective_date`. Negative = before. The skill warns when this is inconsistent with `current_stage`'s expected window. |
| `stages` | list of stage objects | recommended | The canonical 7-stage workback (Discovery / Market Analysis / Scenario Modeling / Approval / Cascade / Implementation / Live) — or your edited version with org-specific labels. Each stage has `name`, `description`, `raci`, and `weeks_offset` [start, end]. |
| `last_cycle.cycle_name` | string | recommended | Prior cycle name. |
| `last_cycle.effective_date` | date | recommended | Prior cycle's effective date. |
| `last_cycle.headline_decision` | string | recommended | 1-2 line summary of what was decided. Skill uses this in Phase 1 to ground "what's changed" framing. |
| `last_cycle.cost_to_company` | string | optional | Total cost of last cycle's adjustment. |
| `last_cycle.scope_changed` | string | optional | What's different about this year's scope vs last (different roles, banner change, etc.). |
| `last_cycle.known_outcomes` | string | optional | What you've observed since — turnover trend, manager pushback, retention wins/losses. Phase 3 cites this when interpretation lines up or contradicts. |
| `last_cycle.deferred_items` | string | optional | Anything explicitly deferred from last cycle to this one. |
| `this_cycle_goals.primary_objective` | string | yes | What success looks like for this cycle. |
| `this_cycle_goals.must_address` | list of strings | recommended | Non-negotiable items. Phase 4 scenarios must address all of these. |
| `this_cycle_goals.nice_to_have` | list of strings | optional | Stretch items. Phase 4 may include in upside scenario only. |
| `this_cycle_goals.envelope_ceiling` | string | recommended | $ cap if known. Hard constraint on Phase 4 modeling. |
| `this_cycle_goals.intake_inputs` | object | optional | Populated after intake forms come back. The intake-mode protocol writes `worry_roles`, `recruiting_pain`, `competitor_moves`, `poaching_signals` here for Phase 1 / Phase 3 reference. |

**Stage-aware skill behavior** (selected examples):

| Current stage / week | Skill emphasis |
|---|---|
| Pre-cycle (week ≤ −15) | Suggest `/init` or `/update` to refresh config before kickoff. |
| Discovery (−12 to −10) | Phase 1 framing emphasizes "align on scope and objectives with the sponsor." Nudge toward `/intake` if `this_cycle_goals.intake_inputs` is empty. |
| Market Analysis (−14 to −10) | Track C/D normal flow; Phase 2 data pull is the work. |
| Scenario Modeling (−9 to −8) | Phase 4 costing is the live deliverable. |
| Approval (−7) | Phase 5 decision-ask is the live deliverable; flag if envelope > ceiling. |
| Cascade (−6 to 0) | Phase 6 cascade-deck spine; manager talking points. |
| Implementation (−6 to −1) | Pre-effective-date support; payroll exception reports. |
| Live (≥ 0) | Decline new strategy work for this cycle; route to next cohort or to retro/audit support. |

### `org` — Organization context

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | Company legal name |
| `industry` | string | recommended | Drives default benchmarks and CBA lookup |
| `banner` | list of strings | optional | For multi-banner orgs (parent → child banners, etc.) |
| `union_landscape` | map of province → union | optional | Triggers `get_cba_wage_scale` lookups in Phase 2 |
| `governance` | string | optional | Sign-off pattern; informs Phase 5 decision-ask phrasing |
| `pay_philosophy` | string | optional | Drives default target percentile; cited in Phase 5 narrative |
| `scale` | string | optional | Headcount tier; informs Phase 4 cost framing |
| `prior_recommendations` | string | optional | Read by R-lite for context continuity |

### `audience` — Audience archetypes

A list of named archetypes. Phase 1 Beat 2 picks an `id` from this list (or asks if not provided). Phase 5 uses the matching archetype's `beliefs`, `typical_objection`, `preferred_framing` to pre-fill audience psychology.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | yes | Short identifier — `board`, `chro`, `hr-ops`, `union-bargaining`, etc. |
| `who` | string | yes | One-line description |
| `beliefs` | string | yes | What they currently believe about pay |
| `typical_objection` | string | yes | The hardest question they'll ask |
| `preferred_framing` | enum | yes | `risk-first` / `strategy-with-options` / `implementation-detail` / `educational` |
| `slide_count_target` | int | recommended | Per-audience slide count for Phase 7 calibration |

### `costing` — Cost-modeling parameters

All values used in Phase 4 formulas. Defaults documented in `references/costing-engine.md`.

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `roll_up_factor` | float OR map of province → float | 1.0 (single) OR per-province map with `default` key | Total benefit cost / straight-time wages. **Per-province preferred** (QC includes QPP/QPIP/CNESST, differs from CPP-only provinces). Single national value acceptable for approximation. |
| `pay_attribution_pct` | float | 0.35 | Fraction of voluntary turnover attributable to pay |
| `voluntary_turnover_pct` | float OR map of province → float | 0.15 (single) OR per-province map with `default` key | Per-province if you have actuals — labour markets differ. Single value if approximating. |
| `replacement_multipliers` | map of level → fraction | per costing-engine.md table | % of annual salary to replace |
| `payroll_burden_pct` | map of province → fraction | QC: 0.142, ON: 0.115 (verify) | Per-province; required field on costing slide caveats |
| `minimum_wage_treatment` | enum | `ask_per_engagement` | `cascade` / `step_1_only` / `ask_per_engagement`. Drives Section 4.0 mandatory floor calc when provincial minimum wage exceeds current step 1. Cascade = every step shifts up to maintain spread (higher floor cost). Step 1 only = lift step 1 only and accept compression at the bottom (lower floor cost but creates remediation work later). Ask = skill prompts at Phase 4 entry. |
| `target_percentile` | int | 50 | Default market positioning reference |
| `rounding` | map | per costing-engine.md | Per-role, aggregate, percentage, compa-ratio precision |
| `effective_date_default` | string | "next-fiscal-year-start" | Used when proration matters |

### `benchmark` — Market data defaults

Used by Phase 2 (Data Gathering). Replaces interactive prompts for percentiles, geographies, peer sets, role aliases.

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `default_percentiles` | list of int | [10,25,50,75,90] | Passed to `get_role_intelligence` |
| `default_province` | string | (prompt) | 2-letter code; the primary province for single-province engagements |
| `scope_provinces` | list of strings | (default = [default_province]) | All provinces this engagement covers. Drives multi-province calculation in Phase 2 (per-province data pulls) and Phase 4 (per-province cost aggregation). |
| `include_economic_regions` | bool | true | Sub-province granularity for multi-site |
| `source_priority` | list | [market_mcp, cba, indeed, web] | Tool selection order |
| `peer_companies` | list of strings | (none) | Used in Indeed `get_company_data` calls |
| `role_aliases` | map of role → NOC code | (none) | Bypasses `search_roles` for known mappings |
| `cba_lookup_required_for` | list of strings | (none) | Triggers `get_cba_wage_scale` automatically |
| `aging_rule` | string | "Market MCP YoY only" | Document when extra aging applies |
| `provincial_minimum_wages` | map of province → {rate, effective, next_review} | (prompt or web-verify) | Per-province minimum wage. Required for entry-rate-vs-min-wage compression checks. Update annually — the skill warns when `next_review` date passes. Verify against provincial labour ministry before citing on slides. |

### `deck` — Presentation defaults

Used by Phase 6 (Production) and Phase 7 (QA).

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `brand` | enum | <org-slug> | `<org-slug>` or `neutral`; overrides per-engagement still possible at Phase 5 |
| `production_mode` | enum | interactive | `interactive` / `silent` / `hybrid`. Drives Phase 6b behavior. Track-level defaults (C/R = interactive, D = silent) lose to this config value when set. `hybrid` builds Cover, Market Context, Appendix silently and prompts for A/B only on Findings, Options, Recommendation — best balance once the user trusts the skill. |
| `slide_count_by_audience` | map of audience id → int | board:8, chro:15, hr_ops:25 | Phase 7 audience-calibration check |
| `required_appendix` | list of strings | (none) | Slides that must exist regardless of audience |
| `voice` | string | (default skill voice) | Tonal guidance for slide copy |
| `decision_ask_pattern` | string | "Approve $X over Y months for Z scope" | Final-slide template |
| `default_chart_types` | map of analysis → chart | per skill defaults | Drives Phase 6 chart selection |
| `callout_size_pt` | int | 60 | Large-number callout font size |
| `artifacts` | list of enum | `[pptx]` | Output artifacts. Always includes `pptx`. Add `xlsx` for cost-scenarios spreadsheet, `csv` for raw market-data table. Both are gated client self-service options. |

### `council` — Strategic deliberation defaults

Used by Track Council (strategic-decision deliberation mode). When absent, skill prompts for mode and perspectives at Council track entry. Full council protocol lives in `references/council-mode.md`.

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `default_mode` | enum | `reasoning` | `reasoning` (full persona blocks + synthesis), `memo` (adds standalone decision memo), `integrated` (feeds Phase 4 or 5 of a consulting engagement) |
| `default_perspectives` | list of enum | `[employment-lawyer, total-rewards-strategist, cfo-finance, hr-business-partner, dei-pay-equity]` | 4-6 recommended; 7 max. Pool: `employment-lawyer`, `total-rewards-strategist`, `cfo-finance`, `hr-business-partner`, `dei-pay-equity`, `employee-union`, `ceo-board` |
| `perspective_overrides` | map of persona-id → {jurisdiction_focus, emphasis} | (none) | Per-persona context tweaks. `jurisdiction_focus` defaults to `benchmark.scope_provinces` if unset |
| `confidence_tags.required` | bool | `true` | When true, every substantive persona claim carries a tag |
| `confidence_tags.vocabulary` | list | `[statcan-wage, live-postings, cba, indeed-company, econometric, statutory, market-data, survey-house, user-provided-cba, professional-judgment, assumption]` | Canonical 11-tag vocabulary used in persona blocks and synthesis. Source of truth: `references/tools-available.md` § Verified-source discipline. The legacy 4-tag shorthand (`statutory`/`market-data`/`professional-judgment`/`assumption`) is deprecated; do not use for new configs. |
| `synthesis_style` | enum | `consensus-tensions` | `consensus-tensions` (default — surfaces disagreement), `vote-count` (tally personas when 2-3 named options), `severity-triage` (rank concerns when evaluating a proposed action) |
| `memo_format.sections` | list | `[situation, options, recommendation, risks, unresolved]` | Memo block structure when `mode: memo` |
| `memo_format.length_cap_words` | int | `800` | Hard cap on memo body length |
| `memo_format.audience_inherits_from` | string | `audience.archetypes` | Pulls audience framing from main config's audience section |
| `persona_voice_profiles` | map of persona-id → string | (none) | Framing overrides per persona |
| `artifacts` | list of enum | `[council-state-yaml, council-memo-md]` | `council-state-yaml` always produced; `council-memo-md` only in memo mode |

### `persistence` — retired (v2)

There is no `persistence` config section in v2. Schema state — orgs, master sections, engagement bodies, cycles, the decision log, brand kits, costing — persists to the `market` MCP backend automatically, keyed to the authenticated login via org membership. There is no backend to select, no repo to name, no folder-visibility gate, and no paste-mode branch. Non-schema artifacts (deliverables, council scratch, `cost-log.jsonl`) stay under local `$STATE_ROOT`. On MCP transport failure, schema reads fall back to the local cache (degraded) and schema writes escalate/halt (P4b D1/D2). A legacy config carrying a `persistence:` block is ignored as a backend selector. Full contract: `references/persistence-and-ledger.md`.

---

## Worked example — Acme QC annual cycle

```yaml
org:
  last_verified: 2026-04-21
  name: "Acme Inc."
  industry: grocery
  banner: ["Marché Acme", "Acme Express"]
  union_landscape: { QC: "TUAC 501" }
  governance: "CHRO sign-off; comp committee for >$1M annual"
  pay_philosophy: "P50 with retention premium for hard-to-fill"
  scale: "~125,000 FTE national"
  prior_recommendations: "2025: approved $4.2M scale lift for QC retail; 2024: deferred merit increase"

audience:
  last_verified: 2026-04-21
  archetypes:
    - id: comp-committee
      who: "Board comp committee — 3 external directors + CEO"
      beliefs: "We pay competitively for retail; corporate is generous"
      typical_objection: "What's the ROI on each dollar?"
      preferred_framing: risk-first
      slide_count_target: 8

costing:
  last_verified: 2026-04-21
  # Single-province engagement: scalar values are fine
  roll_up_factor: 1.38  # QC retail incl. QPP, QPIP, vacation, pension
  pay_attribution_pct: 0.35
  voluntary_turnover_pct: 0.22  # actual QC retail rate
  replacement_multipliers: { hourly: 0.16, professional: 0.55, management: 1.30, executive: 1.80 }
  payroll_burden_pct: { QC: 0.142 }  # actual rate, not estimate
  target_percentile: 50
  rounding: { per_role: 100, aggregate: 1000 }

benchmark:
  last_verified: 2026-04-21
  default_percentiles: [10, 25, 50, 75, 90]  # P10/P90 are floor/ceiling — load-bearing default per references/tools-available.md § Anti-patterns
  default_province: QC
  scope_provinces: [QC]  # single-province engagement
  include_economic_regions: true
  source_priority: [market_mcp, cba, indeed]
  peer_companies: ["Metro Inc.", "Loblaws (Provigo)", "Walmart Canada", "Costco Wholesale Canada"]
  role_aliases:
    "Caissier(ère)": NOC 65100
    "Boucher": NOC 63201
    "Pâtissier": NOC 63202
  cba_lookup_required_for: ["UFCW grocery", "TUAC retail"]
  provincial_minimum_wages:
    QC: { rate: 16.10, effective: 2025-05-01, next_review: 2026-05-01 }

deck:
  last_verified: 2026-04-21
  brand: acme
  slide_count_by_audience: { board: 8, chro: 15, hr_ops: 25 }
  required_appendix: [methodology, assumptions, data-sources, payroll-tax-caveat]
  voice: practitioner French/English bilingual; risk-first tone for board
  decision_ask_pattern: "Approuver $X sur Y mois pour Z portée"
  default_chart_types: { gap_analysis: waterfall, compa_ratio: histogram }

council:
  last_verified: 2026-04-21
  default_mode: integrated  # council runs inside Phase 4/5 of the annual cycle engagement
  default_perspectives:
    - employment-lawyer
    - total-rewards-strategist
    - cfo-finance
    - hr-business-partner
    - employee-union  # TUAC 501 perspective is load-bearing for QC retail
  perspective_overrides:
    employment-lawyer:
      jurisdiction_focus: [QC]
      emphasis: "TUAC 501 CBA interpretation; QC pay equity maintenance"
    dei-pay-equity:
      emphasis: "QC Pay Equity Act predominance logic"
  synthesis_style: consensus-tensions
  memo_format: { length_cap_words: 800 }
```

---

## Worked example — Acme QC council: ATB vs top-step (integrated mode)

This block shows a council-focused engagement where the user wants strategic deliberation on an allocation question inside an approved envelope. Council mode is `integrated` — the output feeds Phase 4 scenario modeling and Phase 5 narrative.

```yaml
org:
  last_verified: 2026-04-21
  name: "Acme Inc."
  industry: grocery
  banner: ["Marché Acme", "Acme Express"]
  union_landscape: { QC: "TUAC 501" }
  pay_philosophy: "P50 with retention premium for hard-to-fill"

audience:
  last_verified: 2026-04-21
  archetypes:
    - id: chro
      who: "CHRO + VP HR (QC)"
      beliefs: "Top-step compression is eroding retention for fully-qualified meat cutters"
      typical_objection: "Where's the evidence the structural change is worth the long-tail cost?"
      preferred_framing: strategy-with-options
      slide_count_target: 15

benchmark:
  last_verified: 2026-04-21
  default_province: QC
  scope_provinces: [QC]
  peer_companies: ["Metro Inc.", "Loblaws (Provigo)"]

council:
  last_verified: 2026-04-21
  default_mode: integrated
  default_perspectives:
    - employment-lawyer
    - total-rewards-strategist
    - cfo-finance
    - hr-business-partner
    - employee-union
    - dei-pay-equity      # six perspectives — predominantly-female classes on some steps
  perspective_overrides:
    employment-lawyer:
      jurisdiction_focus: [QC]
      emphasis: "TUAC 501 reopener exposure if new top step is structurally added mid-CBA"
    cfo-finance:
      emphasis: "5-year roll-up of top-step addition vs. ATB compounding; envelope $4.2M fiscal 2026"
    employee-union:
      emphasis: "Bargaining-unit acceptance of step-structure change vs. ATB"
  synthesis_style: consensus-tensions
  memo_format:
    length_cap_words: 800
    audience_inherits_from: audience.archetypes
  artifacts: [council-state-yaml]  # integrated mode; no standalone memo
```

Skill behavior with this config:
- Phase 0: loads full config including council section; sets `default_mode: integrated`
- Council track (triggered by "run council on ATB vs top-step"): skips persona-selection prompt (6 perspectives pre-set), skips mode prompt, inherits CHRO audience framing
- Phase 4 Option Modeling: council output narrows scenarios to those surviving council synthesis; Phase 4 workers receive the council-state YAML as input
- Phase 5 Narrative Workshop: uses council's recommended path as the deck's central thesis; council tensions become the decision-ask framing
- Phase 6 Production: deck includes 1-3 strategic framing slides derived from the council's consensus + named tension
- `council-state-YYYY-MM-DD-acme-qc.yaml` produced; user saves alongside `engagement-state`

---

## Worked example — National multi-province engagement (Acme all-banner)

```yaml
org:
  last_verified: 2026-04-21
  name: "Acme Inc."
  industry: grocery
  banner: ["Acme", "Acme Express", "Marché Acme", "ValuFresh", "Westgro", "Acme Pharmacy"]
  union_landscape:
    QC: "TUAC 501"
    ON: "UFCW Local 175"
    AB: "UFCW Local 401"
    BC: "UFCW Local 1518"
    NS: "non-union (Westgro), UFCW Local 864 (Acme retail)"
  governance: "CHRO sign-off; comp committee for >$2M annual; board for >$10M"
  pay_philosophy: "P50 with retention premium for hard-to-fill"
  scale: "~125,000 FTE across all banners"

audience:
  last_verified: 2026-04-21
  archetypes:
    - id: comp-committee
      who: "Board comp committee — 3 external directors + CEO"
      beliefs: "Labour cost % is rising; we pay competitively"
      typical_objection: "How do per-province ROI calculations roll up to national?"
      preferred_framing: risk-first
      slide_count_target: 10  # +2 from default for multi-province context

costing:
  last_verified: 2026-04-21
  # Per-province values — multi-province engagement
  roll_up_factor:
    QC: 1.38   # incl. QPP, QPIP, CNESST
    ON: 1.32   # incl. CPP, EI, EHT
    AB: 1.30
    BC: 1.32
    NS: 1.30
    default: 1.32
  pay_attribution_pct: 0.35
  voluntary_turnover_pct:
    QC: 0.22
    ON: 0.18
    AB: 0.20
    BC: 0.21
    NS: 0.16
    default: 0.18
  replacement_multipliers: { hourly: 0.18, professional: 0.55, management: 1.25, executive: 1.80 }
  payroll_burden_pct:
    QC: 0.142
    ON: 0.115
    AB: 0.105
    BC: 0.118
    NS: 0.110
  target_percentile: 50
  rounding: { per_role: 100, aggregate: 1000 }

benchmark:
  last_verified: 2026-04-21
  default_percentiles: [10, 25, 50, 75, 90]  # P10/P90 are floor/ceiling — load-bearing default per references/tools-available.md § Anti-patterns
  default_province: ON  # head-office province; reports default here
  scope_provinces: [QC, ON, AB, BC, NS]  # all provinces in this engagement
  include_economic_regions: true
  source_priority: [market_mcp, cba, indeed]
  peer_companies: ["Loblaws", "Metro", "Walmart Canada", "Costco"]
  cba_lookup_required_for: ["UFCW grocery", "TUAC retail"]
  provincial_minimum_wages:
    QC: { rate: 16.10, effective: 2025-05-01, next_review: 2026-05-01 }
    ON: { rate: 17.20, effective: 2025-10-01, next_review: 2026-10-01 }
    AB: { rate: 15.00, effective: 2024-10-01, next_review: 2026-10-01 }
    BC: { rate: 17.85, effective: 2025-06-01, next_review: 2026-06-01 }
    NS: { rate: 15.70, effective: 2025-04-01, next_review: 2026-04-01 }

deck:
  last_verified: 2026-04-21
  brand: acme
  slide_count_by_audience: { board: 10, chro: 18, hr_ops: 30 }  # +2-5 vs default for multi-province context
  required_appendix: [methodology, assumptions, data-sources, payroll-tax-caveat, per-province-breakdown]
  voice: practitioner, peer-tone
  artifacts: [pptx, xlsx, csv]  # full set for board engagement with multi-province auditability
```

Skill behavior with this config:
- Phase 2: 5 sets of `get_role_intelligence` calls (one per province), per-province CBA lookups (TUAC 501 for QC, UFCW 175 for ON, etc.), per-province minimum-wage compression checks
- Phase 4: per-province cost computation (each scenario shows 5 line items + national aggregate)
- Phase 6: PPTX has per-province breakdown slides + national rollup slide; xlsx has one sheet per province + summary
- Phase 7 QA dimension 4 verifies per-province values were used correctly

---

## Worked example — Generic / first engagement (minimal)

When a user has no saved config, this minimal block lets them get started. Skill prompts for missing fields as their phases activate.

```yaml
org:
  name: "[Client name]"
  industry: "[industry]"

costing:
  roll_up_factor: 1.0  # confirm before Phase 4
  target_percentile: 50

benchmark:
  default_province: "[2-letter code]"
```

Skill behavior with this minimal config:
- Phase 1: full discovery (no audience archetype to skip Beat 2)
- Phase 2: prompts for percentiles + economic regions on first market call
- Phase 4: prompts for the missing 6 costing inputs before scenario modeling
- Phase 5: full audience-psychology workshop (no archetype to pre-fill)
- Phase 7: default brand + audience-default slide counts

---

## Multi-province calculation

When `benchmark.scope_provinces` contains 2+ provinces, the skill runs per-province calculations and aggregates. Single-value config fields (e.g., `costing.roll_up_factor: 1.35`) apply uniformly; map-form fields (e.g., `costing.roll_up_factor: {QC: 1.38, ON: 1.32, default: 1.35}`) apply per-province with `default` as fallback.

### Per-province calculation pattern

For each scenario in Phase 4, the skill produces a per-province breakdown plus a national aggregate:

```
Scenario B: 2.5% scale lift + new top step

Per-province cost (base wage × roll-up):
  QC: $1,420,000 (1.38 roll-up; 8,400 FTE; payroll burden 14.2% adds $202K total cost)
  ON: $1,180,000 (1.32 roll-up; 6,200 FTE; payroll burden 11.5% adds $136K)
  AB:   $580,000 (1.30 roll-up; 3,100 FTE; payroll burden 10.5% adds $61K)
  BC:   $720,000 (1.32 roll-up; 3,800 FTE; payroll burden 11.8% adds $85K)
  NS:   $300,000 (1.30 roll-up; 1,800 FTE; payroll burden 11.0% adds $33K)

National aggregate:
  Base + roll-up: $4,200,000
  + Payroll burden: $517,000
  Total employer cost: $4,717,000
```

### Per-province minimum-wage compression check

For each province in scope, the skill checks entry rate vs that province's minimum wage from `benchmark.provincial_minimum_wages`:

```
Entry rate vs provincial minimum wage:
  QC: $16.85 vs $16.10 minimum (+$0.75 premium — eroding, was +$1.20 last year)
  ON: $17.50 vs $17.20 minimum (+$0.30 premium — at risk; ON minimum rises Oct 2026)
  AB: $16.00 vs $15.00 minimum (+$1.00 premium — healthy)
  BC: $18.50 vs $17.85 minimum (+$0.65 premium — eroding)
  NS: $16.50 vs $15.70 minimum (+$0.80 premium — healthy)
```

When the next-year provincial minimum-wage projection (if known) would push a province's entry rate to <$0.50 above minimum, flag as compression risk for the recommendation slide.

### Aggregation rules

| Metric | Aggregation method |
|--------|-------------------|
| Base wage cost | Sum across provinces |
| Roll-up loaded cost | Sum across provinces (each province uses its own roll-up factor) |
| Payroll burden | Sum across provinces (each province uses its own burden %) |
| Total employer cost | Sum of base + roll-up + payroll burden across provinces |
| Headcount | Sum across provinces |
| Average compa-ratio | Payroll-weighted across provinces (NOT simple average) |
| % of payroll | Calculated against total national payroll across provinces |
| Do-nothing turnover cost | Sum across provinces (each uses its own voluntary_turnover_pct and replacement_multipliers) |

### Stale check for minimum wages

Skill warns at Phase 0 if any `provincial_minimum_wages[X].next_review` date has passed:

```
⚠ Minimum wage stale: ON next_review was 2026-10-01 (today is 2026-10-15). Verify current rate before Phase 2.
```

User should update the config OR the skill should web-search the current value and tag `[WEB-VERIFIED YYYY-MM-DD]` in any slide citation.

---

## Validation rules

When parsing a pasted config:

1. **Required keys per section**: `engagement_scope` requires `budget_owner_role` and `scope_label`. `cycle` requires `cycle_name`, `effective_date`, and `current_stage`. `org` requires `name`. `costing` requires nothing (all defaults). `audience` requires at least one archetype with all 6 fields populated. `benchmark` requires nothing. `deck` requires nothing. `council` requires nothing — all defaults documented in `references/council-mode.md`. (Persistence is not a config section in v2 — see § `persistence` — retired.)
2. **Stale check**: If `last_verified` is more than 180 days old, surface a warning before using that section. For `cycle`, a stale `last_verified` is more concerning than other sections — surface even at 60+ days.
3. **Type check**: numeric fields must parse as float/int. Date fields (`cycle.effective_date`, `cycle.last_cycle.effective_date`) must parse as ISO dates. Enum fields (preferred_framing, brand, council.default_mode, council.synthesis_style) must match allowed values. Persona names in `council.default_perspectives` must be drawn from the 7-persona pool in `council-mode.md`. **`cycle.current_stage` must match either the `name` field (canonical: Discovery / Market Analysis / Scenario Modeling / Approval / Cascade / Implementation / Live) OR the `label` field (user-overridden display name) of one item in `cycle.stages`.** When a user has renamed stages via the `label:` override pattern (e.g., `name: "Discovery"`, `label: "Strategy Kickoff & Market Review"`), `current_stage` may use either form — the skill resolves both to the canonical key for behavior gating.
4. **Cross-section coherence**:
   - If `org.union_landscape` is set and `benchmark.cba_lookup_required_for` is empty, suggest auto-populating from union_landscape.
   - If `council.default_perspectives` includes `employee-union` but `org.union_landscape` is empty, warn — the persona has no labour-context to lean on.
   - If `council.perspective_overrides.<persona>.jurisdiction_focus` is unset for `employment-lawyer` or `dei-pay-equity`, default to `benchmark.scope_provinces`.
   - If `cycle.current_week_offset` is inconsistent with `cycle.current_stage`'s `weeks_offset` window (e.g., `current_stage` = "Final Approval" but `current_week_offset` = -12), surface a warning — one of them is stale.
   - If `cycle.this_cycle_goals.envelope_ceiling` is set, Phase 4 modeling must respect it as a hard constraint and flag any scenario that exceeds.
   - If `engagement_scope.budget_owner_role` references a banner/region that's not in `org.banner` or `benchmark.scope_provinces`, surface as a possible scope mismatch (not blocking).

Report parsed sections and gaps:

```
Loaded engagement config:
- engagement_scope: ✓ (Pharmacy FY26, owner: VP Ops Pharmacy)
- cycle: ✓ (FY26 May cohort, currently at "Strategy Kickoff & Market Review", week -10)  # canonical stage: Discovery — labelled per cycle.stages override
- org: ✓ (verified 2026-04-21, 0 days old)
- audience: ✓ (1 archetype: comp-committee, verified 2026-04-21)
- costing: ✓ (all 7 fields populated, verified 2026-04-21)
- benchmark: ⚠ stale (verified 2025-09-15, 218 days old)
- deck: ✗ not provided — will use skill defaults
- council: ✓ (mode: integrated, 6 perspectives, verified 2026-04-21)

Cycle context: 10 weeks before May 1 effective date. Last cycle: 3% ATB +
meat-cutter step compression fix (FY25, $3.8M). This cycle's primary
objective: close pharmacy assistant gap to P50, hold envelope under $4M.

Will skip: Beat 2 audience questions, Phase 4 costing input prompts, Council
persona-selection prompt.
Will prompt: deck preferences if audience differs from configured archetype.
```

---

## Output: end-of-engagement state file

At Phase 7 completion, the skill produces an `engagement-state-YYYY-MM-DD.yaml` file artifact. User saves it personally (corporate laptop, password manager, Obsidian — wherever). Track R-lite next year reads it alongside the prior PPTX for institutional context.

**Schema:**

```yaml
# engagement-state — produced at Phase 7 completion, saved by user
engagement:
  date: 2026-04-21
  client: "Acme Inc."
  cycle: "2026 annual comp review — Quebec retail"
  audience: comp-committee
  decision_sought: "Approve $4.2M scale lift for QC retail"
  scope:
    roles_count: 14
    geographies: [QC]
    pay_structures: [step]
    headcount_covered: 8400

findings:
  headline:
    - "QC retail top rate at 92% of market P50 — below market for fully qualified workers"
    - "Scale spread is 38% — narrow vs typical 40-60% range"
    - "Step 1 entry rate $0.45 above QC minimum wage — compression risk vs new-hire premium at competitors"
  do_nothing_cost: 1850000  # annual estimated turnover cost
  recommendation: "Scenario B — 2.5% scale lift + add top step"
  recommendation_cost: 4200000
  cost_breakdown:
    base_lift: 3100000
    top_step_addition: 580000
    roll_up_loaded: 4200000  # at 1.35 roll-up

scenarios_modeled:
  - id: A
    description: "1.5% scale lift across all classifications"
    annual_cost: 2500000
    risk_remaining: medium
  - id: B
    description: "2.5% scale lift + new top step at +3%"
    annual_cost: 4200000
    risk_remaining: low
    chosen: true
  - id: C
    description: "Move all classifications to P75 over 3 years"
    annual_cost: 8900000
    risk_remaining: minimal

selection_log:
  # Per-engagement record of A/B/C picks. Phase 4 appends one entry on scenario
  # selection (Checkpoint C). Phase 6b appends one entry per section on framing
  # selection. Future engagements with the same audience archetype + scope read
  # these entries to surface "in last N matching engagements you picked A 3× / B 2×"
  # instead of relying on a static recommendation. Until ledger persistence ships
  # (Batch B), this log accumulates within a single engagement only — cross-session
  # aggregation is the persistence layer's job.
  - phase: 4
    type: scenario
    audience_archetype: comp-committee
    options_presented: [A, B, C]
    picked: B
    picked_label: "2.5% scale lift + new top step at +3%"
    timestamp: 2026-04-21T13:55:00
  - phase: 6b
    type: section_framing
    section: findings
    audience_archetype: comp-committee
    options_presented: [A, B]
    option_a_label: "Lead with the gap"
    option_b_label: "Lead with the trend"
    picked: A
    timestamp: 2026-04-21T14:32:00
  - phase: 6b
    type: section_framing
    section: options
    audience_archetype: comp-committee
    options_presented: [A, B]
    option_a_label: "Do-nothing-first"
    option_b_label: "Recommendation-first"
    picked: B
    timestamp: 2026-04-21T14:38:00

tool_calls:
  # Append-only audit array — every external tool call (Market MCP, the claude.ai
  # Indeed connector, web_search, web_fetch) leaves a trace. Sub-fields per entry:
  # `tool` (full MCP-style name), `args`, `timestamp`, `result_hash` (SHA-256
  # of JSON response for MCP calls / fetched body for web_fetch / null for
  # web_search), `used_in` (list of slide/section IDs or deliverable surfaces).
  # Canonical container per references/tools-available.md § Container for tool_calls[].
  # Every tagged claim in the deck must trace to an entry here — auto-downgrade
  # fires on any tag without a matching entry.
  - tool: mcp__market__get_role_intelligence
    args: { role: "pharmacy assistant", province: "QC" }
    timestamp: 2026-04-21T13:10:00
    result_hash: a3f2c91d…
    used_in: [market_context, findings]
  - tool: mcp__market__get_cba_wage_scale
    args: { union: "UFCW 501", employer: "Acme", province: "QC" }
    timestamp: 2026-04-21T13:14:00
    result_hash: 7c91e4b1…
    used_in: [findings]
  - tool: web_fetch
    args: { url: "https://www.legisquebec.gouv.qc.ca/fr/document/lc/E-12.001" }
    timestamp: 2026-04-21T13:08:00
    result_hash: e4b1a3f2…
    used_in: [risk]

data_sources:
  # Roll-up summary derived from tool_calls[] — counts and last-pull dates only.
  # The detailed audit lives in tool_calls[] above.
  market_mcp:
    queries: 14
    role_id_direct: 11
    role_resolver: 3
    last_pull: 2026-04-20
  cba_lookups: ["TUAC 501 QC retail"]
  indeed_lookups: ["Loblaws (Provigo)", "Metro", "Walmart Canada"]
  uploaded_excel: "qc-retail-headcount-2026.xlsx"

assumptions_used:
  roll_up_factor: 1.38
  pay_attribution_pct: 0.35
  voluntary_turnover_pct: 0.22
  payroll_burden: 0.142

deliverables:
  pptx: "acme-qc-retail-2026-comp-review.pptx"
  xlsx: "acme-qc-retail-2026-cost-scenarios.xlsx"  # if generated
  csv: "acme-qc-retail-2026-market-data.csv"  # if generated

outcome:
  presented_date: null  # filled by user after meeting
  decision: null  # approved | partial | deferred | rejected
  approved_amount: null
  notes: null  # free text
  what_worked: null  # free text — for next cycle's lessons
  what_to_change: null  # free text — for next cycle's improvements

# `outcome` block is the highest-value field. User fills after the board meeting.
# R-lite next year reads this entire file plus the prior PPTX, pre-fills Track R discovery.
```

Naming convention: `engagement-state-YYYY-MM-DD-{client-slug}.yaml`. The skill suggests the filename; user saves to their preferred location.

---

## Output: council-state file (Track Council only)

When Track Council runs (standalone or integrated into an engagement), the skill produces a second state artifact: `council-state-YYYY-MM-DD-{client-slug}.yaml`. Full schema and generation discipline live in `references/council-mode.md` § "council-state output schema".

The two state files serve different purposes:

| File | Produced by | Captures | Read by |
|---|---|---|---|
| `engagement-state-*.yaml` | Phase 7 completion | Findings, scenarios modeled, data sources, assumptions used, post-meeting outcome | Next year's Track R-lite, future Track R |
| `council-state-*.yaml` | Council track completion | Question framing, perspectives run, persona positions with confidence-tag distribution, synthesis (consensus/tensions/unresolved), recommended path, integration feed-forward, post-decision outcome | Future council runs on the same client, Phase 4/5 of a downstream engagement |

When a council runs inside an engagement (integrated mode), both state files are produced. The engagement-state references the council-state via the `council_state_ref` field so the reasoning trail is reconstructable.
