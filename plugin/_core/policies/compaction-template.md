# Compaction Template

Loaded on-demand during `/compact`. See CLAUDE.md § Compaction Policy for thresholds.

Produce a comprehensive metalanguage summary — aim for 2000–4000 words. The post-compaction instance has no memory except this summary and recovery.md; everything not preserved here is permanently lost. Err on the side of too much detail.

Use structured notation: group by conversation phase, label decisions, tag file paths, and annotate tool call patterns. The summary is a technical session transcript in compressed form — not a brief paragraph.

## Must preserve (high fidelity)

1. **Opening intent** — Quote the primary task/goal from the first user message verbatim. Do not paraphrase. The opening intent frames everything.
2. **Conversation arc** — Describe each phase of work in order: what was attempted, what succeeded, what failed, and what transitioned to the next phase. Use phase labels (discovery, research, implementation, review, debugging).
3. **Every decision and rationale** — "Chose X over Y because Z." Losing decisions forces re-deliberation, the most expensive post-compaction failure. Emit as a top-level `decisions:` array with metalanguage entries: `{decision, over, why}`. The session-wide list captures load-bearing choices (typically 3-8); per-phase decisions under `arc` capture local choices. If alternatives weren't actually weighed, write `over: []` and add `decision_alternatives` to `dropped_categories` — never fabricate alternatives.
4. **All file paths** read, written, edited, or created — with line ranges when available. Group by operation type. File paths are the fastest way to re-orient.
5. **All errors, failures, and blocked approaches** — Include the error text or key excerpt. Repeating failed approaches is the most common post-compaction failure mode.
6. **All URLs and hyperlinks** referenced during the session — research sources, documentation links, API endpoints. These are evidence the next instance cannot re-discover without re-searching.
7. **Code changes** — For each edited file, describe what was changed and why (not full diffs, but enough to understand the nature: "added X function", "fixed Y bug by changing Z").
8. **Bash commands** that reveal what was tested, deployed, or debugged — especially commands with non-obvious flags or that produced important output.
9. **Tool call summary** — Count of tool calls by type (Read: N, Edit: N, Bash: N, Agent: N, etc.). Helps the next instance gauge session complexity.
10. **Active issue number** (format: 0NNN-PREFIX-slug) if one was referenced. Issues are the primary work-tracking unit.
11. **Plan file or spec file path** being followed. Plan files are the resumability mechanism for multi-phase pipelines.
12. **Pending work items and explicit next steps** — Quote the user's words when they stated what to do next.
13. **Founder name** (Tim or David) and any stated preferences for this session.
14. **Pipeline state** if a skill was running (/research, /specify, /build — phase name, status, output directory).
15. **Sub-goals** discovered mid-session that were not in the original request.

## Structure template

```
## Session Summary

**Founder**: [name] | **Branch**: [branch] | **Issue**: [0NNN-PREFIX-slug or none]
**Primary goal**: "[quoted from first user message]"

### Decisions (session-wide load-bearing)
- decision: [terse], over: [alternatives], why: [one-line rationale]
- decision: [terse], over: [], why: [why no alternatives were weighed]

### Phase 1: [label] — [one-line summary]
- [what happened, decisions made, files touched]
- Decision: chose X over Y because Z
- Error: [error text] → resolved by [fix] / unresolved

### Phase 2: [label] — [one-line summary]
...

### Files
- Read: [paths]
- Modified: [paths with change descriptions]
- Created: [paths]

### URLs Referenced
- [url] — [what it was used for]

### Tool Summary
Read: N, Edit: N, Write: N, Bash: N, Agent: N, Grep: N, Glob: N

### Pending
- [next action items, quoted where possible]

### Pipeline State
- Skill: [name], Phase: [phase], Plan: [path], Status: [status]
```
