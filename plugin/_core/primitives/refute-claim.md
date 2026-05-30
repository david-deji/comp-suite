---
engine: inline-agent
paid: true
fan_out_max: 3
---

# refute-claim

Comp-suite v2 primitive (SPEC-workflow-phase1.md). The **pre-Write adversarial-verify gate**: it
converts comp-suite's most dangerous prose discipline — "verify-before-assert on factual claims"
(`advisor/main.md:95`) — into a **structural, mode-invoked gate that fires before a deliverable is
written**. It scope-detects the flagged claims in a draft (`[PROXY]`/`[ESTIMATED]` market figures,
`[statutory]` CNESST/equity citations), dispatches perspective-diverse skeptics to fetch evidence
and try to refute each, and surfaces the verdicts **above the existing human gate** (advisor
Checkpoint B for market numbers; the affichage/synthesis confirmation gate for statutory). It
enriches existing gates — it adds no new auto-advance path. FLAG / BLOCK only: a statutory
`disputed`/`unverifiable` blocks auto-finalize until the founder resolves it against a verified
source; the gate never authors replacement text.

## Why this exists

The named dominant risk is **silent failure** — a wrong P50 that scales a $10K error across 200
employees into a ~$2M cost-model error, or a misquoted CNESST article in an arbitration-facing
deck. Both read as perfectly plausible and pass every current gate until Stop. `fact-check.sh`
(Stop) checks citation *presence* (regex ±5 lines), not accuracy, and fires too late;
`anti-slop.sh` (PostToolUse) is lexical and post-write. Neither catches a fluent, well-cited,
*wrong* number. This gate is the missing **pre-Write accuracy** check — it verifies the claim
against fetched evidence at the one moment it is cheap to fix (before the deliverable is written),
and it never trusts "the skeptics failed to refute it" as confirmation.

| Gate | When | Checks |
|---|---|---|
| `fact-check.sh` | Stop (session end) | citation **presence** (regex) — too late, presence≠accuracy |
| `anti-slop.sh` | PostToolUse:Write | never-list terms — post-write, lexical |
| **`refute-claim`** | **pre-Write (mode step)** | claim **accuracy** vs fetched evidence |

## Contract

| | |
|---|---|
| **Signatures** | `refute_claim(claim_text, source_url, claim_class, lens) -> verdict` (one skeptic on one claim); `verify_deliverable(deliverable_draft, engagement_state) -> gate_result` (the mode-invoked wrapper) |
| **Inputs** | `verify_deliverable`: the assembled-but-unwritten draft + the engagement state (for `check_budget`). `refute_claim`: the flagged claim text, its source URL (statutory) or source datum (market), its class, and the lens. |
| **Outputs** | `gate_result` = `{verdicts: list[dict], blocked: list[dict], report_path: str, missing: list[dict]}` — `verdicts` validate against `refute-claim.schema.json`; `blocked` = the claims whose aggregate disposition blocks auto-finalize; `missing` = skeptics absent/invalid after one re-dispatch. |
| **DAG position** | A mode-invoked **pre-Write** step at the deliverable-assembly boundary — **not** a CC hook (`production-gates.md` hooks are all PostToolUse, i.e. post-write). It runs after the draft is assembled and before the branded-text Write. |
| **Engine** | `inline-agent`, `paid: true`. A skeptic may call `perplexity-ask` ($0.03) → the gate runs as inline parallel `Agent` dispatch with per-call `check_budget` (§ engine choice). |
| **Calls** | N skeptics per flagged claim (`subagent_type: refuter`), run in parallel: **statutory N=3** (`fan_out_max: 3`), **market N=2**. Statutory evidence tool: `statute-fetch` (WebFetch builtin, $0) when a URL is cited → when no URL, `web-search` (builtin, $0) to locate the official source then WebFetch it, or `perplexity-ask` ($0.03) when Perplexity is configured. Market: `market-data` ($0) and/or `web-search` ($0) / `perplexity-ask` ($0.03, when configured). Perplexity is optional throughout — the $0 builtins are the guaranteed evidence path; no-evidence still resolves to `unverifiable`, never PASS. |
| **Schema** | Each skeptic return validates against `$ASSET_ROOT/_core/schemas/refute-claim.schema.json` (`additionalProperties:false`, no `replacement_text`; `statutory_evidence` `$ref`s `statutory-evidence.schema.json`). |

## Scope detection (SPEC § 5)

Scan the draft for these tokens only — never a blanket verify over every number:

- **Trigger:** `[PROXY]`, `[ESTIMATED]` → `claim_class: market`; `[statutory]` → `claim_class: statutory`.
- **Skip (already grounded):** `[EXACT]`, `[MATCHED]`, `[WEB-VERIFIED …]`, `[survey-house]`, `[user-provided-cba]`, `[CONSENSUS]`.

A "claim" = the tagged token + its associated number/citation on the same line/sentence + the
nearest source URL (statutory) or source datum (market). Untagged bare numbers are out of scope in
Phase 1 (revisit if false-negatives surface).

## Engine choice — why inline + paid, never the Workflow tool

A skeptic may call a paid tool (`perplexity-ask`), and **every paid call routes through
`check_budget` per-call** (invariant #1, the engine-selection spine). The Workflow tool runs
autonomously and cannot read `cost-log.jsonl`/`registry.yaml` to gate a paid call, nor pause for
`requires_user_confirm` — so a paid-capable gate cannot run inside a Workflow script. Per the
engine rule's fail-safe ("can this agent call Perplexity? If yes or maybe → inline `Agent`"),
refute-claim is inline. It reuses the exact mechanism `council-dispatch.md` already uses (inline
parallel `Agent`, `run_in_background`, max 5 concurrent). The Workflow tool enters at **Phase 2**
(`council-parallel`, all-`$0` lenses) and for batch operations where per-call gating is not in
tension; it is the wrong engine here.

## The skeptic is refuter.md, not critic.md (the one cross-agent constraint)

`critic.md` is read-only (`[Read, Grep, Glob]`, web tools disallowed) — its own "Statutory
Evidence — You Cannot Fetch" section states it "cannot return `confirmed` … because a `confirmed`
verdict requires a fetched verbatim quote and you cannot fetch one," and it names refuter as "a
separate file (refuter fetches and discards unsourced refutations; a critic stays read-only)." So
this gate dispatches **`refuter.md`** (granted `WebFetch`, `perplexity-ask`, `market-data`,
`Read`) — the fetch-capable sibling — never `critic.md`. A refutation with no fetched evidence
artifact is discarded by the refuter, not acted on.

## Model tiering (invariant #6b)

Invariant #6 has two levers: the fan-out cap (above) and **cheapest-model-that-fits**, where
"statutory judgment … → Opus" (SPEC § 0c). The refuter's frontmatter default is `sonnet` (fits
market verification — fetch a counter-source, compare a number). The orchestrator **overrides
statutory dispatches to `model: opus`** at the dispatch call — statutory verification (jurisdiction,
recency, verbatim-match of a CNESST article against fetched law) is the exact statutory-judgment
case invariant #6(b) routes to Opus. This mirrors close-validation, which sets its statutory lens
to Opus at dispatch while the read-only lenses run the `sonnet` default. Frontmatter declares only
the SPEC-pinned `engine`/`paid`/`fan_out_max`; the per-class model lever is realized here at
dispatch.

## Verdict enforcement (tiered — SPEC § 6)

The orchestrator aggregates the N per-lens verdicts into one disposition per claim, then applies:

| claim_class | aggregate verdict | action |
|---|---|---|
| **statutory** | `confirmed` (a lens fetched a verbatim quote matching the cited article; no lens disputed) | tag stays `[statutory]`; proceed |
| statutory | `disputed` (any lens fetched text that contradicts the citation) | **BLOCK auto-finalize**; surface cited claim **and** fetched evidence side-by-side; founder resolves (re-cite / visibly downgrade / remove). Never auto-correct |
| statutory | `unverifiable` (no URL **and** ask fallback empty) | **BLOCK auto-finalize**; surface; founder resolves |
| statutory | `fetch_failed` (URL present, fetch errored/timed out) | **do NOT demote**; surface "could not verify — verify manually"; non-blocking flag (a flaky network must not block a correct citation) |
| **market** | `confirmed` (a counter-source agrees within tolerance) | may upgrade `[PROXY]`/`[ESTIMATED]` → `[WEB-VERIFIED <date>]` (founder-visible) |
| market | `disputed` (a counter-source disagrees materially) | surface **both** values side-by-side (anti-averaging, `advisor/main.md`); recommend `[DISPUTED]`; founder picks; **non-blocking** |
| market | `unverifiable` (no counter-source found) | recommend `[UNVERIFIED]`; surface; **non-blocking** |

**Aggregation rule.** Most-conservative-wins: an evidence-backed `disputed` from **any** lens
dominates (a single sourced refutation is a strong signal). An unsourced `disputed` — one carrying
no fetched contradicting evidence — is first dropped to `unverifiable` by the same no-evidence
post-check that guards `confirmed` (above), so only evidence-backed disputes reach aggregation.
`confirmed` requires at least one evidence-backed confirm and no evidence-backed dispute. All-lenses-`unverifiable` → `unverifiable`.
All-`fetch_failed` → `fetch_failed`. This is the adversarial / perspective-diverse verify pattern —
distinct lenses (statutory: jurisdiction, recency, verbatim-match; market: pricing-source, recency)
catch failure modes redundancy cannot.

**Invariant #5 (no-evidence is never PASS).** After schema validation, the orchestrator re-maps any
`confirmed` carrying no evidence artifact — statutory with empty/absent `statutory_evidence.quote`,
or market with null `retrieved_value` — to `unverifiable`. "Skeptics failed to refute" is not
verification. This is an orchestrator post-check kept off the schema (A1 — a draft-07 `if/then`
would be brittle; the house pattern is orchestrator post-check, same as intent-classification
mode-membership and close-validation's quote check).

**Surfacing.** The gate writes `verification-report.md` to the engagement working dir and surfaces
flags **above** the relevant human checkpoint (Checkpoint B for advisor market claims; the
affichage/synthesis confirmation gate for statutory). "BLOCK auto-finalize" = the orchestrator will
not mark the deliverable final / advance past the checkpoint until the founder resolves each
blocking flag. Founder override is always available.

**Tag propagation.** Resolved tags travel into the deliverable and into `master.yaml`
`decision_log` notes (the same propagation discipline as `[UNRESEARCHED]` in `operations.md`). Tags
never disappear silently.

## The gate barrier (verify_deliverable)

```
verify_deliverable(deliverable_draft, engagement_state):
  flagged = scan_tokens(deliverable_draft)          # § scope — only [PROXY] [ESTIMATED] [statutory]
  verdicts, blocked, missing = [], [], []
  for claim in flagged:
    N    = 3 if claim.class == "statutory" else 2
    tool = evidence_tool(claim)                      # statutory: statute-fetch($0) | ask($0.03 if no URL)
                                                      # market:   market-data($0)   | ask($0.03)
    est  = N * cost_of(tool)                          # $0 tools short-circuit allow in check_budget
    gate = check_budget(engagement_state, tool, est) # PER CLAIM — never batch-pre-approved
    if not gate.allow:
      verdicts.append(verdict(claim, "unverifiable", reason="budget"))   # surface; zero bytes to cost-log
      blocked.append(claim) if claim.class == "statutory" else None
      continue
    if gate.requires_user_confirm and not founder_yes():
      verdicts.append(verdict(claim, "unverifiable", reason="declined")); continue
    lens_returns = parallel_agent(refuter × N, claim,                    # inline, max 5 concurrent
                                  model = "opus" if claim.class=="statutory" else "sonnet")  # #6b
    for r in lens_returns:
      obj = return_message(r)
      if obj is None or not validates(obj, "refute-claim.schema.json"):
        r2 = redispatch_once(r);  obj = return_message(r2)               # one retry, not a loop
      if obj is None or not validates(obj, "refute-claim.schema.json"):
        missing.append({"claim": claim.text, "lens": r.lens, "reason": "absent or schema-invalid"}); continue
      # invariant #5: a 'confirmed' with no evidence artifact -> unverifiable
      if obj.verdict == "confirmed" and not has_evidence(obj):  obj.verdict = "unverifiable"
      # symmetric guard: a 'disputed' with no fetched contradicting evidence is dropped to
      # 'unverifiable' too (the refuter must not return disputed without a fetched artifact) —
      # only evidence-backed disputes reach aggregate(); fail-safe, never under-blocks
      if obj.verdict == "disputed"  and not has_evidence(obj):  obj.verdict = "unverifiable"
      verdicts.append(obj)
      append_cost_log(tool) if tool_is_paid(tool) else None             # orchestrator owns append, AFTER the call
    disposition = aggregate(verdicts_for(claim), claim.class)           # § 6 — most-conservative-wins
    if blocks(disposition):  blocked.append(claim)                      # statutory disputed/unverifiable
  report_path = write_report("verification-report.md", verdicts, blocked, missing)
  return {"verdicts": verdicts, "blocked": blocked, "report_path": report_path, "missing": missing}

# orchestrator, at the deliverable checkpoint, AFTER the gate returns:
#   if blocked is non-empty OR missing is non-empty:
#       surface flags (cited + fetched side-by-side) above the human checkpoint;
#       BLOCK auto-finalize until the founder resolves each blocking flag (override available).
```

- **A statutory `disputed`/`unverifiable` blocks auto-finalize.** A `fetch_failed` does not (verify
  manually). Market verdicts are all non-blocking (surface + recommend a tag).
- **A missing skeptic is not a passing skeptic.** Schema-invalid or absent → re-dispatch once, then
  record in `missing[]` and surface — never silently "no findings".
- **No batch pre-approval.** `check_budget` is called once per claim, never once for the deliverable.
  A refusal writes zero bytes to `cost-log.jsonl`; a successful paid call appends one line *after*.

## Reconciliation with Phase 3 close-validation (F10)

refute-claim and close-validation share the **evidence contract**
(`statutory-evidence.schema.json`) but check **different objects** at **different seams**:

- **refute-claim** fires **pre-Write at the deliverable boundary** (per-claim, on deliverable text).
- **close-validation** fires **pre-write at the `master.yaml` boundary** (per-cycle, on
  `decision_log` entries).

They are not duplicates: refute-claim does not re-verify `master.yaml` decisions, and
close-validation does not re-verify deliverable claims. No shared verified-claims cache is
specified — if the same statute URL recurs across both within a session, the re-fetch is cheap (a
$0 `WebFetch` for a known URL); accept it rather than build a cache. close-validation.md already
records this from the Phase-3 side: when refuter.md ships (now), its statutory lens **may** route
its fetch through this refute-claim path (same evidence contract, distinct seam) — a Phase-1
reconciliation, not a Phase-3 dependency.

## What stays in the orchestrator (never in this primitive)

- The **human checkpoints** (Checkpoint B for advisor market; the affichage/synthesis confirmation
  gate for statutory) — the founder resolving flags. The gate informs them; it never replaces them
  (invariant #3).
- The **aggregate/block decision** over the per-lens verdicts and the gate presentation —
  orchestrator state, never an agent self-report.
- The **cost-log append** (after each successful paid call) and the **budget refusal** (zero bytes
  on refusal) — orchestrator-owned per `budget-check.md`.
- The **deliverable Write** itself — orchestrator-run; the gate only reads the assembled draft.

## Constraints

- **FLAG / BLOCK only.** Skeptics report verdicts; never author replacement text, never edit the
  deliverable. Schema is `additionalProperties:false` with no `replacement_text` — a wrong citation
  is resolved by the founder, never by LLM synthesis.
- **No-evidence is never PASS.** A `confirmed` with no fetched artifact is re-mapped to
  `unverifiable` (invariant #5); a statutory `unverifiable` BLOCKs auto-finalize.
- **`fetch_failed` ≠ `disputed`.** A flaky-network fetch failure surfaces "verify manually" and is
  non-blocking; it never demotes a correct citation. Auto-downgrade happens only when founder-visible.
- **Every paid call gated per-call.** `paid: true`; each `perplexity-ask` routes through
  `check_budget` before dispatch — never batch-pre-approved, never inside a Workflow-tool script
  (invariant #1). Refusal → claim `unverifiable` + surfaced + zero cost-log bytes.
- **Scope to flagged claims only.** `[PROXY]`/`[ESTIMATED]`/`[statutory]` — never a blanket verify
  over every number. Cap N (statutory 3, market 2); `fan_out_max: 3`.
- **The human gate stays human.** No new auto-advance path; the gate surfaces above an existing
  checkpoint and the founder resolves (invariant #3).
- **`fact-check.sh` and `anti-slop.sh` are byte-unchanged** — they remain belt-and-braces backstops
  behind this pre-Write accuracy gate.

## Acceptance (SPEC § 9)

- [ ] `refute-claim.md` declares `engine: inline-agent`, `paid: true`, `fan_out_max: 3`; carries the
      § Contract signatures and § 6 semantics.
- [ ] `refute-claim.schema.json` validates verdicts; `additionalProperties:false`; a verdict with
      `replacement_text` **fails** validation (top level and inside `statutory_evidence`).
- [ ] A `confirmed` with empty `statutory_evidence.quote` (statutory) or null `retrieved_value`
      (market) is re-mapped to `unverifiable` (invariant #5).
- [ ] Scope detection flags only `[PROXY]`/`[ESTIMATED]`/`[statutory]`; skips
      `[EXACT]`/`[MATCHED]`/`[WEB-VERIFIED]`/`[survey-house]`/`[user-provided-cba]`/`[CONSENSUS]`.
- [ ] A statutory `disputed` blocks auto-finalize and surfaces cited + fetched text; no auto-correct.
- [ ] `fetch_failed` is distinct from `disputed` and does not demote the tag.
- [ ] Each paid skeptic call routes through `check_budget` before dispatch; over-budget → claim
      `unverifiable` + surfaced + **zero** cost-log bytes; a cost-log line is appended **after** each
      successful paid call. `check_budget` is per-claim, never batched.
- [ ] The gate is a mode-invoked pre-Write step; `fact-check.sh` and `anti-slop.sh` are byte-unchanged.
- [ ] `mode.yaml: pre_write_gates` includes `refute-claim` on advisor + comms; the orchestrator
      discovers it dynamically (no hardcoded mode list).
- [ ] Model tiering realized (invariant #6b): statutory dispatches Opus; market runs the refuter
      `sonnet` default.
- [ ] Scenarios 18/19/20 pass under `bash $ASSET_ROOT/tests/run.sh` (shape + fixture existence per the bench).

## See also

- `$ASSET_ROOT/SPEC-workflow-phase1.md` — the spec this primitive realizes (§ 3 signatures, § 5 scope, § 6
  enforcement, § 8 refuter, § 9 acceptance).
- the `refuter` agent (dispatched by name via `subagent_type: refuter`) — the fetch-capable skeptic this
  gate dispatches (sibling of `thinker`/`critic`; refuter fetches, critic cannot). Lives at
  `agents/refuter.md` in the plugin, `.claude/agents/refuter.md` in the dev repo; resolution is by name, not path.
- `$ASSET_ROOT/_core/schemas/refute-claim.schema.json` — the verdict schema (no `replacement_text`;
  `statutory_evidence` `$ref`s statutory-evidence).
- `$ASSET_ROOT/_core/schemas/statutory-evidence.schema.json` — the shared `{url, quote}` evidence shape (F6).
- `$ASSET_ROOT/_core/primitives/budget-check.md` — the per-call gate every paid skeptic routes through.
- `$ASSET_ROOT/_core/primitives/close-validation.md` — Phase-3 sibling on the `master.yaml` seam (shares the
  statutory-evidence contract, checks a different object — F10).
- `$ASSET_ROOT/_core/hooks/fact-check.sh` — the Stop-time presence backstop this accuracy gate complements.
- the `comp` orchestrator SKILL § Pre-write gate panels — the orchestrator discovery + blocking table.
- `$ASSET_ROOT/_modes/advisor/main.md:95` — the verify-before-assert prose discipline this gate structuralizes.
- `$ASSET_ROOT/_modes/advisor/references/pay-equity-qc-protocol.md` § Phase 10 — the affichage statutory carve-out.
