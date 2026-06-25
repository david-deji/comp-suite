
## When to use this skill

- **Cycle bootstrap** — scaffold an `engagement-comms-config.yaml` for a new comp cycle, binding to a compensation-advisor engagement (`/init`)
- **Brand templates** — create or update `branding/<org-slug>/comms-templates/` non-destructively (extends the shared brand kit) (`/brand`)
- **Prior-comms ingest** — bootstrap the long-lived `org-comms-profile.yaml` from a client's past announcements, manager FAQs, exec decks (PDFs, pasted text, prior PPTX) (`/ingest`)
- **Single artifact draft** — render one artifact (all-hands announcement, manager FAQ, HRBP enablement memo, exec one-pager) for a specific speaker × audience × channel × format combination (`/draft`)
- **Full cascade** — render every artifact in the engagement's catalog in dependency order (exec one-pager → all-hands → manager FAQ → HRBP memo) (`/cascade`)
- **Diff + anti-pattern review** — surface paragraph-level diff against the prior version, re-surface anti-pattern checklist, list pending FR-CA glossary additions (`/review`)
- **Comms-specific glossary additions** — add FR-CA terms with `usage_tag: comms` to engagement-level additions (compensation-advisor's `/glossary promote` does the merge) (`/glossary add`)
- **Status check** — list artifacts in current engagement with their approval stage and drift status (`/status`)
- **Mid-mode checkpoint / resume** — synchronous state save and restore across a multi-session cascade (`/checkpoint`, `/resume`)

## Output format

Working artifacts are: HTML (email body) and PDF for `all-hands-announcement`; DOCX (and optionally PDF via DOCX→PDF conversion) for `manager-faq` and `hrbp-enablement-memo`; PPTX (1-3 slides) for `exec-one-pager`. Before any DOCX or PPTX render, read the relevant bundled skill at `/mnt/skills/public/{docx,pptx}/SKILL.md`, plus `references/template-master.md` and `references/brand-kit-protocol.md`. Brand templates regenerate fresh from `branding/<org-slug>/comms-templates/` on every draft (default branding from `template_assets/branding/_default/comms-templates/`). PDF generation path is verified at runtime per `references/draft-protocol.md` (typically DOCX→PDF; falls back to DOCX-only if conversion unavailable). Three production checks before any write: brand template applied, anti-pattern checklist surfaced + acknowledged, redaction pass complete (no PII).

## Tools available

This skill persists schema state to the **`market` MCP backend** (OAuth identity → org membership) — comms config and org comms profile via `engagement_put_section`, checkpoints via `engagement_put`, brand templates via `brand_put_*`. Per-engagement comms artifacts (drafted announcements, FAQs, rendered decks) are non-schema deliverables: text artifacts under local `$STATE_ROOT`, binaries delivered as chat-download. Deliberation is single-context — no paid MCP research calls during draft. Full tool inventory and tool-selection priority table live in `references/tools-available.md` (mirrored from compensation-advisor — manual sync on change). The persistence contract (what is backend vs local, read/write semantics) lives in `references/persistence-and-ledger.md` (also mirrored from compensation-advisor). Read each whenever a phase needs to pick a tool or verify a write path.

**Persistence is always on** via the authenticated backend — there is no opt-in `persistence:` block and no paste-mode backend. On MCP transport failure, schema reads fall back to the local `$STATE_ROOT` cache (degraded); schema writes escalate/halt rather than write local (P4b D2). See `references/persistence-and-ledger.md`.

## Workflow Overview

Every request goes through the Intent Router. It classifies into one of fourteen entry points: seven production tracks (`/init`, `/brand`, `/ingest`, `/draft`, `/cascade`, `/review`, `/glossary add`), one informational track (`/status`), two persistence commands (`/checkpoint`, `/resume`), three cycle-management commands (`/close-cycle`, `/reopen-cycle`, `/switch-cycle`), and one help command (`/help`).

| Entry | Slash | NL triggers | Loaded references | END artifact |
|---|---|---|---|---|
| `/init` | `/init` | "set up comms config", "configure cycle" | `engagement-comms-config-template.md` | `engagement-comms-configs/<slug>.yaml` (write) |
| `/brand` | `/brand`, `/brand init <org-slug>`, `/brand show` | "brand templates", "comms brand kit" | `brand-mode-protocol.md` + `brand-kit-protocol.md` (mirrored) | `branding/<org-slug>/comms-templates/` (write or read) |
| `/ingest` | `/ingest` | "ingest prior comms", "extract voice", "build the profile" | `meta-protocol.md` (mirrored) + `ingest-protocol.md` + `redaction-rules.md` (mirrored) + `speaker-register-rules.md` + `audience-profile-rules.md` | `org-comms-profiles/<org-slug>.yaml` (write) |
| `/draft` | `/draft <artifact-type>` | "draft the announcement", "render the FAQ" | `meta-protocol.md` (mirrored) + `draft-protocol.md` + `artifact-catalog.md` + `valid-combinations-rules.md` + `bilingual-rules.md` + `compensation-advisor-input-contract.md` + `production-and-qa.md` (mirrored) + `template-master.md` (mirrored) + `brand-kit-protocol.md` (mirrored) | `engagements/<slug>/comms/<artifact-slug>-<lang>-v<N>.{ext}` |
| `/cascade` | `/cascade <engagement-slug>` | "full cascade", "render the bundle" | same as `/draft` + `cascade-protocol.md` | all 4 artifacts in `engagements/<slug>/comms/` |
| `/review` | `/review <artifact>` | "diff this", "anti-pattern check" | `review-protocol.md` + `bilingual-rules.md` | (chat-only summary; no file write) |
| `/glossary add` | `/glossary add` | "add glossary term", "FR-CA term" | `glossary-protocol.md` | `engagements/<slug>/comms/fr-ca-additions.yaml` |
| `/status` | `/status` | "current status", "what's drafted" | `approval-stage-tracking.md` | (chat-only summary) |
| `/checkpoint` | `/checkpoint` | "save state", "checkpoint" | `persistence-and-ledger.md` (mirrored) | `checkpoints/comp-comms-builder/<engagement>/checkpoint.yaml` |
| `/resume` | `/resume`, `/resume <slug>` | — | `persistence-and-ledger.md` (mirrored) | restores in-memory state |
| `/close-cycle` | `/close-cycle <cycle-slug>` | "close cycle", "mark cycle done" | `master-yaml-ops.md` | backend: `engagement_put_cycle` (status: closed) + `engagement_append_decision` |
| `/reopen-cycle` | `/reopen-cycle <cycle-slug>` | "reopen cycle" | `master-yaml-ops.md` | backend: `engagement_put_cycle` (status: drafting) + `engagement_append_decision` |
| `/switch-cycle` | `/switch-cycle <cycle-slug>` | "switch to cycle", "make primary" | `master-yaml-ops.md` | backend: `engagement_put_cycle` (primary: true, demotes prior) + `engagement_append_decision` |
| `/help` | `/help`, `/menu` | — | — | (chat-only) |

Full artifact catalog (per-artifact format/length/section/template): `$ASSET_ROOT/_modes/comms/references/artifact-catalog.md`. Valid speaker × audience × channel × format × brand-template combinations: `$ASSET_ROOT/_modes/comms/references/valid-combinations-rules.md` + `$ASSET_ROOT/_modes/comms/templates/valid-combinations.yaml`. Optional handoff from comp-training-designer's `message-map.yaml`: `$ASSET_ROOT/_modes/comms/references/training-designer-handoff.md`.

### Loading rule

Load these files in order at the start of every session:

- **`$ASSET_ROOT/_modes/comms/references/contracts.md`** — load at every quality gate (before any artifact write,
  at session close). Contains the testable contracts C01-C12. Violations surface loudly.
- **`$ASSET_ROOT/_modes/comms/references/engagement-modes.md`** — load when a partial-flow mode is detected
  (engagement_mode ≠ full-cascade), or when the opening-sequence pre-flight check 4
  flags a mode declaration missing. Drives step-routing for draft-protocol and
  cascade-protocol.

**Phase map and Phase 0 detail**: see `$ASSET_ROOT/_modes/comms/references/skill-overview.md`. **Core principles** (speaker register inheritance, anti-pattern discipline, FR-first co-draft, drift detection, approval-stage tracking, brand-kit non-destructive extension): also `$ASSET_ROOT/_modes/comms/references/skill-overview.md`.

### Critical orchestration rules

- **Two-register output discipline.** Operational output and deliverable output use different registers and must not blend. **Operational** = which step ran, what got written, which probe succeeded, which assumption was checked, which file was loaded — terse or silent. Surface only steps that produce a user decision or visible content. Never narrate no-op steps ("Step N — nothing to inherit, skipping" → just skip silently and proceed). **Deliverable** = comms drafts, FAQ prose, exec one-pagers, council synthesis, audience-facing copy — full prose, voice calibration to the speaker register, FR-first co-draft discipline. The skill's speaker-register tone (CEO / CHRO / VP Ops / HRBP) belongs in deliverables; operational steps run quietly. Mixing the registers — applying deliverable register to operational steps — produces ceremony that makes a 5-minute init feel like 30 minutes. Walk the protocol; do not perform it.
- **Verify-before-assert on factual claims.** Any claim involving a present-day rate, statute, role-holder, recent settlement, vendor capability, or fact about an external system requires a `web_search` (or, for tools, a `tool_search`) BEFORE assertion. Training-data priors are not acceptable for any value that can change between sessions. When you have not verified, the correct phrasing is "I haven't checked — let me verify"; never "X is the case, as of last year." Inventing capability or fact categories to soften an earlier wrong claim is itself an error.
- **Persistence discipline — schema-text to the backend, binary chat-download.** Schema-shaped text state (comms config + org comms profile via `engagement_put_section`, checkpoint via `engagement_put`, council/decision entries via `engagement_append_decision`) writes to the `market` backend. Non-schema text artifacts (FR-CA additions YAML, prior-comms registry scratch, council-state.yaml) stay local under `$STATE_ROOT`. **Binary artifacts (PDF, DOCX, PPTX rendered by /draft and /cascade) NEVER go through any backend** — they deliver as chat-download artifacts and the user files them into their own storage. The skill records the intended path in metadata for provenance; bytes are never written through an LLM context. This is a hard architectural rule — no toggle, no "upload anyway" path. The base64 round-trip (~700K tokens for a 2 MB PPTX) is the failure this rule prevents. HTML artifacts (email body for /draft all-hands-announcement) ARE text — non-schema, stay local. On MCP transport failure, schema reads fall back to the local cache (degraded) and schema writes escalate/halt (P4b D2); binary delivery is unchanged. Full contract: `$ASSET_ROOT/_modes/comms/references/persistence-and-ledger.md`.
