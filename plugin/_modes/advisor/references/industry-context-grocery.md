# Industry Context — Canadian Grocery

Loaded by SKILL.md at Phase 0 when the loaded engagement-config has `org.industry: grocery` (or when the user's first message clearly indicates grocery sector context). Generic Canadian grocery industry knowledge — employer landscape, role families, union mapping, peer sets, compression patterns.

**Scope:** public/general industry information. Company-specific governance, audience beliefs, and prior-cycle context belong in the user's personal `engagement-config.yaml` `org` and `audience` sections — those don't ship with this skill.

**Verify before citing:** wage minimums and union local numbers change. Web-search the latest values when surfacing them on slides.

---

## Canadian grocery employer landscape

| Employer | Banners | National scale (approx FTE) | Footprint | Union posture |
|----------|---------|----------------------------|-----------|----------------|
| Loblaw Companies | Loblaws, Provigo, No Frills, Real Canadian Superstore, Shoppers Drug Mart, Maxi, T&T | ~220,000 | National | Mixed; Provigo/Maxi unionized in QC (TUAC), Loblaws/Superstore unionized in many provinces (UFCW) |
| Empire Company (Sobeys) | Sobeys, IGA, FreshCo, Foodland, Safeway, Lawtons, Voilà, Compliments | ~125,000 | National | Mixed; QC unionized (TUAC 501), Atlantic and Western mixed |
| Metro Inc. | Metro, Super C, Adonis, Food Basics, Jean Coutu, Brunet | ~95,000 | QC + ON | QC heavily unionized (TUAC), ON mixed (UFCW where unionized) |
| Walmart Canada | Walmart, Walmart Supercentre | ~100,000 | National | Generally non-union; one Quebec store unionized historically |
| Costco Wholesale Canada | Costco | ~50,000 | National | Non-union |
| Pattison Food Group | Save-On-Foods, Buy-Low Foods, PriceSmart Foods, Urban Fare | ~30,000 | Western Canada | Mixed; UFCW Local 1518 in BC |
| Federated Co-operatives | Co-op grocery banners | ~30,000 | Western Canada | Member-owned co-op, mixed union |
| Longo's | Longo's, Grocery Gateway | ~6,000 | ON (GTA) | Non-union |

**Standard peer set for benchmarking** (when client is one of the Big 5, exclude self): Loblaws, Sobeys, Metro, Walmart Canada, Costco. Add regional players when relevant (Save-On-Foods for Western Canada, Longo's for GTA specialty, Federated Co-op for Western co-op context).

---

## Standard role families

### Store-level hourly

| Family | Common titles | Typical structure | Notes |
|--------|---------------|-------------------|-------|
| Front end | Cashier, Customer Service Rep, Self-Checkout Attendant | Step | Highest headcount per store |
| Service counters | Deli Associate, Seafood Clerk, Meat Counter Clerk, Cheese Specialist | Step | Higher entry rate than front end |
| Specialized trades | Meat Cutter, Butcher, Baker, Cake Decorator, Pastry Chef, Sushi Chef | Step + premium | Hard-to-fill; market premium common |
| Pharmacy support | Pharmacy Assistant, Pharmacy Technician | Step | Pharmacist-supervised; technician usually licensed |
| Stocking / receiving | Grocery Clerk, Night Stocker, Receiver, Forklift Operator | Step | Overnight shift premiums common |
| Produce | Produce Clerk, Produce Manager | Step | Department-manager bridge role |

### Store management

| Family | Common titles | Typical structure | Notes |
|--------|---------------|-------------------|-------|
| Department head | Department Manager (Bakery, Meat, Produce, Front End, Grocery, Deli) | Salary band or merit | Compression vs top hourly rate is common pain point |
| Store leadership | Assistant Store Manager, Store Manager | Salary band + bonus | Often outside CBA scope; merit-based |
| Specialty leadership | Pharmacy Manager, Bakery Manager (large stores) | Salary band | Pharmacy Manager almost always pharmacist-licensed |

### Distribution / DC

| Family | Common titles | Typical structure | Notes |
|--------|---------------|-------------------|-------|
| Warehouse | Warehouse Worker, Order Selector, Picker | Step | DCs increasingly compete with Amazon/Costco DC market |
| Equipment operators | Forklift Operator, Reach Truck Operator, Pallet Jack Operator | Step + endorsement premium | Certification-gated |
| DC supervision | DC Supervisor, Shift Lead, DC Operations Manager | Salary band + bonus | Bridges hourly and corporate |

### Corporate / head office

| Family | Common titles | Typical structure | Notes |
|--------|---------------|-------------------|-------|
| Operations support | Category Manager, Pricing Analyst, Replenishment Analyst | Merit (broad band) | Usually national or regional |
| Functional | Finance, HR, IT, Marketing, Supply Chain | Merit | National peer set, not retail peer set |
| Executive | VP, SVP, EVP, C-suite | Salary + STI + LTI | Total rewards comparison required |

---

## Union landscape

### UFCW Canada locals (most common in grocery)

| Local | Region | Notable employers covered |
|-------|--------|--------------------------|
| Local 175 / 633 | Ontario | Sobeys, Loblaws, Metro, FreshCo |
| Local 1006A | Ontario (some) | Loblaws, regional |
| Local 401 | Alberta | Sobeys, Safeway (under Sobeys), regional |
| Local 1518 | British Columbia | Save-On-Foods, Loblaws, Sobeys |
| Local 832 | Manitoba | Sobeys, Safeway |
| Local 247 | British Columbia (other) | Coca-Cola, regional grocery |

### TUAC (Travailleurs et travailleuses unis de l'alimentation et du commerce — UFCW Quebec)

| Local | Notable employers |
|-------|-------------------|
| Local 500 | Loblaws/Provigo, Maxi |
| Local 501 | Sobeys/IGA QC retail |
| Local 503 | Metro QC |
| FTQ-affiliated | Various smaller chains |

### Bargaining patterns common in grocery

- **Cycle:** 3-year agreements typical; 4-year increasingly common
- **Step progression:** hours-worked thresholds (1,040 hrs/step UFCW grocery is canonical); QC sometimes uses calendar-month thresholds
- **Wage scale anchor:** entry rate set at provincial minimum wage + premium ($0.25-$1.50 above), top rate negotiated
- **COLA:** present in some Quebec contracts; uncommon in ROC
- **Pension:** defined-benefit legacy in some longstanding shops (UFCW Multi-Employer Pension Plan); defined-contribution in newer shops
- **Premiums:** overnight, weekend, statutory holiday — typical $0.50-$2.00/hr or 1.5x rate
- **PT/FT ratio caps:** some contracts cap PT % to protect FT hours
- **Non-union departments:** pharmacy and store management commonly carved out

---

## Provincial minimum wages

Minimum wages decay fast — they change at least once per province per year and are not hardcoded in this skill. Source the values from the user's engagement-config under `benchmark.provincial_minimum_wages`, OR web-search the current value from the relevant provincial labour ministry before citing on slides.

If a province is in scope and no value is in the config, prompt the user OR fetch via web search and tag `[USER-PROVIDED]` or `[WEB-VERIFIED with date]` accordingly. Never guess — entry-rate-vs-minimum-wage compression is a high-impact slide call.

Schema reference: `references/engagement-config-template.md` § benchmark.

---

## Industry-specific Phase 1 audience archetypes

These are starting points the user can refine via their engagement-config `audience` section.

### Grocery board / comp committee

- **Beliefs:** "Labour costs are already high relative to margin. We pay competitively for store-level."
- **Typical objections:** ROI per dollar; how does this compare to last year's comp investment outcome; what's the union exposure if we don't.
- **Preferred framing:** risk-first; cost-of-inaction (do-nothing baseline) is the strongest opening; phase implementation to spread budget.
- **Slide count:** 6-10. Strategic; minimal methodology.

### Retail CHRO / VP HR

- **Beliefs:** Mixed — knows pain points by department; usually believes hourly is the gap, salary is fine.
- **Typical objections:** Where's the budget; what does this do to manager pay differential; how do we sequence with bargaining cycle.
- **Preferred framing:** Strategy with options; show 2-3 scenarios with tradeoffs; flag bargaining-cycle timing.
- **Slide count:** 12-18. Methodology + recommendation.

### Store operations HR / comp team

- **Beliefs:** Implementation reality matters most; manager pushback on individual decisions is common.
- **Typical objections:** Can we explain this to managers; will this widen vs narrow compression at department-head level; how do we communicate to staff.
- **Preferred framing:** Implementation detail; manager talking-points; communication plan.
- **Slide count:** 20-30. Full data tables, methodology, FAQ.

### Union bargaining team (employer-side)

- **Beliefs:** Need to predict union ask; benchmark vs CBA peer set, not just market.
- **Typical objections:** What are we offering vs what union will demand; how does this position us in mediation/arbitration.
- **Preferred framing:** CBA-anchored comparison; market data as context not determinant.
- **Slide count:** 8-15. CBA tables prominent.

---

## Pay philosophy patterns common in grocery

| Stance | Implication |
|--------|-------------|
| **P50 with retention premium for hard-to-fill** | Default for most grocers. Hard-to-fill = meat cutter, baker, pharmacy, sushi chef. P50 anchor for general; P75 for premium roles. |
| **Match-CBA for union floor** | CBA scale is the floor; non-union departments (pharmacy, management) compared separately to market. |
| **Lead market for management, lag for hourly** | Common stance: pay management above market to retain leadership pipeline; hourly at market or slightly below. |
| **National parity vs provincial market** | Some grocers pay national-uniform (creates perceived inequity in high-cost provinces); others pay provincial-market. Affects framing of QC vs ON gaps. |

---

## Common compression issues in grocery

1. **Entry-rate-to-minimum-wage compression**
   - Entry step set at $0.50-$1.00 above provincial minimum at last bargaining
   - Minimum wage rises annually; entry premium erodes
   - Within 1-2 years, entry step is at minimum wage — hiring becomes a problem
   - Remediation: scale lift % or scale lift $; add new step 1

2. **Top-rate compression for long-tenured workers**
   - Long-tenured employees max out at top step with no further progression
   - "Add top step" scenario addresses; common ask in bargaining

3. **Department-head-vs-top-hourly compression**
   - Department managers earning <10% above top hourly rate after CBA increases
   - Reduces career-path appeal for hourly workers
   - Remediation: salary band restructure for management

4. **Pharmacy compression**
   - Pharmacy Assistant rates rising due to provincial pharmacy support staff demand
   - Pharmacy Manager pay (salaried) lags hourly + premium combinations of senior assistants
   - Remediation: separate band review for pharmacy supervision

5. **Distribution center wage competition**
   - DC wages historically anchored to retail
   - Amazon/Costco DC market now competing — $22-$28/hr entry common in major markets
   - Retail-anchored DC wages becoming uncompetitive
   - Remediation: DC-specific scale separate from retail

---

## Industry-specific data source notes

- **Statistics Canada NAICS 4451** (Food & Beverage Stores) — useful for industry-level wage trends
- **Loblaws / Sobeys / Metro public reporting** (annual reports, 10-K equivalents) — discloses aggregate workforce stats; rarely role-level wage data
- **Retail Council of Canada** — industry benchmarks (mostly aggregated, paywall)
- **Provincial labour ministries** — minimum wage, public-sector grocery DC wages where applicable
- **CBA databases** — Quebec ministry of labour publishes some agreements; UFCW posts ratified contracts; Local 175 posts ON wage scales

---

## When this file applies

Loaded automatically when:
- `org.industry: grocery` is set in engagement-config, OR
- User's first message clearly references grocery context (banner names, UFCW grocery, "store-level pay", etc.)

Not loaded when:
- Different industry indicated
- User explicitly asks for non-industry-specific generic flow

When loaded, the skill carries this context into Phase 1 (audience archetype defaults), Phase 2 (peer set, role family expectations), Phase 3 (compression-pattern recognition), Phase 5 (audience psychology defaults), Phase 7 (adversarial objections grounded in industry typical objections).
