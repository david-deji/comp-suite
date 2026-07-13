# /brand Mode Protocol

`/brand` reads or writes the engagement brand kit. **The brand kit is shared across the comp-* trilogy** — same `branding/<org-slug>/` folder, same `_default` fallback, same per-org override semantics, same regeneration discipline. comp-training-designer reads from this single source; `/brand` writes here.

Loaded by SKILL.md when intent-router classifies as `/brand`. Loads `brand-kit-protocol.md` (mirrored from compensation-advisor) for the canonical structure, override granularity, and master snippet contract.

This protocol is a **thin wrapper** around `brand-kit-protocol.md`. Where the canonical protocol is silent on training-specific concerns, this file fills the gap.

---

## Subcommands

### `/brand show`

Read-only. Prints the resolved brand kit summary for the engagement's configured `org_slug`:

```
Brand kit summary: <org-slug>

Theme:
  Palette: <N> color tokens (primary, secondary, accent, ...)
  Typography: <N> font tokens (heading: <font>, body: <font>, ...)
Logo: <N> variants (svg, large/small, light/dark) — paths resolved
Masters: <N> active (<N> overridden from _default, <N> inherited)
Footnotes: <N> jurisdiction entries

Drift status:
  Repo _default: <N> masters, palette v<N>, typography v<N>
  Bundle _default: <N> masters (<NEW additions if any>), palette v<N>, typography v<N>
  Recommendation: <up-to-date | run /brand-kit refresh _default>
```

No write. Useful before `/generate` to confirm what the renderer will produce.

### `/brand init <org-slug>`

Scaffolds a new brand kit for `<org-slug>`, persisted via `brand_put_kit` / `brand_put_file` / `brand_put_logo`. **Delegates to canonical `brand-kit-protocol.md` § `/brand-kit init <org-slug>`**. Same behavior:

1. Resolve org membership via `list_my_orgs` (the `market` backend is the brand-kit source of truth). Abort if `<org-slug>` is not a known org.
2. Verify `branding/_default/` exists in the repo. Seed from bundle if not (one-time).
3. Verify no brand kit exists for `<org-slug>` (`brand_get_kit` returns not-found). Abort with friendly message if it does.
4. Scaffold divergence-points only: `theme/palette.json` placeholder, logo placeholder instructions, `footnotes.yaml` placeholder, `_README.md`.
5. Persist via `brand_put_kit` / `brand_put_file` (+ `brand_put_logo` when logos are provided).
6. Surface to user with edit instructions.
7. Do NOT regenerate any deck — that happens on next `/generate` or `/cascade`.

### `/brand` (no subcommand)

Default behavior: read-only summary equivalent to `/brand show`. Prefer `/brand show` for clarity.

---

## What's specific to comp-training-designer

The canonical `brand-kit-protocol.md` covers everything structural. Two training-specific concerns added here:

### 1. Training-deck masters (v1 master inheritance)

v1 reuses the existing 18 masters from `_default/masters/` (designed for comp-advisor decision decks). Training-specific layouts (poll slide, knowledge-check slide, scenario card slide, retrieval-prompt slide) currently render as **content masters with embedded interactive-block markdown rather than dedicated layouts**.

This is intentional in v1 — adding 4 new training masters would force per-org kits to track an 18→22 master delta, complicating the override pattern. v2 may add the 4 training masters; until then, `/generate` produces poll/quiz/scenario/retrieval slides using the existing `04-section-divider.js` or `09-callout.js` masters with the interactive-block markdown rendered as bullet content.

### 2. Per-audience cover slide variants

Each audience deck (`employees.pptx`, `managers.pptx`, `hrbps.pptx`, `execs.pptx`) uses the same `01-title.js` master but with audience-specific subtitle metadata:

- **employees**: subtitle = "Your <cycle-name> Comp Update"
- **managers**: subtitle = "<cycle-name> Manager Briefing"
- **hrbps**: subtitle = "<cycle-name> HRBP Briefing"
- **execs**: subtitle = "<cycle-name> Executive Review"
- **managers-cascade-kit**: subtitle = "Team Meeting: <cycle-name>"

The cover-slide subtitle template lives in `template_assets/facilitator_guide_template.md` § Cover Slide Conventions. Per-org kits MAY override `01-title.js` to change cover layout; the audience-specific subtitle injection happens at slide-construction time regardless.

The `delivery_target` metadata is stamped as a small line on the cover slide (below the subtitle), per `cycle-awareness.md`.

---

## /brand init flow (delegated detail)

Per `brand-kit-protocol.md` § Structure, the scaffold creates:

```
branding/<org-slug>/
├── theme/
│   ├── palette.json                # placeholder with primary + secondary slot
│   └── logo-placeholder.txt        # instructions to drop logo files
├── footnotes.yaml                  # placeholder with schema
└── _README.md                      # override pattern + which files exist
```

The five logo variants (`logo.svg`, `logo-large.png`, `logo-small.png`, `logo-white-large.png`, `logo-white-small.png`) must be provided as a set when the operator drops in real assets. Mixing org logos with default logos creates visual inconsistency; per `brand-kit-protocol.md` § Override granularity.

---

## Failure handling

Per `brand-kit-protocol.md` § Regeneration discipline. Repeated here for clarity:

- **`node` not available in Claude.ai scratch space** — surface "Cannot regenerate brand template — Node.js not available. Falling back to manual deck construction without master inheritance." Degraded mode.
- **`pptxgenjs` install fails** — same degraded mode.
- **Master file throws on `register()`** — surface offending filename + error. Do NOT fall back to a stale PPTX (none exists). Operator must fix the file.
- **Theme JSON parse error** — surface filename + JSON error position. Same fail-loud.
- **Missing logo file** — surface "Logo `<path>` not found. Falling back to `_default` logo for this variant." Soft fallback (logos are non-critical to deck structural integrity).

---

## What this protocol does NOT contain

- Brand kit structure, override granularity, master snippet contract, regeneration discipline, anti-patterns — those live in `brand-kit-protocol.md` (mirrored, canonical at compensation-advisor).
- PPTX QA dimensions — those live in `production-and-qa.md` (mirrored).
- Per-deck slide-construction logic — that lives in `generate-protocol.md` and `cascade-protocol.md`.

This file is the comp-training-designer-specific layer atop the canonical brand-kit-protocol.
