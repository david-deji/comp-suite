# Brand Kit Protocol

Governs how brand kits are structured, resolved, written, and regenerated. Under P4b the brand kit is
**backend state served by the `market` MCP server** (MIM-0041): theme (palette/typography/footnotes),
render files (`build_template.js`, `masters/*.js`), and logos all live in the backend and are read via
`brand_get_kit` / `brand_list_files` / `brand_get_file` and written via `brand_put_kit` / `brand_put_file`
/ `brand_put_logo`. Local disk is used ONLY as a scratch materialization for `node` rendering — the server
stores render templates as opaque text and never executes them (AG-B2). Loaded by SKILL.md at Phase 6a
(deck production) and on `/brand-kit init`.

---

## Structure

A brand kit is a set of backend records for an org:

```
brand kit (org = <slug>, served by `market` MCP)
├── theme            (brand_get_kit / brand_put_kit)
│   ├── palette       — color tokens (C lookup), jsonb
│   ├── typography    — font tokens (F lookup) + size scales, jsonb
│   └── footnotes     — per-jurisdiction disclaimers / methodology, raw text
├── render files     (brand_list_files / brand_get_file / brand_put_file) — opaque text, never executed server-side
│   ├── build_template.js   — entry point: loads theme + masters, writes pptx (run LOCALLY)
│   ├── masters/_helpers.js — shared layout/footer/corner-logo factories
│   └── masters/NN-*.js      — one file per slide master (+ demo)
└── logos            (brand_put_logo; metadata in brand_get_kit) — 5 variants in Supabase Storage
    ├── logo.svg, logo-large.png, logo-small.png, logo-white-large.png, logo-white-small.png
```

The `_default` seed kit ships bundled at `$ASSET_ROOT/_modes/advisor/templates/branding/_default/`. A new
org's kit is seeded into the backend from that bundle on first provisioning (admin/import path); per-org
edits are written back via `brand_put_*`.

---

## Storage posture (P4b)

- **Canonical store = the `market` backend.** Reads: `brand_get_kit` (theme + file index + logo metadata),
  `brand_list_files` (render-file paths + versions), `brand_get_file {file_path}` (one file's content).
  Writes: `brand_put_kit` (theme, optimistic `expected_version`), `brand_put_file {file_path, content,
  expected_version}` (one render file), `brand_put_logo` (a logo variant → Storage).
- **Local disk = render scratch only.** Regeneration materializes the kit's files to a temp dir to run
  `node build_template.js`; that scratch is disposable, never the source of truth.
- **MCP-primary, transport-only fallback** (P4b D1): a tool *not-found* is authoritative (the file/kit
  doesn't exist in the backend); only a *transport* failure falls back to reading a local cached copy, and
  brand WRITES are blocked while MCP is unreachable (P4b D2 — no local-and-reconcile).

---

## Override granularity

Each record is independently overridable in the backend:

- **Theme (`palette` / `typography`)**: deep-merge semantics are applied client-side before
  `brand_put_kit`; store the merged result. Footnotes are raw text, full replacement.
- **Render files (`masters/NN-*.js`, `build_template.js`)**: full-content replacement per file via
  `brand_put_file`. An override master must export the same `register({pres, C, F, helpers, logoPaths})`
  contract.
- **Logos**: full replacement via `brand_put_logo`; provide all five variants as a set (or none — they
  fall back to `_default`); mixing org + default logos creates visual inconsistency.
- **`build_template.js`**: rarely overridden; the entry point resolves theme + masters by path.

---

## Master snippet contract

Every file under `masters/` (except `_helpers.js`) must export `register({pres, C, F, helpers, logoPaths})` that:

1. Calls `pres.defineSlideMaster({...})` once with a `title` matching the file's layout (e.g. `"01_TITLE"`).
2. Optionally adds a demo slide via `pres.addSlide({masterName: "01_TITLE"})`.
3. Reads brand tokens from the `C` (palette) and `F` (typography) lookups — never hardcodes colors/fonts.
4. Reads logo paths from `logoPaths` — never hardcodes paths.
5. Reads helper factories from `helpers` (`cornerLogo`, `cornerLogoWhite`, `makeLayoutTag`,
   `makeLayoutTagWhite`, `makeFooter`, `makeFooterWhite`, `masterObjects`, `addTitleSubtitle`).

The contract is deliberately narrow: a master file has no access to the file system, env, or other
masters. This isolation makes per-file overrides safe — and is why the backend can store them as opaque
text and let comp-suite execute them locally.

---

## `/brand-kit init <org-slug>`

Scaffolds a new org brand kit in the backend.

1. Resolve the org via `engagement_get_master {org_slug}` (must be provisioned — admin path, P4b D4).
2. Confirm the org has no brand kit yet: `brand_get_kit {org_slug}` returns an empty/`found:false` theme.
   If a kit exists → "Org kit already exists. Edit via `brand_put_*`, or reset deliberately." Abort.
3. Seed from the bundled `_default` (`$ASSET_ROOT/_modes/advisor/templates/branding/_default/`):
   - `brand_put_kit {org_slug, palette, typography, footnotes, expected_version: 0}` from the default theme.
   - For each default render file: `brand_put_file {org_slug, file_path, content, expected_version: 0}`.
   - For each of the 5 logo variants: `brand_put_logo {org_slug, ...}`.
4. Surface: "Brand kit for <org-slug> seeded in the backend. Override a master with `brand_put_file`
   (path `masters/NN-*.js`); override theme with `brand_put_kit`. Engagements with
   `engagement.config.brand.org_slug: <org-slug>` use this kit."
5. Do NOT regenerate a deck — that happens on the next engagement that uses the kit.

Writes are MCP-only (P4b D2); on transport failure, escalate — never write a local kit.

---

## Regeneration discipline (Phase 6a)

At Phase 6a entry, regenerate the brand template fresh from the backend kit — no cached PPTX.

**Sequence:**

1. Resolve `brand.org_slug` from engagement config (default `_default`).
2. Materialize the kit to a local scratch dir:
   - `brand_list_files {org_slug}` → the render-file paths.
   - For each path: `brand_get_file {org_slug, file_path}` → write its content into `scratch/branding/<slug>/<path>`.
   - `brand_get_kit {org_slug}` → write `theme/palette.json`, `theme/typography.json`, `footnotes.yaml`,
     and fetch the 5 logo files (from the Storage URLs in the kit's logo metadata) into `theme/`.
3. `cd scratch/branding/<slug>` ; set `ORG=<org-slug>` ; run `node build_template.js`. **Render runs
   LOCALLY** — the server stores templates as opaque text and never executes them (AG-B2 / INV-02).
4. Read the produced PPTX as the engagement's brand template; surface "Brand template regenerated from
   <org_slug> kit (<N> files materialized)."

**Failure handling:**

- **MCP unreachable**: if a local materialization from a prior run exists, warn and render from it
  (read-cache, P4b D1); else escalate "cannot regenerate — backend unreachable and no local materialization."
- **`node` / `pptxgenjs` unavailable in scratch**: degraded mode — "Cannot regenerate — Node.js not
  available; falling back to manual deck construction without master inheritance." (told explicitly).
- **A master throws on `register()`**: surface the filename + error; fix in the backend via `brand_put_file`
  and retry. Do NOT skip the master (broken deck) or fall back to a stale PPTX (none exists).
- **Theme JSON parse error**: surface filename + JSON position; same fail-loud discipline.
- **Missing logo variant**: soft fallback to the `_default` logo for that variant (logos are non-critical to
  structural integrity).

---

## Primitive contract

- **Inputs:** `(org_slug)`
- **Outputs:** parsed `palette` dict + `typography` dict + `footnotes` + render-file index + logo metadata
  (all from `brand_get_kit` / `brand_list_files`), plus a render block string for prompt injection.
- **Reads:** `brand_get_kit` / `brand_list_files` / `brand_get_file` (MCP-primary; local scratch is a
  transport-failure read cache only).
- **Writes:** `brand_put_kit` / `brand_put_file` / `brand_put_logo` (MCP-only; escalate on transport failure).
- **Asserts:** theme present (palette + typography); warns if logos missing; ERRORS if `masters/` index is
  empty AND mode is advisor.
- **Render block:** prompt-injectable summary of palette key colors + typography heading/body + active
  footnote keys.

---

## Anti-patterns

1. **Caching the regenerated PPTX between engagements.** Each engagement regenerates fresh from the backend
   kit; the cost is ~2 s vs. a stale brand deck.
2. **Writing brand state to `$STATE_ROOT`.** Under P4b the backend owns the kit; local is render scratch
   only. A local brand edit diverges from the backend (the failure P4a ended).
3. **Falling back to local on a brand-tool *not-found*.** Not-found is authoritative (the file doesn't
   exist in the backend); only a transport failure uses the local materialization.
4. **Hardcoded colors in master JS.** Always read from `C`. A hardcoded hex makes per-org palette overrides
   impossible.
5. **A master file with side effects beyond `register()`** (file/env/network). Breaks the snippet contract
   and the server's opaque-text storage model.
6. **`/brand-kit init` against an org that already has a kit.** Abort, don't overwrite — overwriting loses
   customization.
