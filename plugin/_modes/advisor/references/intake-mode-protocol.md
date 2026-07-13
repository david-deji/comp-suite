# Intake Mode Protocol

Intake mode generates a strategic intake form (PDF) for a wage review engagement, branded per the active brand kit (defaults to the `_default` kit's neutral placeholder content per `brand-guidelines.md`; per-org kits override the visual + peer-set treatment per `references/brand-kit-protocol.md`). The form is sent to VP HR / VP Operations *before* analysis begins — its purpose is to capture strategic context (worry roles, recruitment pain, competitor intel) that doesn't show up in HRIS or market data.

Loaded by SKILL.md when the Intent Router classifies a request as Intake.

The output PDF is built by `template_assets/build_intake_form_pdf.py`. Intake mode's job is to generate the *content* of the parameterized questions, get user approval on each variant, then run the builder to produce the final fillable PDF.

---

## When Intake Mode Triggers

Intake mode triggers when the user's first message contains any of:

- `/intake`, "intake form", "intake PDF", "strategic intake"
- "build me an intake", "generate an intake form", "intake for [scope]"
- "send intake to [role]", "intake document for [audience]"

If the user invokes intake without naming a scope, ask in the opening response — do not assume.

---

## Why This Protocol Exists

The intake form has a fixed skeleton AND scope-parameterized questions. From the user's standing memory rule:

- **Fixed questions:** Q1, Q2, Q3, Q7, Q10, "Anything Else", and the Completed By / sign-off block. These are the same in every intake.
- **Scope-parameterized questions:** Q4 (worry roles), Q5 (recruiting pain), Q6 (soft intel), Q8 (competitor moves), Q9 (poaching). These flex based on which provinces, banners, and (optionally) role-families are in scope.

**The hard rule:** scope-parameterized questions are never silently generated and embedded. Each variant is presented to the user, **one at a time**, for approve/edit/reject — *before* the PDF is built.

This rule exists because intake forms get sent to senior leaders. A question worded poorly or pointed at the wrong banner is a credibility hit. The one-at-a-time review is a deliberate friction.

---

## Opening Behavior

After Intent Router classifies as Intake, open with a single message that establishes scope.

**If an engagement-config was pasted in the same message** and contains `engagement_scope` and `cycle` sections, frame the intake against that context first:

> "Intake mode for [scope_label] — [cycle_name], [cohort] cohort, currently [N] weeks before [effective_date].
>
> Last cycle's headline: [last_cycle.headline_decision]. This cycle's primary objective: [this_cycle_goals.primary_objective].
>
> The intake form will surface VP Ops / VP HR's view on worry roles, recruiting pain, competitor moves, and poaching — and their answers will get written back into your config under `cycle.this_cycle_goals.intake_inputs` for Phase 1 / Phase 3 reference.
>
> Three things I still need:
> 1. **Provinces.** Which provinces does this intake cover? (intake scope is often narrower than analysis scope — e.g., 'just QC pharmacy' even if the analysis spans multiple provinces)
> 2. **Banners.** Confirm or override the banner from your config: [banner_or_region]
> 3. **Role family.** Confirm in_scope_role_families from config, or narrow further: [in_scope_role_families]"

**If no engagement-config was pasted** (or the config is missing engagement_scope/cycle), open with the original scope-only prompt:

> "Intake mode — I'll generate a fillable strategic intake PDF for VP Ops / VP HR.
>
> Before I draft the questions, I need scope. Three things:
>
> 1. **Provinces.** Which provinces is this intake covering? (e.g., 'all 10', 'QC + ON', 'Atlantic only')
> 2. **Banners.** Which banners? (e.g., 'all company banners', 'a single banner', 'banner A + banner B + banner C')
> 3. **Role family** (optional). Are we narrowing to a role family — e.g., 'meat departments', 'pharmacy', 'store managers'? Say 'all roles' if no narrowing.
>
> Also: what cycle name should appear in the form header? (e.g., 'FY26 Annual Wage Review', 'Q3 Off-Cycle Wage Review — Meat')."

Wait for response. Do not pre-generate questions.

If the user pasted an engagement-config, use `cycle.cycle_name` as the default cycle header but still confirm. **Do not** auto-fill provinces from `benchmark.scope_provinces` — intake scope is often narrower than analysis scope. Always ask.

---

## Scope Parameterization Rules

Once scope is captured, hold these three dimensions in working memory:

| Dimension | Source | Example values |
|---|---|---|
| Provinces | User answer | `[QC, ON]`, `all 10`, `[NS, NB, NL, PE]` |
| Banners | User answer | `all banners`, `[banner A]`, `[banner A, banner B]` |
| Role family | User answer (optional) | `meat departments`, `pharmacy`, `store managers`, `null` |

These three dimensions drive the variants for Q4, Q5, Q6, Q8, Q9. Each variant is generated to be **specific to the named scope** — never generic.

### Variant catalog (read from JSON, do not inline)

The variants for Q4-Q9 are catalogued in `template_assets/intake_variants.json`. The skill MUST read variants from that catalog rather than improvise prose. This pattern: (a) keeps variant additions to a JSON edit, no protocol-prose change needed; (b) makes peer lists per province explicit and overrideable; (c) removes the temptation to invent role examples that don't match the engagement scope.

**Variant-resolution procedure** (run for each of Q4, Q5, Q6, Q8, Q9 in order):

1. **Load** `template_assets/intake_variants.json`.
2. **Find** the entry for the question_id (e.g., `q4_worry_roles`).
3. **Resolve clauses** by matching the engagement's three scope dimensions:
   - **provinces_clause**: pick `single_province` / `multi_province` / `all_provinces` based on the count of provinces in scope.
   - **banner_clause**: pick `named_banner` (substitute `{{banner}}`) or `all_banners` (empty).
   - **role_family_clause**: pick `scoped` (substitute `{{role_family}}` and `{{role_family_examples}}`) or `unscoped` (use the catalog's default fallback).
4. **Substitute template variables**:
   - `{{provinces}}` → human-readable list (e.g., "QC and ON" / "all 10 provinces" / "BC")
   - `{{banner}}` → user-provided banner descriptor
   - `{{role_family}}` → user-provided role family
   - `{{role_family_examples}}` → look up `examples_by_role_family[role_family][province]`, fall back to `[role_family][DEFAULT]` if no province match
   - `{{competitor_list}}` (Q8 only) → comma-join `peer_companies_by_province[province]` for each in-scope province; deduplicate; cap at 6. Override via `engagement-config.benchmark.peer_companies` if present.
   - `{{cycle_name}}` → from `cycle.cycle_name` in the engagement config
5. **Run optional Q8 validation pass** (see § Q8 Competitor Wage Validation below) before presenting Q8.
6. **Present the resolved variant** for approval per § One-At-A-Time Approval Loop.

**Adding a new variant**: edit `template_assets/intake_variants.json`. Add either a new `variants[]` entry (for a new question) or a new clause-key (for a new scope dimension on an existing question). Add new role families to `examples_by_role_family`. Add new provinces' peer lists to `peer_companies_by_province`. No edit to this protocol file is required.

**Adding a new role family** (e.g., the engagement scopes to "frozen foods"): if `examples_by_role_family` does not contain the family, surface to user before generating Q4: "I don't have role examples cached for `frozen foods`. Suggest 2-3 specific roles I should reference (e.g., 'frozen-foods clerks', 'cold-storage warehouse staff'). I'll use them this engagement and add them to the catalog for next time." On user input, append to `examples_by_role_family` AND save the addition to the local `$STATE_ROOT/_orgs/<slug>/intake-additions.json` (non-schema scratch; resolves per `references/library-resolution.md`).

### Q8 Competitor Wage Validation (item 2.1 web grounding)

Before presenting the Q8 variant, optionally run a light validation pass on each of the named peers in the resolved `{{competitor_list}}`. For each peer:

- `web_search` for `"<competitor> wage increase <province> <current year>"` or `"<competitor> hourly rate change"`
- `web_fetch` against any returned careers-page or press-release URL that surfaces a concrete number
- If a verifiable wage move is found, prepend it to the Q8 variant via the catalog's `validation_grounding` clause as a grounding line: `(Per <competitor> careers page accessed YYYY-MM-DD: hourly grocery rates lifted 4% effective 2026-Q1.) What have you heard about [other peers] doing on pay…`

Cap the validation at the catalog's `validation_cap` (currently 3) named peers per Q8 variant — anything beyond that is for Phase 2 to surface, not the intake form. Cite the URL + access date in the appendix of the engagement-state file via the standard `tool_calls[]` array (per `references/persistence-and-ledger.md` § tool_calls block and `references/tools-available.md` § Container for tool_calls[]) — each `web_fetch` call appends one entry with `tool: web_fetch`, `args: {url}`, `timestamp`, `result_hash` (SHA-256 of fetched body), and `used_in: [intake_appendix]`. If no verifiable number is found, skip the grounding line and present the Q8 variant unchanged — do not invent a number, and do not cite "according to a recent article" without the URL.

---

## One-At-A-Time Approval Loop

After scope is captured, generate variants and present them **sequentially, one per response turn**. Never present all five at once — the memory rule is explicit on this.

For each scope-parameterized question, present in this format:

```
[Variant 1 of 5] Question 4 — Worry roles
Scope: QC + ON, all banners, meat departments
Cycle: FY26 Annual Wage Review

Draft:
> Which two or three roles in your QC and ON meat departments are you 
> most worried about losing right now? Name the role and the reason.
>
> Examples of reasons: pay below market, manager issues, schedule, 
> career path, location-specific
> Be specific (e.g., 'meat cutters in Montréal stores' rather than 
> 'meat department').

Approve / edit / reject?
```

Wait for response.

- **Approve** → lock variant, move to next.
- **Edit** → ask "what would you change?", apply the edit, re-show, approve again.
- **Reject** → ask "should I redraft, or skip this question entirely?" If redraft, generate a new variant from a different angle. If skip, mark the question as omitted in the final PDF.

After all five variants are resolved (approved or skipped), summarize before the PDF build:

```
✓ Q4 — approved (worry roles, QC + ON, meat)
✓ Q5 — edited and approved (recruiting pain, narrowed to GTA stores)
✓ Q6 — approved (soft intel)
✗ Q8 — skipped
✓ Q9 — approved (poaching, single-banner only)

Building PDF with: cycle = "FY26 Annual Wage Review", 4 of 5 
scope-parameterized questions included, plus the 6 fixed questions 
and Anything Else.

Confirm and build?
```

Only on explicit confirmation, run the PDF builder.

---

## PDF Build Step

The builder lives at `template_assets/build_intake_form_pdf.py`. It expects:

- `CYCLE_NAME` set at runtime (the cycle string the user provided)
- The script's hard-coded fixed questions (Q1, Q2, Q3, Q7, Q10, Anything Else, sign-off)
- The five scope-parameterized question slots (Q4, Q5, Q6, Q8, Q9), which in the current builder are also hard-coded

**Implementation note:** the bundled `build_intake_form_pdf.py` currently has Q4–Q6, Q8, Q9 written as fixed strings. To support scope-aware variants, intake mode must:

1. Copy the builder script to a working directory.
2. Inject the approved variants by replacing the corresponding `draw_question(...)` calls — match on the `field_name` parameter (`q4_worry_roles`, `q5_recruiting`, `q6_soft_intel`, `q8_competitor_moves`, `q9_poaching`).
3. Update `CYCLE_NAME` at the top of the file.
4. Run the script.
5. Present the resulting PDF to the user via `present_files`.

If a question was skipped, remove the corresponding `draw_question(...)` block entirely (and renumber the remaining questions in the title strings — Q9 becomes Q8 if Q8 was skipped, etc.). The skill must update the visible numbering to match the actual question count.

If the logo file (`headerLogo-1.svg`) is not present in the working directory, fall back to the default brand logo from `template_assets/branding/_default/theme/logo.svg` (or the active per-org override at `template_assets/branding/<org>/theme/logo.svg`). The script's `LOGO_PATH` must be updated accordingly.

---

## Output and Cleanup

The final PDF is presented via `present_files` with a one-line summary:

> "Intake form ready. Filename: `strategic-intake-form-{cycle-slug}-{YYYY-MM-DD}.pdf`. 4 of 5 scope-parameterized questions included, 6 fixed questions, sign-off block. Send to VP Ops / VP HR with a 'please return by [date]' on the form's metadata block."

After delivery, do not auto-suggest a next step. The user owns what happens next.

---

## Closing the Loop: Writing Intake Responses Back to Config

The intake form is one half of "this cycle's goals" — the user-side framing comes from `cycle.this_cycle_goals.primary_objective` and `must_address`, captured at engagement creation. The VP Ops side comes from the intake responses (Q4 worry roles, Q5 recruiting pain, Q8 competitor moves, Q9 poaching).

**When the user later pastes filled-in intake responses back into a session** (typically a separate session, after VP Ops has returned the PDF):

1. Extract the answers to Q4, Q5, Q6, Q8, Q9.
2. If a config was pasted alongside, output an updated `cycle.this_cycle_goals.intake_inputs` block:

```yaml
intake_inputs:
  worry_roles:
    - "Pharmacy assistants in Lower Mainland — pay below market, losing to Shoppers"
    - "Meat cutters in Montréal stores — Maxi paying $2/hr above us"
  recruiting_pain:
    - "8-week vacancy on bakery managers in GTA"
  competitor_moves:
    - "Loblaws lifted hourly grocery rates 4% in ON, effective March 2026"
  poaching_signals:
    - "Costco actively recruiting from our Brampton store"
  source: "strategic-intake-form-fy26-annual-2026-03-12.pdf"
  captured_date: 2026-03-15
```

3. Surface the merge: "Intake responses captured. Updated `intake_inputs` in your config. Phase 1 (Discovery — `cycle.current_stage = Discovery` per the canonical 7-stage list, or whatever your config's override label is) and Phase 3 (Interpretation) will reference these when the analysis engagement starts."

4. If no config was pasted, present the same block as a standalone YAML chunk and instruct the user to paste it under `cycle.this_cycle_goals.intake_inputs` in their saved config.

This is the bridge that makes intake responses persist beyond the form itself. Without it, the rich VP Ops context evaporates after the PDF is filed.

---

## Anti-Patterns

- **Do not generate all 5 variants in one message.** The user's memory rule is explicit: one at a time. Batching defeats the entire safeguard.
- **Do not auto-fill scope from a pasted config.** Intake scope is often narrower than analysis scope. Always ask.
- **Do not skip the approval loop because the variants "look obviously good."** The whole point of the friction is that the user catches things the skill cannot — wrong banner, wrong role family, awkward phrasing for the specific recipient.
- **Do not produce a deck during Intake.** Intake is form-only.
- **Do not edit the fixed questions** (Q1, Q2, Q3, Q7, Q10, Anything Else, sign-off). The builder's hard-coded fixed questions are the source of truth. If the user asks to change a fixed question, push back: "Q1-3, Q7, Q10, and the sign-off block are fixed across all intakes for consistency. If you want to change them permanently, that's a builder-script edit, not an intake-mode change."
- **Do not invent peer companies for Q8.** Peer lists per province come from `template_assets/intake_variants.json` § peer_companies_by_province (overrideable by `engagement-config.benchmark.peer_companies`). If a province's peer list is missing or feels stale, edit the JSON catalog rather than improvising mid-engagement.
- **Do not improvise variants for Q4-Q9.** Variants come from `template_assets/intake_variants.json`. If a needed variant is missing from the catalog, edit the JSON (and save to `$STATE_ROOT/_orgs/<slug>/intake-additions.json` so future cycles inherit it). Never hand-write a variant inline — the JSON is the source of truth.

---

## Edge Cases

**No engagement-config pasted, and the `_default` kit is active (no per-org override).** The bundled intake builder ships with `_default` kit branding (neutral placeholder) and a grocery-industry peer set. When the active kit is `_default` and the user is from a different industry, surface the limitation:

> "Intake mode's bundled builder uses the `_default` kit (neutral placeholder branding, grocery peer set). For other industries, the protocol works but the branding and peer-suggestions won't fit. You can proceed anyway, build a generic version, or scaffold a per-org brand kit first via `/brand-kit init <org-slug>` (which would then produce a kit-appropriate intake)."

When a per-org kit is active (`deck.brand: <org-slug>` in engagement-config and a kit exists at `template_assets/branding/<org-slug>/`), the intake builder uses that kit's branding and the peer-set is taken from `engagement-config.benchmark.peer_companies` rather than the bundled grocery default.

**User invokes `/intake` mid-engagement.** Pause the engagement, run intake protocol, return to the engagement after PDF delivery. Do not let the engagement's discovery answers leak into intake question variants — intake is a *fresh* capture from the recipient, not a re-statement of what the analyst already knows.

**User wants to send the same intake to multiple recipients with different scope.** Run intake mode separately per recipient. The PDF is small enough that running it twice is faster than parameterizing the script for multi-recipient output.

---

## Output Discipline

Intake produces an `intake-form-{cycle-slug}.pdf` **file artifact** as its END deliverable, plus an `intake-form-{cycle-slug}-meta.yaml` capturing variant choices and the `tool_calls[]` audit trail.

- **Variant approval loop happens in chat text** — variant proposals, reactions, and revisions are interactive prose. No artifacts during the iterations themselves.
- **After all variants approved**, the assembled intake PDF is the file artifact. Presented via `present_files`, with cycle name and scope summary in the response text.
- **Delivery**: the intake PDF delivers as a chat-download artifact (never written to a backend — per `references/persistence-and-ledger.md` § Binary deliverables); the `intake-form-{cycle-slug}-meta.yaml` sidecar is non-schema scratch written to the local `$STATE_ROOT/_orgs/<slug>/...`. The operator files the PDF into their own storage; the intended path is recorded in the meta sidecar for provenance.
- Do not narrate the build process step-by-step. The user approved the variants; the build itself is silent.
