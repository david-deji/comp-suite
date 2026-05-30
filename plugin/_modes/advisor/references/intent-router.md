# Intent Router — Full Protocol

Loaded by SKILL.md when classifying an incoming request or handling track switching mid-conversation.

Classify every incoming request into one of nine entry points before doing anything else. Slash commands are checked first; if no slash command is present, evaluate the four engagement signals to assign one of the engagement tracks.

## Pre-classification rules

Apply these two checks BEFORE the slash-command table and the classification signals below.

### Invocation-prefix recognition

The following prefixes are no-op invocations of the skill — strip them and classify the remainder:
- `/compensation-advisor`, `/comp-advisor`, `/comp`

Example: `/compensation-advisor prepare the initial deck for acme ontario fy27`
→ classify on `prepare the initial deck for acme ontario fy27` (which then matches the pre-classification disambiguation rule below).

These prefixes do NOT constitute slash commands. They are a way users invoke the skill by name; the real signal is in the remainder of the message.

### Pre-classification disambiguation

When the deliverable name is generic — not stage-named, not slash-commanded — ask ONE disambiguating question BEFORE routing to a track.

Generic deliverable names that trigger disambiguation:
- "initial deck", "first deck", "kickoff thing"
- "something for [VP]", "deck for [audience]", "a deck"
- "the next thing", "what's next"
- Any deliverable noun without a stage marker (no "Strategy Kickoff", "market review", "Options Review", "approval pitch", etc. attached)

Disambiguation prompt template:

> "I want to make sure I route this correctly. Before I classify:
>
> A. **Stage-keyed deliverable**: this is for one of the canonical stages (Strategy Kickoff, market review, Options Review, approval pitch, cascade kit, payroll execution). Tell me which.
> B. **Pre-engagement work**: this is ahead of the canonical spine — see `references/engagement-modes.md` for narrative-frame-only, data-light-decision, costing-only modes.
> C. **Refresh of a prior deck**: I'll route to Track R or R-lite based on whether you want strategic changes (R) or just numbers (R-lite).
> D. **Council deliberation only**: no deck, just `/council` on a contested decision.
> E. **None of the above**: tell me what you actually need."

Wait for the answer, then route.

---

## Slash-Command Pre-Classification

See `references/slash-command-grammar.md` for the full slash-command grammar (precedence, aliases, NL triggers, dispatch protocols).

**Slash commands take precedence over engagement-signal classification.** When a message contains both a slash command and engagement-style content, the slash command wins. The exception is `/help`, which never overrides an in-progress engagement — it answers the meta-question and the engagement resumes on the next user turn.

**`/init pay-equity-qc` precedence:** the parameterized `/init pay-equity-qc` form must match BEFORE the bare `/init` form. Detection rule: if the message contains the literal string `/init pay-equity-qc` (with the `pay-equity-qc` argument), route to `references/pay-equity-qc-protocol.md` and load the Quebec pay equity protocol. Bare `/init` (no argument or any other argument) routes to the engagement-config setup protocol. Pay-equity natural-language triggers also route to the pay-equity protocol — they do NOT engage `/init` engagement-config setup.

If multiple slash commands appear in the same message (rare), the first one wins. Surface the conflict if the second one looks intentional:

> "I see /quickbench and /council in the same message. Running /quickbench first. After it returns, type /council [topic] to deliberate on the result."

If a slash command is malformed (`/qickbench`, `/iniit`), match by closest substring. If unambiguous, proceed with a small note: "Treating /qickbench as /quickbench." If ambiguous, surface candidates.

## Classification Signals (when no slash command is present)

Classify every non-slash request into one of five engagement tracks. Evaluate four signals from the user's first message, assign a track, then execute that track's opening behavior.

Extract these four signals from the first user message:

1. **Artifact signal** — Did the user upload a `.pptx` file?
2. **Specificity signal** — Did the user state all three of: (a) a deliverable type, (b) an audience, and (c) a decision or purpose?
3. **Explicit routing signal** — Did the user say something like "just build it", "update this deck", "just swap the numbers", "help me think through this"?
4. **Deliberation signal** — Did the user ask for multi-perspective reasoning on a strategic trade-off? Phrases like "run council on", "deliberate on", "multiple perspectives on", "argue both sides of", "stress-test this recommendation", "should we do X or Y" with genuine merit to both.

## Track Assignment Table

| Signals present | Track |
|----------------|-------|
| Explicit init intent (`/init`, "init", "set up config", "configure", "build me a config", "starter config") | **Init** (Config Setup) |
| Deliberation signal present + no deliverable-production intent | **Council** (Strategic Deliberation) |
| (`.pptx` uploaded **OR** prior `engagement-state.yaml` auto-loaded for this scope from the persistence folder **OR** structured prior-cycle paste matching the R-lite extraction shape) + explicit refresh intent ("just update the numbers", "same deck new data", "refresh with current numbers", "same thing new numbers", "just swap the numbers", "update for this year", "new numbers same story") | **R-lite** (Quick Refresh) |
| `.pptx` uploaded **OR** prior `engagement-state.yaml` auto-loaded for this scope, no explicit refresh or override signal | **R** (Full Refresh) |
| **Stage-specific deliverable named** (e.g., "Strategy Kickoff pre-read", "Options Review scenarios", "decision brief for Final Approval", "Manager cascade deck") | **D** (Direct Build) — stage-aware Phase 6a will pick the matching spine |
| All three specificity markers present (deliverable + audience + decision) | **D** (Direct Build) |
| Explicit "just build it" / "skip the questions" / equivalent | **D** (Direct Build) |
| Explicit "help me think" / "let's explore" / "I'm not sure yet" / equivalent | **C** (Consulting) |
| Ambiguous or underspecified | **C** (Consulting) |

When signals conflict, the explicit routing signal always wins. When no explicit signal exists and signals are mixed, default to Track C. Init always wins if its trigger phrase is present — even if a `.pptx` is uploaded (the upload is set aside for that session). Council wins over C when the deliberation signal is explicit — the user is asking for structured multi-lens reasoning, not open-ended consulting.

**Stage-specific deliverable markers** (non-exhaustive): "Strategy Kickoff pre-read", "Strategy Kickoff deck for VP Ops", "market review pre-read", "Options Review deck", "Options Review scenarios", "scenarios for Options Review", "decision brief", "1-page decision brief", "Final Approval brief", "approval-ready deck", "manager cascade", "VP Ops cascade deck", "manager-facing deck on the changes". When any of these appear, classify as Track D and let Phase 6a route to the matching stage-keyed spine. Track D's silent-mode Phase 6b applies (unless `deck.production_mode` config overrides).

## Signal Detection Guidance

**Deliverable type markers** (non-exhaustive): "benchmarking deck", "executive summary", "pay equity analysis", "comp strategy presentation", "merit matrix", "salary band recommendation", "total rewards deck."

**Audience markers**: "board", "C-suite", "CHRO", "VP HR", "HR ops", "comp team", "employees", "managers", "union."

**Decision markers**: "approve budget for", "close gaps in", "restructure bands", "justify raises", "present exposure", "recommend philosophy change", "support retention case."

**Deliberation markers** (non-exhaustive): "run council on", "deliberate on", "multiple perspectives on", "argue both sides of", "stress-test this recommendation", "weigh X vs Y", "should we do X or Y", "which option survives", "before we commit, let's think this through from all angles", "get me a second opinion on", "adversarial review of this comp decision."

The specificity signal requires all three markers. Partial specificity (deliverable only, or deliverable + audience without a decision) is insufficient for Track D. "Benchmarking deck for the board" = Track C (missing decision). "Benchmarking deck for the board showing we're behind market" = Track D.

The deliberation signal differs from Track C in that the user has already framed a specific decision or trade-off and wants structured multi-lens evaluation of it — not open-ended exploration. "Help me think about our comp philosophy" = Track C. "Run council on whether to move from P50 to P65" = Track Council.

## Excel/CSV Upload Handling

When the user uploads `.xlsx` or `.csv` (not `.pptx`), treat it as supplementary data input — not a prior deck. The file contains role/grade data, headcount, or current pay for use in costing scenarios. It does not determine track assignment.

- Acknowledge the upload and preview what you found (number of roles, columns detected) regardless of which track is active.
- When both `.pptx` and `.xlsx`/`.csv` are uploaded together, the `.pptx` drives track assignment (R-lite or R based on explicit signal). The spreadsheet is available as supplementary costing data in any track.

## Design Rule

Every track produces a new deck built from scratch. No track edits the uploaded file. No track preserves the design or theme of a prior deck.

---

## Track Opening Behaviors

### Track Init Opening Behavior

When classified as Init, do not start a consulting engagement. Run the dedicated Init walkthrough that builds an engagement-config YAML block.

**Master.yaml prelude (runs before all other /init steps):** Read `_orgs/<org-slug>/master.yaml` via `master-yaml-utils.md` → `read_master(org_slug)`. If no master.yaml exists for this slug, auto-create one plus an `_orgs/index.yaml` entry (no separate bootstrap command needed). Validate post-read per `master-yaml-utils.md` → `validate_against_schema`. Surface tree view of inheritable groups with freshness signals. Check pull-notifications (filter `decision_log` for cross-skill events since last compensation-advisor init). Then proceed to the 10-step /init flow in `init-mode-protocol.md`.

Opening action: read `references/init-mode-protocol.md` and follow its master-aware 10-step protocol. The 8 original intake sections (Sections 0-7: engagement_scope, cycle, org, audience, costing, benchmark, deck, persistence) are now Step 10 of the master.yaml flow. Output includes an updated `_orgs/<slug>/master.yaml`, a per-cycle state file at `_orgs/<slug>/cycles/<cycle-slug>/advisor/engagement-state.yaml`, and an auto-save to `configs/<slug>.yaml` when persistence is google-drive. No deck, no consulting, no data pull.

If the user pasted an existing config block AND used "/init update" or "update my config", run Update mode (see init-mode-protocol.md).

### Track Council Opening Behavior

When classified as Track Council, the user wants structured multi-perspective reasoning on a defined decision or trade-off. Do not enter consulting, do not plan a deck, do not ingest market data unless the council explicitly needs it.

Opening action: read `references/council-mode.md` and follow its session flow.

1. Load engagement config if present (Phase 0 behavior). If the config has a `council` section, use those defaults for mode, perspectives, synthesis style. If no config, use skill defaults documented in `council-mode.md`.
2. Frame the question in one sentence — including what IS being decided and what is NOT. If the user's framing was vague, ask in one compound turn: "What's the decision or trade-off you want the council to weigh, and what constraint is fixed (envelope, effective date, scope)?"
3. Declare the persona roster (4-6 perspectives) with a one-line justification each.
4. Run persona voice blocks sequentially in a single response.
5. Synthesize (consensus / tensions / unresolved / recommended path).
6. Produce mode-specific output: reasoning stops at synthesis; memo adds decision memo block; integrated adds Phase 4/5 handoff block.
7. Generate `council-state-YYYY-MM-DD-{client-slug}.yaml`. With `persistence.backend: google-drive` it auto-saves to the persistence folder (per `references/council-mode.md` § Step 8); in paste mode it is offered to the user as a file artifact via the file primitive.

No deck is produced by Council track. Council output is chat text + one YAML state artifact (+ optional memo markdown). If the user wants the council output turned into a deck, the user escalates to Track D or Track C after council completes — council-state is read as input.

### Track R-lite Opening Behavior

When classified as R-lite, treat the uploaded prior-year deck as data input. Do not enter the consulting conversation. Follow the R-lite Quick Refresh protocol below.

Opening action: Ingest the deck, extract structured data, and present the extraction summary for confirmation.

### Track R Opening Behavior

When classified as Track R, treat the uploaded prior-year deck as context input — not a template to edit.

1. Ingest the uploaded `.pptx` using `python -m markitdown`. Build a slide inventory: slide titles, data points, narrative arc, audience, benchmarked roles, market positioning, year.
2. If the user also uploaded `.xlsx`/`.csv`, parse it for role/grade/headcount/pay data.
3. Present a brief extraction summary:

> "I'll use your [year] deck as baseline — extracting the data, narrative, and audience context to build a fresh deck with current numbers."
>
> "From your [year] deck: [N roles] benchmarked against [sources], positioned at [market stance], built for [audience]. The narrative was [one-sentence summary of story arc]."

4. Enter the Consulting Protocol at Phase 1 (Discovery). The extracted context pre-fills discovery — you already know the audience, prior narrative, and baseline data. Focus discovery on what has changed: "Has anything shifted since last year — new roles, different audience, changed strategy?"
5. YoY comparison data from the prior deck is preserved and used in the new deck's narrative.

### Track D Opening Behavior

When classified as Track D, the user knows what they want. Confirm and build.

1. Parse the request for: deliverable type, audience, decision/purpose.
2. If all three are clear, respond with a confirmation statement and no questions:

> "Building [deliverable] for [audience] to support [decision]. Starting now."

   Proceed to Production. Load the appropriate example template for production methodology.

3. If 1-2 critical gaps exist, ask in the same message (maximum 2 questions):

> "I'll build [deliverable] for [audience]. Two things before I start: [gap 1]? [gap 2]?"

4. After confirmation, proceed to Production.

Track D requires at minimum deliverable type + audience. If both are stated, you may proceed with an inferred decision stated in the confirmation turn for the user to correct. Never ask more than 2 questions.

### Track C Opening Behavior

When classified as Track C, the user needs to think through the problem. Enter the Consulting Protocol at Phase 1 (Discovery).

Open with a single peer-to-peer question:

> "What decision is this supporting, and who needs to see it?"

Do not present a checklist. Do not ask multiple questions. One compound question covering the two highest-value discovery dimensions (decision and audience).

---

## Mid-Conversation Track Switching

### C to D: Passive Fast-Path Exit

After each user response during consulting, check whether you can fill a complete checkpoint brief: deliverable type, audience, narrative angle, key data points, recommendation direction. If all are present, present the brief for confirmation:

> "Based on what you've told me, here's what I'd build: [brief]. Want me to proceed?"

On confirmation, skip remaining consulting and proceed to Production. This detection is passive — never prompt "do you want to skip ahead?"

### C to D: Explicit Skip

When the user says "just build it" or equivalent during consulting, check whether minimum information exists (deliverable type + audience). If yes, present the checkpoint brief and proceed. If no, ask only for what is missing:

> "I can build now, but I don't know the audience yet. Board? CHRO? HR ops?"

Never refuse to build. Ask for minimum required information and proceed.

### D to C: Uncertainty Escalation

When a Track D user expresses uncertainty before production begins ("actually, let me think about this", "I'm not sure about the angle", "can we explore the data first?"), acknowledge the switch and enter consulting at the appropriate phase:

- Uncertainty about audience or decision → Phase 1 (Discovery)
- Uncertainty about data or findings → Phase 3b (Interpretation)
- Uncertainty about scenarios or direction → Phase 4 (Option Modeling)

Always name the switch explicitly:

> "Let's step back and explore [topic]. [Consulting question]."

### R-lite to R Escalation

When R-lite extraction finds insufficient structured data in the prior deck (no benchmarking numbers, no role list, purely narrative content), escalate to Track R automatically:

> "This deck doesn't have enough structured data for a quick refresh. Let me run through the full process instead."

### R-lite to C

When a user in R-lite signals they want to rethink the approach ("actually, let's rethink this", "I want to change the strategy"), escalate to Track R, which enters the consulting flow with prior deck context.

### Track R Context

Track R always enters the consulting flow. There is no switch out of R — but consulting phases will be shorter because the prior deck pre-fills context. The fast-path exit (C to D) still applies within Track R's consulting flow.

### Into Council from C, R, D (mid-engagement)

When the user, mid-engagement, asks for a council on a specific decision ("before we go to Phase 5, run a council on the philosophy shift"; "I want multiple perspectives on this scenario before I pick"), pause the active track and run Council in integrated mode. The council's output feeds back into the active track's current phase — typically Phase 4 (option modeling) or Phase 5 (narrative workshop).

Switching sequence:
1. Acknowledge the switch: "Running council on [question] before we continue. This will feed back into [Phase N]."
2. Execute Council track per `council-mode.md`, mode = integrated.
3. Produce `council-state-*.yaml`.
4. Resume the original track at the current phase, carrying the council's recommended path forward. Reference the council-state file in the engagement-state under `council_state_ref`.

### Out of Council

Council is a terminal track for the current question — synthesis ends the reasoning. If the user wants to act on the council output (build a deck, model scenarios), switch to Track D (direct build with council-state as input) or Track C (continue consulting with council-state pre-filling context).

## Artifact Discipline

Routing and classification turns are chat-text only — the intent router itself is a meta-decision step, not a deliverable. Artifact production begins inside the assigned track or command.

The chosen track or command WILL produce an artifact at its own end (per SKILL.md § Critical orchestration rules: every track and every utility command except `/help` produces an END deliverable). The router's job is to hand off cleanly, not to start artifact emission itself.

---

### `/close-cycle` Behavior

Slash: `/close-cycle <cycle-slug>` (slash-only). NL triggers: "close cycle", "mark cycle done", "finalize cycle".

Loaded references: `master-yaml-utils.md`. END artifact: `_orgs/<org-slug>/master.yaml` (write — cycle status + decision_log entry).

Verifies the cycle exists in `master.cycles[]` and status ≠ `closed`. Surfaces a confirmation tree showing all skills that touched the cycle and whether each has open work. On confirm: writes this skill's self-rollup entry to `decision_log[]` (`decision_type: cycle_closed`, `tags: [cycle-close, advisor-rollup]`, summary includes scenario shipped, council runs logged, glossary terms promoted, costing artifacts produced). Sets `master.cycles[].status: closed` + `closed_date: <today>`. Does NOT write roll-ups for sibling skills — those are lazy-written on their own next `/init`.

### `/reopen-cycle` Behavior

Slash: `/reopen-cycle <cycle-slug>` (slash-only). NL triggers: "reopen cycle", "re-open cycle".

Loaded references: `master-yaml-utils.md`. END artifact: `_orgs/<org-slug>/master.yaml` (write — cycle status + decision_log entry).

Flips `master.cycles[].status` from `closed` back to `drafting`. Appends `decision_type: cycle_reopened` entry to `decision_log[]` with `refs.related_decision_ids` pointing to the original `cycle_closed` entry ID. Edits land in the existing `cycle_dir` (in-place amend — no cycle versioning).

### `/switch-cycle` Behavior

Slash: `/switch-cycle <cycle-slug>` (slash-only). NL triggers: "switch to cycle", "make primary", "set primary cycle".

Loaded references: `master-yaml-utils.md`. END artifact: `_orgs/<org-slug>/master.yaml` (write — primary pointer + decision_log entry).

Flips `master.cycles[].primary: true` to the named cycle (exactly one cycle may hold `primary: true` at any time). Sets `primary: false` on the previously-primary cycle. Appends `decision_type: cycle_primary_switched` entry to `decision_log[]`.

---

## Phase 0 — Persistence Backend Detection (autonomous, all engagement tracks)

For tracks C, D, R, R-lite, and Council, run this detection step before track opening behavior begins. Skip for `/help`, `/init`, `/update`, `/intake`, `/quickbench` (these don't read prior state). `/resume` and `/ledger` go straight into the persistence-and-ledger.md flow.

### Step 1 — Test Google Drive (Claude.ai connector) availability

Attempt a `google_drive_search` call against `persistence.folder` from the loaded config (or default `comp-advisor-state` when no config is present). Three outcomes:

| Outcome | Mode | Behavior |
|---|---|---|
| Call succeeds, repo accessible | **google-drive** | Continue Steps 2-4 |
| MCP available but repo not found / no access | **google-drive-misconfigured** | Surface the error + setup pointer ("create `comp-advisor-state` and re-run, or paste config inline"). Fall through to paste mode for this session. |
| Google Drive (Claude.ai connector) not installed / not authenticated | **paste mode** | Skip Steps 2-4. Existing paste-driven Phase 0 behavior applies. |

### Step 2 — Auto-load engagement config (google-drive mode only)

If the user's first message names a scope or slug ("starting Pharmacy FY26 engagement", "open atlantic-retail-fy26"), and no inline YAML config was pasted, attempt `google_drive_fetch` for `configs/<slug>.yaml`. If found, load it as the engagement config.

If the user pasted a YAML config inline, the inline paste takes precedence — log it as the active config and skip the auto-load.

### Step 3 — Detect resume opportunity (google-drive mode only)

Call `google_drive_search` for `engagements/<slug>-*/`. For any folder containing `checkpoint.yaml`:

1. Surface a "resume available" line BEFORE proceeding to track classification:

> "Found checkpoint for `pharmacy-fy26` saved 2 days ago at Phase 4. `/resume pharmacy-fy26` to continue, or `/restart` to start a fresh engagement on this scope."

2. If the user types `/resume`, hand off to the persistence-and-ledger.md `/resume` flow. If the user provides any other input, treat the checkpoint as stale-but-preserved and proceed with the new request (do NOT delete the checkpoint).

### Step 4 — Query the ledger for prior cycles (google-drive mode only)

Call `google_drive_fetch` for `ledger/outcome-history.yaml`. Filter entries where `scope_slug` matches the active engagement's `scope_slug`. Compute drift trajectory across cycles (gap-to-target percentile delta, envelope delta, council-followed pattern).

Surface in the Phase 0 loaded-config summary:

> "Persistence: google-drive at `comp-advisor-state`.
>
> Prior engagement context (from ledger, scope = pharmacy):
> - pharmacy-fy25 (closed 2025-05-15): Deferred — committed to look at it FY26.
>   90d outcome: turnover continued to climb 12% YoY.
> - pharmacy-fy24 (closed 2024-05-15): 3% ATB + meat-cutter compression fix QC, $3.8M.
>   Recommendation followed in full.
> - Drift: gap to P50 went from 2% (FY24) → 4% (FY25) → projected 8% (FY26 Phase 2 pull)."

Auto-populate `prior_engagement_refs` in the new in-memory engagement-state from the ledger query. Phase 1 Beat 1 references this when grounding "what's different this cycle."

**Read efficiency:** for repos with many engagements, prefer one `google_drive_search` call to enumerate, then targeted `google_drive_fetch` only for the active scope's files. Don't fetch every engagement-state.yaml at session start — the ledger summary alone is enough context. Full state is fetched only on `/resume` or explicit reference.

### Step 5 — Resolve repo-resident shared assets (google-drive mode only)

After ledger query, scan the repo for shared assets that the active engagement may consume. This is a single batched read, not five separate calls.

Call `google_drive_search` with `recursive=false` against these paths in parallel:

- `branding/` (lists `_default/`, `<org-slug>/` subdirs)
- `cba-library/` (lists `_index.yaml` + agreement files)
- `survey-archive/<vendor>/` for any vendor named in the engagement config (otherwise just `survey-archive/`)
- `vocabulary/` (checks for `fr-ca-glossary.yaml`)
- `personas/` (lists `_index.yaml` + custom persona files)

For each asset class, compute match-strength per `references/library-resolution.md` rules and surface in the Phase 0 loaded-config summary. Match-strength taxonomy: `exact`, `aged`, `geo-adjusted`, `default-fallback`, `bundled-fallback`, `none`.

### Step 6 — Surface loaded-config summary

After Steps 1-5 complete, surface a compact loaded-config block to the user before track classification proceeds:

> "Loaded config summary:
> - Persistence: google-drive at `comp-advisor-state`
> - Brand kit: `<org_slug or _default>` [3 master overrides: 01-title, 09-cost-analysis, 14-methodology]
> - CBA auto-loaded: `tuac-501-acme-qc-retail-2024-2028` (meat-cutter@QC) [exact]
> - Survey archive: Mercer 2026 QC retail [exact]; WTW 2024 ON [aged: 16 months]
> - Vocabulary: repo-canonical (43 terms, last promoted 2026-04-15)
> - Custom personas available: `pension-specialist`, `quebec-only-labour-counsel`
> - Brand kit drift: bundle has 1 new master (`19-comparison-matrix.js`) — run `/brand-kit refresh _default` to merge"

Each line is OMITTED when the asset class has no content. The summary is non-blocking; track classification continues immediately after.

### Paste-mode behavior

When backend mode is `paste` or `google-drive-misconfigured`, Steps 2-5 are skipped. The ledger summary still appears if the user pasted `outcome-history.yaml` alongside their config. Brand kit defaults to bundled `_default`. CBA, survey, vocabulary, persona libraries are unavailable for this session — surface as `unavailable in paste mode` in the loaded-config summary so the user knows the gap.

Full backend behavior, schema, and write paths in `references/persistence-and-ledger.md`. Full library-resolution rules in `references/library-resolution.md`. Brand-kit-specific structure and lifecycle in `references/brand-kit-protocol.md`.

---

## Track R-lite: Quick Refresh — Full Protocol

Track R-lite handles "just swap the numbers" requests. It skips the consulting conversation entirely and rebuilds the deck with updated market data using the prior year's narrative arc.

### When R-lite Applies

All three conditions must be true:

1. **Prior-cycle context is available** via one of three input modes (see § Input Modes below):
   - `.pptx` upload (legacy / no-persistence path)
   - Prior `engagement-state.yaml` auto-loaded for the same `scope_slug` from the persistence folder (preferred when persistence is configured)
   - Structured prior-cycle paste (fallback when neither of the above is available)
2. The user explicitly signaled a data-only refresh ("just update the numbers", "same deck new data", "refresh with current numbers", "update for this year", "new numbers same story", or equivalent).
3. The user did not signal any strategic changes (no new audience, no changed scope, no rethinking the approach).

### Input Modes

R-lite accepts prior-cycle context in three shapes. Phase 0 detection picks the highest-quality mode available, in this priority order:

| Priority | Mode | Trigger | Strength |
|----------|------|---------|----------|
| 1 | **engagement-state.yaml from repo** | Phase 0 backend detection found `engagements/<scope_slug>/<prior_cycle_id>/engagement-state.yaml` in the persistence folder | Strongest — full structured data including `tool_calls[]` audit, narrative frame, scenario picks, outcome block |
| 2 | **`.pptx` upload** | User attached a `.pptx` file in this turn | Medium — extraction via markitdown, narrative arc inferred from slide titles + body |
| 3 | **structured prior-cycle paste** | User pasted a YAML or markdown block matching the R-lite extraction shape (roles, percentiles, narrative bullets, recommendations) | Workable — relies on user to format correctly; skill validates and surfaces gaps |

When more than one mode is available simultaneously (rare — e.g., engagement-state.yaml exists AND user uploaded a fresh `.pptx`), surface the choice:

> "I found a prior engagement-state.yaml for this scope from [date], AND you uploaded a `.pptx`. The YAML is more structured — use it as the base, or rebuild from the deck?"

### R-lite Flow

#### Step 1: Ingest and Extract

**Mode 1 (engagement-state.yaml)**: Read the YAML directly. Extract the same structured fields listed below from the YAML's existing sections (`roles_benchmarked`, `narrative_frame`, `audience`, `recommendations`, `flags`, `pay_structure`). No markitdown call needed; no inference required.

**Mode 2 (`.pptx` upload)**: Ingest the uploaded `.pptx` using `python -m markitdown`. Extract into the internal working document.

**Mode 3 (structured paste)**: Parse the pasted block. If YAML, validate against the R-lite extraction shape. If markdown, extract the same fields by section header matching. Surface gaps: "Your paste is missing [field] — proceeding without it. R-lite will infer or skip the affected slide."

In all three modes, extract:

- **Roles benchmarked**: list with prior-year market percentile positioning
- **Data sources referenced**: survey names, years, geographies
- **Narrative arc**: 3-5 bullet summary of the story the deck told
- **Audience**: who the deck was built for
- **Key recommendations**: what the prior deck recommended
- **Flags**: anything that looks like a manual/policy item (collective agreements, approved budgets)
- **`pay_structure`**: `step | merit | flat | mixed` — inferred from the data patterns

If the user also uploaded `.xlsx`/`.csv`, parse it for role/grade/headcount/pay data as supplementary input — independent of input mode.

#### Step 2: Confirm Scope (Single Turn)

Present the extraction summary and ask for confirmation in one turn:

> "From your [year] deck: [N roles] benchmarked against [sources], positioned at [market stance], built for [audience]. I'll pull current data for all roles and rebuild with the same narrative. Any roles to add or drop before I start?"

This is the only confirmation point. After the user confirms (or adjusts the role list), proceed autonomously.

#### Step 3: Pull Current Market Data

Fetch current market data for all extracted roles using Market MCP as primary source — `search_roles` then `get_role_intelligence` returns the StatCan + live posting + YoY bundle in one call. Use `get_cba_wage_scale` for unionized roles. Use Indeed MCP for posting validation when matches look ambiguous. Web research as final fallback via the `web-search` builtin (or the optional Perplexity tools when configured — see consulting-protocol.md § Web search). Match the same markets, geographies, and percentiles referenced in the prior deck.

#### Step 4: Compute YoY Deltas

For each role, compute the delta between prior-year and current values. Incorporate deltas into the narrative:

> "Warehouse Associate moved from P45 to P42 — gap widened."
> "P50 moved from $22.80 to $23.15 (+1.5%)."

#### Step 5: Build New Deck

Proceed to Production. Build a new deck from scratch with:

- Updated numbers for all roles
- The same narrative arc extracted from the prior deck
- YoY comparison callouts on relevant slides
- Same audience framing, same recommendation direction (updated for current data)

The output is always a new deck — never an edit of the uploaded file, never preserving the prior deck's design or theme.

#### Step 6: QA Loop

Run the standard QA check. The DATA dimension compares slide values against freshly pulled market data.

### R-lite Handoff Object

R-lite does not produce a narrative frame through consulting. Instead, construct a simplified handoff from extraction:

```
R-LITE HANDOFF
==============
Source deck: [filename]
Extracted deliverable type: [from template matching]
Extracted audience: [from deck content]
Extracted decision: [from deck content]
Extracted narrative angle: [from prior deck's story arc]
Pay structure: [step | merit | flat | mixed]
Prior-year data points: [{role, market, percentile, source, date, value}]
Updated data points: [{role, market, percentile, source, date, value}]
YoY deltas: [{role, prior_value, current_value, delta_pct, direction}]
Prior-year scenarios/recommendations: [extracted text]
Scope: [roles, geographies]
Data sources: [original sources + current equivalents with new effective dates]
Payroll jurisdiction: [extracted or inferred from geography]
```

Validate the R-lite handoff against the same Production Prerequisites as the corresponding template. If any prerequisite cannot be satisfied from extraction, escalate to Track R.

### Sufficiency Gate: When to Escalate to Track R

Escalate from R-lite to Track R when any of these are true:

- The prior deck lacks extractable structured data: fewer than 3 roles named, OR fewer than 3 quantitative benchmark data points (percentiles, compa-ratios, gap dollars), OR purely narrative/strategic content with no numbers.
- A prerequisite for the matching production template cannot be filled from extraction alone.
- During data refresh, you detect a significant structural change (a role's market position shifted dramatically, a new gap opened that wasn't present before). In this case, flag the finding to the user and offer the upgrade:

> "The data shows [finding] — this is a significant shift from last year. Want me to run the full consulting process to rethink the approach, or proceed with just the number update?"

### What R-lite Does Not Do

- No consulting conversation (Phases 1-5 are skipped entirely).
- No option modeling or scenario comparison.
- No narrative workshop — the prior deck's narrative is reused directly.
- No discovery questions beyond the single scope confirmation turn.
- No strategic reframing. If the user wants to change the story, escalate to Track R.
