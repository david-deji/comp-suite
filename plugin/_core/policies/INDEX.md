# _core/policies/ — INDEX

> Operating disciplines for comp-suite, ported from the TM monorepo `.claude/rules/` and pinned
> independently. This is the plugin-shipped index: it lists only the **operative** policies. (The
> dev repo additionally keeps four raw TM baselines — `skill-routing.md`, `session-protocol.md`,
> `verify-upstream-before-specify.md`, `writing-standards.md` — for quarterly TM-drift review;
> those are review scaffolding, superseded by the adapted versions below, and are not shipped.)
>
> **Activation model**: lean. Primitives reference specific policies on demand
> (e.g., `$ASSET_ROOT/_core/primitives/budget-check.md` cites `cost-discipline.md`). The
> orchestrator does NOT glob-load this directory. Discovery is by reading this index.

| Policy file | Status | When it applies |
|---|---|---|
| `agentic-workflow-principles.md` | verbatim | Council dispatch, mode dispatch, engagement-state drift diagnosis (10 failure modes) |
| `assumption-verification.md` | verbatim+footer | Cycle-recurring engagements; `/comp resume` after long gap; before debugging deployed integrations |
| `compaction-template.md` | verbatim | Long advisor sessions (council loops, multi-mode handoffs) approaching context limits |
| `cost-discipline.md` | verbatim | All paid-API dispatch (Perplexity, market-data); referenced by `$ASSET_ROOT/_core/primitives/budget-check.md` |
| `dotenv-read-authorization.md` | verbatim | Any `.env` / `.envrc` read; companion to `secret-handling-discipline.md` |
| `multi-terminal-git-safety.md` | verbatim+footer | Concurrent `/comp` sessions on the same engagement; branch-aware push discipline |
| `review-dispatch-budget.md` | verbatim | Council dispatch sizing; multi-perspective audits inside any mode |
| `rule-authoring.md` | verbatim | Meta-rule for writing future comp-suite-specific policies |
| `secret-handling-discipline.md` | verbatim+footer | Any shell consumption of fetched secrets (MCP wrappers, scripts) |
| `skill-routing-comp.md` | adapted | `$ASSET_ROOT/_core/primitives/mode-dispatcher.md` resolution; named-Opus-trigger heuristics for /comp tasks |
| `session-protocol-comp.md` | adapted | `/comp` session start, `/comp resume`, `/comp doctor`; cost-log surfacing, engagement state checks |
| `verify-engagement-state-before-mode.md` | adapted | Before any mode dispatch in a cycle-recurring engagement; before `/comp resume` finalizes mode selection |
| `writing-standards-comp.md` | adapted | Branded-text writes (deliverables/, mode/) — integrates `$ASSET_ROOT/_modes/advisor/references/fr-ca-glossary.md` + `$ASSET_ROOT/_core/hooks/never-list.txt` + anti-slop hook |
