<!-- Source: telos-machina/.claude/rules/dispatch-prompt-anti-patterns.md @ commit af3787cb91fa793e6fcacad7fd8a7b438d9b62ee. Copied verbatim 2026-05-07. -->
# Dispatch Prompt Anti-Patterns

Avoid these when constructing dispatch prompts for subagent workers.

| # | Anti-pattern | Rule | Why |
|---|-------------|------|-----|
| 1 | ALL-CAPS emphasis | Use imperative mood without capitals. "Write the output file before terminating" — not "CRITICAL: You MUST write the output file." | Anthropic best practices: aggressive language causes overtriggering in Claude 4.x |
| 2 | Conditional constraints | Express always-active rules unconditionally. "Tag every claim with a confidence level" — not "If a claim has only one source, tag it UNVERIFIED." | AgentIF (arXiv:2505.16944): 30%+ failure rate on conditional constraint checking |
| 3 | Instruction overload | Cap at 25 instructions for Sonnet workers, 40 for Opus. Exemplars do not count. | IFScale (arXiv:2507.11538): P(all correct) = P(single)^n — 25 instructions at 95% each = 28% all-correct |
| 4 | Format rules competing with task | Specify output format in `<output>` and `<example>` sections — not interleaved with steps in `<task>`. | Deco-G (arXiv:2510.03595): decoupling format from task improved accuracy 1-6% on 7-8B models. Tam et al. (arXiv:2408.02442): format enforcement degrades accuracy 8-64pp depending on model/task |
| 5 | Critical constraints in the middle | Place the most important constraint in `<termination>` at the end — not buried in `<constraints>`. | MOSAIC (arXiv:2601.18554): Claude shows higher compliance for constraints near the end |
| 6 | Unidirectional prohibitions | Always pair a prohibition with the preferred alternative. "Use tables for comparisons instead of inline prose" — not just "Don't use inline prose." | Without an alternative, the model substitutes the next closest behavior, which may be equally wrong. |
| 7 | Bare rules without rationale | For non-obvious rules, include a one-sentence reason so the model generalizes correctly to edge cases. | Without a reason, the model applies literally in the written case and fails to generalize to adjacent cases. |
| 8 | Tool overload | Provide 3-5 core tools per worker. | Vercel case study: 16 → 2 tools = 80% → 100% success rate, 3.5x faster |
