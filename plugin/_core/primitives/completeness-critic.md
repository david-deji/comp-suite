---
engine: workflow-tool
paid: false
fan_out_max: 1
---

# completeness-critic

Comp-suite v2 primitive (SPEC § 4a). A coverage-net checker that reads an assembled
artifact and reports what the brief asked for but the artifact does not deliver. It is
the separate-checker half of the author/checker split: the mode body writes the artifact,
this primitive reads it cold against the brief and returns gaps. It never edits the
artifact and never authors replacement text — it flags, the human gate decides.

Single Read-only critic, no fan-out (`fan_out_max: 1`), zero paid tools → `$0` under the
dollar gate → Workflow-tool eligible (SPEC § 1 engine rule). One critic suffices because
completeness is a single lens (does the artifact cover the brief?), not a panel of
competing perspectives — adding fan-out would duplicate the same read for no coverage gain.

## Why this exists

A mode body can assemble a deliverable, see no error, and declare it complete — while a
required disclaimer is missing, a `{{RENDERED:…}}` placeholder never got substituted, or a
brief item simply went unaddressed. File-write success is not coverage. This primitive
forces a read-the-brief-then-read-the-artifact loop run by an agent that did not write the
artifact, so author blind spots do not survive into the human gate.

## Contract

| | |
|---|---|
| **Signature** | `completeness_critic(artifact_text, deliverable_type, brief) -> {missing[], coverage_pct}` |
| **Inputs** | `artifact_text: str` — the assembled deliverable text (post-redaction for comms; see § Ordering). `deliverable_type: str` — e.g. `affichage`, `narrative`, `cascade`, `assembled-doc`. `brief: str` — the requirements the artifact must satisfy (mode brief, narrative frame, or assembly checklist). |
| **Outputs** | `{missing: list[dict], coverage_pct: number}` — the gaps the critic found and a coverage estimate. **No `blocking` field** — blocking is orchestrator state, never agent output (see § Blocking is orchestrator-computed). |
| **DAG position** | Post-assembly, pre-gate — runs AFTER a mode body assembles an artifact and BEFORE the orchestrator surfaces the corresponding human gate. |
| **Engine** | `workflow-tool` (free; local Read only). May also run as a single inline `Agent` — both are valid for a `$0` dispatch (SPEC § 1). |
| **Calls** | Dispatches one `.claude/agents/critic.md` (the generic critic, SPEC § F7) with a completeness-lens prompt + the completeness-finding schema. The critic uses `Read` to inspect the artifact and any brief files. No Perplexity, no paid MCP. |
| **Schema** | The critic's return validates against `$ASSET_ROOT/_core/schemas/completeness-finding.schema.json` (`additionalProperties: false`, no `replacement_text`, no `blocking`). |

## FLAG-only (SPEC invariants #2, #3)

The critic reports gaps; it never closes them. It does not author a missing disclaimer, fill
a placeholder, or rewrite an underspecified section — it names what is absent and where, and
returns. The completeness-finding schema carries no `replacement_text` property and is sealed
with `additionalProperties: false`, so a verbose critic cannot smuggle a fix into the return.
The human gate downstream resolves every finding; the primitive informs that gate, never
replaces it.

A `missing[]` finding entry carries a category, the gap, and an optional location — not a correction:

```jsonc
// one entry in missing[] — shape matches completeness-finding.schema.json
// required: category (enum), field, issue ; optional: location
{ "category": "unresolved_placeholder",   // | missing_disclaimer | misplaced_disclaimer
                                          // | unaddressed_brief_item | underspecified_section
  "field":    "{{RENDERED:salary_band_table}}",
  "issue":    "placeholder on the affichage was never substituted during assembly",
  "location": "section 3, line 41" }      // optional — omit when the gap has no single locus
```

## Blocking is orchestrator-computed (SPEC § 4a, invariant #6)

The agent never self-reports whether a finding blocks. It returns `missing[]` and
`coverage_pct` only; the orchestrator computes `blocking` deterministically from the returned
findings plus `deliverable_type`:

```python
def is_blocking(missing, deliverable_type):
    if deliverable_type != "affichage":
        return False                       # advisory everywhere except statutory affichage
    return any(
        f["category"] in (
            "unresolved_placeholder",      # {{RENDERED:…}} / {{NARRATIVE:…}} survived assembly
            "missing_disclaimer",
            "misplaced_disclaimer",
        )
        for f in missing
    )
```

Blocking is therefore a property of the orchestrator's deterministic check over the agent's
findings, not a field the agent sets. WHY: a permissive critic that self-reported
`blocking: false` on a real statutory placeholder would re-introduce exactly the silent
failure this gate exists to prevent — so the decision is moved off the agent and made
deterministically from the category enum.

### Blocking surface (statutory affichage only)

Blocking fires only for `deliverable_type == "affichage"` AND at least one finding in one of
two categories:

| Category | What it catches |
|---|---|
| `unresolved_placeholder` | A `{{RENDERED:…}}` or `{{NARRATIVE:…}}` token survived assembly — the affichage would ship with a literal template marker. |
| `missing_disclaimer` / `misplaced_disclaimer` | A required pay-equity affichage disclaimer is absent, or present but outside its mandated position. |

Everywhere else the primitive is **advisory**: `unaddressed_brief_item` and
`underspecified_section` findings, and every finding on a non-`affichage` artifact, surface
to the orchestrator as non-blocking notes. They inform the human gate; they do not halt it.
The single hard line is statutory affichage placeholders and disclaimers — the one place
where a coverage gap is a compliance defect rather than a quality note.

## Dispatch pattern

The primitive does not author a bespoke agent. It dispatches the generic
`.claude/agents/critic.md` (SPEC § F7) with a completeness-lens task prompt and the
completeness-finding schema as the required return shape. The lens prompt instructs the
critic to:

1. Read `brief` (the requirements) before reading the artifact — gaps are found against the
   brief, not against the critic's own expectations.
2. Read `artifact_text` and scan for: surviving `{{RENDERED:…}}` / `{{NARRATIVE:…}}` tokens;
   required disclaimers (presence and position); each brief item's coverage; sections the
   brief calls for that are present but underspecified.
3. Return exactly `completeness-finding.schema.json` — `missing[]` of category-tagged gaps
   plus a `coverage_pct` estimate. Report findings only; never propose or write the fix.

The orchestrator collects the return, validates it against the schema, then runs `is_blocking`
itself. A schema-invalid return is re-dispatched once, then recorded as a gate failure — never
silently treated as "no gaps found" (a missing return is not a passing return).

## Reuse sites

Each site is a thin call: assemble the artifact, hand it (post-redaction where required) to
`completeness_critic`, surface the findings at that site's existing human gate. The brief and
`deliverable_type` differ per site; the contract does not.

| Site | `deliverable_type` | `brief` is | Gate it informs |
|---|---|---|---|
| **advisor Phase 5** | `narrative` | the narrative frame for the recommendation set | the advisor narrative review gate |
| **comms post-cascade** | `cascade` | the cross-artifact consistency checklist | the comms approval gate |
| **pay-equity Phase 10** | `affichage` / `assembled-doc` | the assembled-document requirements (disclaimers, rendered tables) | the Phase-10 close gate — the one site where blocking can fire |
| **engagement-close** | `assembled-doc` | the deliverable-set completeness checklist | the close gate |

Only the pay-equity Phase-10 site passes `affichage`, so it is the only site where a finding
can be orchestrator-computed as blocking. The other three are advisory throughout.

## Ordering (SPEC invariant #7 — comms)

For the comms post-cascade site, the C05 redaction pass must complete on the draft **before**
`artifact_text` reaches this primitive. The critic is a separate agent — a new PII surface
that does not exist in the current in-context self-review. Pass the redacted text, never the
raw draft: redact first, then critique. The other three sites pass already-internal artifacts
and carry no new PII surface, but the rule is uniform — never hand a panel agent text that has
not cleared its mode's redaction or disallowed-fields scan.

## Constraints

- **FLAG-only.** Reports `missing[]`; never authors replacement text, never edits the
  artifact. Schema is `additionalProperties: false` with no `replacement_text`.
- **No `blocking` in the return.** Blocking is orchestrator-computed from category + type;
  the agent never self-reports it.
- **`$0` local-read panel.** Read-only; no Perplexity, no paid MCP. Engine `workflow-tool`,
  `paid: false`, `fan_out_max: 1` — declared in frontmatter so the engine rule and fan-out
  cap (invariant #6) are machine-checkable, not prose-only.
- **Separate checker from author.** The critic agent is not the agent that wrote the
  artifact. Use `critic.md` with a lens prompt; never let the authoring body grade its own
  coverage.
- **Post-redaction text only for comms.** The redaction pass runs before the artifact reaches
  the critic — never pass a pre-redaction draft to a panel agent.
- **Never wrap deterministic Python.** Placeholder/disclaimer presence the orchestrator can
  check with a literal scan stays orchestrator-run Python (`is_blocking` above is exactly
  that); the agent handles the judgment portion (brief coverage, underspecification). Do not
  agent-wrap `render_document` or any deterministic assembly step — this primitive runs on the
  already-assembled strings.
- **A missing return is not a passing return.** Schema-invalid or absent → re-dispatch once,
  then record as a gate failure; never default to "no gaps."

## Acceptance (SPEC § 4f)

- [ ] `completeness-critic.md` exists; declares `engine: workflow-tool`, `paid: false`,
      `fan_out_max: 1`.
- [ ] FLAG-only — return schema has `additionalProperties: false` and no `replacement_text`.
- [ ] Return carries no `blocking` field; blocking is computed by the orchestrator from
      `deliverable_type == "affichage"` AND (unresolved `{{RENDERED:}}`/`{{NARRATIVE:}}`
      placeholder OR missing/misplaced disclaimer).
- [ ] Advisory (non-blocking) on every non-`affichage` deliverable_type and on
      `unaddressed_brief_item` / `underspecified_section` findings.
- [ ] Dispatches the generic `.claude/agents/critic.md` with a completeness-lens prompt +
      `completeness-finding.schema.json`; does not author a bespoke agent.
- [ ] Provably `$0` — local reads only; no Perplexity call (verified against the SPEC § 1
      engine table).
- [ ] Comms site receives post-redaction text only (invariant #7).

## See also

- `$ASSET_ROOT/SPEC-workflow-phases-2-5.md` § 4a — the spec section this primitive realizes; § 0c
  invariants #2/#3/#6/#7; § 4f acceptance.
- `$ASSET_ROOT/_core/schemas/completeness-finding.schema.json` — the return schema (sealed, no
  `replacement_text`, no `blocking`).
- `$ASSET_ROOT/.claude/agents/critic.md` — the generic critic this primitive dispatches with a lens
  prompt (SPEC § F7).
- `$ASSET_ROOT/_core/primitives/visual-qa.md` — sibling Phase-4 coverage-net gate (visual lens panel);
  same FLAG-then-human-gate posture, different artifact (PNGs vs assembled text).
- `$ASSET_ROOT/_core/primitives/budget-check.md` — confirms a `$0` local-read dispatch is a trivial
  budget pass; this primitive never triggers a cost-log entry.
