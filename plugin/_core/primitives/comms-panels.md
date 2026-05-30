---
engine: workflow-tool
paid: false
fan_out_max:
  anti-pattern-verifier: 1
  fr-ca-tell-detector: 1
  perspective-review: 3
---

# comms-panels

Comp-suite v2 primitive (Phase 4 — coverage net). Three FLAG-only adversarial panels that
sit between a comms draft and its human acknowledgment gate, each a **separate checker from the
author**. The current comms self-review runs inside the author's own context — the weakest gate
there is, because the agent that wrote the prose is the one grading it. These panels move the
grading to an independent agent (the generic `critic.md`) that never saw the draft being written.

The three panels:

1. **anti-pattern verifier** — banned-phrase violations against the engagement's anti-pattern list. Hard-block the write if any violation is found.
2. **FR-CA tell-detector** — anglicisms, SVO rigidity, register slips, vous/tu mixing (Bill 96 authenticity).
3. **perspective-diverse `/review` panel** — `correctness × register × legal` lenses in parallel, synthesized by the orchestrator (never by an agent).

All three read **local files only** (the redacted draft + the engagement config) → $0 under the
dollar gate → Workflow-tool-eligible (spec § 1, § 4c). None calls Perplexity. None authors
replacement text. None decides its own blocking status. The orchestrator owns the gate.

## Why this exists

Comms drafts ship to employees, managers, and execs at the most sensitive moment of a comp cycle.
A single banned phrase the CHRO explicitly rejected last cycle, an anglicism that reads as
machine-translated French, or a legal overstatement in a pay-equity announcement is a real
client-facing failure — and the author re-reading its own draft is the failure mode (failure mode
#6, silent failure: plausible prose that reads well and is wrong). Separating the checker from the
author is the structural fix. The panels do not improve the prose; they **find what the author
cannot see in its own output**.

## The load-bearing ordering (invariant #7)

The comms C05 redaction pass must complete on the draft **before** any panel agent receives it.

These panels are the first subagents in comms history to see draft text. Every prior comms
self-review stayed inside the orchestrator's context and never crossed a subagent boundary. A
panel agent is therefore a **new PII surface**: an un-redacted draft carries names, salaries,
headcount, and contact info into the subagent's transcript, where it persists beyond the panel's
own run. The fix is sequencing, not scrubbing-after: redact first per `references/redaction-rules.md`
(C05), then dispatch the panel on the redacted text. Never dispatch a panel on a draft that has not
cleared the redaction pass — surface "redaction incomplete; panels withheld" and stop, rather than
panel-then-redact.

```
draft authored ──▶ C05 redaction pass (references/redaction-rules.md) ──▶ panels dispatched on REDACTED text
                   ▲                                                       ▲
                   PII removed here                                        first subagent boundary —
                   (names→roles, $→bands,                                  must be PII-clean before this
                    headcount→size_band)
```

## Contract

| | |
|---|---|
| **Inputs** | `redacted_draft_path: str` (the artifact draft, post-C05), `engagement_config: dict`, `languages: list[str]` |
| **Outputs** | `{anti_pattern: dict, fr_ca_tells: dict \| null, review: dict}` — three structured panel results; FR-CA panel is `null` when no FR-CA language is enabled |
| **DAG position** | Post-redaction, pre-acknowledgment — runs AFTER C05 completes and BEFORE the operator acknowledgment / approval-stage gate (`references/contracts.md` C03, C07; `references/approval-stage-tracking.md`) |
| **Calls** | Dispatches `critic.md` agents (each with `Read` access to the redacted draft + config); no paid tool, no Perplexity |
| **Engine** | `workflow-tool` (all panels $0; agents inside a workflow keep `Read`) or inline parallel `Agent` (equivalent at $0 — prefer the Workflow tool for its resumable journal) |
| **Schemas** | `comms-anti-pattern.schema.json`, `comms-tell-detector.schema.json`, `comms-review-lens.schema.json` — all `additionalProperties: false`, none carries `replacement_text`, none carries `blocking` |

Each panel supplies its lens prompt + return schema to the **generic** `critic.md` at dispatch
(spec F7 — one critic agent, parameterized; no bespoke agent file per panel). The `critic.md`
posture is "read the inputs, apply the lens in your task prompt, return exactly the schema you are
given" — read-only, never fetch, never author replacement text.

## Panel 1 — anti-pattern verifier (`fan_out_max: 1`)

One critic reads the redacted draft and the engagement's anti-pattern list (from
`org-comms-profiles/<org-slug>.yaml` `anti_patterns[]` + bundled `template_assets/anti-patterns.yaml`,
per C03). It returns every banned-phrase match it finds — and nothing else.

```
anti_pattern_verify(redacted_draft, anti_patterns[]) -> {violations[]}
  violations[]: [{phrase, location, source_note}]   # source_note = why this phrase is banned (e.g. "CHRO explicit rejection FY25")
```

- **Return** validates against `comms-anti-pattern.schema.json` (`{violations: [...]}`, `additionalProperties: false`, no `replacement_text`).
- **Blocking is orchestrator-computed, not agent output.** The critic reports `violations[]`; the orchestrator hard-blocks the write when `violations[]` is non-empty. The agent never sets a `blocking` field — a permissive agent self-reporting `blocking: false` on a real CHRO-rejected phrase would re-introduce the silent failure this panel exists to catch. The orchestrator's rule is mechanical: `block_write = len(violations) > 0`.
- This is **existing comms discipline** (C03 anti-pattern checklist) now structurally separated from the author. Before this primitive, the author surfaced its own anti-pattern check; now an independent critic does, and the orchestrator enforces the block.

Schema shape (source of truth: `$ASSET_ROOT/_core/schemas/comms-anti-pattern.schema.json`):
`{ violations: [{ phrase, location, source_note? }] }` — `additionalProperties:false` at every
level, no `replacement_text`, no `blocking`. `source_note` records why the phrase is banned (for
the operator's surface, not a fix).

## Panel 2 — FR-CA tell-detector (`fan_out_max: 1`)

One critic reads the FR-CA draft and flags the signatures of English-calque French — the tells that
make Québec-audience copy read as machine-translated rather than natively written. Skipped (returns
`null`) when no FR-CA language is enabled for the engagement.

```
fr_ca_tell_detect(redacted_fr_draft) -> {tells[]}
  tells[]: [{category, excerpt, location}]
  category ∈ {anglicism, svo-rigidity, register-slip, vous-tu-mixing}
```

- **anglicism** — English loanwords or calques where a QC-French term exists (e.g. *bénéfices* for *avantages sociaux*).
- **svo-rigidity** — English subject-verb-object word order imposed on French where native phrasing differs.
- **register-slip** — formality drift away from the speaker register resolved per C07 (CEO/CHRO/VP Ops/HRBP).
- **vous-tu-mixing** — inconsistent second-person address within one artifact.

- **Return** validates against `comms-tell-detector.schema.json` (`{tells: [...]}`, `additionalProperties: false`, no `replacement_text`).
- **FLAG-only, advisory.** The tell-detector never blocks and never rewrites; it surfaces `tells[]` to the operator above the acknowledgment gate. Authenticity is a judgment call the human makes — the panel informs it, the FR-first co-draft discipline (C04) and the human gate own it. Surface the flags with the location and category so the operator can decide, instead of silently editing the French.

Schema shape (source of truth: `$ASSET_ROOT/_core/schemas/comms-tell-detector.schema.json`):
`{ tells: [{ category, excerpt, location }] }` where
`category ∈ {anglicism, svo-rigidity, register-slip, vous-tu-mixing}` — `additionalProperties:false`,
no `replacement_text`, no `blocking`. The whole return is `null` when no FR-CA language is enabled.

## Panel 3 — perspective-diverse `/review` panel (`fan_out_max: 3`)

Three critics run in `parallel()`, one lens each, on the redacted draft. The orchestrator
synthesizes the three structured reports — synthesis is **never** delegated to an agent (hard-no,
spec § 0b; `council-output-pattern`).

| Lens | Reads | Checks | Tool |
|---|---|---|---|
| correctness | redacted draft + source recommendation (`master.yaml` advisor section) | does the draft match the decision it communicates — figures, effective dates, eligibility carried correctly from the source? | Read ($0) |
| register | redacted draft + resolved speaker register (C07) | does the prose match the active speaker's `tone_descriptors` / `do_words` / `dont_words`? | Read ($0) |
| legal | redacted draft + cited statutory references | does any claim overstate entitlement, misstate a pay-equity obligation, or assert a figure no source backs? | Read ($0) |

- Each lens returns `comms-review-lens.schema.json` (`{lens, status: pass|flag, findings[]}`, `additionalProperties: false`, no `replacement_text`, no `blocking`).
- **All FLAG-only.** The legal lens flags overstatement; it does not author corrected legal language and does not auto-block — the orchestrator surfaces every `flag` above the existing operator acknowledgment / approval-stage gate, and the human resolves before advancing. The panel informs the gate; it never replaces it (invariant #3).
- **Synthesis is orchestrator-owned.** After the barrier, the orchestrator collects the three lens reports (each critic's schema-validated return message → validate) and assembles one surface for the operator. It does not dispatch a fourth agent to "merge the reviews."
- **Statutory note (invariant #5).** The legal lens runs `Read`-only on the draft and its already-cited references — it does **not** fetch. A legal lens cannot return `confirmed` on a statute it did not fetch; that is `refute-claim`'s job at the deliverable boundary (Phase 1, inline-Agent, paid). Here the legal lens flags *suspected* overstatement for the human and for a downstream `refute-claim` pass — it never asserts a statute is correct from training data alone.

Schema shape (source of truth: `$ASSET_ROOT/_core/schemas/comms-review-lens.schema.json`):
`{ lens: correctness|register|legal, status: pass|flag, findings: [{ description, location, severity? }] }`
— `additionalProperties:false`, no `replacement_text`, no `blocking`. `severity ∈ {high, medium, low}`
is advisory weight for the human, not a block trigger.

## FR-CA co-draft independence (spec § 4c)

The parallel FR+EN co-draft is a separate opportunity, in scope here only under one condition: each
draft agent receives the **source recommendation** (the `master.yaml` advisor section), never the
other language's draft. FR is still drafted first and EN co-drafted from the FR *source* per C04 —
but when the two are produced in parallel, both read the recommendation independently. Feeding the
EN agent the FR draft (or vice versa) reintroduces the translation calque C04 exists to prevent and
couples two agents that must stay independent. Pass both agents the source; never pass either agent
the other's output.

## Orchestrator usage pattern

```python
# 1. Author has written the draft; C05 redaction pass has completed (load-bearing — invariant #7)
if not redaction_complete(draft_path):
    surface("redaction incomplete; panels withheld")   # never panel-then-redact
    return

redacted = redacted_draft_path   # post-C05 path

# 2. Dispatch the three panels on the REDACTED text (Workflow tool, or inline parallel Agent — both $0)
anti     = critic(redacted, lens="anti-pattern",    schema="comms-anti-pattern.schema.json",   anti_patterns=cfg.anti_patterns)
tells    = critic(redacted, lens="fr-ca-tell",      schema="comms-tell-detector.schema.json")  if "fr-ca" in languages else None
review   = parallel(                                                                            # fan-out ≤ 3
    critic(redacted, lens="correctness", schema="comms-review-lens.schema.json", source=advisor_section),
    critic(redacted, lens="register",    schema="comms-review-lens.schema.json", register=resolved_register),
    critic(redacted, lens="legal",       schema="comms-review-lens.schema.json", refs=cited_statutes),
)

# 3. Barrier + validate each return (each critic's schema-validated return message -> schema validate)

# 4. Orchestrator computes blocking — never the agent
block_write = len(anti["violations"]) > 0          # anti-pattern hard-block
if block_write:
    surface(anti["violations"]); abort_write(); return

# 5. Orchestrator synthesizes the /review panel (NOT an agent) and surfaces all flags above the human gate
synthesized = synthesize_review(review)            # orchestrator-inline
surface_above_gate(anti, tells, synthesized)       # operator acknowledges; approval stage stays human

# 6. Only after the human acknowledgment / approval-stage gate may the write proceed.
```

## Constraints

- **FLAG-only across all three panels.** No panel authors replacement text for any phrase, tell, or claim. Surface the location and the reason; let the human decide. The one place this bites hardest is the legal lens — flag suspected overstatement, never rewrite the legal sentence.
- **Blocking is orchestrator state, not agent output.** Only the anti-pattern verifier triggers a hard block, and only the orchestrator computes it (`len(violations) > 0`). No schema here carries a `blocking` field.
- **Post-redaction only.** A panel never receives a draft that has not cleared C05. The sequence is redact-then-panel, never panel-then-redact (invariant #7).
- **Read-only critics.** Each panel agent reads the redacted draft + config; it never writes the draft, never fetches, never calls a paid tool. The generic `critic.md` grant is `[Read, Grep, Glob]` — **no `Write`** (it is a checker, not an author). Collection is the agent's schema-validated **return message**, never a unique file: the `council-output-pattern` unique-file discipline applies only to write-capable agents (e.g. `thinker.md`) on the inline path, where parallel `Write`s would clobber a shared file. A read-only critic has no file to clobber — its return value is the collection, identical under both the Workflow-tool and inline-`Agent` engines.
- **$0 — provably local.** No Phase-4 panel calls Perplexity (spec § 4f). All inputs are local files. The dollar gate is a trivial pass; the only spend control is the per-panel `fan_out_max` (invariant #6).
- **Synthesis is orchestrator-owned.** The `/review` panel's three lens reports are merged inline by the orchestrator — never by a fourth agent (hard-no).
- **Human gate is preserved.** Anti-pattern block aside, every flag surfaces above the existing operator acknowledgment / approval-stage gate (C03, C07; `references/approval-stage-tracking.md`). The panels inform the gate; they add no auto-advance path (invariant #3).

## Gate registration (spec F9)

These panels register in the comms `mode.yaml: pre_write_gates: [...]` field (the field Phase 1
introduced), discovered by the orchestrator via glob — never by enumerating mode names. Adding the
comms panels there is how the orchestrator knows to run them before a comms artifact write. The
anti-pattern verifier is the one entry that carries a hard-block semantic; the tell-detector and the
`/review` panel are advisory entries on the same gate.

## Acceptance

- [ ] Three panels exist, each a separate checker from the author, each dispatching the generic `critic.md` (no bespoke agent file per panel — spec F7).
- [ ] anti-pattern verifier hard-blocks the write on any violation; blocking computed by the orchestrator (`len(violations) > 0`), never self-reported by the agent.
- [ ] FR-CA tell-detector is FLAG-only/advisory; returns `null` when no FR-CA language is enabled.
- [ ] `/review` panel runs `correctness × register × legal` in `parallel()`; the orchestrator synthesizes (no agent synthesis path).
- [ ] C05 redaction pass completes before any panel agent receives the draft; an un-redacted draft withholds the panels (invariant #7).
- [ ] FR-CA co-draft independence preserved — both drafts read the source recommendation, never each other (C04, spec § 4c).
- [ ] All three return schemas have `additionalProperties: false`, no `replacement_text`, no `blocking` field (invariants #2, #6; spec § 4f).
- [ ] No panel calls Perplexity; each is provably $0 (local reads only); frontmatter declares `engine: workflow-tool`, `paid: false`, per-panel `fan_out_max`.

## See also

- `$ASSET_ROOT/SPEC-workflow-phases-2-5.md` § 4c — comms adversarial panels (this primitive's spec), § 0c invariants #2/#6/#7, § 1 engine rule
- `$ASSET_ROOT/.claude/agents/critic.md` — the generic read-only critic agent these panels parameterize (spec F7; grant `[Read, Grep, Glob]`)
- `$ASSET_ROOT/_modes/comms/references/redaction-rules.md` — C05 redaction pass that must complete before any panel runs (the load-bearing ordering)
- `$ASSET_ROOT/_modes/comms/references/contracts.md` — C03 (anti-pattern checklist), C04 (FR-first co-draft), C05 (redaction), C07 (speaker register)
- `$ASSET_ROOT/_modes/comms/references/review-protocol.md` — the existing `/review` chat-only flow these structured panels feed
- `$ASSET_ROOT/_core/primitives/completeness-critic.md` — sibling Phase-4 FLAG-only critic (orchestrator-computed blocking pattern)
- `$ASSET_ROOT/_core/primitives/visual-qa.md` — sibling Phase-4 panel; parallel-lens + orchestrator-await pattern
- `.claude/rules/council-output-pattern.md` (TM harness) — per-agent unique-file discipline for **write-capable** agents (e.g. `thinker.md`); the read-only `critic.md` panels here hold no `Write` grant and collect via schema-validated return instead, so the unique-file rule does not apply to them
