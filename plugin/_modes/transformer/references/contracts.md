# Contracts — comp-team-transformer

Numbered, testable contracts the skill maintains. The quality gate at the end
of each phase MUST verify the contracts that apply to that phase. Violations
are surfaced loudly, not silently corrected.

Contracts marked **(shared)** are byte-identical across the 4 sibling skills
(comp-comms-builder, comp-team-transformer, comp-training-designer mirror
these from compensation-advisor canonical). Contracts not marked are
comp-team-transformer-specific.

## C01 — Persistence: backend for schema, chat-download for binaries **(shared)**

Schema state (yaml/md/json) persists via the `market` MCP backend or local `$STATE_ROOT`. Binary artifacts (PPTX, PDF, DOCX, images, sanitized CSV) deliver as chat-download — never through any backend. No exceptions, no toggle.

Enforced: `references/persistence-and-ledger.md` § Binary deliverables. Verified at: every Phase 7 close, every binary-artifact emit.

## C02 — Redaction: hard rule

Names → titles+functions, salary → bands, headcount → size_band. Refusing to
render an artifact with raw PII is non-negotiable. Does not relax under user
pressure.

Enforced: `references/redaction-rules.md` (all rules). Verified at: Phase 0
input scan, every artifact write (pre-write redaction pass).

## C03 — Cycle gating: no rollouts into live/prep windows

`/transform` and `/roadmap` refuse to schedule rollouts into `live` or `prep`
gating windows without explicit user override. Explicit acknowledgment is
captured in the artifact's Cycle-gating exceptions section.

Enforced: `references/cycle-discovery-and-gating.md` § Gating rule. Verified
at: `/transform` cycle-fit annotation step, `/roadmap` sequence planning step.

## C04 — Discovery before diagnose

`diagnose-only` mode requires `processes/<slug>/<process-slug>/current-state.md`
to exist in the persistence folder before proceeding. If absent: refuse, surface
the missing artifact path, and offer `/discover <process-slug>` as the next step.

Enforced: `references/diagnose-protocol.md` § Pre-flight. Verified at: `/diagnose`
entry, Mode-keyed step routing.

## C05 — Diagnosis before transform

`transform-only` mode requires `processes/<slug>/<process-slug>/diagnosis.md`
to exist in the persistence folder before proceeding. If absent: refuse, surface
the missing artifact path, and offer `/diagnose <process-slug>` as the next step.

Enforced: `references/transform-protocol.md` § Pre-flight. Verified at: `/transform`
entry, Mode-keyed step routing.

## C06 — Roadmap derivation from existing briefs

`/roadmap` sequences EXISTING transformation-briefs. It does not invent candidates
from scratch. If no transformation-brief exists for the process referenced, refuse
and surface: "No transformation brief found for `<slug>`. Run `/transform` first."

Enforced: `references/roadmap-protocol.md` § Pre-flight. Verified at: `/roadmap`
entry, `roadmap-refresh` mode routing.

## C07 — One process slug per engagement

One session = one process slug for production modes (`discovery-only`,
`diagnose-only`, `transform-only`, `roadmap-refresh`). If the user describes work
spanning multiple processes in one session, surface a split recommendation before
proceeding. `council-deliberation` and `full-discovery-to-roadmap` are exempt.

Enforced: `references/skill-overview.md` § Core principles. Verified at: Phase 0
of every production track.

## C08 — Mode declaration before partial-flow work

Any engagement that runs less than `full-discovery-to-roadmap` MUST declare its
`engagement_mode` per `references/engagement-modes.md` BEFORE the first artifact
write. Partial-flow work without a declared mode corrupts the engagement-state
schema and pollutes the closed-engagement ledger.

Enforced: `references/engagement-modes.md` § Mode declaration. Verified at: first
artifact write of every non-full-engagement session.

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

Enforced: `master-yaml-ops.md` § Federation discipline. Verified at: every
master.yaml write.

---

## Per-phase checklist hooks

### Phase 0 entry (every track)
- [ ] C01, C02, C03, C07, C11 visible to current state
- [ ] C04 if mode is `diagnose-only`
- [ ] C05 if mode is `transform-only`
- [ ] C06 if mode is `roadmap-refresh`

### `/discover` entry
- [ ] C02 redaction pass on all pasted inputs
- [ ] C07 single process slug confirmed

### `/diagnose` entry
- [ ] C04 current-state.md present for process slug

### `/transform` entry
- [ ] C05 diagnosis.md present for process slug
- [ ] C03 cycle-fit annotation computed for each Strong Candidate

### `/roadmap` entry
- [ ] C06 transformation-briefs present (≥1; ≥2 recommended)
- [ ] C03 every proposed quarterly slot checked against cycle stages

### First artifact write (any partial-flow track)
- [ ] C08 engagement_mode declared in frontmatter and state file

### Every artifact write
- [ ] C02 pre-write redaction pass complete
- [ ] C09 if any fact was verified this session

### Session close
- [ ] C09, C12 verified before final write
