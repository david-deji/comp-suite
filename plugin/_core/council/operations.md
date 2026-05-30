<!-- Source: telos-machina/internal-ops-bureau/knowledge/council-procedure-reference.md @ commit af3787cb91fa793e6fcacad7fd8a7b438d9b62ee. Adapted for comp-suite v2 2026-05-07: TM-bureau paths replaced; NBJ-specific knowledge-base sections moved out (Industry Outsider replaces NBJ — see _core/council/perspectives.yaml § industry_outsider). Operational mechanics retained verbatim. -->

# Council Procedure — Operational Reference

Governance stub (parameters, mandatory perspective, synthesis styles, quality gate): `$ASSET_ROOT/_core/council/procedure.md`

## Default Perspective Pool

The comp-suite default perspective pool lives in `$ASSET_ROOT/_core/council/perspectives.yaml` (6 durable + Industry Outsider rotation). Use that file's `perspectives:` list as the source of truth for who can be dispatched. Default count: 5 durable + 1 Industry Outsider for deep deliberation, 3-4 for focused topics.

The Industry Outsider perspective is mandatory and rotating — set per-engagement in `engagement-state.yaml` `industry_outsider`. Selection rule: pick the option closest-but-not-equal to the engagement's primary industry (see `perspectives.yaml § industry_outsider.selection_rule`).

## Industry Outsider Selection

Before dispatching the council, the orchestrator resolves the Industry Outsider:

1. Read the engagement's primary industry from `$STATE_ROOT/_orgs/<slug>/master.yaml header.industry` (or `engagement-state.yaml industry` if set there).
2. Read `engagement-state.yaml industry_outsider`. If present, use it.
3. If absent: choose from `perspectives.yaml industry_outsider.options` per `selection_rule` (closest-but-not-equal to engagement's primary industry). Surface the chosen value to the user before dispatch; persist to `engagement-state.yaml`.
4. Build the Industry Outsider's context pack: a one-paragraph briefing on how that industry approaches the deliberation topic (e.g., for `pharma`: regulated comp environment, narrow band ranges, heavy benefits weighting). Pull from `$ASSET_ROOT/_modes/advisor/references/industry-comp-norms/<industry>.md` if present; fall back to LLM general knowledge with explicit `[UNVERIFIED]` tag.

## Industry Outsider Persona

> **Industry Outsider** — Senior comp practitioner from a domain adjacent to the engagement's industry. Brings a different baseline (different market norms, different equity/cash mix, different career-ladder shapes). Stress-tests deliberations against assumptions imported from the engagement's industry. Does NOT replace the Compensation Strategist's primary-industry expertise — provides a check on industry-specific blind spots.

## Industry Outsider Constraint

Add to `<constraints>` block:

> Frame analysis from the [SET INDUSTRY] perspective. Name two practices common in [SET INDUSTRY] that would NOT translate cleanly to the engagement's industry, and one that might transfer well. Ground claims in industry-specific patterns when possible; tag general extrapolations as `[UNVERIFIED]`.

## Gap-First Thinker Dispatch Template

Standard dispatch template for all council thinkers. Modes may extend `<task>` but must not remove gap identification steps.

```
<role>You are the [PERSPECTIVE NAME] on a [COUNCIL TYPE] for [TOPIC/PROJECT].</role>

<input>
Your perspective: [PERSPECTIVE NAME]
Your persona: [DESCRIPTION]

Read these files:
[LIST OF INPUT FILES]
</input>

<task>
1. Read the deliberation prompt and all context files provided.
2. Identify knowledge gaps — what information is missing, uncertain, or unverifiable
   in the materials? Write your `### Knowledge Gaps (Pre-Analysis)` section FIRST.
   [GAP_FLAVOR_QUESTION]
3. Analyze from your perspective: [PERSPECTIVE-SPECIFIC FOCUS AREAS].
4. As you reason, tag new gaps inline: `[GAP: brief description]`
5. State your core position in one sentence.
6. Support with evidence from the provided materials.
7. Identify tensions with other likely perspectives.
[ADDITIONAL MODE-SPECIFIC TASK STEPS]
</task>

<output>
Write your complete analysis to [UNIQUE OUTPUT FILE PATH] using the Write tool.
Also return your complete analysis as your final message.

Structure:
1. Knowledge Gaps (Pre-Analysis) — table of gaps identified before analyzing
2. [PERSPECTIVE-SPECIFIC OUTPUT SECTIONS]
3. Additional Gaps Discovered — table of gaps found during analysis
</output>

<constraints>
- Write Knowledge Gaps BEFORE your analysis — do not skip or defer.
- Do NOT coordinate with other thinkers or reference their analyses.
- Do NOT write to any shared file — your output file is unique to you.
- Ground every claim in evidence from the provided materials.
- Tag recommendations that depend on gap areas: `[UNRESEARCHED]`
</constraints>

<comms>
No preamble, no affirmation.
Ground claims in evidence. Challenge implied preferences — if a position lacks support, say so.
</comms>

<termination>
You are done when all six are true — stop writing and submit:
1. Pre-Analysis gaps table has at least 1 entry (or "None — [one-line justification]")
2. Core Position is stated in 1-2 sentences
3. Every claim in Analysis cites a specific file or section from the input
4. At least 1 actionable recommendation exists (not just observations)
5. Dissent/Concerns names at least 1 tension or assumption that could be wrong
6. Output file is written via the Write tool

If ambiguous, state the ambiguity — do not silently resolve it.
Stop at the checklist. Do not elaborate beyond what evidence supports.
</termination>
```

## Output Collection

1. **Check disk first**: For each thinker, read their unique output file at `$STATE_ROOT/_orgs/<slug>/engagements/<id>/council/<topic>/<perspective-slug>.md`.
2. **Fall back to return message**: If the file is missing, use the thinker's return message content.
3. **Assemble**: Write all thinker analyses into the council assembly file (`$STATE_ROOT/_orgs/<slug>/engagements/<id>/council/<topic>/_assembly.md`) under `### [Perspective Name]` headings.
4. **Intermediate files**: Delete individual thinker files after assembly unless the founder may need to audit individual reasoning.

Dispatch in batches per rate limits: max 5 Opus agents in parallel, then remainder.

## Gap Aggregation

After collecting all thinker outputs and BEFORE synthesis, aggregate knowledge gaps:

1. **Extract all gaps** from each thinker (Pre-Analysis + Additional Gaps tables).
2. **Deduplicate (conservative)**: Merge only when same question about same subject. When uncertain, keep separate.
   - MERGE: "missing pricing data for Quebec market" + "no cost benchmarks for FR-CA region"
   - KEEP SEPARATE: "unknown salary distribution shape" + "unknown role mapping confidence"
3. **Count frequency** and **rank** by `frequency x impact`.
4. **Present to founder** via AskUserQuestion (cap at 5 gaps):

```
Council identified [N] knowledge gaps across [M] thinkers.

Top gaps (by frequency x impact):
1. [Gap description] — flagged by [N] thinkers, affects [what]
...

Options:
A. Research now — dispatch targeted research on top gaps before synthesis
B. Proceed with noted uncertainty — tag gap-dependent claims [UNRESEARCHED]
C. Suppress — synthesize without gap tracking
D. Cherry-pick — tell me which gaps to research
```

5. **If A or D**: Dispatch targeted research (perplexity-research or market-data tool depending on gap type), feed into assembly, then synthesize.
6. **If B**: Synthesize; all gap-dependent claims carry `[UNRESEARCHED]` tags.
7. **If C**: Synthesize normally.

**Zero-gap anomaly**: If ALL thinkers report zero gaps, flag as anomalous (likely non-compliance). Note in synthesis.

## Synthesis Style Details

### consensus-tensions (default — most comp deliberations)

1. **Consensus**: Where did most thinkers agree? Tag `[CONSENSUS]`.
2. **Tensions**: Where did they disagree? Strongest argument from each side.
3. **Single-source claims**: Findings from only one thinker. Tag `[SINGLE SOURCE]`.
4. **Unverified claims**: Claims without evidence. Tag `[UNVERIFIED]`.
5. **Unresearched claims**: Claims dependent on knowledge gaps. Tag `[UNRESEARCHED]`.
6. **Recommended path forward**: What the evidence supports.
7. **Unresolved concerns**: For founder decision.

### vote-count (for binary or N-way decisions)

1. For each decision: count votes per option.
2. **DECIDED**: 4+ thinkers agree on one option.
3. **SPLIT**: 2-3 each — summarize strongest argument per side.
4. **OVERRIDE**: A thinker raised a concern that changes the framing.
5. Escalate SPLIT decisions to the founder.
6. Tag factual claims with confidence tags where applicable.

### severity-triage (for adversarial review of artifacts)

1. Group findings by severity: CRITICAL > HIGH > MEDIUM > LOW.
2. Cross-reviewer consistency check: contradictions, blind spots, convergence.
3. CRITICAL findings block advancement.
4. Dispatch fix workers for CRITICAL and HIGH.
5. Re-review after fixes (focused, single reviewer).

## Gap Flavor by Mode

| Mode | Gap question for thinkers |
|---|---|
| `advisor` | "What market, equity, or sector data would strengthen this analysis?" |
| `comms` | "What audience signals or change-management context is missing?" |
| `transformer` | "What organizational or process realities are unverified in this discovery?" |
| `training` | "What audience-specific knowledge or competency context is missing?" |
| `/comp council` | "What would you need to research to be confident in this analysis?" |

## `[UNRESEARCHED]` Tag Propagation

When the founder chooses option B, gap-dependent claims carry `[UNRESEARCHED]` tags that propagate through the engagement:

- **In deliverables**: Surfaced in decision-doc.md and slide decks. Reviewer (founder) sees the tag and can resolve before client delivery.
- **In master.yaml decision_log entries**: Carry the tag in the `notes` field of the entry. Future cycles surface unresolved tags via `cycle-awareness` primitive.
- **Resolution**: Tags resolved by (1) targeted research, (2) founder accepting risk, or (3) downstream discovery. Note: `[RESEARCHED: was Gap #N — resolved by [source]]`.

Tags never disappear silently.

## Adaptation: Adversarial Review of Artifacts

If a council is dispatched as a review (e.g., review a draft decision-doc), use `severity-triage` synthesis style and frame the prompt as code-review-shaped: file:line findings, severity tags, gap identification via `Unverified Assumptions` output section.
