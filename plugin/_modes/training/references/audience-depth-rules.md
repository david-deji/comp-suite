# Audience Depth Rules — The Differentiated-Depth Twist

The defining property of `comp-training-designer`: the same fact appears at different depths for different audiences. Loaded at `/ingest` Workshop synthesis (validation gate) and at `/generate` per-audience render (filter gate).

---

## Depth scale

Four discrete levels. Not a continuum — choose one per audience per fact.

| Depth | Name | Content | Suitable audiences |
|---|---|---|---|
| **1** | Headline | The one-line message + 1 supporting example | employees |
| **2** | Mechanics | Headline + how it works + objection-handling + cascade prompts | managers |
| **3** | Edge Cases | Headline + mechanics + edge cases + escalation paths | hrbps |
| **4** | Tradeoffs | Headline + tradeoffs + budget + governance | execs |

---

## The non-monotonic constraint

**HRBP depth ≥ manager depth ≥ employee depth on the same fact** (when all three audiences see the fact, i.e., all three depths are non-null in `message-map.yaml`).

**Execs see different cuts** — depth 4 is not "deeper of the same content"; it's a different framing (tradeoffs / budget / governance). Execs may have null depth on facts everyone else sees, AND may have depth-4 content on facts no one else sees. Their slice is not nested inside the others.

### Visual representation

For a single fact `msg-001` (e.g., "merit-vs-market split this cycle is 60/40"):

```
employees:  depth 1   "Your raise has two parts: market adjustment and performance."
managers:   depth 2   [employees content] + "Mechanics: 60% market, 40% merit pool. Common questions: …"
hrbps:      depth 3   [managers content] + "Edge cases: top-of-band freeze, cross-band moves. Escalate to: …"
execs:      depth 4   "Tradeoffs: 60/40 vs 70/30 — chose 60/40 to defend variable-pay envelope."
                      [different framing — execs ratify the decision; they don't need the cascade text]
```

Note: execs do NOT receive depth-1+2+3 content stacked. They receive a different cut.

### When the constraint is violated

If the operator (or a council recommendation) tries to set:
- `manager.depth = 3` while `hrbp.depth = 2` on the same fact → **REFUSE**. Suggestion: either bump HRBP to depth 3 or reduce manager to depth 2.
- `employee.depth = 2` while `manager.depth = 1` on the same fact → **REFUSE**. Suggestion: either bump manager to depth 2 or reduce employee to depth 1.

Validation runs at `/ingest` Workshop synthesis (before message-map.yaml writes) and at `/generate` per-audience render (filter pass). A violation blocks the cycle from advancing.

---

## When an audience is null on a fact

`null` is a valid depth value. It means "this audience does not see this fact at all."

Common patterns:

- **Employee-only fact**: `employee=1, manager=null, hrbp=null, exec=null`. Rare — usually if employees see something, managers should too. But possible (e.g., a benefits FAQ specific to non-managers).
- **Manager-and-up fact**: `employee=null, manager=2, hrbp=3, exec=null`. Cascade-internal mechanics that don't bubble up to execs and don't bubble down to employees.
- **HRBP-only fact**: `employee=null, manager=null, hrbp=3, exec=null`. Edge cases or escalation procedures that are operationally HRBP-only.
- **Exec-only fact**: `employee=null, manager=null, hrbp=null, exec=4`. Tradeoffs / budget / governance that doesn't trickle down. Common.
- **Universal fact**: all four non-null. Rare — most facts cluster around 2-3 audiences.

The non-monotonic constraint applies only to non-null entries. `manager=null, hrbp=3` is valid (HRBP sees it, manager doesn't). `manager=2, hrbp=null` would be unusual (HRBP doesn't see what managers see) and is allowed but flagged at council auto-fire as a cross-audience inconsistency.

---

## Per-audience depth ceilings (engagement-training-config)

`engagement-training-config.depth_layers.<audience>` sets the **maximum depth** that audience sees on any fact. Defaults:

```yaml
depth_layers:
  employees: 1
  managers: 2
  hrbps: 3
  execs: 4
```

Operator may override per-engagement. Common variants:
- **High-literacy employee population**: `employees: 2` (they can handle mechanics inline, e.g., a comp-savvy tech company workforce).
- **Junior manager bench**: `managers: 1` for first-cycle managers; bump to 2 only after first cycle.
- **Lean HRBP team**: `hrbps: 4` if HRBPs also serve as exec interpreters.
- **Compressed exec time**: `execs: 3` if execs want shorter strategic-only decks (drop depth-4 budget detail).

Per-fact depths must NOT exceed the audience's ceiling. Validation refuses messages where `audiences.<audience>.depth > depth_layers.<audience>`.

---

## At `/ingest` — depth assignment flow

During the `audience_depth_assignment` block of `/ingest` (per `audience_design_block.json`):

1. For each captured message, operator + skill walk through:
   - Who sees this at depth 1? (default: employees if relevant)
   - Who sees this at depth 2 (mechanics)? (default: managers if relevant)
   - Who sees this at depth 3 (edge-case / escalation)? (default: HRBPs if relevant)
   - Who sees this at depth 4 (tradeoffs / budget / governance)? (default: execs if relevant)

2. Skill enforces the non-monotonic constraint inline. If operator sets `manager=2, hrbp=null`, surface: "HRBP doesn't see this? Most depth-2 manager content has a depth-3 HRBP equivalent. Confirm null?"

3. Skill enforces the depth ceiling. If operator sets `employee=2` but config says `employees: 1`, surface: "This engagement's depth ceiling for employees is 1. Either reduce to 1 or update the config."

4. At Workshop synthesis, all messages are re-validated against both rules. Violation blocks `message-map.yaml` write.

---

## At `/generate` — depth filter

For each audience under render, `/generate` reads the per-audience slice from `message-map.yaml`:

```python
slice = [
  m for m in message_map.messages
  if m.audiences.<audience>.depth is not None
]
```

The depth value drives which content fields the renderer pulls:

- depth 1: pull `framing` only
- depth 2: pull `framing` + `anticipated_objections` + `cascade_prompt` (if managers)
- depth 3: pull `framing` + `anticipated_objections` + `edge_cases` + `escalation_paths`
- depth 4: pull `framing` + `tradeoffs` + `budget_framing` + `governance`

Each depth's content fields map to specific slide layouts in the deck (per `template-master.md` mirrored).

---

## Cross-audience consistency check

After per-audience council auto-fire (Step 3 in `/generate`), the skill runs a cross-audience consistency check on the locked slices:

- For every fact: do all audiences seeing it have a coherent narrative? E.g., if employee depth-1 says "60/40 split" and manager depth-2 says "70/30 split," that's a contradiction.
- For cascade prompts: does every cascade-prompt match the depth-1 employee message it's about? (Manager asks team about [X]; employees should be able to recognize [X].)

Violations surface as a soft warning before render. Operator decides; render proceeds (the operator's call).

---

## Why this twist matters

Without depth differentiation, training material has two failure modes:

1. **Lowest-common-denominator**: write the deck for employees, then "version it up" by adding more bullets for HRBPs and execs. Result: HRBP and exec decks are bloated, employees get lost in too much.
2. **One-deck-per-audience-from-scratch**: write 4 totally different decks. Result: cross-audience inconsistency (employees and execs hear different versions of the same fact); operator burns 4× the time.

Differentiated depth solves both: ONE message-map (single source of truth) feeds 4 layered renders. Each audience gets their cut. Cross-audience consistency is enforced by construction.

This is the load-bearing differentiation between `comp-training-designer` and a generic deck-templating tool.

---

## What this protocol does NOT contain

- The full message-map.yaml schema — that lives in `template_assets/message_map_template.yaml`.
- Per-mode flow — those live in `ingest-protocol.md` (depth assignment) and `generate-protocol.md` (depth filter).
- Slide-layout mappings per depth — those live in `template-master.md` (mirrored) and the per-audience slide budgets in `generate-protocol.md`.
