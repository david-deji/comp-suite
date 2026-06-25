# /brand Mode Protocol

`/brand` reads or writes the comms-templates extension of the shared brand kit. **The base brand kit is shared across the comp-* trilogy** — same `branding/<org-slug>/` folder, same `_default` fallback, same regeneration discipline. comp-comms-builder adds a `comms-templates/` subdirectory only; it never modifies sibling-owned brand kit files.

Loaded by SKILL.md when intent-router classifies as `/brand`. Loads `brand-kit-protocol.md` (mirrored from compensation-advisor) for the canonical structure and regeneration discipline.

This protocol is a **thin wrapper** around `brand-kit-protocol.md`. Where the canonical protocol is silent on comms-specific concerns, this file fills the gap.

---

## 1. Non-destructive extension rule

comp-comms-builder ONLY writes inside `branding/<org-slug>/comms-templates/`. It NEVER writes to:

- `branding/<org-slug>/theme/` — owned by compensation-advisor and comp-team-transformer
- `branding/<org-slug>/logo.{svg,png}` and logo variants — owned by compensation-advisor
- `branding/<org-slug>/masters/` — PPTX master infrastructure owned by compensation-advisor
- `branding/<org-slug>/footnotes.yaml` — owned by compensation-advisor

Violation of this rule corrupts sibling skills' brand rendering. Enforce hard — no exceptions even if operator requests it.

---

## 2. Subcommands

### 2.1 `/brand show`

Read-only. Prints the resolved comms-templates summary for the engagement's configured `org_slug`:

```
Comms-templates summary: <org-slug>

Templates present:
  docx-master:    <found / not found>
  pdf-master:     <found / not found>
  email-header:   <found / not found>
  email-signatures: <ceo, chro, vp-ops, manager> — <all found / <N> missing>
  pptx-master:    <found / not found>

Bundled _default status:
  Source: template_assets/branding/_default/comms-templates/
  Drift: <up-to-date / run /brand init <org-slug> to sync>

Base brand kit status:
  theme/palette.json:     <found / not found>
  logo.svg:               <found / not found>
  masters/:               <N> master files
  footnotes.yaml:         <found / not found>
```

No write. Useful before `/draft` or `/cascade` to confirm the renderer has what it needs.

### 2.2 `/brand init <org-slug>`

Scaffolds `comms-templates/` inside an existing (or new) `branding/<org-slug>/` folder under local `$STATE_ROOT`. Non-destructive.

**Sequence:**

1. Verify the `market` backend is reachable (Phase 0 check passed). Abort if in transport-failure cache-fallback mode.
2. Verify `branding/<org-slug>/` exists under `$STATE_ROOT` OR is safe to create. Surface if it does not exist: "No brand kit folder found for `<org-slug>`. I'll create the folder and seed comms-templates. The base brand kit (theme, logo, masters) must be set up separately via compensation-advisor's `/brand-kit init`."
3. Verify `branding/<org-slug>/comms-templates/` does NOT already exist. If it does, surface: "comms-templates already initialized for `<org-slug>`. Run `/brand show` to inspect, or delete the subdirectory manually to re-initialize."
4. Copy all files from `template_assets/branding/_default/comms-templates/` to `branding/<org-slug>/comms-templates/`. Files to copy:
   - `docx-master.docx`
   - `pdf-master.yaml`
   - `email-header.html`
   - `email-signature/ceo.txt`
   - `email-signature/chro.txt`
   - `email-signature/vp-ops.txt`
   - `email-signature/manager.txt`
   - `pptx-master/` (directory with contents)
5. Run the comms-templates overrides interview (see § 2.3 below).
6. Write to `branding/<org-slug>/comms-templates/` under `$STATE_ROOT` per `persistence-and-ledger.md`.
7. Surface: "comms-templates initialized for `<org-slug>` at `branding/<org-slug>/comms-templates/`. Base brand kit files (theme, logo, masters) are untouched."

### 2.3 Comms-templates overrides interview (runs after step 4 above)

Sequential prompt → answer → confirm. All optional — operator may hit enter/skip on any.

1. **Email header banner** — "What hex color should the email banner use? (default: pulled from base `theme/palette.json` primary color, or #003366 if not found)"
2. **Email signature style** — "Should speaker signatures use first-last name, first name only, or a fixed string? (e.g., `[First Name], Chief People Officer, Acme Inc.`)" — applied to all signature variants; operator may differentiate per speaker.
3. **PDF page header** — "Should PDFs include a logo in the header? (default: yes, uses base brand logo). If yes, which variant? (svg | large | small | white-large | white-small)"
4. **PPTX accent color** — "The exec one-pager inherits the compensation-advisor PPTX master. Should the comms one-pager slide accent match the master or use a custom color?" (default: inherit master)
5. Confirm full override set, then apply and write.

### 2.4 `/brand` (no subcommand)

Default behavior: read-only summary equivalent to `/brand show`. Prefer `/brand show` for clarity.

---

## 3. Auto-seed on first `/draft`

If `/draft` or `/cascade` is called and `branding/<org-slug>/comms-templates/` is absent, the skill auto-seeds it from `template_assets/branding/_default/comms-templates/` WITHOUT running the overrides interview. Surface:

> "Auto-seeded comms-templates from `_default` — run `/brand init <org-slug>` to specialize (header colors, signature style, PDF branding)."

This ensures cold-start drafts produce usable output. The override interview is optional, not blocking.

---

## 4. What comms-templates contains

| File | Purpose |
|---|---|
| `docx-master.docx` | Branded DOCX template for manager-faq and hrbp-enablement-memo |
| `pdf-master.yaml` | PDF render configuration (header, footer, margin, logo placement) |
| `email-header.html` | HTML banner block injected at top of all-hands email body |
| `email-signature/ceo.txt` | Plain-text signature block for CEO-signed artifacts |
| `email-signature/chro.txt` | Plain-text signature block for CHRO-signed artifacts |
| `email-signature/vp-ops.txt` | Plain-text signature block for VP Ops-signed artifacts |
| `email-signature/manager.txt` | Plain-text signature block for manager-distributed artifacts |
| `pptx-master/` | 1-3 slide exec one-pager template overrides (extends base `masters/` without replacing) |

---

## 5. Failure handling

- **Backend unreachable during init** — surface each file body in chat with explicit save-to-`$STATE_ROOT` instructions per file path. No silent failure.
- **`template_assets/branding/_default/comms-templates/` missing from bundle** — hard error: "Bundle is corrupt — `_default/comms-templates/` not found. Re-download the skill bundle."
- **`docx-master.docx` write failure** — surface: "DOCX master write failed. Check `$STATE_ROOT` write permissions. Proceeding without DOCX master — `/draft` will fall back to unbranded DOCX output."
- **Org slug collision with sibling-owned file** — refuse write if the target path is inside `theme/`, `logo.*`, `masters/`, or `footnotes.yaml`. Surface the refusal with exact path.

---

## 6. What this protocol does NOT contain

- Brand kit structure, override granularity, master snippet contract, regeneration discipline — those live in `brand-kit-protocol.md` (mirrored, canonical at compensation-advisor).
- PPTX master infrastructure detail — that lives in `template-master.md` (mirrored) and `references/artifact-catalog.md` § exec-one-pager.
- Per-artifact slot-construction logic — that lives in `draft-protocol.md` and `cascade-protocol.md`.
- PPTX QA dimensions — that lives in `production-and-qa.md` (mirrored).
