---
engine: workflow-tool
paid: false
fan_out_max: 2
---

# gap-table-skeptics

Comp-suite v2 primitive (SPEC-workflow-phases-2-5.md § 3b). Two adversarial skeptics that read
the pay-equity Phase-8 gap analysis and flag method/regression defects **before** Gate B — the
moment the operator confirms the gap table. It enriches an **existing** human gate (Gate B); it
does not replace it. FLAG-only: findings surface above the Gate B display tagged
"pré-confirmation"; the operator still types `confirmer` (invariant #3 — never auto-confirm a
legal-compliance gate).

It runs in `pay-equity-qc-protocol.md` Phase 8, after `compare_compensation` returns and
**before** the Gate B prompt.

## Why this exists

Phase 8's regression-quality warnings (`n_male_classes < 3`, `R² < 0.50`, `slope ≤ 0`) are
**non-blocking in expert mode** — they display and the operator acknowledges. That is the gap:
a tired operator acknowledges a warning that should have stopped the analysis, or confirms a
gap table built on a method that does not match the method they declared at Gate A. These two
skeptics read the analysis cold and ask the two questions the warning display does not force:
"is this the method you said you'd use?" and "should this regression have blocked instead of
warned?" They surface the answer above Gate B so the operator confirms with eyes open.

## Contract

| | |
|---|---|
| **Signature** | `gap_table_skeptics(compensation_json, session_state) -> {skeptics[], missing[]}` |
| **Inputs** | `compensation_json` — the Phase-8 gap analysis (`compare_compensation` output: per-class gaps, regression block with R²/slope/intercept/n). `session_state` — `session-state.json` (for `operator_decisions.comparison_method`, F8). |
| **Outputs** | `{skeptics: list[dict], missing: list[dict]}` — `skeptics` = the validated skeptic returns (`gap-table-skeptic.schema.json`); `missing` = skeptics absent or schema-invalid after one re-dispatch (`{skeptic, reason}`). |
| **DAG position** | `pay-equity-qc-protocol.md` Phase 8, after `compare_compensation`, before the Gate B prompt. Findings surface above the Gate B display. |
| **Engine** | `workflow-tool` eligible (zero tool calls → $0 → § 1 engine rule) or inline parallel `Agent`. Both valid at $0. |
| **Calls** | 2 read-only `critic.md` agents (`fan_out_max: 2`; `model: sonnet`; `[Read, Grep, Glob]`, web tools disallowed → zero paid tools). `critic.md` already names "gap-table skeptics" as a spawn site. |
| **Schema** | Each skeptic return validates against `$ASSET_ROOT/_core/schemas/gap-table-skeptic.schema.json` (`additionalProperties:false`, no `replacement_text`). |

## The two skeptics

| Skeptic | Reads | Checks |
|---|---|---|
| **method-correctness** | `compensation_json` + `session-state.json` | Does the applied comparison method match `session-state.json:operator_decisions.comparison_method` (F8)? Was any female class silently dropped into warnings with no comparator? |
| **regression-quality** | `compensation_json` | Are `R² < 0.50`, `slope ≤ 0`, or `n_male_classes < 3` logged as warnings-only when they warrant blocking-class attention? |

**F8 file locations (verified).** `operator_decisions.comparison_method` lives in
`session-state.json` (`pay-equity-qc-protocol.md § Session State Schema`). `operator_mode` lives
in `engagement.json`, **not** `session-state.json` — do not read it from session state.

## Engine choice (verified $0)

Both skeptics read JSON via `Read` and call **zero** registry tools → `$0` under comp-suite's
dollar gate → **Workflow-tool eligible** (§ 1). `critic.md` (the agent both dispatch) disallows
`WebSearch`/`WebFetch`, so neither skeptic can fetch — they reason over the already-computed
analysis only. Prefer the Workflow tool for its resumable journal; inline parallel `Agent` is
an equally valid $0 fallback. If a future skeptic ever needs to fetch (it should not — these are
arithmetic/method checks, not statutory ones), it becomes paid → inline per § 1.

## FLAG-only — severity is advisory routing, never an auto-block

A skeptic returns `{skeptic, severity, findings[]}`. `severity` is **advisory routing only** —
it tells the orchestrator how prominently to surface the finding above the Gate B display:

- `severity: block` — surface as a **blocking-class** concern the operator must address before
  confirming. It does **not** auto-block. Gate B stays human: the operator still types
  `confirmer` (invariant #3 — never auto-confirm a legal-compliance gate).
- `severity: warn` — surface as a warning above the gate.
- `severity: info` — pairs with an empty `findings[]` (no concern found).

The `block`/`warn`/`info` vocabulary mirrors the Phase-8 domain language ("logged as
warnings-only when they should block") — the term names the skeptic's exact job (catch
under-severity classification). The no-auto-block guarantee is enforced at the **wiring** layer
(the Gate B prompt still requires `confirmer`), not by the value. The schema carries no
`replacement_text` and is sealed with `additionalProperties:false` — a skeptic flags; it never
rewrites the method, the regression, or a gap figure.

## The collect-then-surface barrier

```
gap_table_skeptics(compensation_json, session_state):
  skeptics, missing = [], []
  returns = parallel() of [                                  # 2; Workflow-tool OR inline parallel Agent
    dispatch(critic.md, "method-correctness", compensation_json + session_state),
    dispatch(critic.md, "regression-quality", compensation_json),
  ]
  for skeptic_name, r in returns:
    obj = return_message(r)
    if obj is not None and validates(obj, "gap-table-skeptic.schema.json"):
      skeptics.append(obj)
    else:
      r2 = redispatch_once(skeptic_name)                     # one retry, not a loop
      obj2 = return_message(r2)
      if obj2 is not None and validates(obj2, "gap-table-skeptic.schema.json"):
        skeptics.append(obj2)
      else:
        missing.append({"skeptic": skeptic_name, "reason": "absent or schema-invalid after one re-dispatch"})
  return {"skeptics": skeptics, "missing": missing}

# orchestrator (pay-equity Phase 8), AFTER the panel returns, BEFORE the Gate B prompt:
#   render the findings ABOVE the Gate B display, tagged "pré-confirmation",
#   block-severity findings first; then present Gate B. The operator types `confirmer`
#   (or `modifier`) — the skeptics never confirm for them (invariant #3).
```

- **A missing skeptic is not a clean skeptic.** Schema-invalid or absent → re-dispatch once,
  then record in `missing[]` and surface the gap above Gate B (never silently "no concern").
- **Gate B stays human.** The panel informs the gate; the operator still types `confirmer`.

## Constraints

- **FLAG-only.** Reports findings; never edits the gap table, the method, or the regression.
  Schema is `additionalProperties:false` with no `replacement_text`.
- **`$0` local-read panel.** `Read` only; no Perplexity, no paid MCP. `engine: workflow-tool`,
  `paid: false`, `fan_out_max: 2` — declared in frontmatter so the engine rule and fan-out cap
  (invariant #6) are machine-checkable.
- **Gate B stays human** (invariant #3). `severity: block` is advisory routing; it never
  auto-confirms. The operator types `confirmer`.
- **No statutory claims.** These are method/arithmetic checks; the schema does not `$ref`
  statutory-evidence (only close-validation / refute-claim / thinker-return do, F6). A skeptic
  never asserts a statute figure — it reasons over the computed analysis.
- **Reads the verified file locations.** `comparison_method` from `session-state.json`;
  `operator_mode` (if ever needed) from `engagement.json` (F8).
- **No agent synthesis.** The orchestrator renders findings above Gate B; it does not delegate
  the gate decision to an agent.

## Acceptance (SPEC § 3c)

- [ ] `gap-table-skeptics.md` exists; declares `engine: workflow-tool`, `paid: false`,
      `fan_out_max: 2`.
- [ ] Both skeptics read `compensation.json` + `session-state.json` only (zero tool calls);
      provably `$0` (verified against the § 1 engine table).
- [ ] method-correctness reads `operator_decisions.comparison_method` from `session-state.json`
      (F8 — not `engagement.json`, which holds `operator_mode`).
- [ ] FLAG-only — return schema has `additionalProperties:false` and no `replacement_text`.
- [ ] Findings surface above the Gate B display; Gate B still requires explicit `confirmer`
      (no auto-confirm — invariant #3).
- [ ] A schema-invalid/absent skeptic is re-dispatched once, then recorded in `missing[]` —
      never silently treated as "no concern".
- [ ] `gap-table-skeptic.schema.json` is additive; the pre-existing schemas are byte-unchanged.

## See also

- `$ASSET_ROOT/SPEC-workflow-phases-2-5.md` § 3b — the spec section this primitive realizes; § 1 engine
  rule; § 0c invariants #3/#6; § 3c acceptance.
- `$ASSET_ROOT/_modes/advisor/references/pay-equity-qc-protocol.md` — Phase 8 is the wiring target; the
  panel runs after `compare_compensation`, before the Gate B prompt.
- `$ASSET_ROOT/_core/schemas/gap-table-skeptic.schema.json` — the per-skeptic return schema (sealed; no
  `replacement_text`; does not `$ref` statutory-evidence).
- `$ASSET_ROOT/.claude/agents/critic.md` — the read-only agent both skeptics dispatch (it names
  "gap-table skeptics" as a spawn site).
- `$ASSET_ROOT/_core/primitives/completeness-critic.md` — sibling `$0` workflow-tool FLAG-only panel.
- `$ASSET_ROOT/_core/primitives/close-validation.md` — the other Phase-3 gate-enrichment panel (close
  seam; paid, inline — contrast: skeptics are $0, workflow-tool-eligible).
