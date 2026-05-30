# Diagnosis: <Process Name>

> Process slug: <slug>
> Date: YYYY-MM-DD
> Source current-state: processes/<slug>/<process-slug>/current-state.md
> Audience: <comp-team-internal | vp-people | external>
> engagement_mode: <mode_id>   # required — matches a v1 mode in engagement-modes.md

## Quick Wins (P0 — do these this week)

1. <action> — owner: <role>, effort: <hours>, expected outcome: <metric>
2. <action> — owner: <role>, effort: <hours>, expected outcome: <metric>
3. <action> — owner: <role>, effort: <hours>, expected outcome: <metric>

> Quick Wins are required (≥2). Each entry must have all four fields. Items without complete fields go to Leverage Points instead.

---

## 1. Context + System Boundary

**Goal:** <what the process is supposed to produce>

**In-scope:** <actors, steps, tools the diagnosis treats as variable>

**Non-scope:** <explicitly excluded — separate processes, downstream consumers, etc.>

**Time horizon:** <1 cycle | 2 cycles | continuous>

**Outcome metrics (1-3):**
- <metric>: <baseline> → <target>
- <metric>: <baseline> → <target>

**Leading indicators (3-7):**
- <indicator>
- <indicator>
- <indicator>

---

## 2. Actors & Incentives Map

| Role | Function in process | Incentive | Constraint |
|------|---------------------|-----------|------------|
| <role> | <function> | <what they optimize for> | <what they can't do> |
| <role> | <function> | <what they optimize for> | <what they can't do> |

> Solo workflow: collapse to `[operator + interfaces]`. Operator is the user; interfaces are vendors, regulators, internal partners.

---

## 3. System Map

10-20 concrete, observable causal links. Mark time delays where they matter.

- <variable A> increases <variable B> [delay: <none | <N> weeks>]
- <variable A> decreases <variable B> [delay: ...]
- ...

> Concrete variables only. No "quality", "alignment", "morale" without operationalization.

---

## 4. Feedback Loops (R/B)

2-6 loops. Each with a one-line "so what".

### Loop 1 — <name> (R | B)

<chain description>

**So what:** <one line — what behavior/pattern this creates over time>

### Loop 2 — <name> (R | B)

<chain description>

**So what:** <one line>

---

## 5. Waste Ledger

| Category | Description | Frequency | Severity (hours-cost) |
|----------|-------------|-----------|------------------------|
| Waiting | <description> | per-cycle / weekly / ad-hoc | <1h / 1-5h / 5-20h / >20h |
| Rework | <description> | ... | ... |
| Handoffs | <description> | ... | ... |
| Over-processing | <description> | ... | ... |
| Manual-when-automatable | <description> | ... | ... |

> At least 3 of the 5 categories must have entries.

---

## 6. Leverage Points + Intervention Plan

3-7 leverage points. Categorized.

| # | Category | Description | Owner | Sequencing |
|---|----------|-------------|-------|-----------|
| 1 | Incentives / Info flows / Rules / Buffers / Tools / Interfaces | <description> | <role> | now / next / later |
| 2 | ... | ... | ... | ... |
| 3 | ... | ... | ... | ... |

> Categories: incentives, information flows, rules/policies, buffers/capacity, tools/automation, interfaces. No uncategorized entries.

---

## 7. Risks / Open Questions / Next Steps

**Risks:**
- <risk>
- <risk>

**Open questions:**
- <question — flag for follow-up `/discover` or external research>

**Next steps:**
- <action> — `/transform`-eligible: yes / no
- <action>
