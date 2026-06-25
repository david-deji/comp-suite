# Slash-Command Grammar — compensation-advisor

Single source of truth for slash-command syntax, precedence, aliases, and
dispatch rules. SKILL.md and `intent-router.md` cross-reference this file;
do not duplicate the grammar elsewhere.

## Grammar table

| Slash command | Aliases | Args | NL triggers | Dispatch protocol |
|---|---|---|---|---|
| `/init` | "init", "initialize" | optional `<org-slug>` | "set up config", "configure" | `init-mode-protocol.md` |
| `/init pay-equity-qc` | (none — exact only) | (none) | "pay equity", "équité salariale", "exercice d'équité" | `pay-equity-qc-protocol.md` |
| `/update` | "/init update" | (paste config required) | "update mode", "update my config" | `update-mode-protocol.md` |
| `/intake` | "/intake form" | (none) | "intake form", "build me an intake" | `intake-mode-protocol.md` |
| `/quickbench` | "/qb" | optional `<role>@<province>` | "quick market check", "quickbench" | `quickbench-mode-protocol.md` |
| `/council` | (none) | optional topic | "run a council on", "deliberate on" | `council-command.md` + `council-mode.md` |
| `/checkpoint` | (none) | (none) | "save state", "checkpoint" | `persistence-and-ledger.md` § /checkpoint |
| `/resume` | (none) | optional `<slug>` | "resume" | `persistence-and-ledger.md` § /resume |
| `/ledger` | (none) | optional `<scope>`, optional `update <slug>` | "outcome history", "ledger" | `persistence-and-ledger.md` § /ledger |
| `/brand-kit init` | "/brand init" | required `<org-slug>` | "create brand kit for" | `brand-kit-protocol.md` |
| `/cba save` | (none) | required `<agreement-id>` | "save this CBA" | `library-resolution.md` + `survey-house-protocol.md` |
| `/glossary promote` | (none) | (none) | "promote glossary terms" | `fr-ca-glossary.md` § 8.5 |
| `/help` | "/menu", "/commands" | optional `<command>` | "help", "what can you do" | `help-mode-protocol.md` |
| `/close-cycle` | (none) | required `<cycle-slug>` | "close cycle" | `master-yaml-ops.md` |
| `/reopen-cycle` | (none) | required `<cycle-slug>` | "reopen cycle" | `master-yaml-ops.md` |
| `/switch-cycle` | (none) | required `<cycle-slug>` | "switch to cycle", "make primary" | `master-yaml-ops.md` |

## Invocation prefixes (no-op — strip and re-classify)

`/compensation-advisor`, `/comp-advisor`, `/comp` — these prefixes invoke the
skill but do NOT classify. Strip them and re-classify the remainder against
the table above (or fall through to `intent-router.md`).

Example: `/compensation-advisor prepare the initial deck for acme ontario fy27`
→ classify on `prepare the initial deck for acme ontario fy27` (which then
matches the pre-classification disambiguation rule in `intent-router.md`).

## Precedence rules

1. **Slash command in message** → routes per the table above. Slash > NL
   pattern always.
2. **Exception**: `/help` never overrides an in-progress engagement. `/help`
   mid-Phase-6b is treated as a help query within the current engagement, not
   a full restart.
3. **`/init pay-equity-qc`** is matched as an exact slash + arg pair, NOT as
   `/init` with subsequent args. The exact pattern routes to
   `pay-equity-qc-protocol.md` directly, bypassing the regular
   `init-mode-protocol.md` flow.
4. **Multi-slash messages** (e.g., `/init pharmacy-fy27 then /quickbench`) —
   process the first slash; surface a "I see you also referenced /quickbench
   — should I run that after /init completes?" prompt before the second.

## Argument validation

Per-command argument schemas live in each command's protocol file. Slug args
universally match `^[a-z][a-z0-9-]{1,40}$`. Cycle slugs additionally encode
`<line>-<region>-<fiscal>` convention (e.g., `pharmacy-fy26`,
`atlantic-retail-may-fy26`).
