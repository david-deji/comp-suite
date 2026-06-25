# Council Command Protocol

The `/council` slash command is the slash-callable entry point to the existing Council track. It does not replace `references/council-mode.md` — it wraps it for faster invocation.

Loaded by SKILL.md when the Intent Router detects a `/council` slash command.

---

## When the /council Command Triggers

The `/council` command triggers when the user's first message contains:

- `/council` (with or without an argument)
- `/council [topic in plain language]` — e.g., `/council should we move from P50 to P65?`
- `/council [argument across multiple lines]`

The natural-language deliberation triggers ("run council on", "deliberate on", "stress-test this") continue to work as documented in `references/intent-router.md` — they route to the same Council track without needing the slash form. The slash command is an alternative, not a replacement.

---

## Why a Slash Command Wraps an Existing Track

Three reasons:

1. **Discoverability.** New users don't always know the natural-language triggers. `/council` is greppable, suggestable, and shows up in the `/help` menu.
2. **Mid-engagement use.** During a Track C or R engagement, a user mid-conversation can type `/council should we lead the market on meat cutters?` and trigger the deliberation cleanly. The slash form parses unambiguously even when the surrounding context is busy.
3. **Argument-or-prompt flexibility.** The user-confirmed pattern: optional argument. With an arg, go straight in. Without an arg, ask once for the topic.

---

## Argument Handling

Per the user's design choice, `/council` takes an **optional** argument.

**With argument** (e.g., `/council should we adopt pay-for-performance for store managers?`):

1. Parse the argument as the council's framing question.
2. Skip the framing-question step from `council-mode.md` § "Frame the question."
3. Proceed directly to persona roster declaration.

**Without argument** (just `/council`):

1. Acknowledge the trigger:

   > "Council mode — what should the council deliberate on?
   >
   > One sentence is enough. Be specific about what's being decided and what's fixed (envelope, effective date, scope)."

2. Wait for response. On answer, treat the response as the framing question and proceed to persona roster.

If the user's argument is too vague to be a useful framing ("`/council comp strategy`"), still accept it but ask one tightening question before the persona roster:

> "Got it — comp strategy. To make the council useful, I need to narrow the question. Are you weighing a specific philosophy shift (e.g., P50 → P65), a structural change (band restructure, pay-for-performance), or a positioning question (lead vs match vs lag against a specific competitor)?"

---

## Handoff to Council Mode Protocol

After the framing question is captured (via argument or follow-up), the rest of the protocol is identical to the existing Council track:

1. Read `references/council-mode.md`.
2. Load engagement config if present (Phase 0 behavior). If a `council` section exists in the config, use those defaults for mode, persona roster, synthesis style.
3. Declare the persona roster (4-6 perspectives) with one-line justifications.
4. **Run the adversarial pre-pass** — 3 hardest objections to the question itself (per `council-mode.md` § Step 3). Mandatory before persona blocks.
5. **Assign per-persona grounding** — one live source fetch per persona, no two personas sharing a source (per `council-mode.md` § Step 4). Mandatory; statute fetches use `web_fetch` against authoritative URLs only.
6. Run persona voice blocks sequentially in a single response — Position line FIRST, then reasoning (per `council-mode.md` § Step 5 position-before-reasoning lock).
7. Synthesize, addressing each pre-pass objection explicitly.
8. Produce mode-specific output (reasoning / memo / integrated).
9. Generate `council-state-YYYY-MM-DD-{client-slug}.yaml` — schema includes the pre-pass objections, per-persona grounding, and any statutory downgrades.

The slash command does not change the Council protocol's substance — only its entry point. The adversarial pre-pass + per-persona grounding + position-before-reasoning lock + statutory enforcement all apply equally to slash-invoked councils, including mid-engagement integrated mode.

---

## Mid-Engagement Slash Use

During an active Track C, R, or D engagement, the user can type `/council [argument]` to trigger an integrated council without ending the engagement. The integrated-mode behavior from `council-mode.md` § "Mid-engagement integrated council" applies:

1. Pause the active track at its current phase.
2. Run the council session in `integrated` mode.
3. Generate `council-state-*.yaml`.
4. Return to the paused track. The council's recommended path becomes a constraint on Phase 4 scenarios; the council's tensions become candidate elements of the Phase 5 narrative frame.

The user does not need to explicitly request `integrated` mode — `/council` mid-engagement defaults to integrated. If the user wants pure-reasoning or memo mode mid-engagement, they specify it: `/council memo: should we…`.

---

## Council Output Modes (Recap)

From `council-mode.md`, summarized here for completeness:

| Mode | Output | When |
|---|---|---|
| `reasoning` | Persona blocks + synthesis. Stops there. | Default for fresh `/council` calls |
| `memo` | Reasoning + decision memo block | When user wants a takeaway artifact |
| `integrated` | Reasoning + Phase 4/5 handoff block | When `/council` is invoked mid-engagement |

Mode can be specified inline: `/council memo: ...`, `/council integrated: ...`. Without a mode prefix, default per the rules above.

---

## Anti-Patterns

- **Do not skip the persona roster declaration.** Even when the slash command provides a clear argument, the roster (4-6 perspectives + one-line justifications) is part of the council's contract with the user.
- **Do not skip the adversarial pre-pass.** The slash form's speed-of-invocation tempts rushing past Step 3 in `council-mode.md`. Don't — the pre-pass is the upstream defense against unanimous-synthesis failure.
- **Do not skip per-persona live grounding.** Each persona's one-fetch obligation applies to slash-invoked councils too. The fetch is the rule, not the exception.
- **Do not draft a `[statutory]`-tagged claim without a `web_fetch` URL + quoted article text.** Auto-downgrade applies regardless of invocation path.
- **Do not produce a deck from `/council` alone.** Council output is reasoning + state YAML + optional memo. To turn it into a deck, the user escalates to Track D after council completes.
- **Do not run council in parallel.** Persona voices are sequential within a single response, never parallel subagent calls.
- **Do not draft synthesis until every persona block is complete.** This is the existing Council rule, repeated here because slash invocation can tempt rushing.
- **Do not lose the engagement config.** When `/council` runs mid-engagement, the engagement's parsed config remains in working memory and is read by the council as input.

---

## Output Discipline

- Output is chat text + one YAML state artifact (+ optional memo).
- The state YAML is written to `$STATE_ROOT/_orgs/<org_slug>/engagements/<slug>/council-state-{date}.yaml` (non-schema artifact — local only; standalone runs use `$STATE_ROOT/_orgs/_council-standalone/<derived-slug>/...`) and presented as a download artifact. See `references/council-mode.md` § Step 8 and `references/persistence-and-ledger.md` § Binary deliverables.
- After delivery, the response ends without a generic next-step suggestion. If the user wants to escalate to a deck, they do.
