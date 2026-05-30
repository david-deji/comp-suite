---
engine: workflow-tool
paid: false
fan_out_max: 7
---

# council-parallel

Comp-suite v2 primitive (SPEC-workflow-phases-2-5.md § 2a). Consolidates the five
hand-rolled parallel-thinker dispatch sites (the `/comp council` Path A loop and any future
parallel-thinker dispatch) into one callable contract with a schema barrier. It does **not**
change council behavior — it makes the existing `council-dispatch.md` Steps 5–7 a primitive,
and upgrades the prose disk-check + return-message-fallback into a structural
validate-or-re-dispatch.

It dispatches **only** the parallel thinker stage. Gap-aggregation, the founder gap-routing
`AskUserQuestion`, and synthesis stay in the orchestrator **after** the corpus returns — the
Workflow tool runs autonomously and cannot host a mid-run human gate, and synthesis is a
hard-no for agent delegation.

## Why this exists

Five sites re-describe the same parallel-thinker loop (dispatch N thinkers → wait → check
each thinker's file on disk → fall back to the return message → use it in synthesis). Re-prose
drifts: one site silently drops a thinker whose file failed to write, another forgets the
return-message fallback. This primitive is the single contract: every site dispatches the same
way, and a thinker that returns malformed output is re-dispatched once and then recorded in
`missing[]` — never silently dropped into a thinner-than-intended council.

## Contract

| | |
|---|---|
| **Signature** | `council_parallel(thinkers, return_schema) -> {corpus[], missing[]}` |
| **Inputs** | `thinkers: list[dict]` — ≤ 7 thinker dispatch specs (perspective name, persona, focus, unique output path, dispatch prompt). `return_schema: str` — the schema each return must validate against (default `thinker-return.schema.json`). |
| **Outputs** | `{corpus: list[dict], missing: list[dict]}` — `corpus` = the validated thinker returns; `missing` = perspectives whose return was absent or schema-invalid after one re-dispatch (`{perspective_name, reason}`). |
| **DAG position** | The parallel stage of a council. Runs AFTER the orchestrator composes the dispatch list (`council-dispatch.md` Steps 1–4) and BEFORE the orchestrator's own gap-aggregate → `AskUserQuestion` → synthesis (Steps 8+). |
| **Engine** | `workflow-tool` eligible (thinkers are `$0` — see § Engine choice) or inline parallel `Agent`. Both valid at `$0`. |
| **Calls** | Dispatches ≤ 7 `thinker.md` agents (`model: opus`; tools `[Read, Grep, Glob, Write]`; `WebSearch`/`WebFetch` disallowed → zero paid tools). |
| **Schema** | Each thinker return validates against `$ASSET_ROOT/_core/schemas/thinker-return.schema.json` (`additionalProperties:false`, no `replacement_text`; `statutory_tags[]` `$ref`s `statutory-evidence.schema.json`). |

## Engine choice (verified $0)

`thinker.md` grants `[Read, Grep, Glob, Write]` and disallows `WebSearch`/`WebFetch`, so a
thinker calls **zero paid registry tools** → `$0` under comp-suite's dollar gate (`budget-check`
keys on Perplexity `est_call_cost_usd`; thinkers never call it). That makes `council-parallel`
**Workflow-tool eligible** (§ 1 engine rule).

- **Prefer the Workflow tool** for its resumable journal — a re-run skips already-completed
  thinkers (matches the disk-check resume the prose pattern did by hand).
- **Fall back to inline parallel `Agent`** if a thinker config ever grants a Perplexity tool.
  Then that thinker is **paid → inline + per-call `check_budget`** (§ 1), and the primitive is
  reclassified for that run — no paid call ever executes inside a Workflow-tool script
  (invariant #1).

## Fan-out cap (invariant #6)

`fan_out_max: 7`. Thinkers are `$0` under the **dollar** gate, but they are `model: opus`, and
`cost-log.jsonl` is blind to Claude **agent-token** spend — a 7-Opus fan-out is real API money
the `$5` cap never sees. The cap is the only control on that invisible spend; never exceed it.
Council sizing (3 / 5 / 7 + the mandatory Industry Outsider, which does not count against
`perspective_count`) is the orchestrator's call per `council-dispatch.md`; this primitive
enforces the ceiling.

## The schema barrier (the one behavioral hardening)

```
council_parallel(thinkers, return_schema):
  returns = parallel() of [dispatch(t) for t in thinkers]   # ≤7; Workflow-tool OR inline parallel Agent
  corpus, missing = [], []
  for t, r in zip(thinkers, returns):
    obj = read_unique_file(t.output_path) or return_message(r)   # disk first, return-message fallback
    if obj is not None and validates(obj, return_schema):
      corpus.append(obj)
    else:
      r2 = redispatch_once(t)                                     # one retry, not a loop
      obj2 = read_unique_file(t.output_path) or return_message(r2)
      if obj2 is not None and validates(obj2, return_schema):
        corpus.append(obj2)
      else:
        missing.append({"perspective_name": t.perspective_name,
                        "reason": "absent or schema-invalid after one re-dispatch"})
  return {"corpus": corpus, "missing": missing}
```

- **A malformed return is re-dispatched once, then recorded in `missing[]`.** It is never
  silently dropped — a thinner-than-intended council is surfaced, not hidden (the failure mode
  the prose pattern allowed).
- **Disk first, return-message fallback.** Thinkers are write-capable, so each writes its own
  unique file per `council-output-pattern` (parallel `Write`s would clobber a shared file). The
  return message is the belt-and-suspenders fallback when the file write failed.
- **Validate, don't trust.** The barrier validates every return against `thinker-return.schema.json`
  before it enters `corpus` — a return that reads plausible but omits `knowledge_gaps`, or smuggles
  a `replacement_text`, fails structurally rather than polluting synthesis (failure mode #6).

## What stays in the orchestrator (never in this primitive)

- **Gap-aggregation** across the corpus, the **founder gap-routing `AskUserQuestion`**, and
  **synthesis** — all orchestrator-inline, after the corpus returns. Synthesis is a hard-no for
  agent delegation (`council-output-pattern`, SPEC § 0b). The Workflow tool cannot host the
  mid-run human gate, which is the structural reason these stay out of the primitive.
- **Industry Outsider selection** and perspective composition stay in `council-dispatch.md`
  Steps 1–4; this primitive receives the composed `thinkers[]`.

## Constraints

- **`paid: false`, verified.** Declared against `thinker.md`'s tool grant (web tools disallowed).
  If any thinker config grants a Perplexity tool, reclassify that run to inline + per-call
  `check_budget` (§ 1 / invariant #1) — never run a paid call inside a Workflow-tool script.
- **Fan-out ≤ 7.** The only bound on Opus thinker token spend that the dollar gate cannot see
  (invariant #6).
- **No silent drop.** A malformed/absent return is re-dispatched once, then recorded in `missing[]`.
- **No agent synthesis.** Synthesis is orchestrator-owned; this primitive returns the corpus, not
  a synthesis (SPEC § 0b).
- **Per-thinker unique files.** Write-capable thinkers each write their own file
  (`council-output-pattern`); never a shared file.
- **FLAG-only returns.** `thinker-return.schema.json` is `additionalProperties:false` with no
  `replacement_text`; a thinker reports positions and gaps, never replacement text.

## Acceptance (SPEC § 2d)

- [ ] `council-parallel.md` exists; declares `engine: workflow-tool`, `paid: false`
      (verified against `thinker.md`'s tool grant), `fan_out_max: 7`.
- [ ] A malformed thinker return is re-dispatched once, then recorded in `missing[]` — never
      silently dropped.
- [ ] Synthesis remains in the orchestrator (no agent synthesis path added).
- [ ] If any thinker config grants a Perplexity tool, the run reclassifies to inline + per-call
      `check_budget`.
- [ ] `thinker-return.schema.json` is additive; the 11 pre-existing schemas are byte-unchanged.

## See also

- `$ASSET_ROOT/SPEC-workflow-phases-2-5.md` § 2a — the spec section this primitive realizes; § 1 engine
  rule; § 0c invariant #6 (fan-out cap).
- `$ASSET_ROOT/.claude/skills/comp/references/council-dispatch.md` — the five dispatch sites; Steps 5–7
  become a call to this primitive.
- `$ASSET_ROOT/.claude/agents/thinker.md` — the agent this primitive dispatches (the `paid: false` source
  of truth).
- `$ASSET_ROOT/_core/schemas/thinker-return.schema.json` — the return schema each thinker validates against.
- `$ASSET_ROOT/_core/schemas/statutory-evidence.schema.json` — the shared `{url, quote}` evidence shape
  `statutory_tags[]` `$ref`s.
- `$ASSET_ROOT/_core/council/output-pattern.md` — per-thinker unique-file + dual-return discipline
  (write-capable agents).
- `$ASSET_ROOT/_core/primitives/refute-claim.md` — sibling primitive on the paid inline-Agent path (Phase 1
  — **forthcoming**; spec at `$ASSET_ROOT/SPEC-workflow-phase1.md`, not yet built per the § 6 build order).
  Contrast when built: thinkers are `$0`, refuters fetch (paid).
