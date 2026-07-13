# Skill Overview

Phase map, Phase 0 detail, and core principles. Loaded by SKILL.md alongside `init-mode-protocol.md` at every track entry that runs Phase 0 (which is every track except `/help`, `/resume`, and `/status` read paths).

---

## 1. Phase map

```
Phase 0 — Config Loading   (every track: identity + backend resolution, config load, redaction scan, surface state)
   │
   ├─→ /init        → engagement-comms-config walkthrough (no production work)
   ├─→ /brand       → comms-templates read or scaffold
   ├─→ /ingest      → Phase 1 (single conversational interview, seven sub-phases)
   ├─→ /draft       → Phase 2 (single-artifact render: anti-pattern surface → resolve → render → write)
   ├─→ /cascade     → Phase 3 (full bundle: exec-one-pager → all-hands → manager-faq → hrbp-memo)
   └─→ /review      → Phase 4 (diff + anti-pattern surface + glossary check; chat-only)

   /glossary add    → appends comms-specific term to engagement-level additions
   /status          → artifact list + approval stages; chat-only
   /checkpoint      → mid-track state save (any phase)
   /resume          → restore from saved checkpoint
   /help            → list of modes and commands; chat-only
```

Typical first-cycle workflow: `/init` → `/brand init <org-slug>` → `/ingest` → `/cascade` → `/review` → (repeat `/draft` for revisions).

---

## 2. Phase 0 detail (Config Loading)

Runs at every track entry except `/help`, `/resume`, `/status`. Four steps in order:

### 2.1 Identity + backend resolution

Resolve OAuth identity → org via `list_my_orgs`, then read the org header via `engagement_get_master`. There is no folder to configure, no backend selector, and no visibility gate — org isolation is enforced by the backend via OAuth membership. Two outcomes:

- **Backend reachable** (identity resolves to an org) — proceed. Schema reads go MCP-first; schema writes are MCP-only and escalate on failure (D2).
- **Transport failure** (connection error, timeout, 5xx, not-yet-authenticated) — read from the local `$STATE_ROOT` cache (D1) for this session; a tool returning not-found/empty is authoritative (never a local fallback on not-found). Writes still escalate/halt — never degrade to chat-paste.

Runs once per session. Cache result for the session.

### 2.2 Config load

Three paths:

- User pasted YAML at session start — parse against `engagement-comms-config-template.md` schema. Validate. If validation fails, surface the specific rule violated and exit.
- User referenced an engagement slug (e.g., "/cascade `pharmacy-fy26`") — auto-load `engagement-comms-configs/pharmacy-fy26.yaml` from persistence.
- Neither — prompt: "No engagement config found. Run `/init` first?" and exit.

After load: resolve `org-comms-profiles/<client-slug>.yaml` from persistence if it exists. If absent, note that bundled defaults will apply.

### 2.3 Redaction input scan

Scan all pasted inputs for banned patterns per `redaction-rules.md`:

- Person names (real employee names, not speaker roles)
- Raw salary figures
- Raw headcount in workforce context
- Personal email / personal phone

On detection: refuse to proceed, surface warning naming the pattern category, instruct re-paste with required transformation. Hard rule.

### 2.4 Surface state to user

One-line summary:

> "Loaded engagement `<slug>` (`<cycle-name>`). `<N>` artifacts configured. Org profile: `<loaded / using bundled defaults>`. Persistence: `<market backend / local cache — transport failure>`."

Then proceed to track-specific protocol.

---

## 3. Core principles

### 3.1 Speaker register inheritance

Four-layer inheritance: bundled default → org (from `org-comms-profiles/<org-slug>.yaml`) → engagement (from `engagement-comms-config.yaml`) → CLI override (if operator specifies `speaker` at draft time). Later layers override earlier. If `org-comms-profile.yaml` is absent (cold-start), bundled defaults from `template_assets/speaker-registers/` apply. Never mix layers mid-draft — resolve fully before rendering.

Full rules: `references/speaker-register-rules.md`.

### 3.2 Anti-pattern discipline

Anti-patterns are surfaced **before** drafting, not during. At the top of every `/draft` and every artifact step in `/cascade`, print the active anti-pattern list and require acknowledgment. Auto-detection mid-draft is deferred to v2. Operator checklist is the v1 gate.

Anti-patterns live in `org-comms-profile.yaml`'s `anti_patterns[]` array (populated via `/ingest`). Bundled common anti-patterns ship in `template_assets/anti-patterns.yaml` (cold-start fallback). Both sources merge at draft time.

### 3.3 FR-first co-draft

Both languages are drafted from intent (from the source recommendation), not by translating one to the other. Render primary language (`languages.primary`, default `fr-ca`) first, then secondary (`languages.secondary`). Each language gets its own versioned file. Approval is tracked per language. FR draft can be in `legal_review` while EN is still in `chro_review`.

Full rules: `references/bilingual-rules.md`.

### 3.4 Drift detection

At every `/draft` call, compare the current hash of the source recommendation (the advisor engagement body read via `engagement_get`) against `last_drift_check_against_recommendation_revision` stored in `engagement-comms-config.artifacts[]`. On mismatch, surface:

> "Source recommendation has changed since v(N-1) was drafted. Refresh? (`refresh` / `proceed-anyway` / `abort`)"

Drift detection prevents comms artifacts from becoming silently inconsistent with the underlying comp decision.

### 3.5 Approval-stage tracking

Per-artifact `approval_stage` field flows: `drafted → chro_review → legal_review → ceo_approved → shipped`. Tracking only — the skill records what stage each artifact is in; it does not verify external approvals happened. Operator advances stage by editing `engagement-comms-config.yaml`. Lock semantics: when `approval_stage == ceo_approved`, re-opening creates a NEW version (v(N+1)); prior approved version stays in history.

Full rules: `references/approval-stage-tracking.md`.

### 3.6 Brand-kit non-destructive extension

comp-comms-builder writes ONLY inside `branding/<org-slug>/comms-templates/`. It NEVER writes to `theme/`, `logo.{svg,png}`, `masters/`, or `footnotes.yaml` — those are owned by sibling skills. If `comms-templates/` is absent, auto-seed from `template_assets/branding/_default/comms-templates/` with a warning. Comms-specific templates co-exist with the shared brand kit; they do not replace it.

Full rules: `references/brand-mode-protocol.md` + `references/brand-kit-protocol.md` (mirrored).

### 3.7 Checkpoint blocking

`/checkpoint` writes are synchronous. The next phase blocks until the user explicitly confirms the write succeeded.

### 3.8 Mirrored references are read-only

`meta-protocol.md`, `persistence-and-ledger.md`, `tools-available.md`, `brand-kit-protocol.md`, `production-and-qa.md`, `template-master.md`, `redaction-rules.md` are manual copies of canonical files in sibling skills. Never edit them here — coordinate with the canonical skill for any change, then re-copy.

### 3.9 Transport-failure fallback

There is no paste-mode. On transport failure (connection error, timeout, 5xx, not-yet-authenticated), the skill reads schema state from the local `$STATE_ROOT` cache (D1); a tool returning not-found/empty is authoritative and never triggers a local fallback. Schema writes are MCP-only — on write failure the skill escalates/halts, never degrading to chat-paste (D2). Rendered binaries (PPTX/DOCX/PDF) deliver as chat-download in all cases — that is normal delivery, not a fallback. Redaction still hard-refuses banned patterns regardless of transport state.

### 3.10 Valid-combinations registry

The skill refuses to render a combination not in `template_assets/valid-combinations.yaml` (artifact × speaker × audience × channel × format × brand-template). If an operator requests an invalid combination, surface valid options for that artifact type. Per-engagement overrides are possible via `engagement-comms-config.yaml` `valid_combinations_overrides:` field.

---

## 4. Where things live (cheat sheet)

| Question | Answer |
|----------|--------|
| Where is the engagement config? | `engagement-comms-configs/<slug>.yaml` — `market` MCP backend (per `persistence-and-ledger.md`) |
| Where is the org voice/brand profile? | `org-comms-profiles/<org-slug>.yaml` — `market` MCP backend (per `persistence-and-ledger.md`) |
| Where are the comms artifacts? | chat-download deliverables + local scratch under `$STATE_ROOT/_orgs/<slug>/comms/` |
| Where are working drafts? | local scratch `$STATE_ROOT/_orgs/<slug>/comms/_drafts/` (cleared on `/approve shipped`) |
| Where are comms brand templates? | org brand kit via `brand_*` tools (`branding/<org-slug>/comms-templates/` namespace) |
| Where are FR-CA additions? | glossary library reference; resolved per the library/persistence contract |
| Where are checkpoints? | engagement body via `engagement_put`; local `checkpoint.yaml` is a cache mirror |
| Where is the persistence contract? | `references/persistence-and-ledger.md` (mirrored from compensation-advisor) |
| Where is the artifact catalog? | `references/artifact-catalog.md` |
| Where are bundled speaker registers? | `template_assets/speaker-registers/` |
| Where are bundled audience profiles? | `template_assets/audience-profiles/` |
| Where are default comms templates? | `template_assets/branding/_default/comms-templates/` |
