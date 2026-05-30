# Review Dispatch Budget

When dispatching reviewer subagents (e.g. Phase 3 review panel in `/build`, code review of large surfaces, multi-perspective audits), each agent has a hard tool-call budget — typically 50–60 calls before truncation. Burning the budget on read-only exploration without producing output wastes the entire dispatch.

The anchor incident: a Phase 3 review panel for spacetime-4x dispatched 4 reviewers in parallel; only 1 returned both an output file and a summary. The other 3 each made 40–60 Read/Grep calls inside their context budget without ever invoking Write. The orchestrator had to redo their work inline, paying for both the failed dispatch and the inline reproduction.

This rule defines how to scope reviewer dispatches so the budget produces value.

## Musts

- **Cap the file set explicitly.** Reviewer prompts must list the files to read, not say "review the whole codebase" or "review everything in `src/`." A reviewer with 50 tool calls cannot meaningfully cover an open-ended surface; concrete file paths force scope discipline upfront.
- **Demand incremental writes.** The prompt must instruct the reviewer to write findings to its output file as soon as it has each finding — not all at the end. Pattern: "After every finding, append it to `[output_path]`. Do not batch. Stop when budget is half-spent and write whatever you have."
- **Specify the output path in the prompt.** Each reviewer writes to its own unique file (per `.claude/rules/council-output-pattern.md`). The prompt must include the absolute path so there's no ambiguity.
- **Require a dual-return.** The prompt must say: "Write your full review to `[path]` AND return the same review as your final message." Belt-and-braces against the file-write failing silently or the agent timing out before flushing.
- **Verify after dispatch.** When all reviewers return, check disk for each expected output file before synthesizing. Missing file → use the agent's return message; missing both → escalate or redo inline.

## Must-Nots

- **Never dispatch a reviewer with a prompt longer than ~60 lines.** Above that, the agent spends budget re-reading the prompt instead of doing the work. Strip the prompt to the file list, the output path, the structure, and the severity rubric.
- **Never tell a reviewer to "be thorough" or "leave no stone unturned."** That language burns budget on coverage anxiety. Tell them what to look for and let them stop when they've found enough.
- **Never dispatch more than 4 reviewers in parallel without a coverage matrix.** With 5+ reviewers covering an unscoped surface, the overlap is high and the budget is wasted on duplicated reads.
- **Never let a reviewer dictate its own scope.** "Review the codebase for security issues" is open-ended; "Review `auth.ts`, `session.ts`, and `middleware.ts` for the OWASP top 10" is bounded. The orchestrator owns scope.

## Preferences

- **Prefer 3 well-scoped reviewers over 6 broad ones.** Three reviewers each given 5-10 specific files outperform six reviewers each told "review everything for X."
- **Prefer the file list be derived from the spec or the diff**, not "every file in the repo." Reviewers reviewing a build should see only the files that build produced.
- **Prefer the orchestrator pre-listing the questions** the reviewer must answer. "Does X hold?" "Is Y bounded?" "Where is Z verified?" — explicit questions cap the scope of "thinking" the agent has to do.
- **Prefer to run reviewers inline** (orchestrator does the review directly) when the surface is small (<10 files) or when the dispatch overhead would exceed the inline cost. Subagents are for parallelism on independent slices, not for "I don't want to read this myself."

## Escalation Triggers

- **A reviewer returns no output file AND no summary.** Don't redispatch the same prompt — first investigate why (budget exhausted? prompt too vague?). Redispatch only with a tighter scope.
- **2+ of N reviewers fail to produce output.** That's a prompt-pattern failure, not bad luck. Stop the panel, fix the dispatch protocol, then resume.
- **Reviewer claims it found nothing in a surface that's known to have issues.** That's a sign the budget ran out before they got to the substantive part. Redispatch with the specific files the issue lives in.

## Dispatch Prompt Template

```
You are reviewing [N] specific files for [aspect].

## Files to read (in this order)
- path/to/a.ts
- path/to/b.ts
...

## Write your findings to: [absolute/path/to/output.md]

Append to that file as you find each issue. Do not batch.

## Structure each finding as:
- File:line
- Severity (CRITICAL | HIGH | MEDIUM | LOW)
- One-line description
- Confidence (VERIFIED | LIKELY | SUSPECTED)

## Stop conditions
- You've reviewed all listed files, OR
- You're at half your tool-call budget — write a partial report and stop

## Final action
Return your full review as your final message AS WELL AS writing it to the file.
```

## Why this overrides "thoroughness"

A reviewer that returned 3 verified findings is more useful than one that returned 0 findings after 50 tool calls of reading. Truncated work is worse than scoped work. The dispatch budget is a hard constraint; treat it like compute, not like time.
