# Costing Engine — Phase 4 (Option Modeling)

Loaded by SKILL.md when running Phase 4. Present 2-3 costed scenarios plus a do-nothing baseline. Each scenario is a distinct strategic direction, not just different dollar amounts. All costs in real dollars computed from uploaded Excel data using inline Python via code execution.

**Arithmetic discipline**: Never write a dollar figure in chat that wasn't produced by a code-execution call you can show. All scenario costs go through the Python sandbox. If code execution is unavailable, state that explicitly and present formulas only — do not compute inline.

**Multi-province discipline**: When the engagement spans 2+ provinces (`benchmark.scope_provinces`), every scenario cost is computed per-province first using that province's `roll_up_factor`, `payroll_burden_pct`, `voluntary_turnover_pct` from config (resolving map-form values per province, falling back to the `default` key when a province is absent). Per-province subtotals are reported alongside the national aggregate. Never collapse to a single national average — the differences compound and compress to misleading totals.

See `references/engagement-config-template.md` § Multi-province calculation for the aggregation pattern and per-province minimum-wage compression checks.

---

## Phase 4 Entry — Costing Inputs

Before modeling any scenarios, confirm the 7 costing inputs.

**Data upload — privacy and template requirements** (surface this at Phase 4 entry whenever the user has not yet uploaded workforce data):

> "Phase 4 needs your workforce data. **Use the CSV templates in `template_assets/wage_data_template_step.csv` and `wage_data_template_merit.csv`** — they contain the minimum columns the skill needs (job code, job title, location code, hourly rate / salary, weekly hours, experience hours or years in role) and intentionally exclude employee names, IDs, dates of birth, addresses, performance comments, and other PII.
>
> **Do not upload a raw HRIS export.** The skill will scan column names for disallowed fields and refuse to proceed if any are found — and by then the file is already in conversation context. The right time to filter is before export. See `template_assets/wage_data_template_README.md` for the column-by-column reference and the disallowed-fields list.
>
> Templates ready to use: step roles → `wage_data_template_step.csv`; salaried merit → `wage_data_template_merit.csv`; mixed workforce → both files separately."

If the user has already uploaded a file by the time Phase 4 starts, run the disallowed-fields scan before computing anything. See section § Disallowed-fields scan below.

**If `costing` section was loaded in Phase 0** (engagement-config provided):
- Use the loaded values directly. Do not re-prompt.
- For map-form values (e.g., `roll_up_factor: {QC: 1.38, ON: 1.32, default: 1.35}`), resolve per-province using `benchmark.scope_provinces`. Use the `default` key for any province missing from the map.
- Show the user a one-line confirmation listing the resolved per-province values:
  > "Using loaded costing config across 5 provinces: roll-up QC 1.38, ON 1.32, AB 1.30, BC 1.32, NS 1.30. Payroll burden QC 14.2%, ON 11.5%, AB 10.5%, BC 11.8%, NS 11.0%. Pay-attribution 35%, target P50. Proceeding to scenarios."
- If `last_verified` for the section is >180 days old, ask: "Costing config was last verified [N] days ago. Still accurate?"
- If any province in `scope_provinces` has no value in `provincial_minimum_wages`, prompt the user before continuing.

**Config-key precedence**: when the `costing` section is loaded from engagement-config (per `references/engagement-config-template.md` § costing), use the loaded values without prompting. Each of the 7 inputs below maps to a config field: roll-up → `costing.roll_up_factor` (single or per-province map), pay-attribution → `costing.pay_attribution_pct`, turnover → `costing.voluntary_turnover_pct`, replacement multipliers → `costing.replacement_multipliers` (per-level map), payroll burden → `costing.payroll_burden_pct` (per-province map), target percentile → `costing.target_percentile`, rounding → `costing.rounding`. If a single field is missing, prompt only for that field — do not re-ask the entire 7-input set.

**If no `costing` section was loaded at all**, prompt for the 7 inputs in one message before any scenario math:

```
Before I model scenarios, confirm 7 costing inputs (or accept defaults):
1. Roll-up factor (benefits/pension on base wage)? Default 1.0 — typical 1.30-1.40 for unionized retail.
2. Pay-attribution % for turnover? Default 0.35 (midpoint of Canadian/US survey range).
3. Voluntary turnover rate %? Default 0.15 if no actuals.
4. Replacement multipliers (% of salary): hourly 18%, professional 55%, mgmt 125%, exec 180%. Override?
5. Payroll burden % for [province from Phase 1]? Default QC 13.5%, ON 11.5%, other 12%.
6. Target market percentile? Default P50.
7. Rounding: per-role $100, aggregate $1K. OK?
```

Capture answers, hold in conversation context, reuse across all 4.1-4.7 calculations. If the user wants to save these for next time, suggest: "If you'll model costs for this org regularly, run `/init` to bake these into a reusable engagement-config."

---

## Disallowed-fields scan (mandatory before any data parse)

Whenever the user uploads `.csv` or `.xlsx` workforce data for Phase 4, scan column names against the disallowed-fields list **before** parsing rows. If any disallowed field is detected, refuse to proceed.

**Disallowed field detection** — match column names case-insensitively against this list (substring or regex match — "Employee Name", "First Name", "Worker ID" all hit):

```
Employee ID, Worker ID, Person ID, User ID, Login, Username, Badge Number, SIN, NAS, SSN, Tax ID
Employee Name, First Name, Last Name, Preferred Name, Display Name, Full Name
Date of Birth, DOB, Birth Date, Hire Date, Original Hire Date, Termination Date, Last Day Worked, Service Date
Email, Personal Email, Work Email, Phone, Mobile, Home Phone
Address, Street, Postal Code, ZIP, Home Address, Mailing Address
Manager, Manager ID, Manager Name, Reports To, Direct Reports, Supervisor
Performance Rating, Rating Description, Last Review Date, Manager Comments, Review Comments
Bonus History, Salary History, Last Increase Date, Last Increase Amount, Pay History
Disability Status, Accommodation Notes, Leave Status, Leave Reason, Medical
Gender, Sex, Ethnicity, Race, Self-ID, Veteran Status, Indigenous, Marital Status
Banking, Account Number, Routing Number, Direct Deposit
Participating Company, Reporter, Submitted By, Source Company, Company ID
```

The last line covers survey-house exports (Mercer, WTW, Korn Ferry, etc.) — these vendors often include participating-company columns that identify which competitors submitted data. Strip via the survey vendor's anonymized-export option before upload. See `references/survey-house-protocol.md` for the full survey ingestion workflow.

**Refusal pattern** when disallowed fields are detected:

> "I detected one or more PII columns in your upload: [list of detected columns]. The skill cannot proceed with this file because the data is already in our conversation context — re-uploading a clean version doesn't undo the original exposure.
>
> Two things to do:
>
> 1. **Right now:** delete this conversation and start a new one. Don't continue here.
> 2. **Before next upload:** re-export your data using `template_assets/wage_data_template_step.csv` (for step roles) or `wage_data_template_merit.csv` (for salaried merit roles). The README in the same folder explains exactly which columns to keep and which to drop.
>
> Sorry for the friction. Privacy is one of the few things the skill enforces hard rather than nudges."

After surfacing the refusal, do not parse any of the file's rows — even though they're technically already in context, do not display, summarize, or compute against them. Treat the file as if it doesn't exist for the rest of the conversation.

**If the user insists on proceeding** ("just go ahead, this is fine"): do not proceed. The privacy rule is one of the few hard rules in the skill. The right escalation is the user starting a new conversation with a clean file. Surface that calmly and stop. Note: this is the skill's strictest behavior — it does not relax under pressure or for "just this once" framing.

**No disallowed fields detected — column-template match check:**

If column names match one of the canonical templates exactly (`wage_data_template_step.csv` or `wage_data_template_merit.csv` columns), skip the column-mapping prompt entirely and confirm:

> "Recognized step-rate template — 16 rows, 3 classifications across 2 locations. Proceeding to Phase 4 costing."

If column names don't match a template but no disallowed fields are present, fall back to the legacy column-mapping behavior in `references/consulting-protocol.md` § Phase 2.2a — slower, more error-prone, but functional.

---

## 4.0 Mandatory Cost Floor (compute first, before any scenario)

Every step-rate engagement starts with a **mandatory cost floor** — the spend that happens regardless of any strategic decision. VP Ops doesn't have agency over this, but it has to be in the conversation, because it changes what "doing nothing" actually costs and reframes what fraction of any scenario is discretionary.

The skill computes two components by default:

1. **Statutory minimum-wage compliance** — when provincial minimum wage rises above the current step 1 rate, step 1 must move. The user decides whether the increase cascades up the scale (every step shifts up to maintain spread) or stops at step 1 only (typically followed by compression remediation later). The skill asks this once at Phase 4 entry.
2. **Normal step progression** — employees advancing from step N to step N+1 at their next anniversary or hours-worked threshold. Contractual under CBAs, policy under non-union scales. Happens whether you do nothing or take the most aggressive scenario.

CBA-mandated annual increases (already-negotiated locked-in lifts) and prior-cycle phased rollouts (phase 2+ of multi-year prior decisions) are **not** rolled into the mandatory floor by default — they live separately:
- CBA-locked increases surface via `get_cba_wage_scale` in section 4.2.
- Prior phased rollouts surface via `cycle.last_cycle.deferred_items` and Phase 3 drift detection.

Treating them separately means the floor stays clean and interpretable; bundling everything would obscure which costs come from which decision.

### Phase 4 entry — the cascade question

When the engagement has step roles in scope (any role with `pay_structure = step`), determine the cascade behavior in this priority order:

1. **`costing.minimum_wage_treatment` config value** — if set to `cascade` or `step_1_only`, use it without prompting and surface the choice in chat: "Using configured minimum-wage treatment: cascade (every step shifts up to maintain spread)."
2. **`ask_per_engagement` (config default if unset)** — prompt the user.

When prompting, use this pattern:

> "Before I model scenarios, one cost-floor question: when statutory minimum wage forces step 1 up [for any province in scope where the new minimum wage exceeds your current step 1], do we **cascade** the increase up the scale (every step shifts up by the same amount or %, maintaining spread) or **lift step 1 only** (knowing this compresses the scale and likely needs a remediation slide later)?
>
> Defaults vary by banner — some banners historically cascade; others have done both. Check your config or your VP Ops preference."

Capture the answer; reuse for the rest of Phase 4. If the engagement spans multiple provinces and the user wants different behavior per province, accept that and note it. Suggest at engagement end: "Want me to add `costing.minimum_wage_treatment: cascade` to your config so you don't get asked next time?"

### Statutory minimum-wage compliance — formula

For each province `p` in `benchmark.scope_provinces`:

```python
new_min_wage = benchmark.provincial_minimum_wages[p].rate  # already in config
current_step_1 = current_scale[p].step_rates[0]

if new_min_wage > current_step_1:
    delta = new_min_wage - current_step_1
    if cascade:
        # Every step shifts up by delta
        min_wage_compliance_cost[p] = sum(
            delta * headcount_at_step[s] * annual_hours
            for s in range(num_steps)
        ) * roll_up_factor[p]
    else:  # step_1_only
        min_wage_compliance_cost[p] = (
            delta * headcount_at_step[0] * annual_hours
        ) * roll_up_factor[p]
        # Flag compression: post-move spread = (top_rate - new_min_wage) / new_min_wage
        # Surface remediation cost estimate: typically 0.5-1.5% of payroll
else:
    min_wage_compliance_cost[p] = 0  # no statutory pressure
```

Apply effective-date proration if the minimum-wage effective date differs from the wage scale effective date: `cost * (months_in_effect / 12)`.

### Normal step progression — formula

Step progression is governed by the time-or-hours-worked threshold per scale. For UFCW grocery this is typically 1,040 hours per step for part-time workers and 12 months for full-time. Configure per scale.

For each role and province:

```python
# For each employee currently at step N, project their advance during the cost period
for employee in step_workforce:
    if employee.hours_to_next_step <= effective_period_hours:
        delta_rate = scale[employee.classification].step_rates[employee.current_step + 1] \
                   - scale[employee.classification].step_rates[employee.current_step]
        progression_cost += delta_rate * employee.annual_hours_remaining_in_period * roll_up_factor[province]
```

If individual progression timing isn't available (just headcount per step), use a uniform approximation:

```python
# Assume employees are evenly distributed across "time to next step"
# So 1/N of them advance during a 12-month period (where N = avg months/step)
avg_months_per_step = 12  # or 24, or per-scale config
fraction_advancing = 12 / avg_months_per_step

for step in range(num_steps - 1):  # top step doesn't advance
    delta_rate = step_rates[step + 1] - step_rates[step]
    progression_cost += (
        delta_rate
        * headcount_at_step[step]
        * fraction_advancing
        * annual_hours
        * roll_up_factor[province]
    )
```

Tag the result with `[ESTIMATED]` when using the uniform approximation; `[EXACT]` when individual progression timing is in the data.

### Mandatory floor total

```python
mandatory_floor[province] = (
    min_wage_compliance_cost[province]
    + normal_step_progression_cost[province]
)

mandatory_floor_national = sum(mandatory_floor.values())
```

### Presentation in chat (aggregated, not split)

In chat during Phase 4, present the floor as a single total — do not split min-wage vs progression line items in conversation:

> "Mandatory cost floor for the May cohort, all provinces: ~$1.2M. This is what your wage scale will cost regardless of any strategic decision — minimum-wage compliance + normal step progression. Scenarios below add discretionary spend on top of this."

The detailed breakdown (per-province, by component, with cascade/step-1-only rationale) lives on deck slides only — see Phase 6 stage-keyed spines for the dedicated "Mandatory Cost Floor" slide structure.

### Why this section exists separately from 4.1 (Do-Nothing Baseline)

The do-nothing baseline in section 4.1 captures the **cost of not closing the market gap** (turnover-driven). The mandatory floor in 4.0 captures the **cost of legally and contractually running the existing scale**. These are different categories and conflating them obscures the real strategic question:

- 4.0 asks: "what's the locked-in spend for this cycle?" (no agency)
- 4.1 asks: "what does the market gap cost us if we don't act?" (some agency — you can act on it or not)
- 4.2-4.4 ask: "what discretionary moves close the gap?" (full agency)

The Options Review conversation with VP Ops is about 4.2-4.4. The Final Approval conversation is about confirming the discretionary spend on top of 4.0.

---

## 4.1 Do-Nothing Baseline

Always present the do-nothing baseline first. It reframes investment scenarios as "cost of fixing" vs. "cost of not fixing."

**Formula:**
```python
do_nothing_cost = sum(
    turnover_rate * headcount * 0.35 * replacement_multiplier * annual_salary
    for each below-market role
)
```

**Replacement cost multipliers:**

When `costing.replacement_multipliers` is set in engagement-config (per `references/engagement-config-template.md` § costing — per-level map: `hourly`, `professional`, `management`, `executive`, `unknown`), use those values without prompting. Otherwise apply the defaults below:

| Role Level | Multiplier |
|---|---|
| Entry-level / hourly | 16-20% of annual salary |
| Professional / technical | 50-60% |
| Management | 100-150% |
| Executive / senior leadership | 150-213% |
| Unknown level (default) | 50% |

**Pay-attribution heuristic**: 35% of voluntary turnover is attributable to below-market pay. This is the midpoint of the 31-37% range from Canadian and US survey data. If the user provides actual turnover data, use it instead of the 15% default voluntary rate.

**Presentation pattern:**
"Before we look at options — doing nothing isn't free. With [X] roles below market and [Y]% average gap, the estimated annual cost of pay-attributable turnover is ~$[Z]K. That's [N] replacements per year at [average multiplier]% of salary, with about a third of voluntary exits tied to pay."

If turnover data unavailable and no role-level classification: present qualitatively instead of fabricating numbers.

---

## 4.2 Step-Rate Scenarios (discretionary lifts above the mandatory floor)

When the workforce (or segment) has `pay_structure = step`, present scenarios from this menu. **Every scenario cost is computed as a discretionary lift on top of the mandatory floor from section 4.0** — not as a standalone total. Skill computes both numbers, surfaces the total in chat as a single aggregated figure, but separates floor and lift on the side-by-side comparison (4.7) and the deck cost slides.

**Config-key precedence applies throughout this section.** Roll-up factor → `costing.roll_up_factor` (single OR per-province map per `references/engagement-config-template.md` § costing); payroll burden for the side-by-side and the cost-slide caveat → `costing.payroll_burden_pct` (per-province map); target percentile for the compa-ratio readout → `costing.target_percentile`; rounding for chat figures and per-row deck values → `costing.rounding`. Do not prompt for any of these when the engagement-config provides them; only prompt for the per-scenario lift parameters (lift %, lift $, top-step increment, etc.) — those are decision inputs, not calibration constants.

In Phase 4 chat presentation, the pattern is:

> "Scenario A — 2% scale lift across all classifications: ~$2.8M total ($1.2M mandatory floor + $1.6M discretionary lift). Closes the entry-rate gap to P25 in QC and ON."

Not:

> "Scenario A: $1.6M" (this would mislead — VP Ops thinks the choice is $1.6M when the actual cost showing up in payroll is $2.8M).

And not:

> "Scenario A — mandatory floor: $1.2M (min wage $0.4M + step progression $0.8M); discretionary lift: $1.6M; total $2.8M…" (this is too much for chat — the breakdown belongs on the deck cost slides, not in conversation).

**CBA anchor (mandatory for unionized step scales):** Before presenting scenarios, call `get_cba_wage_scale(role, province)` to retrieve the negotiated scale (UFCW grocery, construction, healthcare, public sector). Surface the negotiated scale alongside the user's actual scale — gaps between negotiated floor and actual rates change the cost equation, and any scenario that pushes rates below the CBA floor is non-viable. CBA-locked annual increases (already negotiated for the agreement term) are surfaced here as a **separate line** alongside the mandatory floor — they're locked but conceptually different from minimum-wage compliance and step progression. If multiple CBAs apply (multi-province, multi-banner), pull each.

The five discretionary scenario types:

**Scale Lift %**: Apply X% to every rate at every step in every classification.
```python
discretionary_lift = sum(
    (rate * lift_pct) * headcount_at_step * annual_hours * roll_up_factor
    for each step in each classification
)
total_scenario_cost = mandatory_floor + discretionary_lift
```
Note: percentage increases widen absolute dollar gap between top and bottom of scale.

**Scale Lift $**: Apply flat $X to every rate at every step. Same formula with `delta = lift_dollar`. Dollar increases compress the scale spread.

**Add Top Step**: New step rate = existing top rate × (1 + step_increment_pct), typically 2-5% above current top.
```python
discretionary_lift = (new_top_rate - current_top_rate) * headcount_at_current_top * annual_hours * roll_up_factor
total_scenario_cost = mandatory_floor + discretionary_lift
```
Report compression check: `top_rate / bottom_rate` before and after. Adding a top step without adjusting lower steps narrows percentage spread.

**Compress Steps**: Reduce number of steps or narrow spread.
```python
discretionary_lift_year_1 = sum(
    (new_mapped_rate - current_rate) * affected_headcount * annual_hours * roll_up_factor
)
```
Also model structural cost: fewer steps = faster progression to top = permanently higher mandatory floor at years 2, 3, 5. Show year 1 and structural cost separately on the deck cost slide.

**Accelerate Progression**: Reduce hours or months required per step advance. This scenario is unusual — it doesn't add a discretionary lift on top of the floor; it inflates the floor itself by speeding up the normal-progression component. Model immediate cost (employees who now qualify for advance) and structural cost at years 1, 3, 5. For UFCW grocery, hours-worked thresholds (typically 1,040 hrs/step) control progression velocity — PT workers affected more than FT.

**Lump Sums and One-Time Payments** (added scenario type — purely discretionary, no floor interaction):
```python
discretionary_lift = lump_sum_amount * eligible_headcount * roll_up_factor  # if pensionable
```
If the lump sum is non-pensionable (typical for retention bonuses, signing bonuses), `roll_up_factor = 1.0` for that line — no benefits ride on it. Note this on the cost slide. Lump sums don't compound across years; flag this when comparing against scale-lift scenarios that *do* compound.

All step scenarios report:
- Total cost (mandatory floor + discretionary lift) — what shows up in payroll
- Discretionary lift only — what VP Ops actually has agency over
- Resulting top-rate compa-ratio vs. market P50
- Per-province breakdown when multi-province

Apply roll-up factor to all base wage increases. Apply effective-date proration: `cost * (effective_months / 12)` for mid-year implementations.

---

## 4.3 Merit-Based Scenarios

When the workforce (or segment) has `pay_structure = merit`, present scenarios from this menu.

**Config-key precedence**: target percentile for the band-vs-market comparison → `costing.target_percentile` (per `references/engagement-config-template.md` § costing); benchmark percentile set used to anchor band positioning → `benchmark.default_percentiles` (`[10, 25, 50, 75, 90]` is the load-bearing default — never silently subset to `[25, 50, 75]`); peer-set anchor for compa-ratio sanity check → `benchmark.peer_companies`; aging rule when bands were last set more than 12 months ago → `benchmark.aging_rule`. Do not prompt for any of these when the engagement-config provides them.

**Move to Midpoint**: Floor adjustment — only below-midpoint employees generate cost.
```python
cost = sum(max(0, band_mid - salary) * headcount for each employee/role)
```
Above-midpoint employees: $0. Red-circle employees (above band max): excluded, handled separately.

**Merit Matrix**: Build a performance × compa-ratio quartile matrix.
```python
total_merit_cost = sum(salary_i * matrix[perf_i][quartile_i] for each employee)
budget_pct = total_merit_cost / total_payroll * 100
```
Quartile assignment: Q1 (<0.90 CR), Q2 (0.90-1.00), Q3 (1.00-1.10), Q4 (>=1.10).
Compare resulting budget % to benchmark (3.5-4.2% typical 2025 merit pool). If weighted average exceeds approved budget, report overage and suggest which cells to reduce.

When individual data unavailable, use normal distribution approximation (CR mean=1.0, sigma=0.09) to estimate quartile fractions. Flag as `[ESTIMATED - distribution approximation]`.

**Band Restructure**: New min/mid/max per grade.
```python
green_circle_cost = sum(max(0, new_min - salary) * headcount)  # below new minimum
red_circle_lump = sum(salary * merit_pct * headcount)           # above new maximum
compression_remediation = total_payroll * 0.005 to 0.015        # separate from merit pool
total = green_circle_cost + red_circle_lump + merit_pool_for_in_range + compression_remediation
```
Present red-circle handling options: (a) freeze salary until band catches up, (b) lump-sum in lieu of merit, (c) phase with accelerated merit. Note retention risk for freeze approach.

Detect compression: flag when `avg_CR(0-2yr cohort) > avg_CR(3-5yr cohort)` for same role/grade. Remediation budget: 0.5-1.5% of payroll depending on severity, separate from merit pool.

---

## 4.4 Universal Scenarios

**Cost-to-Target-Percentile**: For any pay structure.
```python
gap_per_employee = max(0, market_target_percentile - current_pay)
annual_gap = gap_per_employee * annual_hours  # if hourly; as-is if salaried
role_cost = annual_gap * headcount
```
Interpolate percentiles when exact target not in source data: `P60 = P50 + (P75 - P50) * (60-50)/(75-50)`.

---

## 4.5 Mixed Workforce Handling

When the Excel contains both step and merit-based roles:
- Present separate scenario sets by pay_structure. Step roles get step scenarios; merit roles get merit scenarios.
- Cost each set independently.
- Present a combined total: "Step-rate adjustments: $[X]K. Salaried adjustments: $[Y]K. Combined annual investment: $[Z]K."
- The do-nothing baseline is also split by pay_structure, then combined.
- Never apply compa-ratio/merit-matrix logic to step rows. Never apply step-progression cost to merit-range rows. If the user requests a cross-structure scenario, warn and redirect to the appropriate alternative.

---

## 4.6 Costing Computation Details

**Annualization**: hourly rate × weekly_hours × 52; salary as-is.

**Roll-up factor**: Multiply base wage increase by roll_up_factor (total benefit costs / straight-time wages). A roll-up of 1.35 means every $1 base increase costs $1.35 total (overtime premiums, holiday pay, vacation pay, pension, benefits riding on base rate). Apply to all step base wage increases. Ask once for the value and reuse.

**Rounding**: Per-role amounts to nearest $100. Aggregates to nearest $1,000. Percentages to one decimal. Compa-ratios to two decimals.

**Confidence tagging**: Tag every data point: `[EXACT]` (from uploaded data), `[MATCHED]` (direct market match), `[PROXY]` (related role), `[ESTIMATED]` (assumption-based), `[USER-PROVIDED]` (stated in conversation). State the proportion of EXACT+MATCHED vs. PROXY+ESTIMATED in aggregate figures.

**Assumptions section**: Include in every cost output: hours/year, benefits loading, roll-up factor, aging factor, replacement cost multipliers, pay-attributable turnover fraction, market benchmark anchor (top rate for step, midpoint for merit).

**Payroll tax caveat**: Pull the actual per-province burden % from `costing.payroll_burden_pct` (loaded from engagement-config). Include in every scenario output:

- **Single-province engagement**: "Costs shown are base wage increases. Employer payroll burden adds [X]% in [province] (CPP/QPP, EI, [QPIP if QC], EHT/HSF, WSIB/CNESST)."
- **Multi-province engagement**: per-province line items, then a national aggregate line:
  > "Costs shown are base wage increases. Employer payroll burden by province: QC 14.2%, ON 11.5%, AB 10.5%, BC 11.8%, NS 11.0%. National aggregate burden: $517K on top of $4.2M base = $4.72M total employer cost."
- **Province with no config value**: "Costs shown are base wage increases. Employer payroll burden for [province] not configured — verify before citing total cost on slides."

Always cite the source: `[CONFIG: payroll_burden_pct, last_verified YYYY-MM-DD]`. Place on the methodology/assumptions slide AND as a footnote on the first costing slide.

---

## 4.7 Scenario Presentation

Present all scenarios in a single message as a comparison. Use a compact format showing for each scenario: total annual cost, per-role breakdown, what it fixes, risk remaining, and narrative angle.

After presenting, offer blending: "Which direction? Or a blend — like Scenario A for warehouse roles + Scenario C for management?"

**Side-by-side comparison table** — this is where the mandatory-floor vs. discretionary-lift split becomes visible. In chat (Phase 4), the totals stay aggregated; the split only appears here and on cost slides.

**Multi-province framing**: when `benchmark.scope_provinces` has 2+ provinces, the per-province subtotals (computed earlier in §§ 4.0–4.6) MUST already have been surfaced before this comparison table appears. The "National total" row below is the rollup of those per-province lines — never present this row in a multi-province engagement without the per-province subtotals visible above it. The rule from § 1 ("Never collapse to a single national average") applies here: this table is acceptable because it follows the per-province breakdown, not in place of it.

| | Do Nothing | Scenario A | Scenario B | Scenario C |
|---|---|---|---|---|
| **Mandatory floor** (min wage + step progression) | $1.2M | $1.2M | $1.2M | $1.2M |
| **CBA-locked annual increase** (if applicable) | $0.4M | $0.4M | $0.4M | $0.4M |
| **Discretionary lift** | $0 | $1.6M | $2.4M | $3.6M |
| **National total** (sum of per-province lines) | $1.6M | $3.2M | $4.0M | $5.2M |
| **% of total that is discretionary** | 0% | 50% | 60% | 69% |
| **Cost of inaction** (turnover from market gap) | $X | reduced by Y% | reduced by Z% | reduced by W% |
| Roles fixed | 0 | N | M | P |
| % of gap closed | 0% | X% | Y% | Z% |
| Risk remaining | High | Medium | Low | Minimal |
| Best for audience | — | "Budget-conscious board" | "Full alignment" | "Talent investment" |

The "% of total that is discretionary" row is the most important callout for the VP Ops conversation — it shows what fraction of the spend is actually a strategic choice. A scenario that's 70% mandatory and 30% discretionary is a different conversation from one that's 30% mandatory and 70% discretionary, even if the totals match.

**Handling partial data:** If no headcount, present in percentage terms with a note that dollar figures require headcount. If some roles unmatched, note which are excluded.

**Checkpoint C**: "Which direction (or blend) for the deck?" Block Phase 5 until confirmed.

**On user pick**: append a `selection_log` entry to the in-memory engagement state with `phase: 4`, `type: scenario`, the options presented (e.g., `[A, B, C]`), the audience archetype, the pick (or blend specification), and the timestamp. Phase 7 emits the full `selection_log` in the engagement-state YAML. See `references/engagement-config-template.md` § Output: end-of-engagement state file for the schema.

**Auto-checkpoint on Checkpoint C confirmation**: write/update `engagements/<slug>/checkpoint.yaml` via Google Drive (Claude.ai connector) per `references/persistence-and-ledger.md` § /checkpoint command. Set `saved_at_phase: 4`, capture `scenario_chosen` (with mandatory floor + discretionary lift breakdown), the running `tool_calls[]` array (canonical container per `references/tools-available.md` § Container for tool_calls[]), and the freshly-appended `selection_log` array. Silent unless write fails.

**Phase 4 output**: User's chosen scenario direction (or blend specification), with mandatory floor and discretionary lift computed separately for downstream slide generation.
