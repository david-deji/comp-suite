# Brand Kit Protocol

Governs how brand kits are structured, resolved, scaffolded, and regenerated. Loaded by SKILL.md at Phase 6a entry (deck production) and on `/brand-kit init`.

For the cross-asset resolution principle (repo-first / bundled-fallback), see `library-resolution.md`. This file covers brand-kit-specific structure and lifecycle.

---

## Structure

A brand kit is a directory of files, persisted in the `market` MCP backend (`brand_get_kit` / `brand_list_files` / `brand_get_file` for reads; `brand_put_kit` / `brand_put_file` / `brand_put_logo` for writes) and cached locally under `branding/` in `$STATE_ROOT`:

```
branding/
├── _default/                            # the seed kit, always present
│   ├── build_template.js                # entry point — loads theme + masters, writes pptx
│   ├── theme/
│   │   ├── palette.json                 # color tokens (C lookup)
│   │   ├── typography.json              # font tokens (F lookup) + size scales
│   │   ├── logo.svg                     # vector logo
│   │   ├── logo-large.png               # raster, on-light large
│   │   ├── logo-small.png               # raster, on-light small (corner mark)
│   │   ├── logo-white-large.png         # raster, on-dark large
│   │   └── logo-white-small.png         # raster, on-dark small (corner mark)
│   ├── masters/
│   │   ├── _helpers.js                  # shared layout-tag, footer, corner-logo factories
│   │   ├── 01-title.js                  # one file per slide master + demo
│   │   ├── 02-toc.js
│   │   └── ... (18 files total)
│   └── footnotes.yaml                   # per-jurisdiction disclaimers, methodology language
└── <org-slug>/                          # per-org override, only diverging files
    └── (any subset of _default's structure)
```

The bundle ships a complete `_default` at `template_assets/branding/_default/`. The repo's `branding/_default/` is created on first `/brand-kit init` and seeded from the bundle. Per-org kits are created via `/brand-kit init <org-slug>` and contain ONLY the files that diverge from `_default`.

---

## Override granularity

Each file in a brand kit is independently overridable:

- **Theme JSONs (`palette.json`, `typography.json`)**: deep-merge override. The org file may declare only the keys that diverge; missing keys inherit from `_default`. Example: `branding/acme/theme/palette.json` with just `{"green": "00A36C", "deepPurple": "1E3A8A"}` overrides those two colors and inherits the rest.
- **Logo files**: full-file replacement. The org logo, when present, replaces the default entirely. All five logo variants should be provided as a set (or all five fall back to `_default`); mixing org logos with default logos creates visual inconsistency.
- **Master JS files**: full-file replacement per master. Override `01-title.js` to change the cover slide; the other 17 masters continue to inherit from `_default`. The override file must export the same `register({pres, C, F, helpers, logoPaths})` contract as the default.
- **`footnotes.yaml`**: full-file replacement. The org file, when present, replaces the default entirely; the user is responsible for including all required disclaimer keys.
- **`build_template.js`**: NOT typically overridden. The entry point resolves theme + masters from the right paths automatically. Override only if the org needs a fundamentally different render flow (rare; most use cases are covered by overriding masters).

---

## Master snippet contract

Every file under `masters/` (except `_helpers.js`) must export a function `register({pres, C, F, helpers, logoPaths})` that:

1. Calls `pres.defineSlideMaster({...})` once with a `title` matching the file's layout (e.g., `"01_TITLE"` for `01-title.js`).
2. Optionally adds a demo slide via `pres.addSlide({masterName: "01_TITLE"})`. Demo slides illustrate intended usage and ship in the generated template; they are deleted by the author when starting a real deck.
3. Reads brand tokens from the `C` (palette) and `F` (typography) lookups passed in — does not hardcode colors or fonts.
4. Reads logo paths from the `logoPaths` object — does not hardcode paths.
5. Reads helper factories from the `helpers` object (`cornerLogo`, `cornerLogoWhite`, `makeLayoutTag`, `makeLayoutTagWhite`, `makeFooter`, `makeFooterWhite`, `masterObjects`, `addTitleSubtitle`).

The contract is deliberately narrow: a master file does not have access to the file system, environment variables, or other masters. This isolation makes per-file overrides safe.

---

## `/brand-kit init <org-slug>`

Scaffolds a new brand kit for `<org-slug>`, persisted to the `market` MCP backend via `brand_put_kit` / `brand_put_file`.

**Behavior:**

1. Resolve the caller's org from OAuth identity via `list_my_orgs`. If the identity has no matching org membership, surface error and abort — org creation is admin-path (D4), not a `/brand-kit` operation.
2. Verify the org's `_default` brand kit exists in the backend (via `brand_list_files`). If not, seed it from the bundled `template_assets/branding/_default/` first (one-time auto-seed) and persist via `brand_put_file` (each with `expected_version: 0`).
3. Verify `branding/<org-slug>/` does NOT already exist. If it does, surface "Org kit already exists at branding/<org-slug>/. Use direct file edit to modify, or `/brand-kit reset <org-slug>` to start over." Abort.
4. Scaffold the divergence-points only:
   - `branding/<org-slug>/theme/palette.json` with placeholder content: `{"_meta": {"name": "<org-slug> palette", "inherits_from": "_default"}, "green": "<HEX>", "deepPurple": "<HEX>"}` and a comment header explaining override semantics.
   - `branding/<org-slug>/theme/logo-placeholder.txt` with instructions: "Drop logo.svg, logo-large.png, logo-small.png, logo-white-large.png, logo-white-small.png here. All five required as a set."
   - `branding/<org-slug>/footnotes.yaml` with placeholder content showing the schema.
   - `branding/<org-slug>/_README.md` explaining the override pattern, listing which files exist, and pointing to `branding/_default/` for the master JS files that haven't been overridden.
5. Persist the scaffold to the backend via `brand_put_kit` + `brand_put_file` (each with `expected_version: 0` to create).
6. Surface to user: "Brand kit branding/<org-slug>/ scaffolded. Edit theme/palette.json + drop logo files to customize. To override a slide master, copy the file from `_default/masters/` to `<org-slug>/masters/` and edit. Engagements that set `engagement.config.brand.org_slug: <org-slug>` will use this kit."
7. Do NOT regenerate any deck — that happens on the next engagement that uses the kit.

---

## Regeneration discipline (Phase 6a)

At Phase 6a entry, the skill regenerates the brand template fresh from `build_template.js` rather than using a cached PPTX. This is the load-bearing reason no bundled PPTX exists post-Batch E.

**Sequence:**

1. Resolve `brand.org_slug` from engagement config (default `_default`).
2. Run the regeneration in the Claude.ai scratch space:
   - `cd` to a temp working dir.
   - Copy `branding/_default/` from the bundle (or fetch the org's kit from the backend via `brand_get_kit` / `brand_list_files` / `brand_get_file`).
   - If `org_slug != _default`, fetch `branding/<org_slug>/` overlay on top.
   - Set `ORG=<org-slug>` env var.
   - Run `node build_template.js`.
   - Read the produced PPTX as the engagement's brand template.
3. Surface to user the regenerated template: "Brand template regenerated from <org_slug> kit. <N> overrides applied: <list>."
4. Proceed with Phase 6 deck assembly using the regenerated template as base.

**Failure handling:**

- **`node` not available in scratch space**: surface "Cannot regenerate brand template — Node.js not available. Falling back to manual deck construction without master inheritance." This is a degraded mode; the deck will not have the brand kit's slide masters. User is told explicitly.
- **`pptxgenjs` install fails**: same degraded mode as above.
- **A master file throws on `register()`**: surface the offending filename + error message: "Master `<filename>` failed during regeneration: <error>. Fix the file in branding/<org_slug>/masters/ and retry." Do NOT fall back to a stale PPTX (none exists). Do NOT skip the master and continue (would produce a broken deck).
- **Theme JSON parse error**: surface filename + JSON error position. Same fail-loud discipline.
- **Missing logo file**: surface "Logo `<path>` not found in branding/<org_slug>/theme/. Falling back to `_default` logo for this variant." This IS a soft fallback because logos are non-critical to deck structural integrity.

---

## Drift between repo `_default` and bundled `_default`

Over time, the bundled `_default` may evolve (new master added, palette refresh, helpers refactor). The repo's `branding/_default/` was seeded from the bundle on first `/brand-kit init` and does not auto-update.

**Drift surfacing:**

At Phase 0 loaded-config summary, when `branding/_default/` exists in the repo, the skill compares its file list against the bundled `template_assets/branding/_default/` and surfaces:

```
Brand kit drift:
  Repo _default: 18 masters, palette v2, typography v2
  Bundle _default: 19 masters (NEW: 19-comparison-matrix.js), palette v2, typography v2
  → Run `/brand-kit refresh _default` to merge bundle additions (preserves your overrides).
```

The user opts in to refresh; the skill never auto-merges. Refresh logic: bundle files NOT in repo are added; bundle files that ARE in repo are NOT touched (preserves user customization to `_default`).

---

## Done criteria

A brand kit implementation is complete when:

- [ ] Phase 6a regenerates `<ORG>_Comp_Deck_Template.pptx` from the resolved brand kit before deck assembly
- [ ] `/brand-kit init <org>` scaffolds `branding/<org>/` with placeholder palette + logo instructions + README
- [ ] An override of `branding/<org>/masters/01-title.js` produces a deck with the new cover; other masters inherit from `_default`
- [ ] An override of `branding/<org>/theme/palette.json` with partial keys deep-merges over `_default`'s palette
- [ ] Drift between repo `_default` and bundled `_default` is surfaced at Phase 0 with a `refresh` recommendation
- [ ] Master regen failure surfaces the filename + error; does NOT fall back to a stale PPTX
- [ ] No bundled `Comp_Deck_Template.pptx` exists in the .skill bundle

---

## Anti-patterns

1. **Caching the regenerated PPTX between engagements.** Each engagement regenerates fresh; brand kits change, masters get edited, the cost of regen is small (~2 sec) compared to the cost of a stale brand deck.
2. **Copying all 18 master files into a new org kit.** Override only what diverges; let `_default` carry the rest. Copying everything fragments maintenance — when `_default` adds a new master, the org kit doesn't get it automatically.
3. **Mixing org-specific content into bundled `_default`.** The bundled `_default` ships with the skill and is read-only at runtime. Persist customizations to the `market` backend via `brand_put_*` — never modify the bundle in place.
4. **Hardcoded colors in master JS files.** Always read from the `C` lookup. A hardcoded `"#4AA447"` in `01-title.js` makes per-org palette overrides impossible.
5. **Master file with side effects beyond `register()`.** A master file should not write files, fetch URLs, or read environment variables (other than what the entry point passes in). Side effects break the snippet contract and make per-file overrides unsafe.
6. **`/brand-kit init` against an existing org-slug.** The command must abort, not overwrite. Overwriting silently loses customization the user spent time on.

---

## v2 path adaptation (appended on port)

This file is a verbatim port of v1 `_shared/references/brand-kit-protocol.md` (commit `47cfd1e`). The body above describes v1 paths; resolve them in v2 as:

| v1 reference | v2 destination |
|---|---|
| `branding/_default/` (the bundled seed) | `$ASSET_ROOT/_modes/advisor/templates/branding/_default/` |
| `branding/<org-slug>/` (per-org override) | `$STATE_ROOT/_orgs/<slug>/brand/` |
| `template_assets/branding/_default/` | `$ASSET_ROOT/_modes/advisor/templates/branding/_default/` (same as seed) |
| `library-resolution.md` (cross-ref) | `$ASSET_ROOT/_modes/advisor/references/library-resolution.md` |
| The local cache + regeneration working root (authoritative store is the `market` backend via `brand_get_kit` / `brand_put_*`) | `$STATE_ROOT/_orgs/<slug>/` |

### Org-creation seeding flow

When the orchestrator's `engagement-create` primitive runs `find_or_create_org(<slug>)` and the org doesn't exist:

1. Create `$STATE_ROOT/_orgs/<slug>/`
2. `cp -r $ASSET_ROOT/_modes/advisor/templates/branding/_default/* $STATE_ROOT/_orgs/<slug>/brand/`
3. Update `$STATE_ROOT/_orgs/index.yaml` per `orgs-index.schema.json`
4. Initialize `master.yaml` skeleton

Per-org overrides are authored by editing the local working copy under `$STATE_ROOT/_orgs/<slug>/brand/`, then persisted to the backend via `brand_put_*` (per Anti-pattern 3) — the local edit alone is not persistence; the `market` backend is the authoritative store (persistence contract D2). The `branding/<org-slug>/` overlay pattern from v1 is collapsed in v2: each org gets a complete brand directory (no `_default` fallback at runtime), seeded once from the advisor template.

### Primitive contract

- **Inputs:** `(org_slug)`
- **Outputs:** brand directory path + parsed `palette.json` dict + parsed `typography.json` dict + parsed `footnotes.yaml` dict + render block string for prompt injection
- **Resolves:** `$STATE_ROOT/_orgs/<slug>/brand/`
- **Asserts:** `theme/palette.json`, `theme/typography.json`, `footnotes.yaml` exist; warns if logos missing; ERRORS if `masters/` is missing AND mode is advisor
- **Render block:** prompt-injectable summary of palette key colors + typography heading/body + active footnote keys
- **Schema:** validates per-org brand directory presence against `$ASSET_ROOT/_core/schemas/brand-kit.schema.json`
