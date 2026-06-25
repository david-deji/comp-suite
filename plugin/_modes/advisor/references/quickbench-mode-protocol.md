# Quickbench Mode Protocol

Quickbench mode is a single-role market pull with no engagement, no consulting, and no deck. It exists for the *between* moments — when the user is prepping for a call or a quick exec question and needs a number in two minutes, not a deck in two hours.

Loaded by SKILL.md when the Intent Router classifies a request as Quickbench.

---

## When Quickbench Mode Triggers

Quickbench mode triggers when the user's first message contains any of:

- `/quickbench`, `/qb`, "quickbench"
- "quick benchmark", "quick market check", "fast benchmark"
- "what does the market pay for [role] in [province]" (only when phrased as a quick lookup, not as the start of an engagement)
- "/quickbench [role] [province]" (positional args)

When the trigger phrase is "what does the market pay…" without `/quickbench`, classify carefully. If the user follows up with audience or decision context, route to Track C/D instead. Quickbench is for the bare lookup.

---

## Why This Mode Exists

The full consulting flow (Phase 1 Discovery onward) is overkill for "what's a meat cutter making in BC right now?" Without Quickbench, that question routes to Track C, which opens with "What decision is this supporting, and who needs to see it?" — perfectly correct, completely wrong tone for a 90-second lookup.

Quickbench is the fast lane. It assumes:
- The user already knows what they're asking.
- No deliverable is needed.
- The output is consumed in chat, not exported.
- The user can escalate to a real engagement if the answer surfaces something interesting.

---

## Required Inputs

Quickbench needs three things to run:

1. **Role.** The job title or role family. ("Meat cutter", "store manager", "pharmacy technician".)
2. **Province.** A single province, two-letter code preferred. (Quebec / QC, Ontario / ON, etc.)
3. **Pay structure** (optional). "Hourly" / "salaried" / "step rate" / "merit-based." Defaults to inferring from the role.

Optional inputs (used if provided, never asked for):

- **Banner or company context** — "for a grocery cashier", "for a specific banner", "competitor data only"
- **Time horizon** — "current", "as of Q1", "year-end", or an explicit month count. Defaults to current (`window_months=3`).
- **Currency** — defaults to CAD for Canadian provinces.

**Unit-conversion rule for time windows**: if the user specifies a time window in days, weeks, or any non-month unit, convert to the closest integer month count and confirm before calling the Market MCP:

> "You said 90 days — that maps to `window_months=3` (the default). Sound right, or did you want `window_months=4` (a wider window)?"

Do NOT silently substitute month-equivalent for day-spec. The Market MCP only takes `window_months`; the conversion is the skill's responsibility, but it must be visible to the user.

---

## Opening Behavior

If the user invokes `/quickbench` with positional args (`/quickbench meat cutter BC`), parse and proceed without asking. If the user invokes `/quickbench` with no args:

> "Quickbench — quick market pull, no deck.
>
> Tell me: which role, which province? (e.g., 'meat cutter, BC' or 'pharmacy tech, QC'). If the role is hourly vs salaried matters, let me know — otherwise I'll infer from the role."

Wait for response. Once role + province are clear, proceed directly to data pull. Do not ask follow-up questions about audience, decision, or purpose — those are out of scope for Quickbench.

---

## Data Pull

Use the Market MCP toolchain in this order:

1. **`mcp__market__search_roles(query_text, province)`** — discover the right role first. Capture the `role_id` of the top match if `match_score >= 0.7` and `weak_match: false`. If `weak_match: true`, do NOT pick a `role_id` — pass the original title to the next call.
2. **`mcp__market__get_role_intelligence(role_id or role, province, percentiles=[10,25,50,75,90])`** — primary call. Returns:
   - `benchmarks.statcan.{p10, p25, p50, p75, p90}` — government wage-survey percentiles (StatCan-published, wrapped inside Market MCP)
   - `benchmarks.live_posting_start_rate.{p10, ...}` and `live_posting_top_rate.{p10, ...}` — live job posting rates (entry vs top of role's posting range)
   - `market_drift_pct`, `transparency_tier`, `recent_posting_count`, `salary_disclosure_rate`
   - `trends[]` — monthly array with YoY deltas
   **Always request all five percentiles** — P10 and P90 are the floor/ceiling and are load-bearing for range framing in the mini-report.
3. **`mcp__market__get_cba_wage_scale(role, province)`** — only if the role is unionized in the named province. The grocery industry context file lists which roles are CBA-bound where (UFCW Local 175 in ON, TUAC 501 in QC, UFCW 1518 in BC, etc.).
4. **`mcp__indeed__get_company_data(competitor, role, province)`** — supplementary (secondary source), only if `get_role_intelligence` returns `transparency_tier: LOW_DISCLOSURE` or `recent_posting_count` < 30. Pull 1-2 named competitors max; do not run a full peer-set sweep. Indeed is for company-level intel + posting validation, not for primary percentile evidence.

### Wrong-family safety check (between Step 1 and Step 2)

After `search_roles` returns and `get_role_intelligence` has been called, inspect `resolution.matched_title` (or the equivalent resolved title field on the return) against the user's original query. If the matched title differs in **role family** from the query, do NOT proceed with the data — surface the mismatch:

> "Heads-up: I searched for 'grocery clerk' but the closest match in the data is 'retail and wholesale trade managers' (NOC 60020). These are different role families. Do you want me to (a) try a different role title, (b) confirm 'manager' is what you meant, or (c) accept the manager data with a flag in the report?"

**Role-family escalation list** — any cross-family match triggers the prompt:

| Family A | ↔ | Family B |
|----------|---|----------|
| clerk / cashier / associate / attendant | ↔ | supervisor / manager / director |
| technician / specialist / coordinator | ↔ | engineer / scientist / professional |
| assistant / aide | ↔ | manager / lead / head |
| hourly / part-time / casual | ↔ | salaried / full-time professional |
| apprentice / trainee / junior | ↔ | journeyman / certified / senior |

This check fires regardless of `match_score` value. A SEMANTIC match with high `match_score` can still be wrong-family (e.g., "grocery clerk" → "retail manager" via the Industry/NAICS bridge). Wrong-family data is unsafe for compensation positioning even when the title is "close" linguistically.

If the data pull fails (no match, MCP error, role too vague), surface the error in plain language and offer alternatives:

> "I couldn't find clean data for 'shelf person' in Saskatchewan. The closest matches in the Market data are 'grocery clerk' and 'stocker'. Which is closer, or do you want me to try a different role title?"

Do not silently substitute a role. Always confirm the match if the user-named role doesn't resolve cleanly.

---

## Output Format — Mini-Report

Default output is a compact mini-report: short markdown table + 2-3 sentences of interpretation + a soft offer to escalate. Total length should fit on one mobile screen — roughly 15-25 lines of output.

Format:

```
**[Role] — [Province], [Date]**

| Percentile | StatCan (gov't wage survey) | Live posting top rate | Live posting start rate |
|---|---|---|---|
| P10 (floor) | $X.XX | $X.XX | $X.XX |
| P25 | $X.XX | $X.XX | $X.XX |
| P50 (median) | $X.XX | $X.XX | $X.XX |
| P75 | $X.XX | $X.XX | $X.XX |
| P90 (ceiling) | $X.XX | $X.XX | $X.XX |

Market drift: +X.X% (postings vs StatCan) · Transparency: HIGH/MEDIUM/LOW · Sample size: [recent_posting_count=N] · Recency: [trends[0].month]

Sources cited per the 11-tag verified-source discipline in `references/tools-available.md`. Use the fine-grained tag matching each column's data source — never the legacy `[market-data]` shorthand for Market MCP returns:

- StatCan-wage column → `[statcan-wage: mcp__market__get_role_intelligence(role_id=X, province=Y, percentiles=[10,25,50,75,90]) captured YYYY-MM-DD, benchmarks.statcan]`
- Live-Posting Start column → `[live-postings: mcp__market__get_role_intelligence(...) captured YYYY-MM-DD, benchmarks.live_posting_start_rate]`
- Live-Posting Top column → `[live-postings: mcp__market__get_role_intelligence(...) captured YYYY-MM-DD, benchmarks.live_posting_top_rate]`

The `[market-data]` tag is reserved for `web_fetch` fallback against sources Market MCP does not cover (e.g., BLS US data); do not use it for any Market MCP return.

**Read:** [2-3 sentences of interpretation. What's the spread? Is it 
unusually compressed or wide? Are competitor postings landing above 
or below P50? Anything notable about CBA scales vs non-union?]

Want this turned into a deck for [a likely audience inferred from 
context], or pull it for another province / role?
```

The "Read" section is short, plain-language, peer-to-peer. No jargon for jargon's sake. If there's nothing notable to flag (clean data, normal spread, no surprises), say so in one sentence: "Clean data, normal spread, P50 sits where you'd expect."

The escalation offer is always soft and optional. Suggest a likely audience based on what the data showed (e.g., "for a CHRO retention case" if the data shows below-market positioning), but never demand a follow-up.

---

## Multi-Province or Multi-Role Quickbench

If the user asks for two provinces in one quickbench (`/quickbench meat cutter QC ON`), produce two mini-reports stacked, with a one-line comparison at the bottom:

> "QC P50 sits ~$2.10 above ON P50 for this role — typical for skilled meat positions reflecting the QC unionization premium."

If the user asks for three or more roles or three or more provinces in one call, push back:

> "Quickbench is built for one role × one province (or two of one × one of the other). For a multi-role or multi-province sweep, that's really a Track C engagement. Want me to escalate, or run these as separate quickbenches?"

**3+ provinces (when user overrides the soft pushback)**: when the user insists on running 3+ provinces in one quickbench, collapse to one row per province with all five percentiles inline. This trades the per-source breakdown (StatCan vs live-postings columns) for the cross-province comparison. When the cross-province comparison IS the primary value, this is the right trade.

```
**[Role] — [region label, e.g., "Atlantic provinces"], [Date]**

| Province | P10 | P25 | P50 | P75 | P90 | Sample (n) |
|----------|-----|-----|-----|-----|-----|------------|
| NS | $X.XX | $X.XX | $X.XX | $X.XX | $X.XX | N |
| NB | $X.XX | $X.XX | $X.XX | $X.XX | $X.XX | N |
| NL | $X.XX | $X.XX | $X.XX | $X.XX | $X.XX | N |
| PE | $X.XX | $X.XX | $X.XX | $X.XX | $X.XX | N |

Source list: [statcan-wage: get_role_intelligence calls 1-4, captured YYYY-MM-DD]

**Read:** [2-3 sentences highlighting the cross-province pattern — which province leads, where the spread compresses, anything jurisdictional driving the gap]
```

Surface that the source breakdown was collapsed: "Note: I rolled up StatCan + live-postings into single P10-P90 rows per province for cross-province comparison. Want the per-source breakdown for any single province, run it as its own quickbench."

---

## When Quickbench Should Escalate

Quickbench is meant to be self-contained, but the data sometimes surfaces something that demands more than a 2-sentence read. Escalate the offer (more firmly) when:

- **Data is below P25 internal floor.** If the user mentioned an internal pay rate and the market pull shows it sitting under P25, the data is telling a retention story. Offer: "This is below P25. If retention is a concern in this role, want me to model what closing the gap would cost?"
- **Sample size is too small to be conclusive.** Flag it explicitly: "Sample is n=12 — directional only. For a real recommendation, we'd want to triangulate with Indeed live postings or a custom Mercer pull. Want me to expand?"
- **The user follows up with audience or decision context.** That's a track switch, not a quickbench. Move into Track C/D using `references/consulting-protocol.md` § Track C-to-D switching.

The escalation is always offered, never assumed. The user's path of least resistance should remain "thanks, that's what I needed" with no further action.

---

## Anti-Patterns

- **Do not run discovery questions.** No "what's this for?", no "who's the audience?", no "what's the decision?". Quickbench is exempt from Phase 1.
- **Do not produce a deck.** Even if the data is striking. The escalation offer is text — the deck only happens if the user accepts the offer.
- **Do not pull more than 1-2 competitor data points via Indeed.** Quickbench is fast; full peer-set sweeps are Track C.
- **Do not skip source attribution.** Every percentile in the table cites its source. Quick ≠ sloppy.
- **Do not invent currency or geo conversions.** If the user asks for "QC pharmacy techs in USD", convert with a clearly stated rate and cite it. Don't bury the conversion.

---

## Edge Cases

**Role doesn't exist in Market data.** Surface alternatives, ask for confirmation. Do not invent percentiles.

**Province is non-Canadian.** Quickbench's primary tool is the Market MCP, which is Canadian-focused. For US states or international, surface the limitation: "The Market MCP is Canada-focused. For [state/country], I can pull from BLS / Eurostat / equivalent — slower, less granular. Want me to try?"

**User provides internal pay context** ("we pay $24.50, what's market?"). Compare the internal rate against the percentiles in the Read section, classify as Below / At / Above market using the standard 0.95 / 1.05 compa-ratio thresholds. This stays within Quickbench scope as long as the user doesn't pivot to "what should we do about it" — that's a track switch.

**User asks for total compensation, not just base.** Quickbench's default is base salary or hourly rate. If the user asks for total cash or TDC, surface what's available: "Market data has base only for this role. Total cash and TDC are typically Mercer/Radford pulls — happy to escalate if that's what you need."

---

## Output Discipline

Quickbench produces a `quickbench-{role-slug}-{province}-{YYYY-MM-DD}.md` **file artifact** as its END deliverable. The artifact contains the mini-report (markdown body) plus a YAML frontmatter block capturing `tool_calls[]` and resolution metadata. The same content is previewed inline in chat so the user can react without opening the file.

- Also write to local `$STATE_ROOT/_orgs/<slug>/quickbench-archive/{YYYY-MM-DD}-{role-slug}-{province}.md` (non-schema artifact; see `references/persistence-and-ledger.md` § Where each thing lives). Deliver the file artifact in the chat for download.
- **Mini-report fits on one mobile screen (~15-25 lines)** as both file body and chat preview.
- Tables use compact markdown — three columns max in the percentile table (or the multi-province override layout per § Multi-Province when 3+ provinces).
- The escalation offer is one sentence, ends with a question mark, easy to ignore.
- After the response, end the turn. Do not chain follow-up suggestions or "would you also like…" prompts.

The captured `tool_calls[]` block in the frontmatter is the audit trail. Verified-source discipline applies to every percentile cited — see `references/tools-available.md` § Verified-source discipline § Container for tool_calls[].
