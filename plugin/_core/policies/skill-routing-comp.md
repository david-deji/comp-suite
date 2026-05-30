# Skill Routing — Comp-Suite Adaptation

> **Adaptation of**: `skill-routing.md` (verbatim TM port, sibling file)
> **TM source**: `.claude/rules/skill-routing.md` @ commit `4b1dd5d7`
> **Authoritative for**: `/comp` mode + tool dispatch. The verbatim raw is review-baseline only.
> **Date**: 2026-05-08 | Pinned independently of TM.
>
> **What changed from TM**: Dropped TM-skill-specific routing tables (`/research`, `/specify`, `/build`, `/brand`, `/presentation`) — comp-suite has none of those. Kept and ported the **named-Opus-trigger heuristics** and the **Haiku-default class** taxonomy verbatim — they are model-class theory, not skill theory. Merged with v2's existing 7-task taxonomy at `$ASSET_ROOT/_core/routing.yaml` as the override layer that decides when to escalate UP from a task default.

---

## 1. Decision Order (precedence — high to low)

When dispatching any agentic work in `/comp` (mode body, council, primitive
sub-call, tool dispatch), apply in order:

1. **Skill match?** → comp-suite has one skill (`/comp` itself). Sub-routing happens via
   modes (advisor / comms / training / transformer). Mode body owns its model + tool
   budget + prompt discipline. Examples: comms cascade drafting → comms mode body
   handles task taxonomy; advisor pay-equity council → advisor mode body dispatches
   council.
2. **Skill-level / mode-level model pin?** → if `$ASSET_ROOT/_modes/<name>/mode.yaml` pins a specific
   model for a task class (e.g., `model.overrides.council: opus`), the pin wins over the
   per-task matrix. WHY: mode authors have task-specific evidence the orchestrator does not.
3. **No mode-level pin → apply the per-task taxonomy** at `$ASSET_ROOT/_core/routing.yaml`
   (extraction / draft / synthesis / council / research / validation / long_horizon → series).
4. **Apply Opus-trigger heuristics** (§ 3 below) ONLY when the task default would route to
   sonnet but a named trigger fires. This is the override layer — it escalates UP, never DOWN.

Resolution precedence (re-stated, matches `routing.yaml` comments):

```
mode override > task default > global default > Opus-trigger override (UP only)
```

---

## 2. Haiku-default class (route DOWN from Sonnet — already in routing.yaml)

These task shapes already route to Haiku per `routing.yaml`. Listed here for completeness
of the model-class theory:

| Task shape | Series | Why Haiku |
|---|---|---|
| Document/file extraction subagents (find facts in N files, return structured) | `extraction → haiku` | Haiku 4.5 matches Sonnet 4 on extraction at 67% lower cost |
| Classification, routing/triage, dedup, format normalization | `validation → haiku` | Pattern matching = grep + classify; no judgment |
| Schema check, format check | `validation → haiku` | Deterministic, mechanical |
| Short-answer factual lookup (1-3 tool calls, deterministic) | (inline orchestrator, no dispatch) | Anything Sonnet adds is wasted |
| Transcript cleanup, lint, normalization passes | `validation → haiku` | Throughput 2x Sonnet |

If a /comp task is a "find facts in N engagement files and classify" shape, the orchestrator
dispatches with `task: extraction` → resolves to haiku via `routing.yaml`.

---

## 3. Opus triggers (route UP from Sonnet — named only, no "ambiguous" fallback)

When a task would otherwise route to sonnet (the routing.yaml default), escalate to opus
ONLY when one of these named triggers is present in the task. If you cannot name which
trigger applies, the task does not need Opus.

| Trigger | Comp-suite anchor |
|---|---|
| **Long-horizon agentic loop**: 50+ tool calls or multi-hour | Council deliberation with > 6 thinkers + research dispatch loop; pay-equity engagement that traverses entire workforce roster + multi-cycle decision_log |
| **Blank-canvas judgment**: Council, NBJ-substitute (Industry Outsider) thinker, review panel synthesis | Every council per `$ASSET_ROOT/_core/council/procedure.md` (already pinned `council → opus` in routing.yaml) |
| **Architecture / system design from scratch** | Comp-suite-internal: rare — only when adding a new mode (mode #5) or a new primitive. Otherwise mode bodies operate on established schemas. |
| **Vision/multimodal heavy work** | Decks with image-heavy interpretation (org charts, comp band visuals); reading scanned compensation policies. See model-registry.md § Opus 4.7 named exceptions. |
| **Specs/migration where wrong-model output = 10x rework** (asymmetric error cost) | Pay-equity legal-review where exact contract clause distinctions matter; engagement-state schema migration (v2.x → v3.x). |
| **Adversarial review of LARGE surface** (>10 files OR cross-cutting) | A council reviewing an entire engagement's deliverable bundle (4 modes touching 30+ files); multi-cycle audit |

**Triggers comp-suite drops from TM's list** (irrelevant to comp scope):
- "Multi-file refactor: >5 files OR >100k tokens" — comp-suite isn't a refactor target; modes operate on engagement state, not codebase
- "Cursor-shape coding agent work" — comp-suite is not a coding agent

---

## 4. Default = Sonnet (everything else)

- Standard mode body execution on a normalized engagement
- Draft generation (deck slides, comms drafts, training kits, decision documents)
- Synthesis of pre-curated material (advisor decision-doc from already-summarized council outputs — wait: that's `synthesis → opus` per routing.yaml; routing.yaml's pin wins over this default)
- Document analysis with bounded scope (between extraction and judgment)
- Multi-file edits within ONE engagement (typical)

**Trigger language** (encode verbatim in mode body dispatch decisions):

> Default to Sonnet. Escalate to Opus only when one of the named Opus triggers above is
> present in the task. If you cannot name which trigger applies, the task does not need Opus.

---

## 5. Why named-trigger over route-UP-on-ambiguity

(Inherited verbatim reasoning from TM 2026-05-02 cost-driven revert — see TM source body.)

A "route UP when ambiguous" rule over-routes to Opus and inflates subagent-heavy session
cost. External evidence from Mar-May 2026 shows Sonnet 4.6 handles 70-80% of mode-body
workloads at 40% lower cost. The seven named triggers above are the validated set; the
default is sonnet.

For comp-suite specifically: every paid Perplexity dispatch already costs 0.03–0.30 USD
per call (per `tools/registry.yaml` cost tiers), and councils dispatch up to 6+ thinkers.
Routing the orchestrator alone to Opus by default would compound with these dispatch costs
in the wrong direction. See `cost-discipline.md` (sibling policy).

---

## 6. Comp-suite cost guardrails interaction

Model class is one cost lever; per-engagement budget is another. The mode-dispatcher
primitive (`$ASSET_ROOT/_core/primitives/mode-dispatcher.md`) resolves the model series; the
budget-check primitive (`$ASSET_ROOT/_core/primitives/budget-check.md`) enforces the dollar cap. Both
must pass before any tool dispatch with `est_call_cost_usd > 0`.

If the orchestrator can satisfy a task with sonnet at 1/5 the per-token cost of opus,
that frees budget for more Perplexity research within the engagement's `budget_usd`. The
two levers compound: cheap-but-correct model + named-trigger upward escalation = sustainable
Perplexity-bearing engagements on a personal credit card.

---

## See Also

- `$ASSET_ROOT/_core/routing.yaml` — the 7-task taxonomy this rule layers on top of
- `$ASSET_ROOT/_core/policies/skill-routing.md` — verbatim TM raw (review baseline)
- `$ASSET_ROOT/_core/policies/cost-discipline.md` — companion: cap experiments before starting
- `$ASSET_ROOT/_core/model-registry.md` — series → specific model ID resolution
- `$ASSET_ROOT/_core/primitives/mode-dispatcher.md` — the consumer of this rule
