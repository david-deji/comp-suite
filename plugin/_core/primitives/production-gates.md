# Production Gates Primitive

Glue reference describing how production-gate hooks are scoped, when they fire, and how modes opt in or out. The hook scripts themselves live at `$ASSET_ROOT/_core/hooks/{anti-slop.sh, french-accent-check.sh, fact-check.sh}` with shared helpers in `lib.sh`. This file is the contract — a v2-only artifact (no v1 equivalent).

## Hook inventory

| Hook | Trigger | What it checks | Default exit |
|---|---|---|---|
| `anti-slop.sh` | `PostToolUse:Write` on branded-text paths | never-list match (corporate slop terms — port of v1 `production-and-qa.md` slop list) | `1` (warn) for first 30 days; promote to `2` (block) after <5% false-positive rate observed |
| `french-accent-check.sh` | `PostToolUse:Write` on branded-text paths tagged FR | accent regex (port of v1 FR rule) | `1` (warn) |
| `fact-check.sh` | `Stop` | every claim in deliverables this session has source URL or file:line cite | `1` (warn) |

The wiring lives in `$ASSET_ROOT/.claude/settings.json` (which Claude Code reads at session start). This file describes the **logic** that wiring depends on.

## Path scoping (lib.sh:is_branded_text)

Each Write hook fires at the CC harness level on every Write, but immediately bails (exit 0 silent) if the path is not branded text. Path scoping is the primary defense against hook flooding on internal state writes.

### Branded-text patterns (hooks RUN)

```
$STATE_ROOT/_orgs/*/engagements/*/deliverables/**/*.md
$STATE_ROOT/_orgs/*/engagements/*/<mode>/**/*.md   # for each mode discovered under $ASSET_ROOT/_modes/*/
```

The mode list is **dynamic** — discovered at runtime via glob `$ASSET_ROOT/_modes/*/`. Adding a 5th mode does NOT require editing any hook script (B3 fix from Run 2; verified by hooks/lib.sh:is_branded_text using a `for mode_name in "$modes_dir"/*/` loop).

### Non-branded paths (hooks SKIP)

| Path pattern | Reason |
|---|---|
| `*.yaml`, `*.json`, `*.jsonl` | Internal state, manifests, schemas, cost log |
| `$STATE_ROOT/_orgs/*/engagements/*/council/**` | Per-thinker scratch — deliberation, not deliverable |
| `$STATE_ROOT/_orgs/*/engagements/*/checkpoint.yaml` | Mid-flight session state |
| `$STATE_ROOT/_orgs/*/engagements/*/engagement-state.yaml` | Transient session state |
| `$STATE_ROOT/_orgs/*/engagements/*/close-progress.yaml` | Mid-close checkpoint |
| `$STATE_ROOT/_orgs/*/engagements/*/close-validation-errors.md` | Transient validation report |
| `$STATE_ROOT/_orgs/*/engagements/*/cost-log.jsonl` | Append-only spend log |
| `$STATE_ROOT/ledger/**` | Global outcome ledger |
| `$ASSET_ROOT/tests/**`, `$ASSET_ROOT/_core/**`, `$ASSET_ROOT/_modes/**`, `$ASSET_ROOT/.claude/**`, `$ASSET_ROOT/.build-state/**` | Source code paths |

Verified by test scenario 12 (`hook-path-scoping`).

## Language tag resolution (french-accent-check)

Resolution order in `lib.sh:read_lang_tag`:

1. **Filename suffix:** `*-fr.md`, `*.fr.md`, `*-fr-ca.md`, `*.fr-ca.md`, `*-en.md`, `*.en.md`
2. **Frontmatter:** first 20 lines for `^language:\s*[a-z-]+`
3. **Mode default:** `mode.yaml.default_language` if `COMP_ACTIVE_MODE` is set

If no tag resolved → assume EN, skip accent check.

## First-30-day warn policy

For the first 30 days after each hook lands, default exit on issue is `1` (warn — Write proceeds, stderr surfaces). Promote to `2` (block — Write rolled back) only after observing <5% false-positive rate on real engagement deliverables.

This policy is **per `.claude/rules/cost-discipline.md`** in TM context — applied here as v2 hardening. Never-list false-positive heat is real (e.g., the term `placeholder` is in `never-list.txt:52` per Run 2 finding L2 — hits "this is a placeholder for legal review" in legitimate drafts). Promotion threshold prevents tuning for false positives by punishing real writes.

## Mode opt-in / opt-out

Each mode's `mode.yaml.hooks_enabled` lists hooks the mode subscribes to. Modes can also opt-out per-hook in `hooks.yaml`:

```yaml
opt_in:
  - anti-slop
  - french-accent-check
opt_out: []
```

Hooks check `COMP_ACTIVE_MODE` env var (set by orchestrator before tool dispatch) and call `lib.sh:mode_opted_in <hook>`. If the mode hasn't opted in, the hook silently bails exit 0.

If `COMP_ACTIVE_MODE` is unset (dev/test write), the default is to run all hooks (per lib.sh:mode_opted_in default-on policy).

## Hook script contracts

Each script reads CC's hook JSON payload from stdin via `lib.sh:payload_path`. Standard payload: `tool_input.file_path` for PostToolUse:Write. Standard exit codes:

- `0` — pass silently (default for non-branded-text or no issue)
- `1` — warn (stderr visible to operator, Write proceeds — first 30 days)
- `2` — block (Write rolled back, stderr surfaced — post-tuning)

Scripts MUST NOT read or modify state files; they read the just-written deliverable file from `tool_input.file_path` and exit.

## Why this is a glue file (not a v1 port)

v1's `production-and-qa.md` mixed slop-term data (now in `never-list.txt`) with hook configuration (now in `settings.json`) with operator guidance (now in this file). v2 separates them:

| v1 concern | v2 location |
|---|---|
| Slop term list (data) | `$ASSET_ROOT/_core/hooks/never-list.txt` |
| Accent regex (data) | inline in `french-accent-check.sh` |
| Hook wiring (config) | `$ASSET_ROOT/.claude/settings.json` |
| Operator policy (this file) | `_core/primitives/production-gates.md` |
| Path scoping logic | `$ASSET_ROOT/_core/hooks/lib.sh:is_branded_text` |

The split is explicit per spec § 4.1 ("v1 production-and-qa.md → split: hooks → _core/hooks/*.sh; reference → _core/primitives/production-gates.md").

## Acceptance

- Test scenario 12 (`hook-path-scoping`) — verifies state/yaml writes do NOT fire branded-text hooks; deliverable .md DOES.
- Test scenario 13 (`mcp-server-unavailable`) — verifies hook flooding does NOT happen when MCP fails.
