---
engine: inline-agent
paid: true
fan_out_max: 3
---

# close-validation

Comp-suite v2 primitive (SPEC-workflow-phases-2-5.md § 3a). A perspective-diverse panel that
reads the **proposed** `master.yaml` before the atomic close write and flags problems the
single-pass schema validation (`close-flow.md` Step 3) cannot see: a decision that contradicts
a prior cycle, a cited statute figure that has gone stale, a proposed cost that breaks the
org's budget envelope. It enriches an **existing** human gate (the `/comp close` write gate) —
it does not add a new auto-advance path. FLAG-only: a `flag` blocks the atomic write until the
founder resolves it; the panel never edits `master.yaml`.

It runs **after** `close-flow.md` Step 3 (structural schema validation) succeeds and **before**
Step 5a (the atomic `master.yaml` write). The orchestrator surfaces any `flag` at the close
gate; the founder resolves, then re-runs `/comp close` (idempotent).

## Why this exists

`close-flow.md` Step 3 validates that the proposed `master.yaml` is *structurally* correct
(schemas pass, decision_log entries well-formed). It cannot tell that this cycle's decision
*contradicts* a decision three cycles back, that a cited CNESST figure changed last quarter, or
that the proposed adjustments exceed the budget the founder set at intake. Those are semantic
defects a cold reader catches and a schema does not. This panel is that cold reader — three of
them, each on its own lens — run on the proposed state at the one moment it is cheap to fix
(before the atomic write) rather than after the cycle is closed and archived.

## Contract

| | |
|---|---|
| **Signature** | `close_validation(proposed_master, prior_decision_log, budget_envelope) -> {lenses[], missing[]}` |
| **Inputs** | `proposed_master` — the in-memory proposed `master.yaml` (`close-flow.md` Step 2 output, written to `proposed-master.yaml.tmp`). `prior_decision_log` — the existing `master.decision_log[]` (for the internal-consistency lens). `budget_envelope` — the org's stated budget envelope (for the budget-coherence lens). |
| **Outputs** | `{lenses: list[dict], missing: list[dict]}` — `lenses` = the validated per-lens returns (`close-validation.schema.json`); `missing` = lenses absent or schema-invalid after one re-dispatch (`{lens, reason}`). |
| **DAG position** | Between `close-flow.md` Step 3 (validation success) and Step 5a (atomic write). The orchestrator surfaces flags at the close gate; the founder resolves before the write. |
| **Engine** | `inline-agent`, `paid: true`. The statutory-accuracy lens fetches (may call `perplexity-ask`) → the panel runs inline with per-call `check_budget` (§ 1 engine rule). A 3-lens panel split across two engines is not worth the complexity (§ 3a) — keep the whole panel inline. |
| **Calls** | 3 lenses in parallel (`fan_out_max: 3`). internal-consistency + budget-coherence dispatch the read-only `critic.md` ($0 Read). statutory-accuracy dispatches a **fetch-capable inline Agent** (`critic.md` cannot fetch) granted `[Read, WebSearch, perplexity-ask]` (plus the `$0` `WebFetch`-builtin for a statute URL); `WebSearch`/`WebFetch` are the guaranteed $0 evidence path, `perplexity-ask` is optional-when-configured. Each paid call gated per-call by `check_budget`. |
| **Schema** | Each lens return validates against `$ASSET_ROOT/_core/schemas/close-validation.schema.json` (`additionalProperties:false`, no `replacement_text`, no `blocking`; `statutory_tags[]` `$ref`s `statutory-evidence.schema.json`). |

## The three lenses

| Lens | Reads | Checks | Tool | Cost |
|---|---|---|---|---|
| **internal-consistency** | proposed `master.yaml` + `prior_decision_log` | this cycle's decisions vs prior `decision_log[]` contradictions | `Read` | `$0` |
| **statutory-accuracy** | proposed `master.yaml` + cited statute URLs | cited CNESST / pay-equity figures match current QC law | `WebSearch`/`WebFetch` builtin ($0) / `perplexity-ask` (paid, optional) | **paid** |
| **budget-coherence** | proposed `master.yaml` + `budget_envelope` | proposed comp costs vs the org's stated budget envelope | `Read` | `$0` |

## Engine choice — why the whole panel is inline + paid

The two $0 lenses *could* run on the Workflow tool, but the statutory-accuracy lens fetches and
the Workflow script cannot read `cost-log.jsonl`/`registry.yaml` to gate a paid call, nor pause
for `requires_user_confirm` (it runs autonomously) — invariant #1. Per the engine rule's
fail-safe ("can this agent call Perplexity? If yes or maybe → inline `Agent`"), the statutory
lens is inline. Rather than split a 3-lens panel across two engines for one $0 saving, the
whole panel runs as an inline parallel `Agent` dispatch (§ 3a). `paid: true` is declared
because at least one lens may call a paid tool; every such call routes through `check_budget`
per-call (never batch-pre-approved).

## The statutory lens cannot use critic.md (the one cross-agent constraint)

`critic.md` is read-only (`[Read, Grep, Glob]`, web tools disallowed) — its own "Statutory
Evidence — You Cannot Fetch" section states it "cannot return `confirmed` on a statutory or
market claim, because a `confirmed` verdict requires a fetched verbatim quote and you cannot
fetch one." So:

- **internal-consistency, budget-coherence** → dispatch `critic.md` with the lens prompt + the
  close-validation schema. Read-only is exactly right.
- **statutory-accuracy** → dispatch a **fetch-capable inline Agent** (granted `[Read, WebSearch,
  perplexity-ask]`, with the $0 `WebFetch`-builtin available for a statute URL; `WebSearch`+`WebFetch`
  are the guaranteed $0 path when no URL or no Perplexity), per-call `check_budget`. Its return still
  validates against `close-validation.schema.json` and carries the fetched `statutory_tags[].{url, quote}`.

**Invariant #5 (statutory quote post-check).** A statutory-accuracy return with `status: pass`
but no non-empty `statutory_tags[].quote` is **asserted-but-not-confirmed**. The orchestrator
downgrades it to a `flag` — reasoning from training data is never verification. This is an
orchestrator post-check (kept off the schema for the same reason intent-classification keeps
mode-membership off the schema, A1: a draft-07 `if/then` would be brittle and the house pattern
is an orchestrator post-check). Empty quote ⇒ not confirmed ⇒ flag.

## Model tiering (invariant #6b)

Invariant #6 has two levers: the fan-out cap (above) and **cheapest-model-that-fits**, where
"statutory judgment … → Opus" (SPEC § 0c). Apply both to this panel:

- **internal-consistency, budget-coherence** → the read-only `critic.md` default (`sonnet`).
  These are structural/arithmetic reads (decision_log diffing, cost-vs-envelope) — not statutory
  judgment; `sonnet` fits.
- **statutory-accuracy** → **Opus**. This is the panel's one statutory-judgment lens (does a
  cited CNESST/equity figure match current law given the fetched quote) — the exact case
  invariant #6(b) routes to Opus. Override the agent's default at dispatch (`model: opus`); the
  lens is already a bespoke fetch-capable inline Agent (not `critic.md`), so the model is set at
  the dispatch call.

Frontmatter declares only `engine`/`paid`/`fan_out_max` (the SPEC-pinned fields); the per-lens
model lever is realized here at dispatch, not in frontmatter.

## Reconciliation with Phase 1 refute-claim (F10)

The close-validation statutory lens and Phase 1's `refute-claim` statutory path share the
**evidence contract** (`statutory-evidence.schema.json`) but check **different objects**:

- `refute-claim` fires **pre-Write at the deliverable boundary** (per-claim, on deliverable
  text).
- close-validation fires **pre-write at the `master.yaml` boundary** (per-cycle, on
  `decision_log` entries).

They are different seams, not duplicates — close-validation does not re-verify already
`refute-claim`-confirmed deliverable claims; it checks the cycle's `decision_log` entries. No
shared verified-claims cache is specified: if the same statute URL recurs across both within a
session, the re-fetch is cheap (a $0 `WebFetch` for a known URL) — accept it rather than build a
cache (F10). **Build-order note:** Phase 1 (refuter.md) builds *after* Phase 3 per the § 6
order, so this primitive does not depend on it. At Phase 3 the statutory lens dispatches a
fetch-capable inline Agent directly; when refuter.md ships, the statutory lens MAY route its
fetch through the refute-claim path (same evidence contract, distinct seam) — a Phase-1
reconciliation, not a Phase-3 dependency.

## The flag-blocks-write barrier

```
close_validation(proposed_master, prior_decision_log, budget_envelope):
  lenses, missing = [], []
  returns = parallel() of [
    dispatch(critic.md, "internal-consistency", proposed_master + prior_decision_log),
    dispatch(fetch_agent, "statutory-accuracy", proposed_master),   # paid; per-call check_budget
    dispatch(critic.md, "budget-coherence", proposed_master + budget_envelope),
  ]
  for lens_name, r in returns:
    obj = return_message(r)
    if obj is not None and validates(obj, "close-validation.schema.json"):
      # invariant #5: statutory pass with no non-empty quote -> downgrade to flag
      if lens_name == "statutory-accuracy" and obj.status == "pass" \
         and not any(t.quote for t in obj.get("statutory_tags", [])):
        obj.status = "flag"
      lenses.append(obj)
    else:
      r2 = redispatch_once(lens_name)                                # one retry, not a loop
      obj2 = return_message(r2)
      if obj2 is not None and validates(obj2, "close-validation.schema.json"):
        lenses.append(obj2)
      else:
        missing.append({"lens": lens_name, "reason": "absent or schema-invalid after one re-dispatch"})
  return {"lenses": lenses, "missing": missing}

# orchestrator (close-flow.md Step 4.5), AFTER the panel returns:
#   if any lens.status == "flag" OR missing is non-empty:
#       surface flags + missing at the close gate; BLOCK the atomic write (Step 5a)
#       until the founder resolves and re-runs /comp close (idempotent)
```

- **A `flag` blocks the atomic write.** The founder resolves the flagged decision/figure/cost,
  then re-runs `/comp close` — idempotency makes re-run safe (`close-flow.md` § Idempotency).
- **A missing lens is not a passing lens.** Schema-invalid or absent → re-dispatch once, then
  record in `missing[]` and treat as a blocking gate failure (never silently "no findings").
- **Synthesis stays in the orchestrator.** The primitive returns the three validated lens
  returns; the orchestrator decides block/allow and surfaces at the gate. It never delegates
  the close decision to an agent.

## What stays in the orchestrator (never in this primitive)

- The **close gate** itself (the founder resolving flags, the re-run) — a human gate, never
  auto-advanced (invariant #3).
- The **block/allow decision** over the lens returns and the gate presentation — orchestrator
  state, never an agent self-report.
- `master.yaml` **assembly + atomic write** (`close-flow.md` Steps 2, 5) — orchestrator-run;
  the panel only reads the proposed state.

## Constraints

- **FLAG-only.** Lenses report findings; never author replacement text, never edit
  `master.yaml`. Schema is `additionalProperties:false` with no `replacement_text`, no `blocking`.
- **Statutory needs a fetched quote.** A `pass` with no non-empty `statutory_tags[].quote` is
  downgraded to a flag (invariant #5). The statutory lens cannot be the read-only `critic.md` —
  it must be a fetch-capable inline Agent.
- **Every paid call gated.** `paid: true`; the statutory lens routes each fetch through
  `check_budget` per-call — never batch-pre-approved, never inside a Workflow-tool script
  (invariant #1).
- **A `flag` blocks the atomic write** until founder-resolved; no auto-correct to `master.yaml`
  and no auto-advance past the close gate (invariant #3).
- **Fan-out ≤ 3** (the three lenses) — a bound on the panel's agent-token spend (invariant
  #6a); `cost-log.jsonl` is blind to it.
- **Model tiering (invariant #6b).** statutory-accuracy → Opus (statutory judgment); the two
  read-only lenses → `critic.md` default `sonnet`. Set the statutory lens model at dispatch.
- **No agent synthesis.** Synthesis/block decision is orchestrator-owned.

## Acceptance (SPEC § 3c)

- [ ] `close-validation.md` exists; declares `engine: inline-agent`, `paid: true`, `fan_out_max: 3`.
- [ ] Close-validation is FLAG-only; a `flag` blocks the atomic write until founder-resolved; no
      auto-correct to `master.yaml`.
- [ ] Statutory-accuracy lens routes its fetch through `check_budget` per-call; the two $0 lenses
      (internal-consistency, budget-coherence) do not consume budget.
- [ ] A statutory `pass` with no non-empty `statutory_tags[].quote` is downgraded to a flag
      (invariant #5).
- [ ] No new auto-advance path past the close gate (invariant #3).
- [ ] Model tiering realized (invariant #6b): statutory-accuracy dispatches Opus; the two
      read-only lenses run `critic.md`'s `sonnet` default.
- [ ] `close-validation.schema.json` is additive; the pre-existing schemas are byte-unchanged.

## See also

- `v2/SPEC-workflow-phases-2-5.md` § 3a — the spec section this primitive realizes; § 1 engine
  rule; § 0c invariants #1/#2/#3/#5/#6; § 3c acceptance.
- `v2/.claude/skills/comp/references/close-flow.md` — the wiring target; Step 4.5 invokes this
  panel between Step 3 (validation) and Step 5a (atomic write).
- `$ASSET_ROOT/_core/schemas/close-validation.schema.json` — the per-lens return schema (sealed; no
  `replacement_text`, no `blocking`; `statutory_tags[]` `$ref`s statutory-evidence).
- `$ASSET_ROOT/_core/schemas/statutory-evidence.schema.json` — the shared `{url, quote}` evidence shape
  the statutory lens carries (F6).
- `v2/.claude/agents/critic.md` — the read-only agent the two $0 lenses dispatch (it names
  "close-validation $0 lenses" as a spawn site and documents that it cannot fetch).
- `$ASSET_ROOT/_core/primitives/budget-check.md` — the per-call gate the statutory lens routes through.
- `$ASSET_ROOT/_core/primitives/completeness-critic.md` — sibling Phase-3/4 FLAG-then-human-gate panel.
- `$ASSET_ROOT/_core/primitives/refute-claim.md` — Phase 1 sibling on the deliverable seam (forthcoming;
  shares the statutory-evidence contract, checks a different object — F10).
