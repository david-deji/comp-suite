# Contracts — compensation-advisor

Numbered, testable contracts the skill maintains. The quality gate at the end
of each phase MUST verify the contracts that apply to that phase. Violations
are surfaced loudly, not silently corrected.

Contracts marked **(shared)** are byte-identical across the 4 sibling skills
(comp-comms-builder, comp-team-transformer, comp-training-designer mirror
these from compensation-advisor canonical). Contracts not marked are
compensation-advisor-specific.

## C01 — Persistence: text-only Drive **(shared)**

Drive holds metadata only (yaml/md/json). Binary artifacts (PPTX, PDF, DOCX,
images, sanitized CSV) deliver as chat-download. No exceptions, no toggle.

Enforced: `references/persistence-and-ledger.md` § Binary artifacts never go
through Drive. Verified at: every Phase 7 close, every binary-artifact emit.

## C02 — Selection-log integrity

`selection_log` entries are appended ONLY by Phase 4 (scenario pick) and Phase
6b (section framing pick). No other phase appends. Faking entries from
clarification prompts or council picks corrupts the cross-engagement learning
loop.

Enforced: `references/artifact-generation.md` § engagement-state.yaml schema.
Verified at: Phase 7 close, Phase 6b each section, Phase 4 each scenario pick.

## C03 — One engagement = one budget owner

Strong nudge, not hard gate. If the user describes a multi-budget-owner
engagement, surface the conflict and recommend splitting before proceeding.

Enforced: `SKILL.md` § Critical orchestration rules + `init-mode-protocol.md`
Section 0 § Budget-owner rule. Verified at: `/init` Section 0, Phase 0 of
every track.

## C04 — Cycle-stage symmetric calibration

At week ≥ 0 (post-launch), decline new strategy work. At week < target_stage − 4
(too-early), propose pre-engagement mode menu before proceeding. Don't blindly
run the canonical phase work outside its window.

Enforced: `consulting-protocol.md` § Too-late rule + § Too-early protocol.
Verified at: Phase 0 of every track, `opening-sequence.md` pre-flight check 4.

## C05 — Workforce data: CSV templates only

`.csv`/`.xlsx` workforce uploads scanned against disallowed-fields BEFORE
parsing. PII detection → refuse and re-instruct with templates. Hard rule, no
override.

Enforced: `SKILL.md` § Critical orchestration rules + `costing-engine.md`
§ Disallowed-fields scan. Verified at: every workforce data upload, Phase 4
entry.

## C06 — Multi-province per-province first

For multi-province engagements, every market pull, costing, and slide cost
figure is per-province first, then aggregated. Never collapse to national
average when per-province values exist.

Enforced: `SKILL.md` § Critical orchestration rules + `costing-engine.md`
§ Per-province handling. Verified at: Phase 2 entry, Phase 4 entry, Phase 6b
each cost-bearing slide.

## C07 — Provincial minimum wage: never guess

Sourced from `benchmark.provincial_minimum_wages` per province. Skill warns
when `next_review` passes. Never invent a rate from training data. TODO
markers are explicit unfilled placeholders, not guesses.

Enforced: `init-mode-protocol.md` Section 5 § dummy-mode rule + `SKILL.md`
§ Critical orchestration rules. Verified at: Phase 4 entry, every
minimum-wage citation.

## C08 — Mode declaration before partial-flow work

Any engagement that runs less than the full Phase 1-7 MUST declare its
`engagement_mode` per `references/engagement-modes.md` BEFORE Phase 5 begins.
Partial-flow work without a declared mode corrupts the engagement-state schema
and pollutes the closed-engagement ledger.

Enforced: `references/engagement-modes.md` § Mode declaration. Verified at:
Phase 5 entry of every non-full-engagement track.

## C09 — Verified-fact propagation **(shared)**

When a fact is verified during a session (web_search, user correction,
web_fetch of an authoritative source), the verified value propagates
atomically to every state file that holds the same fact, in the same write
batch.

Enforced: `persistence-and-ledger.md` § Verified-fact propagation. Verified
at: every close-time write sequence, every verification event.

## C10 — Recommendation discipline (all `ask_user_input`)

`ask_user_input` options are presented neutrally — pros/cons, no
"recommended" labeling — until `selection_log` data exists for the matching
audience archetype. Editorializing pre-locks the answer. Discipline applies
to EVERY `ask_user_input` call, regardless of phase (Phase 6b
section-framing, clarification-time picks, scope picks, cover-framing,
slide-count, audience selection, mode selection — all of them).

Enforced: `production-and-qa.md` § Recommendation discipline. Verified at:
every `ask_user_input` call.

## C11 — Drive folder visibility (private only) **(shared)**

Skill verifies the persistence folder is owned by the user and not publicly
shared (no "Anyone with link") before any write. Public-link sharing → hard
refuse with a setup pointer.

Enforced: `persistence-and-ledger.md` § Privacy & cleanup. Verified at: every
session start (Phase 0 backend probe), every close-time write.

## C12 — Federated section ownership (master.yaml) **(shared)**

Each skill writes to its own federated section only (compensation-advisor →
`master.advisor.*`; comp-comms-builder → `master.comms.*`; comp-team-transformer
→ `master.transformer.*`; comp-training-designer → `master.training.*`). Reads
all other sections read-only. Appends to `master.decision_log[]` are
append-only; no skill mutates prior entries authored by any skill (its own or
sibling).

Enforced: `master-yaml-utils.md` § Federation discipline. Verified at: every
master.yaml write.

## C13 — Visual QA before deliverable announce **(shared)**

No `.pptx` deliverable surfaces as "done" until it has been rendered to
per-slide PNGs via `$ASSET_ROOT/_core/primitives/visual-qa.md` and the orchestrator has
visually inspected each PNG via the `Read` tool against the inspection
checklist (text overflow, text collision, logo present, color conformance,
slide-edge clipping, empty space, cross-slide consistency).

File size, "wrote N bytes" stdout, and absence of errors from the producer are
NOT visual quality signals. Hard rule, no override — promoted from a high-severity
operator-flagged friction event after three distinct visible defects shipped
in one session (missing logo, title/subtitle overlap, slide-bottom clipping).

Enforced: `$ASSET_ROOT/_core/primitives/visual-qa.md` § Trigger points. Verified at:
Phase 6c (deck assembly close), every showcase/preview slide render, every
binary-artifact emit that contains slides.

## C14 — Performative emptyspeak banned outside one home **(shared)**

Branded text never uses register that performs (reassures, manages emotion,
demonstrates thoroughness) instead of informing. Tells: reassurance theatre,
padded substance, sales-pitch register in working documents, emotional-
management projection. Example of the banned register: *"We're 21 weeks out.
This plan locks in your decision points ahead of time so nothing on the FY27
wage scale lands as a surprise."* — zero substantive payload, four
performative tells.

The single allowed home is `comms` mode's "saying-nothing-with-many-words"
track (embargoed announcements, regulatory-placeholder language during legal
review, holding-pattern responses during M&A blackouts). Comms invokes that
register explicitly when needed; it never appears in advisor / transformer /
training deliverables and it is never a default in comms either.

Enforced: `$ASSET_ROOT/_core/policies/writing-standards-comp.md` § Performative
emptyspeak + `$ASSET_ROOT/_core/hooks/never-list.txt` § Performative emptyspeak compound
phrases + `$ASSET_ROOT/_core/primitives/visual-qa.md` inspection checklist item 8.
Verified at: every branded-text Write (anti-slop hook), Phase 6c, Phase 7
close.

---

## Per-phase checklist hooks

### Phase 0 entry
- [ ] C01, C02, C03, C04, C05, C11 visible to current state

### Phase 4 entry
- [ ] C05, C06, C07 verified for current data set

### Phase 5 entry
- [ ] C08 mode declared if < full engagement

### Phase 6a/b
- [ ] C02, C06, C10 enforced for each section

### Phase 6c (deck assembly close — hard gate)
- [ ] C13 enforced — `.pptx` rendered to per-slide PNGs via `$ASSET_ROOT/_core/primitives/visual-qa.md`
- [ ] Each PNG inspected against the 7-point inspection checklist (text overflow / collision / logo / color / clipping / empty space / cross-slide consistency)
- [ ] Any defect aborts "done" announcement; fix the generator and re-run the primitive (never patch the PNG)

### Phase 7 close
- [ ] C01, C02, C09, C12, C13 verified before write
- [ ] All C-numbers in this table reviewed against current state
