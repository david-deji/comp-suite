# Cycle Discovery and Gating

Two responsibilities:

1. **Discover** the comp cycle during a `/discover` session — anchor event, stages, gating windows. Populates `team-config.cycle.*`.
2. **Gate** transformation rollouts against the discovered cycle — `/transform` and `/roadmap` refuse to schedule into `live` or `prep` windows.

Loaded conditionally — only when `team-config.cycle.stages == []` (during `/discover`) or when `/transform` / `/roadmap` is computing rollout windows.

---

## Why cycle stages are discovered, not pre-configured

Pre-configuring cycle stages in `/init` produced wrong gating decisions in early prototypes. Examples of mis-statement that an interview catches but a config-form doesn't:

- "We have a cycle that runs Jan-Aug" — true, but the team also has a smaller mid-year refresh; the real anchor is the effective date, not the first month.
- "Effective date is September 1" — true for most years, but the user's specific cycle this year is a 3-month early refresh.
- "Stage X is in November" — week offset from anchor, not absolute calendar week, is what matters for gating.

The cycle-mapping interview block forces the interviewee to walk backwards from the anchor event. Stages that don't anchor cleanly to a workback get caught.

---

## Cycle-mapping block (interview, mandatory when `cycle.stages == []`)

Inserts during the Intake sub-phase of `/discover`. Six prompts in order:

```
1. Anchor event for the cycle? (e.g., "effective date YYYY-MM-DD", "scale ships YYYY-MM-DD")
2. Walk me through the workback stages by name — from anchor backwards.
3. For each stage, what's the approximate week offset from anchor? (Negative = before anchor.)
4. Tag each stage: live | prep | slack
   - live    = active execution; no transformations may ship
   - prep    = preparation; no disruptive change
   - slack   = post-cycle or pre-cycle calm; transformations may ship
5. Today, what stage are we in? What's the current week offset?
6. Confirm: anchor date is _____.
```

Each prompt is one conversational question. Ask them in order; wait for the operator's answer before moving to the next. Skill captures answers in structured form, then writes to `team-config.cycle.*` after the reflect-and-verify gate.

### Output schema (`team-config.cycle.*`)

```yaml
cycle:
  stages:
    - name: <stage name, e.g., "Intake & scope">
      week_offset: -16             # negative = before anchor
      anchor_date: 2026-09-01      # absolute date for this stage start
      gating: live | prep | slack
      description: <free text>
  current_stage: <stage name>      # computed at Phase 0 from anchor + today
  current_week_offset: -8          # computed at Phase 0
  anchor_event: "effective date 2026-09-01"
  last_discovered: 2026-05-02
```

`anchor_date` per stage is computed from `anchor_event_date + (week_offset * 7)` and cached. If the user later changes `anchor_event`, all `anchor_date` values recompute on next session start.

---

## Gating rule

Used by `/transform` (cycle-fit annotation per spec) and `/roadmap` (sequencing into quarterly slots).

| Gating tag | Meaning | Rollout allowed? |
|------------|---------|-----------------|
| `live` | Active cycle execution (e.g., approval, cascade, payroll, effective-date weeks) | **No.** Hard refuse. |
| `prep` | Preparation weeks where disruptive change risks the cycle (e.g., market refresh, options modeling) | **No.** Hard refuse. |
| `slack` | Post-cycle or pre-cycle calm | **Yes.** Eligible for rollout. |

### How gating fires

**`/transform` cycle-fit annotation** (per buildable spec, §11 schema):

For each Strong Candidate, compute the earliest viable rollout window:

1. Walk forward from `current_week_offset` through the cycle stages.
2. Find the next `slack` stage.
3. Compute the calendar quarter that stage starts in.
4. Annotate the spec: `Earliest viable rollout: <Qx YYYY> (slack window in <stage name>)`.

If no `slack` stage exists within the next 2 quarters, surface warning:

> "No slack window in next 2 quarters. This candidate would need to wait `<N>` weeks. Surface to roadmap as Needs Groundwork or accept the wait?"

**`/roadmap` sequence rejection:**

For each transformation brief, check the proposed quarterly slot against `cycle.stages` for that quarter:

- If any stage in that quarter is `live` or `prep` AND the rollout would land during that stage's weeks, **reject** the placement.
- Surface the rejection: "Placing `<spec>` into `<Qx>` lands in `<live/prep stage name>`. Move to `<next slack window>`?"

User may override with explicit acknowledgment:

> "Override: I want to ship in `<Qx>` despite the `<live/prep>` overlap. Reason: `<user input>`."

Override is captured in `roadmap-<Qx>.md § Cycle-gating exceptions`. Acceptance is explicit; never silent.

---

## Too-early

When a `/transform` or `/roadmap` request arrives but the team does not yet have a
discovered cycle (`cycle.stages == []`), the rollout windows are unknown and gating
cannot run. Surface the pre-engagement mode menu before proceeding.

**Trigger:** `cycle.stages == []` AND user requests `/transform` or `/roadmap`.

**Pre-engagement mode menu (5 options):**

| Option | What happens | Artifact |
|---|---|---|
| **A. Run `/discover` first (recommended)** | Map the cycle now, then continue to the requested command | cycle data in team-config + intended artifact |
| **B. Proceed without gating** | Skip cycle-fit annotation; no live/prep protection | artifact with `cycle_gating: bypassed` flag in frontmatter |
| **C. Discovery-only for now** | Map the cycle only — do not proceed to the requested command | team-config updated; user returns with a new request |
| **D. Diagnose-only (if diagnosis is the goal)** | Deferred transformation scope; produce diagnosis only | diagnosis.md only |
| **E. None of the above — let me re-state** | User clarifies intent | — |

The pre-engagement menu fires ONCE per session. If the user picks B, capture the
bypass in `team-config.cycle.notes` and append a `decision_log` entry with
`decision_type: cycle_gating_bypassed`. Do NOT prompt again mid-session.

---

## Edge cases

- **Cycle changes mid-build** — if the user later runs `/discover` on a new process and the cycle-mapping prompts surface different stages, the new stages override `team-config.cycle.stages` in the team-config update. Old stages are not preserved as v2 history (deferred). Surface a warning: "Cycle stages updated — `/transform` and `/roadmap` will use the new gating from now on."
- **No cycle exists** — some teams have no annual cycle (e.g., a benchmarking-on-demand team). User answers "n/a" to anchor event. Skill sets `cycle.stages = []` permanently and skips gating in `/transform` and `/roadmap`. Captured in `team-config.cycle.anchor_event: null` post-discovery.
- **Multiple cycles per team** — if a team runs two cycles (e.g., annual + mid-year refresh), v1 captures only the dominant cycle. The smaller cycle is noted in `team-config.cycle.notes` (free-text field, v2 makes this structured). Surface to user: "I'm capturing the annual cycle as the gating cycle. The mid-year refresh will be noted but won't gate `/transform` decisions in v1."

---

## v2 considerations (not in v1)

- **Multi-cycle gating** — structured second-cycle support for teams with annual + mid-year cycles.
- **Cycle drift detection** — when `last_discovered` is older than 6 months, surface staleness warning at Phase 0.
- **Cycle-stage history** — preserve prior stage definitions on update so `/ledger` can correlate intervention outcomes against the cycle that was live at intervention time.
- **Industry-specific cycle templates** — pre-built cycle templates per industry (retail, healthcare, public sector) with editable defaults, replacing the cold-start interview for teams that match a template.
