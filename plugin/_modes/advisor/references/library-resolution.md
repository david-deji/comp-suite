# Library Resolution

The single source of truth for the **repo-first / bundled-fallback** pattern that governs every shared asset library: brand kits, CBA library, survey archive, vocabulary glossary, persona library.

Loaded by SKILL.md whenever an asset class needs to be resolved — at Phase 0 (loaded-config summary), at Phase 2g (CBA / survey lookups), at Phase 6a (brand kit selection), and on council entry (persona pool).

---

## Resolution principle

**Repo wins, bundle is the seed.** When the persistence folder (default `comp-advisor-state`) has a matching asset, it takes precedence over the bundled fallback. The bundled assets serve two roles:

1. **Seed**: the source from which `_default` and per-org scaffolds are populated on first use.
2. **Fallback**: the value used when the persistence backend is unavailable (paste-mode) or the repo has no matching asset.

The skill never edits bundled assets at runtime. All persistent additions land in the repo.

---

## Resolution order — per asset class

### Brand kit

```
1. branding/<org-slug>/<sub-path>          # if engagement.config.brand.org_slug is set
                                           #   AND file exists in repo
2. branding/_default/<sub-path>            # if file exists in repo (post `/brand-kit init` or auto-seed)
3. template_assets/branding/_default/<sub-path>   # bundled fallback (always present)
```

`<sub-path>` examples: `theme/palette.json`, `theme/typography.json`, `theme/logo.svg`, `masters/01-title.js`, `footnotes.yaml`, `build_template.js`.

Per-file resolution: each file resolves independently. An org override of `masters/01-title.js` does NOT require copying the other 17 master files — they continue to resolve from `_default`.

Theme JSONs (`palette.json`, `typography.json`) support **partial override** via deep-merge: the org file may declare only the keys that diverge from `_default`, all others inherit. Logos, master JS files, and `footnotes.yaml` are **full-file replacement** — the org version, when present, replaces the default entirely.

### CBA library

Match key: `agreement_id` (canonical) OR `(role, province)` lookup via `_index.yaml`.

```
1. cba-library/<agreement_id>.yaml         # if engagement scope explicitly references this CBA
2. cba-library/_index.yaml → <agreement_id>.yaml   # via (role, province) lookup
3. (none — surface a "no user-CBA on file" note; fall through to Market MCP `get_cba_wage_scale`)
```

**Match strength**: a `cba-library/_index.yaml` entry matches when the engagement's `(role, province)` tuple is present in its `applies_to:` list AND the agreement's `expiry_date` is either in the future OR within the engagement's analysis window. Expired-by-more-than-12-months CBAs are NOT auto-loaded; surface them in the loaded-config summary as "expired CBA available — load explicitly with `/cba load <agreement-id>` to override."

**Cross-check**: when both a user-CBA AND a Market MCP `get_cba_wage_scale` result exist for the same agreement, the user-CBA wins for top-rate values, but the skill must surface a warning if top-rate delta exceeds 5% — this signals either MCP cache staleness or a misextraction in the user-provided data.

### Survey archive

Match key: `(vendor, year, regional_cut, role)` tuple.

```
1. survey-archive/<vendor>/<year>/<cut>.yaml      # exact match
2. survey-archive/<vendor>/<year-1>/<cut>.yaml    # prior year — load with aging warning
3. survey-archive/<vendor>/<year>/<adjacent-cut>.yaml   # adjacent regional cut — load with geo-adjustment warning
4. (none — prompt user to upload the survey)
```

**Staleness rule**: surveys > 18 months old MUST be flagged in the loaded-config summary; > 36 months old auto-suppress (do not load — prompt user to confirm or upload newer). Aging factor still applies per `survey-house-protocol.md`.

### Vocabulary glossary (FR-CA)

Match key: language (only `fr-ca` currently).

```
1. vocabulary/fr-ca-glossary.yaml         # canonical, post `/glossary promote`
2. (bundled) references/fr-ca-glossary.md  # seed/fallback — used as canonical when (1) does not exist
```

Per-engagement additions accumulate in `engagements/<slug>/fr-ca-additions.yaml` regardless of which canonical is active. `/glossary promote` walks the union of all engagement-level addition files, presents each candidate, on approval merges into `vocabulary/fr-ca-glossary.yaml` (creating it from the bundled seed if not yet present).

### Persona library (council)

Match key: persona pool resolution at council entry.

```
1. (bundled) references/council-mode.md § Persona pool   # the 7 default personas, always available
2. personas/_index.yaml → personas/<persona_id>.yaml     # custom personas, additive — never replace bundled
```

The pool is a **union**: bundled-7 ∪ repo-personas. Custom personas cannot override bundled personas with the same `id`; if a collision is detected, the skill must surface a warning and skip the custom one.

---

## Match-strength taxonomy

When the skill loads an asset, it must classify the match strength and surface it in the Phase 0 loaded-config summary. The user needs to know whether they got an exact-fit asset or a degraded fallback.

| Strength | Meaning | UX treatment |
|----------|---------|--------------|
| `exact` | Match key fully satisfied (e.g., `(vendor, year, cut, role)` all match) | Surface as confirmed: "Loaded: [asset]" |
| `aged` | Year-prior match for survey, or near-expiry CBA | Surface with year-shift note: "Loaded with aging: [asset] ([N] months old)" |
| `geo-adjusted` | Adjacent regional cut for survey | Surface with geo note: "Loaded geo-adjusted: [asset] ([from-cut] → [to-cut])" |
| `default-fallback` | No org-specific match; using `_default` brand kit | Surface as default: "Brand: _default (no org kit)" |
| `bundled-fallback` | Repo has no entry; using bundled seed | Surface as bundled: "Loaded from bundle: [asset] (no repo copy)" |
| `none` | No match anywhere | Surface as gap: "No [asset class] available — [recommended action]" |

The match-strength field travels with the asset for the entire engagement and is surfaced in the appendix of any deliverable that consumed it.

---

## Phase 0 loaded-config summary — required fields

When persistence backend resolves to `google-drive`, Phase 0 must surface to the user, before any analysis begins:

```
Loaded config summary:
  Persistence backend: google-drive (repo: <folder>)
  Brand kit: <org_slug or _default> [<override-files-listed>]
  CBA auto-loaded: <agreement_id> (<role>@<province>) [<match-strength>]
  Survey archive matches: <vendor> <year> <cut> [<match-strength>]
  Vocabulary: <repo-canonical | bundled-seed>
  Custom personas available: <persona_id_1>, <persona_id_2>, ... (or "none")
```

Each line is omitted when it has no content (e.g., no CBA matches → no CBA line). The summary is non-blocking; the user may proceed without acting on it, but it is the single moment where degraded-fallback or aged-data signals reach the user.

---

## Failure handling

- **Repo unreachable** (network failure, Google Drive (Claude.ai connector) misconfigured): fall through to bundled-fallback for everything; surface as "Persistence backend: paste-mode (repo unreachable)" in loaded-config summary; warn that auto-saves will not occur this session.
- **Repo file corrupt** (YAML parse fails, JS module throws on require): surface the exact filename and parse error to the user; do NOT silently fall back to default — this is a corruption signal the user needs to fix manually.
- **Asset class entirely missing from repo** (e.g., no `cba-library/` folder yet): treat as match-strength `none`; do not error.
- **Override-file collision** (e.g., persona `id` collision between bundled and custom): skip the custom one with a warning; the bundled one wins because the bundled set is the load-bearing default.
- **Brand kit master-file regen failure**: surface the offending master filename; do NOT fall back to a stale PPTX — by design, no stale PPTX exists post-Batch E. The user must fix the master file.

---

## Auto-save destinations (where post-engagement assets land)

| Asset | Auto-save destination | Trigger |
|-------|----------------------|---------|
| User-provided CBA | `cba-library/<agreement_id>.yaml` + update `_index.yaml` mapping | Post-extraction, after user confirms field values |
| Survey-house data | `survey-archive/<vendor>/<year>/<cut>.yaml` | Post-ingestion, after user confirms vendor + year + cut |
| FR-CA term added during engagement | `engagements/<slug>/fr-ca-additions.yaml` | When the skill encounters an unapproved term and the user provides the FR-CA equivalent |
| Brand-kit org scaffold | `branding/<org-slug>/` skeleton | `/brand-kit init <org-slug>` |

Auto-saves go through the standard close-time close-time write sequence pattern (`Drive batch write`) per `persistence-and-ledger.md` — they are NOT separate commits. This preserves the all-or-nothing close discipline.

---

## Done criteria

A library-resolution implementation is complete when:

- [ ] Phase 0 loaded-config summary surfaces all five asset classes (brand kit, CBA, survey, vocabulary, personas) with their match-strength tags
- [ ] Per-file brand kit override works (org override of one master file leaves other 17 inheriting from _default)
- [ ] Theme JSON deep-merge works (org palette.json with 3 keys overrides only those 3, rest inherit)
- [ ] CBA `(role, province)` index lookup auto-loads when scope matches; expired CBAs are flagged not auto-loaded
- [ ] Survey aged/geo-adjusted matches surface their warning class
- [ ] Vocabulary canonical resolves repo-first when present, bundle-fallback when not
- [ ] Custom personas appear in council pool; bundled personas always present; collision skipped with warning
- [ ] Repo-unreachable fallback works without erroring; surfaces as paste-mode
- [ ] Asset-corruption surfaces filename + parse error, does NOT silently fall back

---

## Anti-patterns

1. **Silent fallback to bundle.** When a repo file is corrupt, the skill MUST surface the error, not silently use the bundle. Hidden fallback masks user data corruption.
2. **Auto-save on every change.** Auto-saves are batched into the close-time commit. Per-change commits would shred ledger atomicity and bloat repo history.
3. **Cross-class fallback.** A missing brand kit does NOT cause CBA library to fall back; each asset class resolves independently. Failure isolation prevents cascade.
4. **Override without surface.** When an org brand kit overrides a master, the loaded-config summary MUST list which masters were overridden. Hidden overrides surprise the user when the deck looks different than expected.
5. **Bundled-canonical for vocabulary after promotion.** Once `vocabulary/fr-ca-glossary.yaml` exists in the repo, the bundled file is seed/fallback ONLY — never re-read as canonical, even for engagements that don't reference any custom terms.
