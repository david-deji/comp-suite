# visual-qa

Comp-suite v2 primitive. Renders any `.pptx` deliverable to per-slide PNG images
so the orchestrator can visually inspect what it just produced **before** announcing
done. Closes the gap that ships visible defects (missing logos, text overflow,
slide-edge clipping) when the orchestrator only checks file size or "wrote N bytes."

## Why this exists

The orchestrator can write a `.pptx`, see no error, and declare success — while
the rendered slide has overlapping text, a bar that runs off the slide edge, or a
logo that was never embedded. File size and stdout success are not visual quality
signals. This primitive forces a render-then-look loop.

Logged friction events that motivate this primitive:
- Brand-kit showcase shipped a text wordmark instead of `addImage(logoPaths.whiteLarge)` — caught only on user review.
- Stakeholder pre-read decks shipped with title/subtitle overlap on the cover, narrow-bar text overflow on the timeline, and a next-step callout clipped by the slide bottom — three defects across one batch, all visible at first glance, none surfaced by the producer.

See `$STATE_ROOT/harness/friction.jsonl` events with `target_class: primitive` /
`target_path: _core/primitives/visual-qa.md`.

## Contract

| | |
|---|---|
| **Inputs** | `pptx_paths: list[str]` — absolute or repo-relative paths to `.pptx` files |
| **Outputs** | `{rendered: list[dict], errors: list[dict]}` — PNG paths + render metadata + any toolchain errors |
| **DAG position** | Post-deliverable — runs AFTER any tool/mode that produces a `.pptx` and BEFORE the orchestrator surfaces "done" to the operator |
| **Calls** | Shells out to `libreoffice --headless` and `pdftoppm`; reads PNG via the harness `Read` tool when the orchestrator inspects |
| **Schema** | Findings dict validates against `$ASSET_ROOT/_core/schemas/visual-qa-result.schema.json` (pending — v2.1.1) |

## Toolchain

Hard dependencies:
- `libreoffice` (24.x or newer) — provides headless `.pptx` → `.pdf` conversion. Bundled font set must include any fonts referenced by the deck (Noto Serif, Lexend Deca for the `_default` brand kit).
- `pdftoppm` (poppler-utils) — provides `.pdf` → `.png` per-page conversion.

Verify availability on first invocation:

```bash
which libreoffice >/dev/null || { echo "FATAL: libreoffice not installed"; exit 2; }
which pdftoppm    >/dev/null || { echo "FATAL: pdftoppm (poppler-utils) not installed"; exit 2; }
```

On Arch: `pacman -S libreoffice-fresh poppler`.
On Debian/Ubuntu: `apt install libreoffice poppler-utils`.
On macOS: `brew install libreoffice poppler`.

If either is missing, the primitive fails LOUD with the install command. It does NOT fall back to "skip QA and trust the file size" — that would defeat the purpose.

## `render_pptx_to_pngs(pptx_paths, dpi=110)`

Renders one or more `.pptx` files into per-slide PNGs in a scratch directory
co-located with each deliverable.

```python
import os, subprocess, glob
from datetime import datetime, timezone

def render_pptx_to_pngs(pptx_paths, dpi=110):
    """
    Render each .pptx into per-slide PNGs.

    Inputs:
        pptx_paths: list of absolute paths to .pptx files
        dpi: pdftoppm rendering DPI (default 110 — balance between fidelity
             and file size for orchestrator inspection)

    Returns:
        {
          "rendered": [
            {
              "pptx_path": str,
              "pdf_path":  str,
              "png_paths": [str, ...],   # one per slide, in slide order
              "slide_count": int,
              "rendered_at": str,        # ISO 8601 UTC
              "scratch_dir": str
            }, ...
          ],
          "errors": [{"pptx_path": str, "error": str}, ...]
        }
    """
    rendered, errors = [], []

    for pptx in pptx_paths:
        if not os.path.exists(pptx):
            errors.append({"pptx_path": pptx, "error": "file not found"})
            continue

        deliverable_dir = os.path.dirname(pptx)
        deck_name = os.path.splitext(os.path.basename(pptx))[0]
        # Scratch is hidden, co-located with the deliverable. Gitignored
        # because it sits inside <STATE_ROOT>/_orgs/ which is gitignored as a whole.
        scratch = os.path.join(deliverable_dir, ".qa-scratch", deck_name)
        os.makedirs(scratch, exist_ok=True)

        # 1. .pptx → .pdf (libreoffice headless)
        pdf_result = subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf",
             "--outdir", scratch, pptx],
            capture_output=True, text=True, timeout=120
        )
        if pdf_result.returncode != 0:
            errors.append({"pptx_path": pptx,
                           "error": f"libreoffice convert failed: {pdf_result.stderr.strip()}"})
            continue

        pdf_path = os.path.join(scratch, f"{deck_name}.pdf")
        if not os.path.exists(pdf_path):
            errors.append({"pptx_path": pptx,
                           "error": "libreoffice produced no .pdf — check font availability"})
            continue

        # 2. .pdf → .png per slide (pdftoppm)
        png_prefix = os.path.join(scratch, deck_name)
        png_result = subprocess.run(
            ["pdftoppm", "-r", str(dpi), "-png", pdf_path, png_prefix],
            capture_output=True, text=True, timeout=60
        )
        if png_result.returncode != 0:
            errors.append({"pptx_path": pptx,
                           "error": f"pdftoppm failed: {png_result.stderr.strip()}"})
            continue

        png_paths = sorted(glob.glob(f"{png_prefix}-*.png"))
        if not png_paths:
            errors.append({"pptx_path": pptx,
                           "error": "pdftoppm produced no .png — empty .pdf?"})
            continue

        rendered.append({
            "pptx_path": pptx,
            "pdf_path": pdf_path,
            "png_paths": png_paths,
            "slide_count": len(png_paths),
            "rendered_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "scratch_dir": scratch,
        })

    return {"rendered": rendered, "errors": errors}
```

## Orchestrator usage pattern

After any mode body produces a `.pptx`, the orchestrator runs the primitive then
inspects the PNGs via its `Read` tool (which accepts image paths and returns
the image content for visual inspection):

```python
# 1. Mode body wrote one or more .pptx files
deliverable_pptx = [
    f"{STATE_ROOT}/_orgs/<slug>/engagements/<id>/deliverables/<deck>.pptx",
    ...
]

# 2. Render
result = render_pptx_to_pngs(deliverable_pptx)

# 3. Surface errors immediately — do NOT proceed if any
if result["errors"]:
    surface_errors(result["errors"])
    abort_done_announcement()
    return

# 4. Inspect each PNG via Read tool
for entry in result["rendered"]:
    for png in entry["png_paths"]:
        image_data = read_tool(png)             # accepts image paths
        inspect_for_defects(image_data)         # orchestrator's eye

# 5. Only NOW may the orchestrator surface "done" to the operator.
```

The `inspect_for_defects` step is the orchestrator's own visual judgment (LLM
seeing the PNG) when run solo. The multi-lens panel below splits that single
judgment into independent checkers so one checklist item cannot mentally
overwrite another — but the underlying discipline is the same: the orchestrator
always looks before declaring done. Future automation hooks (v2.2) can layer in:
- Text-overflow detection via PIL bounding-box analysis
- Logo-presence detection via image hashing against `branding/<org>/theme/logo-*.png`
- Palette-conformance via per-pixel color-distance against `branding/<org>/theme/palette.json`

Until those land, this primitive is **render-then-look** — solo when the panel is
skipped, fan-out across lenses when it runs.

## Multi-lens panel (Phase 4 — workflow-native coverage net)

```
engine: workflow-tool      # $0 local-read panel — Read-only; no Perplexity, no paid MCP
paid: false
fan_out_max: slides × 4    # 4 lenses per rendered slide; the only control on token spend (invariant #6)
```

The solo render-then-look pass put all seven inspection-checklist items in one
orchestrator context, where a single attention can let one defect overwrite
another — the documented 3-defect batch miss (see § Why this exists: cover overlap
+ timeline overflow + clipped callout, all in one batch, none surfaced). The panel
fixes that by fanning the checklist across four independent lens agents per slide,
each carrying exactly one slice of the checklist. Independent checkers do not share
an attention budget; each reports against its own lens or stays silent.

This is a **$0 local-read panel**: every lens reads PNGs already on disk via the
harness `Read` tool. No Perplexity, no paid MCP, no network. It is Workflow-tool
eligible under the engine rule (§ 1) because it calls only $0.00 tools — but it
declares `fan_out_max` because `cost-log.jsonl` is blind to Claude agent-token
spend (invariant #6); the cap is the only bound on a `slides × 4` fan-out.

### Lenses (each maps to a slice of the inspection checklist below)

| Lens | Checklist items it owns | Reads |
|---|---|---|
| `text-overflow+collision` | 1 (overflow), 2 (collision) | the slide PNG |
| `logo+color-conformance` | 3 (logo present), 4 (color conformance) | the slide PNG + `branding/<org>/theme/` reference |
| `edge-clipping+empty-space` | 5 (edge clipping), 6 (empty-space pattern) | the slide PNG |
| `cross-slide-consistency` | 7 (cross-slide register) | every slide PNG in the deck (whole-deck lens) |

The performative-emptyspeak read (checklist item 8) is text register, not a visual
defect; it stays with the comms emptyspeak track and the orchestrator's own read —
do not add it as a visual lens here.

### Dispatch — each lens runs the generic critic

Each lens is a dispatch of the generic `critic.md` agent (the one critic the
panels share — see SPEC § 1, F7), not a bespoke agent file. The panel supplies the
lens prompt and the return schema at dispatch; the critic reads the inputs, applies
the lens it was handed, and returns exactly that schema. Author lens prompts at the
dispatch site — never fork a per-lens agent file, which would re-introduce the
`.claude/agents/` sprawl F7 forbids.

```
visual_qa_panel(rendered_entry) -> [LensReturn, ...]   # one per (slide × lens) + 1 deck-wide consistency return
  # rendered_entry is one item from render_pptx_to_pngs()["rendered"]
  parallel() of critic dispatches:
    for each png in rendered_entry["png_paths"]:
        critic(lens="text-overflow+collision",   inputs=[png],                          schema=visual-qa-lens)
        critic(lens="logo+color-conformance",     inputs=[png, branding_theme_dir],      schema=visual-qa-lens)
        critic(lens="edge-clipping+empty-space",  inputs=[png],                          schema=visual-qa-lens)
    critic(lens="cross-slide-consistency",        inputs=rendered_entry["png_paths"],    schema=visual-qa-lens)   # whole-deck, once
  barrier: collect all lens returns
  for each return -> validate against visual-qa-lens.schema.json
    invalid/missing -> re-dispatch that lens once, then record verdict="fail" with a defect noting the missing return
  return [LensReturn, ...]
```

Each lens return validates against the on-disk `$ASSET_ROOT/_core/schemas/visual-qa-lens.schema.json`
(single source of truth — the schema body is **not** duplicated here, so the primitive and the
file cannot drift):

Shape: `{ lens, defects: [{ category, description, slide? }], verdict: pass|fail }`

- `lens` — free-text string naming the lens (e.g. `text-overflow+collision`,
  `logo+color-conformance`, `edge-clipping+empty-space`, `cross-slide-consistency`). Free-text by
  design, so the panel can add a lens without a schema bump; the orchestrator supplies the lens
  name at dispatch.
- `defects[]` — each item carries `category` (short defect class, e.g. `text-overflow`,
  `off-brand-color`, `logo-misplacement`), `description` (what is wrong and where on the slide),
  and an optional `slide` (1-based integer; **omit** on the whole-deck `cross-slide-consistency`
  lens). An empty array pairs with `verdict: pass`.
- `verdict` — `pass | fail`. Any `fail` blocks the done announcement (orchestrator-enforced hard
  gate).
- `additionalProperties:false` at every level; no `replacement_text` — FLAG-only: the lens reports
  the defect, never the fix.

The lens is a **checker, separate from the author** — it reports `defects[]`, it
never authors a corrected slide or replacement text. The schema has no
`replacement_text` property and `additionalProperties: false`; fixing a defect
means fixing the generator code and re-rendering, never patching the PNG or
having the lens emit a substitute (see § Constraints, § Error shapes).

### Barrier and the done gate (stays hard)

The panel is the parallel form of the existing hard gate, not a softening of it.

```python
# After render_pptx_to_pngs() succeeds for an entry (toolchain hard-abort already
# enforced upstream — see § Toolchain, § Error shapes; the panel does not relax it):
lens_returns = visual_qa_panel(entry)            # parallel critics; orchestrator AWAITS the barrier

# Any single fail blocks the done announcement. No averaging, no quorum — one
# fail is one shipped defect, the exact class every cited friction event was.
if any(r["verdict"] == "fail" for r in lens_returns):
    surface_lens_defects(lens_returns)
    abort_done_announcement()                    # hard gate — orchestrator fixes the generator, re-renders, re-runs the panel
    return

# Only when every lens verdict == "pass" across every slide may the orchestrator
# surface "done" to the operator.
```

Three properties hold, by spec (§ 4b, § 4f) and are not negotiable at build time:

- **The orchestrator awaits the barrier before the done gate (F12).** The Workflow
  tool runs background/async; the done gate stays synchronous. The orchestrator
  blocks on the panel's barrier — it does not announce done while lenses are still
  in flight, and it does not fire-and-forget the panel.
- **Any `verdict == "fail"` blocks the done announcement.** This stays a hard gate —
  there is no soft-fail path (see the barrier code above and § Error shapes). The panel
  makes the gate parallel and independent; it does not make it advisory. Re-render only after the
  generator code is fixed — do not patch PNGs and do not re-run the lens hoping for
  a different read.
- **Toolchain failure stays a hard abort.** If `render_pptx_to_pngs()` returns any
  `errors[]`, the orchestrator aborts before the panel ever dispatches — there is no
  retry-loop softening of the toolchain abort, and the panel never runs against a
  partial or missing render (see § Error shapes).

### Why a panel and not just the solo checklist

The solo checklist is correct and stays the lens-prompt source — each lens prompt
is one or two of its items, quoted. The panel adds one thing the solo pass cannot
give: **independence**. A single orchestrator reading a 7-item checklist against a
PNG can satisfice — confirm the logo, relax on the overflow. Four agents each
holding one slice cannot trade one defect against another, because no agent sees
the others' slice. That independence is the entire reason this is a panel and not
a longer prompt to one reader.

## Inspection checklist (orchestrator-side)

For every PNG inspected, run through this checklist mentally:

1. **Text overflow** — Does any text run off the slide edge or out of its container?
2. **Text collision** — Do any text elements overlap each other (title vs subtitle, label vs bar)?
3. **Logo present** — Is the brand logo where it should be? (Empty green rail = bug.)
4. **Color conformance** — Are accent colors from the active brand kit, not arbitrary RGB?
5. **Slide-edge clipping** — Does any element (especially callouts at the bottom) extend past slide bounds (`y > 7.5"` for `LAYOUT_WIDE`)?
6. **Empty space pattern** — Is empty space deliberate (whitespace) or accidental (failed text fit)?
7. **Cross-slide consistency** — Do all slides share the same brand register (palette, typography, header style)?
8. **Performance vs information register** — Does any copy perform competence rather than communicate work? Read every cover paragraph, decision card, and risk description aloud. Ask: "Would a fluent reader find any sentence here unnecessary?" Phrases that should never appear outside the comms-mode emptyspeak track: *"decision points ahead of time"*, *"lands as a surprise"*, *"stop-and-discuss point — not a fly-by"*, *"to keep momentum"*, *"locks in your"*. Per writing-standards-comp.md § Performative emptyspeak. The hook layer (`anti-slop.sh` + `never-list.txt` performative-emptyspeak section) catches the high-confidence phrase patterns; this checklist item catches what slips through (full-paragraph register failures, sales-pitch tone, reassurance theatre that doesn't trip a single phrase).

A defect in any of these aborts the "done" announcement. Re-render only after the
underlying generator code is fixed; do not patch PNGs directly.

## Trigger points (where this primitive runs)

| Mode / phase | Trigger | Required? |
|---|---|---|
| `advisor` Phase 6c — deck assembly close | Yes — every deck | **Hard gate** |
| `advisor` showcase / preview slide rendering | Yes — every preview | **Hard gate** |
| `comms` cascade-pack render (any visual artifact) | Yes | **Hard gate** |
| `training` per-audience bundle (when bundle includes slides) | Yes | **Hard gate** |
| `transformer` diagrams / process maps in PPTX form | Yes | **Hard gate** |
| `/comp doctor --visual <engagement_id>` | On-demand re-QA of all `deliverables/*.pptx` | Operator-invoked |

The gate is hard because every cited friction event in this primitive's
provenance was a visual defect that no non-visual signal would have caught. The
multi-lens panel (§ Multi-lens panel) runs per slide at each hard-gate trigger
above and keeps the gate hard — any lens `verdict == "fail"` blocks the same
done announcement the solo checklist would.

## Scratch directory hygiene

PNGs live at `<engagement>/.qa-scratch/<deck_name>/<deck_name>-N.png`. They are:
- **Co-located** with the deliverable so the orchestrator can find them without path arithmetic.
- **Hidden** (`.qa-scratch`) so file pickers and `walk_sibling_assets` skip them by convention.
- **Gitignored** by inheritance — the entire `<STATE_ROOT>/_orgs/` tree is gitignored.
- **Regenerated fresh** every render — never trust a cached PNG.

`/comp doctor --fix` may sweep `.qa-scratch/` directories older than the parent
`.pptx` `mtime` to keep the tree tidy. Stale PNGs are not a correctness risk
(they're regenerated on next QA pass) but accumulate disk over many engagements.

## Error shapes

| Error | Severity | Surface |
|---|---|---|
| `libreoffice` / `pdftoppm` not installed | Hard — abort | `"FATAL: <tool> not installed — see $ASSET_ROOT/_core/primitives/visual-qa.md § Toolchain"` |
| `.pptx` not found | Hard — abort | `"file not found: <pptx_path>"` |
| `libreoffice` exit non-zero | Hard — abort | `"libreoffice convert failed: <stderr>"` |
| `libreoffice` succeeds but emits no PDF | Hard — abort | `"libreoffice produced no .pdf — check font availability"` |
| `pdftoppm` exit non-zero | Hard — abort | `"pdftoppm failed: <stderr>"` |
| `pdftoppm` produces zero PNGs | Hard — abort | `"pdftoppm produced no .png — empty .pdf?"` |
| Render-then-look pass with operator-detected defect | Hard — re-render | Operator surfaces the defect; orchestrator fixes the generator and re-runs the primitive. PNG itself is not patched. |

All hard errors prevent the "done" announcement. There is no soft-fail path.

## Constraints

- **Read-only on the `.pptx`.** Never edits the deliverable file.
- **No upload, no Drive sync.** PNGs stay local in `.qa-scratch/`.
- **No OCR or pixel analysis** (yet). v2.1 is render-and-let-the-orchestrator-look.
- **No caching across renders.** Every QA pass regenerates fresh — masters change, palette changes, content changes, and stale PNGs would mask regressions.
- **Atomic per `.pptx`.** Each file is rendered independently; one failure does not abort the batch (logged in `errors[]`, others proceed).
- **DPI default 110** — empirically sufficient for orchestrator visual inspection. Higher DPI inflates PNG size without improving defect-detection. Phase 7 close-of-engagement may opt for higher DPI when the operator explicitly archives PNGs alongside the deliverable.

## Acceptance

- Render-toolchain test (pending — `24-visual-qa-render.yaml`; numbered out of the 18–20 range,
  which Phase 1 reserves for `refute-claim`) verifies:
  - 3-slide deck renders to 3 PNGs at expected paths
  - Missing `libreoffice` triggers the FATAL message
  - Missing `pdftoppm` triggers the FATAL message
  - Unreadable `.pptx` (zero bytes) surfaces a clear error
  - PNG paths are sorted in slide order
  - `.qa-scratch/` directory is created if absent
- Multi-lens panel acceptance (SPEC § 4f) — covered by `tests/scenarios/22-visual-qa-lens-panel.yaml`:
  - `visual-qa.md` declares `engine: workflow-tool`, `paid: false`, `fan_out_max: slides × 4`
  - Per slide, four lenses dispatch the generic `critic.md`; each returns `visual-qa-lens.schema.json`
  - `visual-qa-lens.schema.json` has `additionalProperties: false` and no `replacement_text` property
  - Any lens `verdict == "fail"` aborts the done announcement (hard gate preserved)
  - A toolchain `errors[]` aborts before the panel dispatches; the panel adds no retry-loop softening
  - The orchestrator awaits the panel barrier before the done gate (no fire-and-forget)

## See also

- `$ASSET_ROOT/_core/policies/cost-discipline.md` — local-tool runs (libreoffice, pdftoppm) and the $0 local-read lens panel are not paid MCP calls; no cost-log entry required. The panel's bound on Claude agent-token spend is `fan_out_max`, not the dollar gate (invariant #6)
- `$ASSET_ROOT/_core/schemas/visual-qa-lens.schema.json` — the `{lens, defects[], verdict}` return each lens validates against (Phase 4 additive schema; FLAG-only)
- `$ASSET_ROOT/.claude/agents/critic.md` — the one generic critic each lens dispatches (SPEC § 1, F7); never fork a per-lens agent file
- `$ASSET_ROOT/SPEC-workflow-phases-2-5.md` § 4b, § 4f — the multi-lens panel spec and acceptance criteria; § 0c invariants #2 (FLAG-only), #6 (fan-out cap), #7 (post-redaction)
- `$ASSET_ROOT/_modes/advisor/references/contracts.md` — Phase 6c "deck assembly close" contract should reference this primitive as a gate
- `$ASSET_ROOT/_core/primitives/brand-kit.md` § Regeneration discipline — visual QA runs after kit regeneration produces the deck, not against the bundled template alone
- `$ASSET_ROOT/.claude/skills/comp/references/friction-capture.md` — operator-flagged visual defects logged here continue to drive primitive priorities
