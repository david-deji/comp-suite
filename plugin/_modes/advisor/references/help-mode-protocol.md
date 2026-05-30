# Help Mode Protocol

Help mode is the discoverability layer for the skill. It lists what commands exist, what they do, and how to invoke them — with a two-tier structure so users can scan quickly or drill into a specific command.

Loaded by SKILL.md when the Intent Router detects `/help`, `/menu`, or equivalent.

---

## When Help Mode Triggers

Help mode triggers when the user's first message is any of:

- `/help`, `/menu`, `/commands`
- `/help [command-name]` — e.g., `/help intake`, `/help council`
- "what can you do?", "show me the commands", "list the modes" (only when phrased as discoverability requests, not as the start of an engagement — context-dependent)

When the trigger is `/help` with no argument, output the **Tier 1** compact list. When the trigger is `/help [command]`, output **Tier 2** detail for that specific command.

If the user's question is ambiguous between "list commands" and "help me think through this comp problem," classify as Track C and answer the substantive question. `/help` is for the meta question; "help me with X" is for the substantive one.

---

## Tier 1 — Compact List (default `/help` output)

Output the compact list as a single response. Goal: fit one screen, give the user enough to pick a path.

Format:

```
Compensation Advisor — what I can do

**Engagements** (produce a deck or formal output):
  Track C        Full consulting flow — "help me think through this"
  Track D        Direct build — "build a [X] for [audience] showing [Y]"
  Track R        Refresh — upload last year's .pptx, build new with current data
  Track R-lite   Quick refresh — same deck, just swap the numbers

**Slash commands** (specific tasks):
  /init          Build a reusable engagement config (15-25 min, one-time)
  /update        Refresh an existing config (3-10 min, between engagements)
  /intake        Generate a strategic intake form PDF for VP HR/Ops
  /quickbench    Single-role market pull, no deck (~2 min)
  /council       Multi-perspective deliberation on a strategic trade-off
  /checkpoint    Save engagement state to persistence folder
  /resume        Resume an in-progress engagement from a checkpoint
  /ledger        Read prior-cycle outcomes; update outcome windows
  /brand-kit     init <org-slug> — scaffold a per-org brand kit from _default
  /cba           save <agreement-id> — manually save a user-CBA to the library
  /glossary      promote — review and merge engagement-level FR-CA additions
  /help [cmd]    Detail on any command (e.g., /help intake)

**Reasoning-only**:
  Council        "Run council on [decision]" — no deck, just structured 
                 multi-lens reasoning + optional decision memo

Type /help <command-name> for details on any of the above.
```

The compact list uses fixed-width formatting (column alignment via spaces) for readability. Emojis are not used. The list is comprehensive but not exhaustive — internal phases (Phase 0-7) are not exposed at this tier.

---

## Tier 2 — Per-Command Detail (`/help <command>`)

When the user types `/help intake`, `/help council`, `/help quickbench`, etc., produce a detail block for that command. Each detail block follows the same structure:

```
**/[command]** — [one-line purpose]

**What it produces:** [output type — text, YAML, PDF, deck, etc.]
**Time:** [typical time on task]
**Input needed:** [what the user provides]

**How to invoke:**
  [primary form]
  [variant forms, if any]

**What happens:**
  1. [step]
  2. [step]
  3. [step]

**When NOT to use it:** [contrast with adjacent commands]

**Example:**
  > [example invocation]
  → [what the skill does]
```

---

## Tier 2 Detail — /init

```
**/init** — Build a reusable engagement config from scratch

**What it produces:** A YAML config block (chat output, user copies & saves)
**Time:** 20-35 min
**Input needed:** Answers to ~30 questions across 7 sections

**How to invoke:**
  /init
  "set up config" / "configure" / "starter config"

**What happens:**
  1. Walks 7 sections: engagement_scope, cycle, org, audience, costing, benchmark, deck
  2. Sections 0 (engagement_scope) and 1 (cycle) are pushed hard — they
     define one-engagement-equals-one-budget-owner and where you sit in
     the annual wage-review workback (last cycle / this cycle / current stage)
  3. Sections 2-6 are optional; "skip" is always valid
  4. Final YAML emitted as a copy-pasteable code block

**When NOT to use it:** If you already have a config and just need to 
refresh stale dates → /update is faster.

**Example:**
  > /init
  → "Init mode — I'll walk you through 7 sections..."
```

---

## Tier 2 Detail — /update

```
**/update** — Refresh an existing engagement config

**What it produces:** Updated YAML config block
**Time:** 3-10 min (faster if only dates are stale)
**Input needed:** Your existing config pasted in the same message

**How to invoke:**
  /update
  (must paste existing YAML in the same message)

**What happens:**
  1. Parses your config, scans for stale items (>180 days) and conflicts
  2. Asks: "refresh all in one pass, or review each one-by-one?"
  3. Web-verifies values where possible (minimum wages, etc.); asks 
     directly for anything unverifiable
  4. Emits merged YAML with a one-line changelog

**When NOT to use it:** If your config is >12 months old, /init may 
be cleaner than surgical updates.

**Example:**
  > /update
  > [pasted config]
  → "Loaded your config. 3 stale items. Refresh all or review each?"
```

---

## Tier 2 Detail — /intake

```
**/intake** — Generate a strategic intake form PDF (branded per the active brand kit; defaults to the neutral placeholder `_default` kit)

**What it produces:** Fillable PDF (active-kit branded — `_default` kit ships a neutral placeholder brand; per-org kits override per `references/brand-kit-protocol.md`) plus an `intake-form-meta-{slug}-{date}.yaml` metadata sidecar
**Time:** 5-10 min (depends on how many variants you edit)
**Input needed:** Scope (provinces + banners, optional role family) 
                  + cycle name

**How to invoke:**
  /intake
  /intake [scope description]

**What happens:**
  1. Asks for scope: provinces, banners, optional role family, cycle name
  2. Generates 5 scope-parameterized question variants (Q4, Q5, Q6, Q8, Q9)
  3. Presents each variant ONE AT A TIME for approve/edit/reject
  4. Builds the PDF with approved variants + 6 fixed questions
  5. Delivers PDF via present_files

**When NOT to use it:** If you need quick market data, not a strategic 
intake → /quickbench. If the recipient just needs a deck, not a form 
→ Track D.

**Example:**
  > /intake
  → "Intake mode — I'll generate a fillable strategic intake PDF.
     Tell me: provinces, banners, role family (optional), cycle name."
```

---

## Tier 2 Detail — /quickbench

```
**/quickbench** — Single-role market pull, no engagement

**What it produces:** Mini-report in chat (table + 2-3 sentence read)
**Time:** ~2 min
**Input needed:** Role + province (and optionally pay structure)

**How to invoke:**
  /quickbench
  /quickbench [role] [province]
  /qb [role] [province]

**What happens:**
  1. Pulls market data via get_role_intelligence (P10/P25/P50/P75/P90)
  2. Adds CBA scale if the role is unionized in that province
  3. Outputs a compact table + plain-language interpretation
  4. Soft-offers escalation to a deck if the data warrants it

**When NOT to use it:** If you need a deck or recommendation → Track D 
or Track C. If you need multi-role / multi-province sweep → Track C.

**Example:**
  > /quickbench meat cutter BC
  → [Pulls data, returns mini-report with P50, sample size, sources, 
     and "want this turned into a deck?" offer]
```

---

## Tier 2 Detail — /council

```
**/council** — Multi-perspective deliberation on a strategic trade-off

**What it produces:** Reasoning text + YAML state file (+ optional memo)
**Time:** 5-15 min depending on scope
**Input needed:** A specific decision or trade-off to weigh (1 sentence)

**How to invoke:**
  /council
  /council [framing question]
  /council memo: [framing question]
  /council integrated: [framing question]   (default mid-engagement)

  Also triggers via natural language:
  "run council on [X]", "deliberate on [X]", "stress-test [X]"

**What happens:**
  1. If no argument, asks for the framing question
  2. Declares 4-6 personas with one-line justifications each
  3. Runs persona voice blocks sequentially in a single response
  4. Synthesizes (consensus / tensions / unresolved / recommended path)
  5. Generates council-state-*.yaml as a state artifact

**When NOT to use it:** If you want open-ended exploration → Track C. 
If you want a deck of options → Track D. Council is for structured 
weighing of a defined choice.

**Example:**
  > /council should we move from P50 to P65 for store managers?
  → [Declares roster: Operator, Finance, HR, Skeptic, Union Watcher, 
     Strategist. Runs 6 persona blocks. Synthesizes.]
```

---

## Tier 2 Detail — /checkpoint

```
**/checkpoint** — Save engagement state to the persistence folder

**What it produces:** A `checkpoint.yaml` committed to the persistence folder
**Time:** Instant
**Input needed:** None (operates on current in-flight engagement)

**How to invoke:**
  /checkpoint
  "save state" / "checkpoint now"

  Auto-fires (silent, no user action) at:
    - Checkpoint A confirmation (engagement brief)
    - Checkpoint B confirmation (interpretation)
    - Checkpoint C confirmation (scenario direction)
    - Checkpoint D confirmation (narrative frame)
    - Every section approval in Phase 6b
    - Just before Phase 7 QA

**What happens:**
  1. Captures current state (phase, section in progress, all confirmed
     outputs so far, accumulated selection_log) into checkpoint.yaml
  2. Commits to engagements/<slug>/checkpoint.yaml via Google Drive (Claude.ai connector)
  3. Surfaces "Checkpoint saved at Phase X — Y. Resume with /resume <slug>."

**When NOT to use it:** No reason to skip — auto-checkpoint runs at every
phase boundary regardless. Manual /checkpoint is for ad-hoc save points
between automatic ones.

**Example:**
  > /checkpoint
  → "Checkpoint saved at Phase 6b — Findings (in progress).
     Resume in any session with /resume pharmacy-fy26."
```

---

## Tier 2 Detail — /resume

```
**/resume** — Restore an in-progress engagement from its checkpoint

**What it produces:** Restored conversation context + resumed phase
**Time:** ~30 seconds
**Input needed:** Engagement slug (or none — bare /resume lists checkpoints)

**How to invoke:**
  /resume                  # lists all available checkpoints with phase + age
  /resume <slug>           # resume specific engagement

**What happens:**
  1. Reads engagements/<slug>/checkpoint.yaml from persistence folder
  2. Validates freshness — warns if checkpoint > 30 days old or if config
     has changed since checkpoint was saved
  3. Restores engagement brief, narrative frame, sections built so far,
     and the accumulated selection_log
  4. Resumes from the saved phase — does not re-run completed checkpoints

**When NOT to use it:** If the engagement is already closed, /resume
surfaces the closed status and offers next-cycle, deliverables, or
/ledger update options instead.

**Example:**
  > /resume pharmacy-fy26
  → "Resuming pharmacy-fy26 from Phase 6b — Findings (in progress).
     Engagement brief: [...]. Built so far: Cover, Market Context.
     Continue from Findings?"
```

---

## Tier 2 Detail — /ledger

```
**/ledger** — Read prior-cycle outcomes; update outcome windows

**What it produces:** Chat output (read modes) or single ledger commit (update)
**Time:** Instant (read) / 2-5 min (update walk)
**Input needed:** None (read modes); engagement slug + outcome data (update)

**How to invoke:**
  /ledger                       # summary of all closed engagements, grouped by scope
  /ledger <scope>               # full history for one scope_slug, with drift trajectory
  /ledger update <slug>         # walk the 4 outcome windows (30d, 90d, 180d, 1y),
                                # accept free text, commit only the ledger file

**What happens:**
  1. Read modes: google_drive_fetch on ledger/outcome-history.yaml,
     filter and format
  2. Update mode: walks outcome windows in order, accepts user input,
     writes back via google_drive_create_file (single-file write, message:
     "ledger: <slug> outcome <window>d filled")

**When NOT to use it:** If you want to start a new cycle (not update an
existing closed one), use the normal track entry — Phase 0 surfaces
prior-cycle ledger context automatically.

**Example:**
  > /ledger pharmacy
  → "Scope: pharmacy — 3 closed engagements
     pharmacy-fy26 (closed 2026-04-29, effective 2026-05-01)
       Recommended: $4.0M Scenario B  Adopted: $3.6M Scenario B + 6mo phased
       Outcomes: 30d ☐  90d ☐  180d ☐  1y ☐
     ..."
```

---

## Tier 2 Detail — /brand-kit init

```
**/brand-kit init <org-slug>** — Scaffold a per-org brand kit from _default

**What it produces:** A new branding/<org-slug>/ folder in the persistence folder
                      with placeholder palette + logo instructions + footnotes
**Time:** ~30 seconds (scaffold + commit)
**Input needed:** org-slug (kebab-case identifier for the org)

**How to invoke:**
  /brand-kit init acme
  /brand-kit init <client-org-slug>

**What happens:**
  1. Verifies google-drive backend (aborts in paste-mode)
  2. Auto-seeds branding/_default/ in repo from bundle if not present
  3. Verifies branding/<org-slug>/ does NOT already exist (aborts if it does)
  4. Scaffolds divergence-points only:
       - theme/palette.json (placeholder with override semantics comment)
       - theme/logo-placeholder.txt (instructions for 5 logo variants)
       - footnotes.yaml (placeholder showing schema)
       - _README.md (override pattern explanation)
  5. Commits as: `branding: init <org-slug> kit`
  6. Surfaces edit instructions to user

**When NOT to use it:** When the org already has a kit (use direct file edit
instead). When you only want to override one slide master across all orgs (edit
branding/_default/masters/<file>.js directly — but be aware the bundled _default
will diverge from your repo _default).

**Example:**
  > /brand-kit init acme
  → "Brand kit branding/acme/ scaffolded. Edit theme/palette.json + drop
     logo files to customize. To override a slide master, copy the file from
     _default/masters/ to acme/masters/ and edit. Engagements that set
     engagement.config.brand.org_slug: acme will use this kit."
```

---

## Tier 2 Detail — /cba save

```
**/cba save <agreement-id>** — Manually save a user-CBA to the library

**What it produces:** A cba-library/<agreement-id-slug>.yaml file + updated
                      cba-library/_index.yaml mapping in the persistence folder
**Time:** ~15 seconds (slug derivation + commit)
**Input needed:** Agreement-id, OR none (re-uses the current engagement's
                  active user-CBA if one is loaded)

**How to invoke:**
  /cba save                                       # uses active engagement's CBA
  /cba save tuac-501-acme-qc-retail-2024-2028   # explicit slug

**What happens:**
  1. Verifies a user-CBA is loaded in the active engagement
     (prompts upload via /intake or extraction path if not)
  2. Confirms extracted fields with user (re-prompts the role list to map
     into _index.yaml `applies_to`)
  3. Idempotency check: if file exists, prompts to overwrite or keep
  4. Cross-check vs Market MCP `get_cba_wage_scale` (>5% delta surfaces warning)
  5. Auto-runs disallowed-fields scan
  6. Commits via close-time close-time write sequence (or immediately if invoked
     standalone outside an active engagement)

**When NOT to use it:** When the auto-save path already saved (post-extraction
auto-save runs at close-time by default). Use this only to force a save mid-
engagement or to save a CBA loaded in a non-engagement context.

**Example:**
  > /cba save
  → "Saving user-CBA `TUAC 501 Acme QC retail 2024-2028` to library.
     Mapped to roles: meat-cutter@QC, butcher@QC, meat-cutter-class-a@QC.
     Cross-check vs Market MCP: top-rate delta 1.8% (within tolerance).
     Saved on close commit."
```

---

## Tier 2 Detail — /glossary promote

```
**/glossary promote** — Review and merge engagement-level FR-CA additions

**What it produces:** A canonical vocabulary/fr-ca-glossary.yaml in the
                      persistence folder (created from bundled seed if first run)
                      + updated vocabulary/_rejected.yaml for declined terms
**Time:** ~30 sec to 5 min depending on candidate count (interactive review)
**Input needed:** None (walks all engagements/*/fr-ca-additions.yaml files)

**How to invoke:**
  /glossary promote

**What happens:**
  1. Verifies google-drive backend (aborts in paste-mode)
  2. Discovers candidates: lists every fr-ca-additions.yaml across engagements
  3. Aggregates by english term, surfaces conflicts (multiple FR-CA candidates)
  4. Walks each candidate one at a time:
       - Approve  → adds to vocabulary/fr-ca-glossary.yaml
       - Edit     → prompts revised FR-CA, then adds
       - Reject   → logs to vocabulary/_rejected.yaml (won't re-prompt)
       - Skip     → leaves for next promotion run
  5. Single close-time write sequence at end: `vocabulary: promote N terms (<engagements>)`
  6. Marks each promoted term in source fr-ca-additions.yaml with promoted_at

**When NOT to use it:** When working on an active engagement (run between
engagements instead — promoting mid-engagement causes a context-switch). When
all additions are already promoted (the command surfaces "No new candidates"
and exits).

**Example:**
  > /glossary promote
  → "Found 14 candidates across 3 engagements. Walking each one..."
  → "Candidate 1 of 14: 'Total rewards committee' → 'Comité de la rémunération
     globale' (pharmacy-fy26). Approve, edit, reject, or skip?"
  → ... [interactive] ...
  → "Promoted 11, rejected 2, skipped 1. Committing as `vocabulary: promote
     11 terms (pharmacy-fy26, atlantic-retail-fy26, qc-pharmacy-fy26)`."
```

---

## Tier 2 Detail — /help

```
**/help** — Show this menu

**What it produces:** Compact list (default) or per-command detail
**Time:** Instant

**How to invoke:**
  /help
  /menu
  /commands
  /help [command-name]

**Example:**
  > /help intake
  → [Shows the detail block for /intake]
```

---

## Anti-Patterns

- **Do not produce a deck from /help.** It's a meta command. The output is always plain chat text.
- **Do not list internal phases (Phase 0-7) at Tier 1.** Phases are implementation detail. Users invoke tracks and commands; phases happen inside.
- **Do not auto-suggest a follow-up command after /help.** The user can read and choose.
- **Do not extend Tier 1 beyond what fits one screen.** Adding a sixth slash command means restructuring, not appending. The constraint is intentional.
- **Do not duplicate detail across tiers.** Tier 1 is one line per command; Tier 2 is the depth. Don't put example invocations in Tier 1.
- **Do not run /help mid-engagement and lose engagement state.** /help is a side query. After /help responds, the active engagement (if any) resumes.

---

## Edge Cases

**User types `/help` with a typo'd command name** (`/help quikbnch`). Match by closest prefix or substring. If unambiguous, proceed:

> "Showing /help for **/quickbench**:
> ..."

If genuinely ambiguous, list candidates:

> "Did you mean /quickbench or /quickstart? (No /quickstart exists, but /quickbench does — try `/help quickbench`.)"

**User types `/help` for a command that doesn't exist.** Surface available commands and offer the closest match:

> "/banana isn't a command. Closest match: /quickbench? Or type /help to see all commands."

**User types `/help` mid-engagement.** Output the help and end the turn. Do not lose engagement state. The user's next message resumes the engagement.

---

## Output Discipline

- All output is chat text. **/help is the only command that does not produce an artifact** — it's a meta-query about the skill itself, not a deliverable.
- Tier 1 fits one mobile screen.
- Tier 2 detail blocks are ~25-35 lines each.
- No emojis. Use bold/italic markdown sparingly for scanability.
- After /help responds, end the turn cleanly. No follow-up question.
