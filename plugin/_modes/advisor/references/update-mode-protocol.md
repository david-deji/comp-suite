# Update Mode Protocol

Update mode is a guided refresh of an existing engagement-config YAML block. It is the maintenance counterpart to Init — same schema (Sections 0-6), same output format, but the user pastes their current config and only stale or changed sections get walked. Update is also where the user shifts the `cycle` section as the wage review progresses week-over-week (e.g., "we're now at Options Review, week −9, this cycle's intake came back with these answers").

Loaded by SKILL.md when the Intent Router classifies a request as Update.

---

## When Update Mode Triggers

Update mode triggers when the user's first message contains any of:

- `/update`, "update mode", "update my config", "refresh my config"
- `/init update` (legacy phrasing — same behavior)

**Required:** the user must paste an existing engagement-config YAML block in the same message. If the trigger is present but no config is pasted:

> "Update mode needs your existing config to refresh against. Paste the YAML block from your last engagement and I'll walk through what's stale or changed. Or if you don't have one yet, run `/init` to build a fresh config from scratch."

If the user pasted a config but the YAML is malformed, surface the parse error and ask for a corrected paste — do not auto-fix silently.

---

## Update Mode vs. Init Mode

| Dimension | Init | Update |
|---|---|---|
| Input | Nothing (or a few facts the user types) | Full pasted YAML config |
| Walk-through | All sections, all questions | Only sections flagged stale, conflicting, or changed (and `cycle` whenever the user signals progress) |
| Speed | 20-35 minutes | 3-10 minutes typical, faster if only dates are stale |
| Output | New YAML block | Merged YAML block: untouched sections preserved verbatim, refreshed sections rewritten |

When in doubt — for example, the user pastes a config older than 12 months and asks for a "refresh" — offer both options:

> "Your config is from [date], 14 months old. I can either update it surgically (just refresh what's changed) or run a full /init to rethink the structure. Which do you want?"

---

## Opening Behavior

Step 1: Parse the pasted config and validate. Use `references/engagement-config-template.md` § Validation rules. If parse fails, surface the error and stop.

Step 2: Scan for stale and missing items. A section is **stale** when its `last_verified` date is older than 180 days. An item within a section is stale when it has its own `last_verified` or `next_review` field that has passed (most common: `benchmark.provincial_minimum_wages.{province}.next_review`). A section is **missing** if it was left blank or marked `# to be filled` during Init.

Step 3: Present the scan summary, **then ask the routing question.** Never start walking sections until the user picks a path.

```
Loaded your config (Acme Inc., last full update 2026-05-01).

Status by section:
- org: ✓ verified 2026-05-01
- audience: ✓ verified 2026-05-01
- costing: ⚠ pay_attribution_pct flagged low-confidence; payroll_burden 
  for AB/BC/NS/NB/MB/SK/NL/PE marked placeholder
- benchmark: ⚠ 3 provincial minimum wages past next_review 
  (NS, ON, MB — all due 2026-10-01)
- deck: ✓ verified 2026-05-01

I see 3 stale items. Refresh all in one pass, or review each one-by-one?
```

The routing question follows the user-confirmed pattern: **"refresh all" vs "review each."** Both paths are valid; the choice is about pace, not correctness.

---

## Routing Path A — "Refresh All"

When the user picks the all-at-once path:

1. **For provincial minimum wages, payroll-burden placeholders, and other web-verifiable values:** use web search to find current values, present a diff table, ask for one-shot approval.

   ```
   Found these refreshed values:

   | Field | Old | New | Source |
   |---|---|---|---|
   | benchmark.provincial_minimum_wages.NS.current_rate | 16.75 | 17.00 | NS Labour, eff 2026-10-01 |
   | benchmark.provincial_minimum_wages.ON.current_rate | 17.60 | 17.95 | ON MoL, eff 2026-10-01 |
   | benchmark.provincial_minimum_wages.MB.current_rate | 16.00 | 16.40 | MB Finance, eff 2026-10-01 |

   Apply all? (yes / edit / skip)
   ```

2. **For low-confidence flags (e.g., `pay_attribution_pct`):** ask the user directly. These can't be web-resolved.

   > "Your `pay_attribution_pct` is flagged low-confidence at 0.35. Want to refine it now, leave the flag in place, or remove the flag and lock it as final?"

3. **For placeholders (e.g., payroll burden 0.12 for several provinces):** ask whether to keep them, replace with verified values from finance, or remove the placeholder note.

4. After all stale items are resolved, emit the merged YAML and stop.

---

## Routing Path B — "Review Each"

When the user picks the one-by-one path:

For each stale item, present in this format:

```
[1 of 3] benchmark.provincial_minimum_wages.NS.current_rate
Current: 16.75 (effective 2026-04-01, next_review 2026-10-01)
Web check: 17.00 effective 2026-10-01 per NS Labour
  → Update to 17.00 / Keep current / Edit manually / Skip
```

Wait for response. Move to next item. Allow `back` to revisit the previous item, `done` to stop reviewing and emit what's been confirmed so far. Hold pending updates in working memory; only commit them in the final emitted YAML.

---

## Section-Level Refreshes

Sometimes the user wants to refresh a whole section, not just stale items — for example, "audience changed, my new VP HR is different from the last one." In that case:

1. Show the current section's YAML.
2. Ask whether to **edit in place** (walk question-by-question with current values pre-filled as defaults) or **rebuild from scratch** (treat the section as blank and run the Init questions for it).
3. For edit-in-place, when the user accepts a default by saying "keep" or pressing through, do not re-prompt.

Trigger phrases that indicate a section-level refresh request: "redo audience", "rebuild costing", "refresh benchmark", "audience changed", or naming a specific archetype/role to add or remove.

---

## Persistence config (legacy block)

Configs produced by older versions of `/init` may carry a `persistence:` block with a `backend: google-drive` or `backend: paste-mode` selector. That block is retired — persistence is now handled by the market MCP backend (OAuth identity → org membership) and is not configured per-engagement. When Update mode encounters a `persistence:` block in the pasted config, remove it from the merged output and note: "Removed legacy `persistence:` block — backend is now the market MCP backend, no per-config selector required." See `references/persistence-and-ledger.md`.

---

## Adding New Items to Existing Sections

The user may want to add without changing existing items:

- **Add a new audience archetype:** ask the 4 audience-archetype questions from Init Section 2, append to the existing list, do not touch existing archetypes.
- **Add a new peer company to `benchmark.peer_companies`:** ask which list (primary / regional / specialty), append, confirm.
- **Add a new role alias to `benchmark.role_aliases`:** ask for the user-facing name and the canonical NOC code, append, confirm.
- **Add a new province to `benchmark.scope_provinces`:** add to the list, then ask whether to populate the matching `provincial_minimum_wages` and `payroll_burden_pct` entries (default: yes, web-verify).

In all add-cases, the YAML emitted at the end shows the additions in context, not just the new lines.

---

## Removing Items

If the user wants to remove items:

1. Confirm by quoting the line(s) to be removed.
2. After confirmation, remove and update the surrounding YAML.
3. If the removal would leave a section empty (e.g., removing the only audience archetype), warn before proceeding.

Never remove an item without explicit confirmation, even when the user says "clean up" or "drop the stale stuff" — confirmation is per-item.

---

## Output Format

Final output is a single YAML code block, schema-identical to Init output. Include:

- An updated `_meta:` block reflecting the update (provenance lives in fields, not header comments):
  ```yaml
  _meta:
    schema_version: 1
    created_date: YYYY-MM-DD          # original creation date preserved
    updated_date: YYYY-MM-DD          # date of this update run
    created_by_skill: compensation-advisor
    created_via: /init
    last_updated_via: /update
    sibling_skills: [comp-comms-builder, comp-team-transformer, comp-training-designer]
  ```
- All sections that existed in the input, with refreshed `last_verified` dates **only on sections actually touched.**
- New sections appended in canonical order if added.

After the YAML block, add a one-line plain-text changelog:

```
Updated: benchmark.provincial_minimum_wages (NS, ON, MB), 
costing.pay_attribution_pct (confidence raised to medium).
Untouched: org, audience, deck.
```

---

## Cross-Reference: Stale Detection Inside Engagements

The 180-day stale warning that runs at Phase 0 (config load during a real engagement) is intentionally a *warning*, not a forced update. Track C/R/D/R-lite continue with the stale config — they don't redirect to Update mode. The skill's suggestion at warning time should be:

> "Your benchmark section is 218 days old. I'll proceed with these values for this engagement. When you're done, consider running `/update` to refresh — especially the provincial minimum wages, which decay fast."

This keeps Update mode out of the engagement flow and reserves it for between-engagement maintenance.

---

## Anti-Patterns

- **Do not silently auto-refresh.** Even on the "refresh all" path, the diff table is shown and approval requested. The user owns the config.
- **Do not produce a deck during Update.** Like Init, Update is config-only. Set aside any uploaded `.pptx` for the session.
- **Do not run partial walk + partial auto-refresh in the same response turn.** Pick a path per item.
- **Do not change the schema.** Update edits values within the existing schema. Schema changes (new sections, new keys) are an Init concern.

---

## Output Discipline

Update produces an updated `engagement-config-{slug}.yaml` **file artifact** as its END deliverable — same shape as Init's output, but reflecting the deltas applied in this session.

- Update writes the new revision to `configs/<slug>.yaml` via `engagement_put` (market backend). Surfaces a chat confirmation with a one-line summary of changed fields.
- On transport failure: deliver the updated config as a downloadable file artifact in the chat. The user pastes it back on reconnection.
- **Mid-walkthrough turns**: chat text + YAML code-block previews of the deltas, so the user sees what's about to change.
- After emit, do not auto-suggest a next engagement. End the session with one line confirming the artifact + commit and stop.
