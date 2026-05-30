# Rule Authoring

When writing CLAUDE.md content, `.claude/rules/` directives, dispatch prompts, or specifications:

1. Every line must pass: "would removing this cause the agent to make mistakes?" If no, cut it.
2. Categorize rules as: musts, must-nots, preferences, or escalation triggers. Don't flatten into one list.
3. Include a one-line WHY for non-obvious rules. Claude generalizes better from reasoning than from bare directives.
4. Write rules from anticipated failure modes — "what would a smart agent do wrong without this?" — not from abstract principles.
5. Define verifiable done criteria before writing any rule or spec. If you can't state correctness, the rule isn't ready.
6. Make every rule self-contained. If it depends on unstated context, it will fail silently.
7. Encode intent (goals + tradeoffs + decision boundaries), not just behaviors. Rules without intent get followed literally and violated in spirit.
8. For async/long-running work: encode every constraint you'd normally enforce by watching. The governance doc replaces real-time oversight.
9. Workers get minimum viable context — broad org rules stay in the orchestrator, not in worker prompts.
10. Persist durable rules in files, not just in context. Context compaction is lossy.

Full reference with NBJ citations: `policy-bureau/knowledge/rules-for-writing-rules.md`
