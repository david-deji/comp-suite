# Tools Available — Verified-Source Discipline + tool_calls[] Container

Canonical reference for the advisor mode's source-tag vocabulary, per-tag verification artifacts, the auto-downgrade table, and the append-only `tool_calls[]` container schema. Loaded by SKILL.md whenever a claim is tagged, a footnote is emitted, or an `engagement-state.yaml` / `council-state.yaml` `tool_calls[]` array is written.

This file is the single source of truth for the 11-tag vocabulary. `references/council-mode.md` (§ Confidence tagging), `references/fr-ca-glossary.md` (§ Section 5 footnotes), and `references/artifact-generation.md` (§ 2 tool_calls block) all defer here — they carry usage subsets, never a competing definition. If a tag or a downgrade rule appears to conflict across those files, this file wins.

Everything below assumes the OAuth-exclusive, market-MCP-primary v2 reality: the `market` server is the one required MCP server (HTTP, OAuth via headerless `.mcp.json` — no Bearer/Authorization header, no token ceremony), all its tools are $0.00, the claude.ai Indeed connector authenticates through claude.ai's own OAuth, and `web_search` / `web_fetch` are key-free builtins. There is no StatCan MCP server — CPI / unemployment / econometric context is `web_fetch`-sourced against `statcan.gc.ca`.

---

## Verified-source discipline

Every substantive claim in a deck slide, a footnote, a persona block, or a synthesis carries exactly one tag from the canonical 11-tag vocabulary below. A tag is a promise: it names the source class the claim rests on and the verification artifact that must exist in the engagement's `tool_calls[]` array for the claim to hold at its tagged strength.

Two of the eleven — `[professional-judgment]` and `[assumption]` — are ungrounded by design. They are not source claims and are excluded from the verification rule; they carry an author + rationale instead of a tool-call trace. The other nine are source claims and each requires a matching `tool_calls[]` entry.

Do not use the legacy 4-tag shorthand (`statutory` / `market-data` / `professional-judgment` / `assumption`) for anything new. The fine-grained 11-tag set is what enables per-source-class auto-downgrade.

### The 11-tag vocabulary

| Tag | Source class it covers | Backing tool / source | Required verification artifact (in `tool_calls[]`) |
|---|---|---|---|
| `[statcan-wage]` | StatCan wage-table percentiles (Market MCP wraps StatCan's wage tables in `benchmarks.statcan`). | `mcp__market__get_role_intelligence` | Entry with `role_id`, `province`, `percentiles`, timestamp, and field path `benchmarks.statcan.<percentile>`. |
| `[live-postings]` | Live job-posting rates (start / midpoint / top rate). | `mcp__market__get_role_intelligence` (`benchmarks.live_posting_*_rate`) OR `mcp__claude_ai_Indeed__search_jobs` (job_id list). | Entry with field path `benchmarks.live_posting_top_rate.<percentile>` (or `start_rate` / `midpoint`) + timestamp; or Indeed `search_jobs` entry with job_id list + timestamp. |
| `[cba]` | Collective-agreement wage scales for unionized roles (grocery, construction, healthcare, public sector). | `mcp__market__get_cba_wage_scale` | Entry with agreement reference, scope, and retrieval timestamp. |
| `[indeed-company]` | Competitor intel — company ratings, posting volume, hiring signals. | `mcp__claude_ai_Indeed__get_company_data` (claude.ai Indeed connector). | Entry with company name, query, and retrieval timestamp. |
| `[econometric]` | CPI / unemployment / GDP context — **NOT wages**. | `web_fetch` against `statcan.gc.ca`. There is no StatCan MCP server. | web_fetch entry with the fetched URL + access date (StatCan table number in the claim line). |
| `[statutory]` | Named statute, regulation, or CBA article text. | `web_fetch` against the statute domain (`legisquebec.gouv.qc.ca` / `laws-lois.justice.gc.ca` / `canlii.org` / the published CBA URL). | web_fetch entry with the statute URL + access date, **plus a verbatim quote of the cited article in the same claim line.** A `web_search` snippet is not sufficient — the fetch must point at the statute itself. |
| `[market-data]` | Market value not served (or not yet served) by a fine-grained Market MCP block. | Primary: `mcp__market__get_role_intelligence` (name the function + field path). Fallback: `web_fetch` (BLS, Job Bank, employer site) for roles/provinces outside Market MCP coverage. | Market MCP entry with function + field path, or a web_fetch entry with URL + access date. Prefer `[statcan-wage]` / `[live-postings]` for anything Market MCP serves — reserve `[market-data]` for the web fallback. |
| `[survey-house]` | Third-party salary survey (Mercer, WTW, Korn Ferry, etc.), supplied as an analyst-provided / user-uploaded block — not a live tool call. | Analyst-provided survey block (see `references/survey-house-protocol.md`). | Vendor + survey year + cut + aging note — all four. |
| `[user-provided-cba]` | A CBA the user pasted or uploaded (not in Market MCP). | Analyst-provided CBA block. | Agreement ID + expiry date — both. |
| `[professional-judgment]` | Experienced comp-professional inference, not directly sourced. **Not a source claim** — excluded from the verification rule. | — (author's own reasoning). | Author / persona name + one-line rationale. |
| `[assumption]` | Stated belief not yet verified, flagged for follow-up. **Not a source claim.** | — (unverified). | One-line statement of what would falsify it. |

### Tag → footnote-citation mapping

The FR-CA footnote families in `references/fr-ca-glossary.md` § Section 5 collapse the eleven tags onto five citation patterns:

| Footnote citation family (fr-ca-glossary § 5) | Tags it renders |
|---|---|
| Market MCP citation (`Source : Market MCP, données de …`) | `[statcan-wage]`, `[live-postings]`, `[market-data]` |
| CBA citation (`Source : Convention collective …`) | `[cba]`, `[user-provided-cba]` |
| Indeed citation (`Source : Affichages Indeed …`) | `[indeed-company]` |
| Web fetch citation (`Source : [URL], consulté le …`) | `[statutory]`, `[econometric]` |
| User-provided data citation (`Source : Données fournies par le client …`) | `[user-provided-cba]`, analyst-provided `[survey-house]` blocks |

`[professional-judgment]` and `[assumption]` emit no data-source footnote — when a claim has no verifiable source, omit the footnote and tag the claim per `references/judgment-notes.md`.

### Auto-downgrade table

A source-tagged claim whose required verification artifact is absent from `tool_calls[]` does not silently pass — it auto-downgrades. The general rule: **any of the nine source tags without its matching `tool_calls[]` entry (or, for the two analyst-provided tags, without its required metadata fields) downgrades.** The specific targets:

| Tag | Downgrade trigger | Downgrades to |
|---|---|---|
| `[statcan-wage]` | No `tool_calls[]` entry for the `get_role_intelligence` call, or the `benchmarks.statcan.<percentile>` field path is missing. | `[professional-judgment]` |
| `[live-postings]` | No `tool_calls[]` entry (neither the `get_role_intelligence` live-posting block nor an Indeed `search_jobs` job_id list). | `[professional-judgment]` |
| `[cba]` | No `tool_calls[]` entry for `get_cba_wage_scale`. | `[professional-judgment]` |
| `[indeed-company]` | No `tool_calls[]` entry for `get_company_data`. | `[professional-judgment]` |
| `[econometric]` | No web_fetch `tool_calls[]` entry; **OR** the tag was applied to a wage claim (wages are `[statcan-wage]` / `[live-postings]` / `[market-data]`, never `[econometric]`). | `[professional-judgment]` |
| `[statutory]` | Missing the fetched statute URL **or** the verbatim article quote in the claim line. | `[professional-judgment]` |
| `[market-data]` | No `tool_calls[]` entry (neither a Market MCP call with field path nor a web_fetch with URL + access date). | `[professional-judgment]` |
| `[survey-house]` | Missing any of vendor / survey year / cut / aging note. | `[professional-judgment]` |
| `[user-provided-cba]` | Missing agreement ID **or** expiry date. | `[assumption]` |
| `[professional-judgment]` | Terminal — not a source claim, does not downgrade further. | — |
| `[assumption]` | Terminal — not a source claim, does not downgrade further. | — |

The scan runs at synthesis time (council Step 6) and at Phase 7 QA. Every downgrade is counted; a deck or council carrying multiple downgrades is weak grounding and the count is surfaced, not hidden. WHY: an unsourced `[statutory]` or `[statcan-wage]` claim that reads plausibly is the silent-failure mode — it travels into the deck and gets re-cited as gospel in HR, legal review, and arbitration. Downgrading on missing-artifact makes the gap visible before delivery.

---

## Container for tool_calls[]

`tool_calls` is one **flat, append-only array** on `engagement-state.yaml` (and on `council-state.yaml` for council runs). Every Market MCP call, every claude.ai Indeed connector call, and every `web_search` / `web_fetch` call appends exactly one entry. The array is the verified-source audit trail the downgrade scan reads against, and the cache key for re-runs. It is never displayed in the deck.

### Entry schema

Each entry has five fields:

| Field | Meaning |
|---|---|
| `tool` | Full MCP-style tool name — e.g. `mcp__market__get_role_intelligence`, `mcp__market__get_cba_wage_scale`, `mcp__claude_ai_Indeed__get_company_data`, `web_fetch`, `web_search`. |
| `args` | The arguments the call was made with (role_id, province, percentiles, employer, query, URL, etc.). |
| `timestamp` | ISO-8601 retrieval time. |
| `result_hash` | SHA-256 of the JSON response for MCP calls; SHA-256 of the fetched body for `web_fetch`; `null` for `web_search` (result set is non-deterministic snippets, not a stable body). |
| `used_in` | List of the slide IDs / section IDs / deliverable surfaces the call's result was used in. |

### Shape

```yaml
tool_calls:
  - tool: mcp__market__get_role_intelligence
    args: { role_id: "meat-cutter-qc", province: QC, percentiles: [10, 25, 50, 75, 90] }
    timestamp: 2026-07-01T14:08:00
    result_hash: "sha256:9f2c…"           # SHA-256 of the JSON response
    used_in: [findings-p50-slide, market-context-slide, market-data.csv]
  - tool: mcp__claude_ai_Indeed__get_company_data
    args: { company: "Loblaw", province: QC }
    timestamp: 2026-07-01T14:11:00
    result_hash: "sha256:1ab7…"
    used_in: [competitor-intel-slide]
  - tool: web_fetch
    args: { url: "https://www.legisquebec.gouv.qc.ca/fr/document/lc/E-12.001" }
    timestamp: 2026-07-01T14:12:00
    result_hash: "sha256:44de…"           # SHA-256 of the fetched body
    used_in: [risks-slide]
  - tool: web_search
    args: { query: "QC grocery sector labour cost ratio 2026" }
    timestamp: 2026-07-01T14:13:00
    result_hash: null                       # web_search results are non-deterministic — no stable body to hash
    used_in: [cfo-framing-slide]
```

### Discipline

- One call = one entry. Never batch multiple calls into a single entry, never mutate an existing entry — append only. WHY: the array doubles as an audit trail; a mutated entry breaks the correspondence between a tagged claim and the call that grounds it.
- `result_hash` is `null` only for `web_search`. Any MCP call or `web_fetch` with a `null` hash is treated as unverifiable and triggers the auto-downgrade above.
- Every source-tagged claim must be traceable to at least one `tool_calls[]` entry via its `used_in` surface. The Phase 7 / council-Step-6 scan walks the array, matches each tag to its entry, and downgrades any tag with no match.
- Never write client-confidential narrative into `args` — keep entries machine-parseable (IDs, codes, URLs, query strings).

---

## Real v2 tool set

The machine-readable registry of every tool available to the advisor mode — required vs optional server, entry name, cost tier, and per-call cost — is `_core/tools/registry.yaml`. That file is authoritative for what is callable and what `budget-check` will resolve; this file is authoritative for how a call's output is tagged and traced. Key facts from the registry that bind the discipline above:

- `market` is the one required MCP server (OAuth, headerless — no token). All `mcp__market__*` tools are `$0.00`.
- `perplexity` is optional; when absent, web research falls back to the `web_search` / `web_fetch` builtins. `perplexity_*` calls, when used, append to `tool_calls[]` under their full tool names like any other.
- `web_search` and `web_fetch` (registry: `web-search`, `statute-fetch`) are `$0.00` key-free builtins available in every session.
- `budget-check` blocks any tool not found in the registry — an unregistered $0 tool fails closed, not open. If a call you intend to trace is not in `registry.yaml`, that is a registry gap to reconcile before the call, not a tag to invent here.
