# Contracts — comp-training-designer

Numbered, testable contracts the skill maintains. The quality gate at the end
of each phase MUST verify the contracts that apply to that phase. Violations
are surfaced loudly, not silently corrected.

Contracts marked **(shared)** are byte-identical across the 4 sibling skills
(compensation-advisor, comp-comms-builder, comp-team-transformer mirror
these from compensation-advisor canonical). Contracts not marked are
comp-training-designer-specific.

## C01 — Persistence: schema via backend, binaries as chat-download **(shared)**

The `market` MCP backend holds schema state (yaml/json). Non-schema artifacts
(decks, facilitator guides, council scratch) write to local `$STATE_ROOT`.
Binary artifacts (PPTX, PDF, DOCX, images, sanitized CSV) deliver as
chat-download only — never written to any backend or local path as schema state.
No exceptions, no toggle.

Enforced: `references/persistence-and-ledger.md` § Binary deliverables.
Verified at: every Phase 7 close, every binary-artifact emit.

## C02 — Differentiated depth

On the same fact (`msg-XXX` in message-map.yaml), HRBP depth ≥ manager depth
≥ employee depth when all three are non-null. Execs see different cuts
(tradeoffs / budget / governance) — depth-4 framing, not deeper-of-the-same.
Violation → refuse to render the affected audience.

Enforced: `references/audience-depth-rules.md` § Depth constraint. Verified at:
every `/ingest` Workshop synthesis close, every `/generate` audience render start.

## C03 — Delivery-target metadata stamp

Every rendered deck (employees / managers / managers-cascade-kit / hrbps / execs)
carries a `delivery_target` metadata stamp on the cover slide and in deck
frontmatter. Not a gating condition — stamp is always required, regardless of
whether the target date is past. Soft warning fires only if target is in the past.

Enforced: `references/cycle-awareness.md` § Delivery-target metadata. Verified at:
every `/generate` per-audience render complete, every `/cascade` render complete.

## C04 — Audience scope

`single-audience` mode emits one PPTX + facilitator guide + interactive blocks
for the chosen audience only. `full-bundle` mode emits all 4 audiences (employees,
managers, hrbps, execs). Running `/generate batch` in `single-audience` mode is a
refused state — the mode constrains batch.

Enforced: `references/engagement-modes.md` § single-audience + full-bundle. Verified
at: `/generate` mode check, every batch call.

## C05 — Ingest-then-generate

`full-bundle` mode requires an existing `message-map.yaml` for the cycle produced
by `/ingest`. If no message-map exists for the cycle slug, `/generate batch` is
refused with: "No message-map found for `<cycle-slug>`. Run `/ingest` first?"
Hard rule, no override.

Enforced: `references/generate-protocol.md` § Prerequisites. Verified at: every
`/generate` entry when `engagement_mode: full-bundle`.

## C06 — Cascade derivation

`cascade-only` mode requires `cycles/<engagement>/<cycle-slug>/managers.pptx` to
exist. The cascade kit derives from the manager deck, not from scratch. If the
manager deck is missing, `/cascade` is refused with: "No manager deck found for
`<cycle-slug>`. Run `/generate managers` first?"

Enforced: `references/cascade-protocol.md` § Prerequisites. Verified at: every
`/cascade` entry.

## C07 — Facilitator-guide pairing

Every audience PPTX produced by `/generate` must have a corresponding
`<audience>-facilitator.md`. Emitting a PPTX without its facilitator guide is a
refused state. The guide is produced in the same render pass as the deck, not
deferred. Same applies to `/cascade` — `managers-cascade-kit.pptx` requires
`managers-cascade-facilitator.md`.

Enforced: `references/generate-protocol.md` § Bundle render. Verified at: every
`/generate` per-audience render complete, every `/cascade` render complete.

## C08 — Mode declaration before partial-flow work

Any session that runs less than the full `full-bundle` flow MUST declare its
`engagement_mode` per `references/engagement-modes.md` BEFORE `/generate` begins.
Partial-flow work without a declared mode corrupts the engagement-training-config
schema and pollutes the closed-engagement ledger.

Enforced: `references/engagement-modes.md` § Mode declaration. Verified at:
every `/generate` entry in non-full-bundle mode.

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
to EVERY `ask_user_input` call, regardless of phase (audience-design
interview questions, mode selection, delivery-target picks, cycle slug
confirmation — all of them).

Enforced: `production-and-qa.md` § Recommendation discipline. Verified at:
every `ask_user_input` call.

## C11 — Artifact visibility (private only) **(shared)**

Backend writes are scoped to the authenticated org via OAuth identity — no
public-link surface exists. Local `$STATE_ROOT` artifacts must not be exposed
via public share. Hard refuse if visibility cannot be confirmed.

Enforced: `persistence-and-ledger.md` § Privacy. Verified at: every
session start (Phase 0 backend check), every close-time write.

## C12 — Federated section ownership (master.yaml) **(shared)**

Each skill writes to its own federated section only (compensation-advisor →
`master.advisor.*`; comp-comms-builder → `master.comms.*`; comp-team-transformer
→ `master.transformer.*`; comp-training-designer → `master.training.*`). Reads
all other sections read-only. Appends to `master.decision_log[]` are
append-only; no skill mutates prior entries authored by any skill (its own or
sibling).

Enforced: `master-yaml-ops.md` § Federation discipline. Verified at: every
master.yaml write.

---

## Per-phase checklist hooks

### Session start / Phase 0 entry
- [ ] C01, C08, C11 visible to current state
- [ ] C09 enforcement active for this session

### /ingest Workshop close
- [ ] C02 depth constraint verified for all audience+message pairs

### /generate entry (per audience)
- [ ] C04 audience scope matches declared engagement_mode
- [ ] C05 message-map.yaml present (full-bundle only)
- [ ] C07 facilitator guide will be produced in this render pass

### /cascade entry
- [ ] C06 manager deck present for cascade-only mode

### Every artifact render complete
- [ ] C03 delivery-target metadata stamped on cover and in frontmatter
- [ ] C07 facilitator guide paired with PPTX

### Session close / write sequence
- [ ] C01 no binary artifacts written to backend or local schema path
- [ ] C09, C12 verified before write
- [ ] C10 enforced for every ask_user_input in this session
