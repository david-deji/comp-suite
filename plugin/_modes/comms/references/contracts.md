# Contracts — comp-comms-builder

Numbered, testable contracts the skill maintains. The quality gate at the end
of each step MUST verify the contracts that apply to that step. Violations
are surfaced loudly, not silently corrected.

Contracts marked **(shared)** are byte-identical across the 4 sibling skills
(comp-comms-builder, comp-team-transformer, comp-training-designer mirror
these from compensation-advisor canonical). Contracts not marked are
comp-comms-builder-specific.

## C01 — Persistence: text-only Drive **(shared)**

Drive holds metadata only (yaml/md/json). Binary artifacts (PPTX, PDF, DOCX,
images, sanitized CSV) deliver as chat-download. No exceptions, no toggle.

Enforced: `references/persistence-and-ledger.md` § Binary artifacts never go
through Drive. Verified at: every Phase 7 close, every binary-artifact emit.

## C02 — Prior-comms registry integrity

`prior_comms_registry` entries are appended ONLY by `/ingest` (at workshop
synthesis close). No other command appends entries. `/draft` and `/cascade` read
the registry but MUST NOT write to it. Writing entries from draft context fakes
shipment history and corrupts the cross-cycle voice-inheritance signal.

Enforced: `references/ingest-protocol.md` § Workshop synthesis close.
Verified at: every `/ingest` close, every `/cascade` close, every Drive write
touching `master.comms.prior_comms_registry`.

## C03 — Anti-pattern checklist surfaced before any /draft write

Before any artifact write, the current anti-pattern list (from
`org-comms-profiles/<client-slug>.yaml` `anti_patterns[]` + bundled
`template_assets/anti-patterns.yaml`) MUST be surfaced and the operator MUST
acknowledge. Silent-skip of the anti-pattern check is a contract violation.

Enforced: `references/draft-protocol.md` § Pre-draft anti-pattern checklist.
Verified at: every `/draft` before write, every `/cascade` per-artifact
before write.

## C04 — FR-first co-draft

FR-CA MUST be drafted first. EN is co-drafted from the FR source — NOT
translated from EN. Drafting EN first then translating to FR introduces
translation calque (French that reads like English). If the engagement config
specifies `languages.primary: en`, surface:

> "Config declares EN primary. FR-first co-draft requires FR drafted first.
> Options: A. Switch primary to fr-ca (recommended for QC). B. Proceed with
> EN-first (non-QC employer, board-only cycle). C. Clarify intent."

Wait for selection. Do not override silently.

Enforced: `references/bilingual-rules.md` § FR-first discipline.
Verified at: every bilingual `/draft`, every bilingual `/cascade` artifact.

## C05 — Redaction pass complete before any artifact write

Before any artifact file is written (Drive or chat-download), a full redaction
pass MUST be complete: no PII (names, SINs, salaries, addresses) in any draft.
Role titles and functions replace names. Band ranges replace individual salaries.

Enforced: `references/redaction-rules.md` § Redaction discipline.
Verified at: every `/draft` before write, every `/cascade` per-artifact.

## C06 — Brand template applied before any artifact write

The artifact's audience × channel × format combination resolves a brand template
from `branding/<org-slug>/comms-templates/` (or `_default` if org-specific
templates are absent). Template MUST be applied before write. Drafting in plain
text and adding brand post-write produces layout drift.

Enforced: `references/brand-kit-protocol.md` § Template application order.
Verified at: every `/draft` before write, every `/cascade` per-artifact.

## C07 — Speaker register matches the active speaker

The artifact's speaker field (from engagement-comms-config) resolves a speaker
register via the 4-layer inheritance chain (bundled → org → engagement → CLI).
The drafted content MUST match the resolved register's `tone_descriptors`,
`do_words`, and `dont_words`. CEO register prose MUST NOT appear in an HRBP
memo.

Enforced: `references/speaker-register-rules.md` § Register calibration check.
Verified at: every `/draft` Step 3 (register resolution), every `/cascade`
per-artifact Step 3.

## C08 — Mode declaration before partial-flow /draft

Any `/draft` that runs less than the full cascade (i.e., any mode other than
`full-cascade`) MUST declare its `engagement_mode` per
`references/engagement-modes.md` BEFORE the first artifact write. Partial-flow
work without a declared mode leaves `state_shape_variant` ambiguous and
pollutes the closed-cycle ledger.

Enforced: `references/engagement-modes.md` § Mode declaration.
Verified at: opening-sequence pre-flight check 4, every non-full-cascade
`/draft` or `/cascade` call.

## C09 — Verified-fact propagation **(shared)**

When a fact is verified during a session (web_search, user correction,
web_fetch of an authoritative source), the verified value propagates
atomically to every state file that holds the same fact, in the same write
batch.

Enforced: `persistence-and-ledger.md` § Verified-fact propagation. Verified
at: every close-time write sequence, every verification event.

## C10 — (reserved — see compensation-advisor canonical for numbering context)

This slot is intentionally unassigned in v1 for comp-comms-builder to
keep C-numbering aligned with sibling skills. Assignment deferred to v1.1
based on friction log.

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

## Per-step checklist hooks

### Session start (pre-flight)
- [ ] C01, C02, C11 state visible (config loaded, registry readable)
- [ ] C08 mode declared if engagement-comms-config present

### /ingest close (workshop synthesis)
- [ ] C02 — registry append is this write's only source; no stale entries

### /draft Step 3 (register resolution)
- [ ] C07 — resolved register loaded; tone calibration check

### /draft before write
- [ ] C03 — anti-pattern checklist surfaced + operator acknowledged
- [ ] C04 — FR drafted first if bilingual config
- [ ] C05 — redaction pass complete
- [ ] C06 — brand template applied

### /cascade per-artifact before write
- [ ] C03, C04, C05, C06, C07 each artifact

### Close-time write (Drive)
- [ ] C01, C09, C11, C12 verified before write
- [ ] All C-numbers reviewed against current state
