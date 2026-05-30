<!-- Source: telos-machina/.claude/rules/council-output-pattern.md @ commit af3787cb91fa793e6fcacad7fd8a7b438d9b62ee. Copied verbatim 2026-05-07. -->
# Council Output Pattern

When dispatching parallel thinker agents, each thinker must write to its own uniquely named file. The `Write` tool overwrites entire files — parallel writes clobber each other.

## Pattern

**1. Per-thinker unique files.** Assign each thinker a unique path in the dispatch prompt:
```
[output-dir]/[prefix]-council-[perspective-slug].md
```

**2. Dual-return.** Each thinker's prompt must include: "Write your complete analysis to [your unique file path] using the Write tool. Also return your complete analysis as your final message." If the Write tool fails silently, the return message has the content.

**3. Orchestrator assembles.** After all thinkers complete: check disk for each output file; if missing, use the thinker's return message content; assemble into the final council file under `### [Perspective Name]` headings; write the synthesis section. Assembly is complete when: every thinker has a section, the `## Synthesis` section exists, and no placeholder text remains.

**4. Intermediate files**: delete after assembly unless the founder may need to audit individual thinker reasoning separately.

## Anti-pattern

Do not instruct thinkers to write to a shared file or a placeholder section within a shared file. `Write` replaces the entire file; `Edit` fails when another agent has modified the file since read.
