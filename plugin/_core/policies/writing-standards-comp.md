# Writing Standards — Comp-Suite Adaptation

> **Adaptation of**: `writing-standards.md` (verbatim TM port, sibling file)
> **TM source**: `.claude/rules/writing-standards.md` @ commit `4b1dd5d7`
> **Authoritative for**: branded-text writes in `/comp` (deliverables, mode-working files). The verbatim raw is review-baseline only.
> **Date**: 2026-05-08 | Pinned independently of TM.
>
> **What changed from TM**: Replaced TM's `clients/<slug>/voice-profile-{lang}.md` resolution path with comp-suite's `state/_orgs/<slug>/...` path. Replaced TM's `.claude/skills/write-core/references/` glossary path with comp-suite's `_modes/advisor/references/fr-ca-glossary.md`. Replaced TM's "skills that comply" registry with comp-suite's anti-slop hook integration. Kept the em-dash limits, anti-slop pcheck pattern, and client-facing-copy section verbatim in spirit (the discipline is universal).

Applies to all branded text comp-suite produces: deck content (advisor), decision documents,
cascade messages (comms), training kits, transformer roadmaps, council per-thinker output
when it lands in a deliverable. Does NOT apply to internal state files (engagement-state.yaml,
checkpoint.yaml), council scratch files (deliberation, not deliverable), or mode-working
intermediate notes.

---

## Branded-text scope

The hook layer at `$ASSET_ROOT/_core/hooks/lib.sh:is_branded_text` already encodes the path scoping
(B3 fix from `a4868cd`). This policy is the prose form of the same scoping:

**Hooks RUN against** (branded text — anti-slop + french-accent-check + fact-check fire):

```
$STATE_ROOT/_orgs/*/engagements/*/deliverables/**/*.md
$STATE_ROOT/_orgs/*/engagements/*/advisor/**/*.md
$STATE_ROOT/_orgs/*/engagements/*/comms/**/*.md
$STATE_ROOT/_orgs/*/engagements/*/training/**/*.md
$STATE_ROOT/_orgs/*/engagements/*/transformer/**/*.md
```

**Hooks SKIP** (non-branded — exit 0 silently):

- All `*.yaml` and `*.json` files (state, manifests, schemas, configs)
- `$STATE_ROOT/_orgs/*/engagements/*/council/**` (per-thinker scratch, not deliverable)
- `$STATE_ROOT/_orgs/*/engagements/*/checkpoint.yaml`, `engagement-state.yaml`
- `$STATE_ROOT/ledger/**`
- Any path under `v2/tests/`, `$ASSET_ROOT/_core/`, `$ASSET_ROOT/_modes/`, `v2/.claude/`, `v2/.build-state/`

The hook layer is the enforcement. This policy is the rationale.

---

## Voice profile resolution

When a mode body produces branded text, it loads a voice profile in this resolution
order. The first existing file wins; the search stops at the first hit.

1. **Per-engagement override** (highest precedence — rare):
   `$STATE_ROOT/_orgs/<slug>/engagements/<id>/voice-profile-{lang}.md`
   Use when a single engagement needs to deviate (e.g., a tonal pivot mid-cycle).
2. **Per-org default** (most common):
   `$STATE_ROOT/_orgs/<slug>/voice-profile-{lang}.md`
   Use this for the standard org voice. Created during `find_or_create_org` if the
   founder has voice samples for that org; otherwise omitted.
3. **Mode default**:
   `$ASSET_ROOT/_modes/<mode>/references/voice-profile-{lang}.md`
   Per-mode tonal default (e.g., comms's cascade voice differs from advisor's
   decision-doc voice). Optional.
4. **Fallback** (no voice profile present):
   Plain professional voice. FR-CA: courtois, clair, sans jargon administratif. EN:
   plain professional, action-oriented, no marketing fluff.

**No CWD-based discovery.** The mode body never infers `<slug>` or `<id>` from the
working directory. Either the orchestrator passes them explicitly during context assembly
(per `$ASSET_ROOT/_core/primitives/engagement-loader.md`) or the mode falls through to the fallback
voice. This eliminates the silent-failure mode where a session running in `$STATE_ROOT/_orgs/<slug>/`
would unexpectedly load that org's voice profile in an unrelated context.

**Frontmatter `org:` mismatch is hard-fail.** A loaded voice profile whose `org:`
frontmatter field disagrees with the resolved engagement's `org_slug` is the strongest
available signal that the wrong file was loaded — silently using it would ship a
deliverable in the wrong org's voice. Stop the mode body and surface the mismatch.

---

## Comp-domain glossary integration

`$ASSET_ROOT/_modes/advisor/references/fr-ca-glossary.md` (verbatim port from v1, lands in
`SPEC-port.md`'s scope) is the comp-domain FR-CA glossary. The other modes (comms,
training, transformer) reference it.

When a mode body writes branded FR-CA text, the orchestrator includes the glossary's key
mappings in the dispatch prompt (e.g., "compensation" → « rémunération », "pay equity"
→ « équité salariale », "decision document" → « note décisionnelle »). The glossary is
prompt-injectable, not a hook check.

The anti-slop hook (next section) handles violations.

---

## Anti-slop hook integration

`$ASSET_ROOT/_core/hooks/anti-slop.sh` reads `$ASSET_ROOT/_core/hooks/never-list.txt` and greps every branded-text
write for matches. The never-list is the discipline catalog; this policy is the rationale.

**Banned vocabulary categories** (already in never-list.txt or to be appended at first
violation):

- AI-tell adjectives: "delve", "leverage" (as verb), "synergies", "landscape" (as metaphor),
  "cutting-edge", "revolutionize", "empower", "transformative", "moreover" (transition tic)
- Placeholder leakage: "TBD", "TODO", "Lorem ipsum", "Coming soon", "[bracket placeholder]"
- Comp-jargon overload: "high-impact", "best-in-class", "world-class", "next-generation"
- Em-dash bash on FR (see § Em-dash limit below)

**First-30-days policy**: anti-slop.sh defaults to `exit 1` (warn — Write proceeds, stderr
visible) for the first 30 days of an engagement. Promote to `exit 2` (block — Write rolled
back) only after observing < 5% false-positive rate on real deliverables. This mirrors
TM's `cost-discipline.md` "validation that produces false positives gets disabled within
2 sessions" logic — promote slowly to avoid disabling the hook entirely.

**Comp-domain additions to never-list.txt** are deferred until the first paying engagement
surfaces real violations. Anti-slop drift is a tuning concern, not a launch blocker.

---

## Performative emptyspeak (banned everywhere except one home)

A higher-order register failure that single-word slop does not catch. The
sentence "We're 21 weeks out. This plan locks in your decision points ahead
of time so nothing on the FY27 wage scale lands as a surprise" contains zero
banned vocabulary, yet reads as obviously AI-prepared. The defect is the
**register**, not the word list — writing that performs (reassures, manages
emotion, demonstrates thoroughness) instead of informing.

### Tells

1. **Reassurance theatre** — sentences whose only payload is "this is
   well-thought-out" or "you'll be in control." A peer pre-read does not
   reassure; it reports. *"so nothing… lands as a surprise"* exists to make
   the reader feel managed, not to inform.
2. **Padded substance** — three weak phrases stitched around one substantive
   phrase. *"We're 21 weeks out"* (filler) + *"locks in your decision points"*
   (filler) + *"ahead of time"* (tautological pad) wraps the actual content
   *"FY27 plan."* in three layers of nothing.
3. **Sales-pitch register in working documents** — *"your decision points"*,
   *"lands as a surprise"*, *"stop-and-discuss point — not a fly-by"*. This is
   proposal language used on clients you already serve. It auditions for work
   already won.
4. **Emotional management projection** — language that projects a need
   (avoiding surprises, keeping momentum, building alignment) onto the reader
   without evidence the reader has that need. The reader didn't ask to be
   managed; they asked for the work.

### Why banned

In a working document to a peer or client you already serve, performative
emptyspeak betrays that the writer doesn't trust the work to speak for
itself. Real internal-comms register is terse, factual, assumes fluency, and
allows imperfection ("FY26 outcome — Tim, I owe you Wednesday"). The tells
are not subtle once you look for them.

### Examples

| Banned | Terse equivalent (allowed) |
|---|---|
| "We're 21 weeks out. This plan locks in your decision points ahead of time so nothing on the FY27 wage scale lands as a surprise." | "Krista — FY27 plan. Three decisions, six deliverables. Aug 13 is the only date that has to land." |
| "Each is a stop-and-discuss point — not a fly-by." | "Each one we sit on for 30 min." |
| "Three risks shape the cycle. One ask now to keep momentum." | "Three risks. One ask: confirm FY26 outcomes by June 15." |
| "Six deliverables across the cycle. Each one is a stop-and-discuss point." | "Six deliverables. List below." |

### The one allowed home

`comms` mode runs a **"saying-nothing-with-many-words" track** for legitimate
use cases where being specific is the wrong move:

- Embargoed announcements where leadership has approved direction but not specifics
- Regulatory-placeholder language during legal review windows
- Statement-of-direction copy for cascade emails when concrete numbers haven't dropped
- Holding-pattern responses during M&A or restructuring blackout periods

In those contexts the register is a tool, used intentionally. Comms invokes
it explicitly via `comms` mode protocols — it is never a default and never
appears in advisor / transformer / training deliverables. Cross-ref:
`$ASSET_ROOT/_modes/comms/references/cascade-protocol.md` § Statement-of-direction
register (pending — author when first such cascade lands).

### Detection

- **Hook-side**: phrase patterns in `$ASSET_ROOT/_core/hooks/never-list.txt` (the
  multi-word entries appended for this rule). Anti-slop fires on branded-text
  Write the same way it fires for single-token slop.
- **Orchestrator-side**: visual-qa inspection checklist item 8 — "Does any
  copy perform competence rather than communicate work?" Catch what the
  hook misses.
- **Self-check pre-render**: before announcing any deliverable done, read your
  cover/intro paragraph aloud and ask "Would Krista, who has done five of these
  cycles, find any sentence here unnecessary?" If yes, cut it.

---

## Em-dash limit

**French (FR-CA): zero em dashes (—).** Em dashes in French read as Anglicism + AI-generation
tell at once; they have no native rhythm in QC FR copy. Replace every em dash with: period
+ capital for independent clauses, comma for continuation, colon for label-description
lists, parentheses for asides.

**English: maximum 2 em dashes per piece, prefer 0-1.** Since early 2025, em dashes are a
recognized AI-generation tell in English too. Same replacement palette as French.

The french-accent-check.sh hook also flags em-dashes in FR-tagged content. This is the
operational enforcement; the prose rule is the rationale.

---

## Client-facing copy — internal vs external content

Client-facing copy (decision documents, deck slides, cascade messages, training facilitator
guides) does NOT lead with internal compliance, regulatory, or process artifacts. Clients
hire comp-suite-via-David to absorb that complexity, not to be lectured about it.

### Never in client-facing copy

- **Regulatory framework names**: « Loi sur l'équité salariale », CNESST, Loi 25, Bill C-25,
  pay-transparency-act-by-name. Translate to outcomes.
- **Internal verification gates**: "EFVP signing", "PRP designation", "DSAR pathways",
  "DPIA workflow". These are comp-suite-internal ops items.
- **Acronym-laden expertise signaling**: PRP, EFVP, DSAR, DPO, CBA-clause-by-number.
  Translate to plain-language outcomes in any language the client reads.

### Do put in client-facing copy

- **Outcomes**: « votre programme respecte la Loi sur l'équité salariale par défaut » —
  not « audit CNESST avec PRP désignée ».
- **Trust signals via familiar vendor names**: « basé sur les enquêtes McLagan / Mercer »
  — not « méthodologie hybride survey-house v3 ».
- **Concrete deliverables**: « note décisionnelle pour le comité de direction » — not
  « advisor mode body output rendered via deck driver ».

### Where the regulatory + verification work goes

It does not disappear — comp-suite still performs it. It lives in comp-suite-internal
artifacts:

- Mode-references: `$ASSET_ROOT/_modes/advisor/references/pay-equity-qc-protocol.md`,
  `costing-engine.md`, etc. (technical playbooks)
- Engagement-state: `engagement-state.yaml` carries the verification status per phase
- Decision frameworks: `$ASSET_ROOT/_modes/advisor/references/council-mode.md` (deliberation
  procedures, never quoted to clients verbatim)

### One-sentence test

Before any line lands in a client-facing artifact, ask: "Would the client describe this
as something they pay for, or something they pay comp-suite-via-David to handle?" If the
second, it stays internal.

---

## See Also

- `$ASSET_ROOT/_core/policies/writing-standards.md` — verbatim TM raw (review baseline)
- `$ASSET_ROOT/_core/hooks/anti-slop.sh` + `$ASSET_ROOT/_core/hooks/never-list.txt` — operational enforcement
- `$ASSET_ROOT/_core/hooks/french-accent-check.sh` — FR-specific enforcement (em-dash + accent)
- `$ASSET_ROOT/_modes/advisor/references/fr-ca-glossary.md` — the comp-domain glossary
- `$ASSET_ROOT/_core/primitives/persona.md` + `$ASSET_ROOT/_modes/<name>/references/persona-library.md` — voice
  is one dimension; persona shapes voice for the audience
