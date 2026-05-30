# Opening Sequence — First 90 Seconds

The first thing to consult on every session. Routes the user's request to a spine
in 4 checks before falling back to `intent-router.md` for full classification.
This file lives at the top of the load order — read it first, every session.

## 1. Slash command in the message?

- `/init`, `/init pay-equity-qc`, `/update`, `/intake`, `/quickbench`, `/council`,
  `/checkpoint`, `/resume`, `/ledger`, `/brand-kit init <slug>`, `/cba save`,
  `/glossary promote`, `/help`, `/close-cycle`, `/reopen-cycle`, `/switch-cycle`
  → route to that command's protocol per the slash-command grammar
  (`references/slash-command-grammar.md`). DONE.
- `/compensation-advisor`, `/comp-advisor`, `/comp` → these are no-op invocation
  prefixes. Strip them and re-classify the remainder.

## 2. .pptx upload in the message?

- + explicit "just numbers" / "refresh numbers" / "no strategic changes"
  → Track R-lite (Quick Refresh). DONE.
- + no explicit refresh signal → Track R (Refresh, full Phase 1+ run with
  prior-deck context). DONE.

## 3. Stage-named deliverable in the message?

- "Strategy Kickoff", "market review pre-read", "Options Review deck",
  "approval pitch", "cascade kit", "payroll execution"
  → Track D + stage-keyed spine from `consulting-protocol.md` § Stage spines.
  Skip Phase 1 ambiguity, go straight to Phase 6a planning. DONE.

## 4. Generic deliverable name in the message?

- "initial deck", "first deck", "kickoff thing", "something for VP Ops"
  → Pre-classification disambiguation: ask ONE question to resolve which stage
  + which engagement mode (see `references/engagement-modes.md`) before routing.
  See `intent-router.md` § Pre-classification rules for the prompt template.

## 5. Else → read `references/intent-router.md` for full classification.

---

## Mandatory pre-flight (every track, every session)

Before producing any deliverable:

1. **Drive backend probe** (per `persistence-and-ledger.md` § Backend detection
   — procedural three-probe check). ~10 seconds.
2. **Load matching config + master.yaml** if a slug is referenced or implied.
3. **Compute current_week_offset** = today − config.cycle.effective_date.
4. **Cycle-stage check** (symmetric — both directions):
   - If `week_offset > 0` (post-launch) AND new strategy work requested
     → declined per the too-late rule in `consulting-protocol.md`.
   - If `week_offset < target_stage_offset − 4` (more than 4 weeks early)
     → too-early protocol per `consulting-protocol.md` § Too-early. Surface a
     pre-engagement mode menu before proceeding.
5. **If config or master.yaml is missing** → run `/init` flow, do NOT improvise.
