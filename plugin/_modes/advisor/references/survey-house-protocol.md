# Survey-House and User-Provided CBA Protocol

Loaded by SKILL.md when an engagement uses third-party survey data (Mercer, Willis Towers Watson, Korn Ferry, McLean & Co, Aon, Hay Group, custom industry surveys) OR user-provided collective agreements that are NOT in `mcp__market__get_cba_wage_scale`. These are the two "data sources Market MCP doesn't cover" patterns the skill must handle without falling back to non-union market estimates or improvised survey extraction.

This file does NOT replace Market MCP — it complements it. Market MCP remains the primary source for Canadian wage data. Survey-house and user-CBA paths fill the gaps where Market MCP is sparse, where the user has paid for a specific survey cut, or where a unionized scope's CBA isn't in the Market MCP CBA table.

---

## When to use this protocol

Activate one or both paths when any of the following is true at Phase 2 entry:

| Trigger | Path activated |
|---|---|
| User uploads a third-party survey PDF / spreadsheet (Mercer, WTW, Korn Ferry, etc.) | Survey-house path |
| User mentions a survey by name in their first message ("we have the Mercer Total Compensation Survey for grocery") | Survey-house path (prompt for upload) |
| User uploads or pastes a CBA wage scale that `get_cba_wage_scale` does not return for that role/province | User-provided CBA path |
| User says "use this CBA, not Market MCP's" for a unionized role | User-provided CBA path |
| `get_cba_wage_scale` returns no data for a unionized role and the user has the CBA on hand | User-provided CBA path (prompt for upload/paste) |
| User says "the public wage data isn't right for our scope — we have better internal benchmarks" | Survey-house path (treat as private survey) |

If neither trigger fires, do NOT activate this protocol — Market MCP + Indeed MCP remain the data source.

---

## Survey-house path

### Ingestion patterns

Three common upload formats. Resolve based on what the user provides.

| Format | Tool | Output |
|---|---|---|
| **Survey PDF report** (typical Mercer / WTW deliverable) | `python -m markitdown <file.pdf>` | Extracted text + tables; parse percentile rows by role |
| **Survey raw spreadsheet** (.xlsx with role × percentile cells) | `openpyxl` or `pandas` | Structured per-role/per-percentile values |
| **Survey CSV export** | `pandas.read_csv` | Same as spreadsheet path |

For PDF surveys, expect tables with role title columns and percentile columns (P10, P25, P50, P75, P90) for one or more cuts (national, regional, sector-specific, revenue-band). Extract by:

1. Run `markitdown` on the PDF.
2. Identify the data tables — typically have a column header row matching the percentile pattern (`P10`, `P25`, `P50`, `P75`, `P90` or `25th`, `50th`, `75th`).
3. Per row, extract `role_title`, percentile values, sample size if present, effective date if present.
4. Store as a normalized dictionary structure mirroring Market MCP's `get_role_intelligence` output shape (so downstream costing logic doesn't branch on source).

If `markitdown` returns malformed tables (common for image-based PDFs or complex layouts), fall back to asking the user: "I can read [N] of [M] tables from your PDF. The remaining tables are image-based or complex layouts I can't reliably parse. Can you re-export as a spreadsheet, or paste the relevant rows directly?"

### Survey-data normalization

Apply these adjustments before using the data in costing or interpretation:

1. **Aging factor**. Survey effective date is often older than the engagement's analysis date. Apply a per-role aging factor:
   - If survey publication date > 6 months old, ask the user for an aging factor or use a default 3% YoY (configurable via `benchmark.survey_aging_pct`).
   - Tag every aged data point: `[survey-house: <vendor>, <year>, aged +X% to <analysis_date>]`
2. **Geo-adjustment**. Most survey houses publish national data with optional regional differentials. If the engagement scope is provincial:
   - If survey provides a regional cut, use it directly (e.g., Mercer's "Quebec retail" cut for QC scope).
   - If only national data is available, ask the user to provide a geo-differential or use Statistics Canada's wage geo-differentials as a fallback (`web_fetch` against `statcan.gc.ca` Table 14-10-0064 or equivalent).
   - Tag: `[geo-adjusted: national → QC -8%]` or `[geo-adjusted: regional cut native]`.
3. **Job-match confidence**. Survey job titles rarely match the user's HRIS titles 1:1. For each role:
   - Strong match (survey title is the same role at the same scope): tag `[MATCHED]`.
   - Approximate match (survey has a similar role with different scope, e.g., "Pharmacy Manager" vs the user's "Pharmacy Operations Manager"): tag `[PROXY]` with a one-line note.
   - No match: do NOT invent a match. Surface the gap to the user: "Survey doesn't have a comparable to `[user role]`. Closest candidates: `[A]`, `[B]`. Pick one as proxy, or skip this role from survey analysis."
4. **Sample size**. Always carry forward the survey's sample size per role. Flag roles with sample size < 10 as `[low-N: N=8]` and surface in interpretation.

### Confidence tag (new)

Add `[survey-house]` to the council-mode confidence tag vocabulary (per `references/council-mode.md` § Confidence tagging). Required citation form:

`[survey-house: <vendor>, <survey_year>, <cut>, <aging_note>]`

Example: `[survey-house: Mercer, 2026 Total Compensation Survey, QC retail cut, aged +1.2% to 2026-04]`

A `[survey-house]` tag without vendor + year + cut auto-downgrades to `[professional-judgment]` — same enforcement pattern as `[statutory]`.

### Auto-save to survey archive (post-ingestion)

After the user confirms the extracted survey-house data (vendor, year, cut, percentile rows), queue a write to the persistence folder at `survey-archive/<vendor-slug>/<year>/<cut-slug>.yaml`. The write joins the close-time close-time write sequence per `references/persistence-and-ledger.md` § Close-time close-time write sequence — it is NOT a separate commit.

**Slug rules:**

- `<vendor-slug>`: lowercase, hyphenated, drop suffixes ("Mercer Canada Inc." → `mercer`, "Willis Towers Watson" → `willis-towers-watson`, "Korn Ferry" → `korn-ferry`).
- `<year>`: 4-digit calendar year of survey publication (not engagement date).
- `<cut-slug>`: lowercase, hyphenated, includes geo + sector + revenue-band where applicable ("QC retail" → `qc-retail`, "National manufacturing > $500M" → `national-manufacturing-rev-500m-plus`).

**File schema** (mirror of `get_role_intelligence` shape so downstream code doesn't branch on source):

```yaml
survey:
  vendor: "Mercer"
  vendor_slug: "mercer"
  survey_name: "2026 Total Compensation Survey"
  year: 2026
  publication_date: 2026-01-15
  cut: "QC retail"
  cut_slug: "qc-retail"
  geo_scope: "QC"
  sector_scope: "retail"
  ingested_from: "user-uploaded PDF: Mercer_TCS_2026_QC_Retail.pdf"
  ingested_at: 2026-04-21T13:32:00
  aging_default_pct: 3.0
  source_priority_hint: 3   # mirrors source-priority precedence position
roles:
  - role_title: "Pharmacy Manager"
    matched_to_internal: "Pharmacy Operations Manager"
    match_strength: "PROXY"
    match_note: "Survey scope is single-store; internal role spans 4 stores."
    sample_size: 142
    percentiles:
      P10: 38.50
      P25: 42.10
      P50: 46.80
      P75: 51.40
      P90: 56.00
  - role_title: "Cashier"
    matched_to_internal: "Cashier"
    match_strength: "MATCHED"
    sample_size: 1840
    percentiles:
      P10: 16.20
      P25: 17.50
      P50: 18.90
      P75: 20.40
      P90: 22.10
```

**Update `_index.yaml`** at `survey-archive/_index.yaml` to record the new entry: `{vendor, year, cut, file: <path>, ingested_at}`. The index is what `library-resolution.md` § Survey archive scans at Phase 0.

**Idempotency**: if `survey-archive/<vendor-slug>/<year>/<cut-slug>.yaml` already exists, surface to the user: "Survey archive already has Mercer 2026 QC retail (ingested 2026-02-10). Overwrite with this upload, or keep the existing file?" Default to keep; user opts in to overwrite. On overwrite, append to a `_history.yaml` log so prior versions aren't lost silently.

**Disallowed-fields scan still runs**: the auto-save respects the privacy disallowed-fields scan in § Disallowed-fields scan below. If participating-company identifiers are present, the auto-save is blocked until the user re-exports.

---

## User-provided CBA path

### When user-CBA replaces Market MCP CBA

For unionized roles, the default data source is `mcp__market__get_cba_wage_scale`. The user-provided CBA path activates when:

- `get_cba_wage_scale(role, province)` returns no data for the role/province combination
- The user has a more current CBA than Market MCP's cached version
- The user has a CBA from a private/local agreement not in any public CBA database
- The user explicitly wants to use their own CBA instead of Market MCP's

When user-CBA path is active, it takes precedence over `get_cba_wage_scale` for that role/province combination. Source-priority precedence (default; overrideable per engagement):

1. **User-provided CBA** (if active for this role/province)
2. `get_cba_wage_scale` (Market MCP CBA)
3. Survey-house data (for non-CBA roles)
4. `get_role_intelligence` (Market MCP non-CBA)
5. Indeed MCP postings
6. Web search fallback

Override via `engagement-config.benchmark.source_priority_override` if the user wants a different precedence (e.g., "trust my survey over CBA for non-union roles in our company").

### Ingestion patterns

Three input forms.

| Format | Procedure |
|---|---|
| **Pasted CBA text in chat** | Ask the user to paste the wage-scale section verbatim. Extract: agreement_id (collective agreement name + signing parties), effective_date, expiry_date, classification, step rates per step, scale length, annual increase schedule, top-rate. |
| **Uploaded CBA PDF** | `python -m markitdown <file.pdf>`; navigate to the wage-scale appendix; extract same fields as above. CBA PDFs are often 200+ pages; the wage scale is usually in Schedule A or Appendix A. |
| **Uploaded wage-grid spreadsheet** | `openpyxl` parse; expect classification column + step columns OR step rows + classification rows. Confirm the layout with the user before parsing. |

### Required CBA fields

Capture and confirm with the user before using:

```yaml
user_provided_cba:
  agreement_id: "TUAC 501 Acme QC retail 2024-2028"
  parties: ["Acme QC", "TUAC section locale 501"]
  effective_date: 2024-05-01
  expiry_date: 2028-04-30
  classification: "Meat cutter — Class A"
  province: QC
  scale_length_steps: 6
  hours_to_advance_per_step: 1040
  steps:
    - { step: 1, rate: 18.50, percent_of_top: 60 }
    - { step: 2, rate: 21.00, percent_of_top: 68 }
    - { step: 3, rate: 23.50, percent_of_top: 76 }
    - { step: 4, rate: 26.00, percent_of_top: 84 }
    - { step: 5, rate: 28.50, percent_of_top: 92 }
    - { step: 6, rate: 31.00, percent_of_top: 100 }   # top rate
  annual_increase_schedule:
    - { effective: 2024-05-01, lift_pct: 0 }
    - { effective: 2025-05-01, lift_pct: 2.5 }
    - { effective: 2026-05-01, lift_pct: 2.5 }
    - { effective: 2027-05-01, lift_pct: 2.0 }
  source: "user-uploaded PDF: tuac-501-acme-qc-retail-2024-2028.pdf"
  ingested_at: 2026-04-21T13:32:00
```

Surface back to the user for confirmation before any costing calculation: "I extracted the following from your CBA. Confirm before I use it for [role] benchmarking."

### Confidence tag (new)

Add `[user-provided-cba]` to the council-mode confidence tag vocabulary. Required citation form:

`[user-provided-cba: <agreement_id>, expires <date>]`

Example: `[user-provided-cba: TUAC 501 Acme QC retail 2024-2028, expires 2028-04-30]`

A `[user-provided-cba]` tag without agreement_id + expiry auto-downgrades to `[assumption]` (a CBA without source identification is unreliable for any decision).

### Cross-check against Market MCP (when both are available)

When both the user-CBA AND `get_cba_wage_scale` return data for the same role/province, run a 2-line cross-check before using user-CBA:

1. Compare top rates: if delta > 5%, surface to user: "Your CBA shows top rate $31.00; Market MCP CBA cache shows $30.20. The 2.6% delta could mean MCP is outdated or your CBA is more recent. Confirm which to trust."
2. Compare expiry: if user-CBA expiry < today, warn: "Your CBA expired [date]. Use the post-expiry rates only if a renewal is in force or status quo applies — otherwise this is stale data."

The cross-check is a one-time confirmation; once the user confirms, the user-CBA takes precedence for the rest of the engagement.

### Auto-save to CBA library (post-extraction)

After the user confirms the extracted CBA fields (per § Required CBA fields), queue a write to the persistence folder at `cba-library/<agreement-id-slug>.yaml`. The write joins the close-time close-time write sequence per `references/persistence-and-ledger.md` § Close-time close-time write sequence.

**`<agreement-id-slug>`**: lowercase, hyphenated, derived from the `agreement_id` field. Example: `"TUAC 501 Acme QC retail 2024-2028"` → `tuac-501-acme-qc-retail-2024-2028`.

**File schema**: the `user_provided_cba` block from § Required CBA fields, written verbatim. Include the `source` and `ingested_at` provenance fields.

**Update `_index.yaml`** at `cba-library/_index.yaml` to record the role/province → agreement-id mapping that drives auto-load at Phase 0:

```yaml
mappings:
  - applies_to:
      - { role: "meat-cutter", province: "QC" }
      - { role: "meat-cutter-class-a", province: "QC" }
      - { role: "butcher", province: "QC" }
    agreement_id: "TUAC 501 Acme QC retail 2024-2028"
    agreement_slug: "tuac-501-acme-qc-retail-2024-2028"
    expiry_date: 2028-04-30
    parties: ["Acme QC", "TUAC section locale 501"]
    ingested_at: 2026-04-21T13:32:00
```

**`applies_to` discovery**: at extraction time, ask the user: "Which roles does this CBA cover? I detected `meat cutter Class A`. Should I also map `butcher`, `meat-cutter` (no class), or other related role slugs to this agreement so future engagements auto-load it?" Capture the user's confirmed role list into the mapping.

**Idempotency**: if `cba-library/<agreement-id-slug>.yaml` already exists, surface: "CBA library already has `<agreement_id>` (ingested 2026-02-10). Overwrite with this upload, or keep existing?" Default to keep; user opts in. On overwrite, append prior version to `cba-library/_history/<agreement-id-slug>-v<N>.yaml`.

**Cross-check on save**: re-run the Market-MCP cross-check (§ above) at save time using the latest cache, not the cached snapshot from extraction. If the delta has grown since extraction, surface to the user before committing the save.

**Manual save via `/cba save <agreement-id>`**: the user can also explicitly invoke `/cba save tuac-501-acme-qc-retail-2024-2028` mid-engagement to force a save without waiting for close-time. Behaviorally identical to the auto-save path; surface the same idempotency prompts.

---

## Phase 2g integration (where this slots in)

`references/consulting-protocol.md` § Phase 2g — Market Data Pull defines the core role-resolution + market-data fetch sequence. This protocol inserts two new steps in the priority order, between `compare_pay_scale_to_market` and `get_cba_wage_scale`:

**Updated Phase 2g priority sequence (when this protocol is active):**

1. `search_roles` → role resolution
2. `get_role_intelligence` → comprehensive bundle
3. `compare_pay_scale_to_market` → wage grid evaluation
4. **NEW — User-provided CBA check**: if active for this role/province, use it as primary CBA source. Skip step 5.
5. `get_cba_wage_scale` → Market MCP CBA (skipped if user-CBA active)
6. **NEW — Survey-house data check**: if active, augment Market MCP data with survey percentiles per role. Tag survey-sourced rows separately so the deck can show both side-by-side.
7. `compare_offer_to_market` → single-offer evaluation
8. `compare_roles` → cross-cuts
9. Indeed MCP for posting validation
10. Web search fallback

Steps 4 and 6 are optional inserts — they fire only when the survey-house or user-CBA path is active.

### Multi-source presentation pattern

When both Market MCP and survey-house data exist for the same role, present both in the deck rather than picking one. Pattern:

| Source | P25 | P50 | P75 | Sample size | As of |
|---|---|---|---|---|---|
| Market MCP (StatCan + live postings) | $24.10 | $26.40 | $28.90 | n/a | 2026-04 |
| Mercer 2026 Total Comp (QC retail cut) | $25.00 | $27.20 | $29.80 | 142 | 2026-01 (aged +1.2%) |
| User-provided CBA top rate | — | — | — | — | $31.00 (top step, expires 2028-04-30) |

The decision-maker sees the source convergence (or divergence) — that's the real value of having multiple sources. Do not silently average them.

---

## Council-mode integration

When a council runs on an engagement that has survey-house or user-CBA data, the per-persona grounding (per `references/council-mode.md` § Step 4) gains two new source types:

- `total-rewards-strategist` may ground in survey-house cuts as well as Market MCP
- `employee-union` may ground in the user-provided CBA as well as the local's news page

The asymmetric rule still holds — no two personas hit the same survey or the same CBA section. If both `total-rewards-strategist` and `cfo-finance` want to ground in the same Mercer cut, reassign one (cfo-finance to a financial benchmark instead).

---

## Disallowed-fields scan (privacy)

Survey-house exports can contain company-identifiable data (participating company list, response rates per company). Extend the `references/costing-engine.md` disallowed-fields scan to flag survey-export columns that name participating companies in an identifiable way:

- `Participating Company`, `Reporter`, `Submitted By`, `Source Company`, `Company ID`

If detected, refuse to proceed with that file and ask the user to re-export with the participant list stripped (most survey vendors offer an anonymized export option).

User-provided CBA inputs do not raise PII concerns — CBAs are typically published documents and the wage data within them is structured for collective use.

---

## Done criteria

A test session against an engagement with both a Mercer survey PDF AND a user-provided CBA should:

1. ☐ Detect the survey upload, parse percentile tables, surface the validation summary with aging note + geo-adjustment status
2. ☐ Detect the user-CBA upload, extract the structured fields, surface for confirmation
3. ☐ Run a cross-check between user-CBA top rate and `get_cba_wage_scale` top rate when both exist; warn on > 5% delta
4. ☐ Use user-CBA in Phase 4 costing as primary source for that role/province
5. ☐ Present multi-source comparison table in the deck (Market MCP + survey + user-CBA) rather than silently averaging
6. ☐ Tag survey claims with `[survey-house: <vendor>, <year>, <cut>, <aging>]` and CBA claims with `[user-provided-cba: <agreement_id>, expires <date>]`
7. ☐ Refuse to proceed if survey export contains participating-company identifiers
8. ☐ Council mode (if invoked) grounds `total-rewards-strategist` in the survey and `employee-union` in the user-CBA — no overlap with other personas' sources

---

## Anti-patterns

- **Do not silently average across sources.** Survey, Market MCP, and user-CBA each have different methodologies, populations, and aging — averaging hides which source the decision rests on. Present side-by-side; let the user pick.
- **Do not treat survey-house data as more authoritative than Market MCP by default.** Surveys have small samples, sector cuts, and self-selection bias. Market MCP draws on StatCan + live postings — broader coverage. Default to "show both; user picks the lens."
- **Do not use a survey beyond its scope.** A US-published Mercer survey doesn't apply to Canadian roles unless explicitly cut for Canada. A retail survey doesn't apply to corporate HQ roles.
- **Do not extract a CBA wage scale from prose or summary text.** The wage scale is structured (steps × rates × dates) — extract from the actual schedule appendix, not from a press release or news summary.
- **Do not use a user-CBA past its expiry without confirmation.** Expired CBAs may have status-quo provisions OR the parties may be renegotiating. Ask before assuming.
- **Do not invent a job-match between a survey title and a user role.** When the match is `[PROXY]` or worse, surface to the user and let them confirm or reject the proxy.
- **Do not include the survey-house's licensing fine-print in the deck.** Survey vendors publish data with usage restrictions — stay within the user's license, do not redistribute the survey itself in the deck. Cite the source and scope; don't quote large blocks.
