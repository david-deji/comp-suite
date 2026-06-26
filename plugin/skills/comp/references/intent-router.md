# Intent Router

> Loaded from `SKILL.md` Step 1 when `/comp` is invoked with no positional arg.
> Implements SPEC § 3.1.

## Purpose

Help the founder pick a mode when they invoked `/comp` without a flag. Two paths:

1. **Numbered list** — show available modes, founder picks by number
2. **Free text** — founder describes the task in their own words; you classify

## Procedure

### 1. Discover modes

```bash
for f in "$ASSET_ROOT"/_modes/*/mode.yaml; do
  name=$(yq '.name' "$f")
  desc=$(yq '.description' "$f" | head -1)
  echo "$name : $desc"
done
```

### 2. Present options

Use `AskUserQuestion` with the discovered modes as options. Add a final option `Other` mapped to free-text classification.

```
Which mode do you want?
1. advisor — Lead consulting work — market data, pay equity, decks, decision documents.
2. comms — Post-decision cascade artifacts (manager talking points, employee FAQ, …).
3. transformer — Process discovery + AI-transformation roadmap.
4. training — Per-audience training bundle generation.
Other — Describe the task in your own words.
```

### 3. If founder picks `Other`

Run free-text classification. Use the active session model (`inherit`) via a self-call (you ARE the orchestrator session — just classify in-context, no subagent needed).

Classification prompt template (use this verbatim):

```
You are routing a comp consulting task to one of these modes:

[NUMBERED LIST OF MODES WITH DESCRIPTIONS FROM mode.yaml]

User said: "[USER DESCRIPTION]"

Return YAML: { mode: <name>, confidence: high|medium|low, rationale: <one line> }
If the description is ambiguous (could fit 2+ modes), return confidence: low.
```

Parse the returned YAML, then **validate it before branching** (SPEC § 2b — replaces the old
convention of branching on unvalidated parsed YAML):

1. **Schema-validate** the parsed object against
   `$ASSET_ROOT/_core/schemas/intent-classification.schema.json` (`mode` non-empty string,
   `confidence ∈ {high,medium,low}`, `rationale` non-empty, `additionalProperties:false`). A
   malformed or typo'd classification fails here — re-run the classification once, then re-ask
   the founder rather than branch on garbage.
2. **Post-check `mode` membership** against the glob-discovered mode set (Step 1). A schema-valid
   but unknown mode (e.g. a hallucinated `benefits`) fails the membership check and re-asks — no
   silent mis-route. (A1: membership in a runtime-discovered set cannot live in a static schema,
   so it is an orchestrator post-check, not a schema enum.)

Only a classification that passes BOTH the schema and the membership check reaches the branch:

| Confidence | Action |
|---|---|
| `high` | Dispatch directly to the chosen mode. Tell the founder one line: "Routing to <mode>: <rationale>." |
| `medium` | Confirm with the founder before dispatching. "I think this is <mode> work (<rationale>). Proceed?" |
| `low` | Mandatory confirm. Show all candidate modes ranked. "I'm not sure — best guesses: 1) <mode-a> 2) <mode-b>. Or describe more?" |

### 4. Dispatch

Once a mode is chosen, jump to `SKILL.md` Step 2 with that mode as `$1`.

## Edge cases

- **No modes installed**: `$ASSET_ROOT/_modes/` is empty. Surface error: "No modes installed. Run `/comp doctor` to diagnose." Exit non-zero.
- **All `mode.yaml` files unparseable**: surface YAML parse errors per file; do not fabricate a mode list.
- **Founder cancels**: exit cleanly, no state touched.

## Acceptance

Test scenario 15 (`ambiguous-routing`): description "I need to brief the team on the new pay band" — could be `comms` or `advisor`. Returns `confidence: low`, prompts user to confirm, then dispatches.

Phase 2 gate (SPEC § 2b/§ 2d): a classification that fails `intent-classification.schema.json`, or names a mode not in the discovered set, fails the gate and re-asks — it never branches on an unvalidated or unknown-mode classification (no silent mis-route).
