# Agentic Workflow Principles

Applies to all agents designing, building, or debugging agentic workflows — TM pipelines and client-facing systems.

## Ten Failure Modes

When a pipeline produces bad output, diagnose which mode is active before attempting fixes.

| # | Mode | Symptom | Diagnostic |
|---|------|---------|-----------|
| 1 | **Context degradation** | Quality drops over long sessions | Did quality decline gradually? Is context near capacity? |
| 2 | **Specification drift** | Agent forgets requirements mid-task | Does output match the spec or a mutation of it? |
| 3 | **Sycophantic confirmation** | Agent builds on incorrect input without questioning | Was input data verified before consumption? |
| 4 | **Tool selection errors** | Agent picks the wrong tool | Are tool descriptions clear, non-overlapping, and few? |
| 5 | **Cascading failure** | One agent's error propagates uncorrected | Are there correction loops between agents? |
| 6 | **Silent failure** | Output looks plausible but is wrong | Is there a functional correctness check, not just semantic? |
| 7 | **Reasoning-action mismatch** | Stated reasoning and actual behavior diverge | Does the explanation match what the agent actually did? |
| 8 | **Information withholding** | Correct information fails to reach downstream agents | Did the upstream agent's output include all relevant findings? |
| 9 | **Incorrect verification** | A check that is itself wrong produces false confidence | Did the verification step actually test what it claims? |
| 10 | **Premature termination** | Agent stops before objectives are complete | Did the agent complete all deliverables against the spec? |

Modes 7-10 derived from the MAST empirical taxonomy (arXiv 2503.13657) — 14 failure modes across 1,642 execution traces in 7 multi-agent frameworks. Modes 1-6 are from TM operational experience.

Silent failure (#6) and incorrect verification (#9) are the most dangerous — both look like success. Treat plausible output with the same suspicion as obviously broken output until verified.

## Ten Anti-Patterns

1. **Reading fluency as correctness** — accepting AI output because it reads well, without verifying accuracy
2. **Vague specification** — leaving gaps for the agent to fill; agents do not reliably reproduce intent from blanks
3. **Feeding unverified data** — agents sycophantically confirm bad data and build incorrect systems on top of it
4. **Misscoping for the harness** — large task for single-threaded agent, or vague task for planner without subtask definitions
5. **Accepting semantic correctness** — evaluating whether output "sounds right" instead of whether it "is right"
6. **Ignoring silent failure** — assuming plausible-looking output is correct output
7. **Ignoring token economics** — running large agent processes without prototyping cost assumptions first
8. **Over-tooling** — 10+ tools or verbose descriptions degrade tool selection accuracy sharply
9. **No correction loops** — multi-agent chains with no mechanism for downstream agents to catch upstream errors
10. **Agent washing** — applying multi-agent systems where simpler automation suffices; if steps are known in advance and require no autonomous decisions, use automation

Full reference (decision heuristics, verification standards, workflow advisor triggers): `internal-ops-bureau/knowledge/agentic-workflow-reference.md`
