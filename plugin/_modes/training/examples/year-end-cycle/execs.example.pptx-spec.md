---
engagement_slug: acme-corp
cycle_slug: year-end-2026
audience: execs
date: 2026-11-15
delivery_target: "Week -4 / Approval / target date 2026-11-15"
source_message_map: cycles/acme-corp/year-end-2026/message-map.yaml
source_council_state: council-states/acme-corp/year-end-2026-execs-generate.yaml
audience_tag: execs-internal
posture: broadcast-with-checkpoints
slide_count: 9
total_duration_minutes: 30
---

# Execs Deck — Spec for pptxgenjs Render

Exec ratification deck. Delivered Week -4 / Approval stage / Nov 15. The decision in front of the room is: ratify the 60/40 split + $1.2M envelope, or send back. Tradeoff-framing focus, not mechanics. Depth-4 throughout.

---

## Slide 1: Cover

**Layout master:** `01-title.js`
**Title:** "Year-End 2026 — Comp Cycle Ratification"
**Subtitle:** "<cycle-name> Executive Review"
**Delivery target:** "Week -4 / Approval / target date 2026-11-15"

---

## Slide 2: The decision in front of you

**Layout master:** `09-callout.js`
**Title:** "Today's decision"
**Callout (large):** "Ratify the 60/40 split + $1.2M envelope, or send back to comp committee."
**Body:**
- Recommended position: Ratify
- Comp Committee approval: 2026-10-15
- Final ratification ask at Board Comp Subcommittee: 2026-12-08

**Source message:** msg-004 governance + msg-001 governance

---

## Slide 3: The tradeoff — 60/40 vs alternatives

**Layout master:** `09-callout.js`
**Title:** "Why 60/40, not 50/50 or 70/30?"
**Body:**
- **50/50 (last cycle's mix)**: would have left the market gap widening; vacancy/turnover signals indicated the gap was outpacing internal performance variance
- **70/30 (more market-defense)**: would have flattened performance differentiation; merit signal at 30% no longer meaningfully differentiates top performers
- **60/40 (recommended)**: defends market position while preserving merit signal for top performers

**Source message:** msg-001 execs tradeoffs (depth-4)

---

## Slide 4: The budget — $1.2M envelope

**Layout master:** `09-callout.js`
**Title:** "$1.2M cycle envelope"
**Body:**
- 60% ($720K): market-driven, effectively non-discretionary given current vacancy/turnover signals
- 40% ($480K): merit-discretionary — the genuinely flexible lever for next-cycle adjustment
- Implied $X.YM in payroll-burden cost (CPP/QPP/EI/HSF approx 13% in QC)
- True total cost: ~$X.YM

**ROI argument:** vacancy/turnover signals indicated $1.5M-$2M opportunity cost from competitor poaching. $1.2M is the defended-spending choice — closes most of the gap while preserving budget flexibility.

**Source message:** msg-004 execs budget_framing (depth-4)

---

## Slide 5: Poll — checkpoint (decision commit)

**Layout master:** `04-section-divider.js`
**Title:** "Quick alignment check"
**Question:** "Where are you sitting on the 60/40 + $1.2M envelope right now?"
**Options:**
- A: Aligned — ready to ratify
- B: Aligned with concerns — discuss before ratifying
- C: Not aligned — need to send back to comp committee

**Block reference:** `execs-interactive-blocks.md` § Block 1

**Time:** 2 minutes — surface dissent before deeper discussion

---

## Slide 6: What we considered and rejected

**Layout master:** `02-toc.js`
**Title:** "Alternatives we considered"
**Body:**
- **$0.9M envelope**: would have left market gap widening; rejected for retention risk
- **$1.5M envelope**: would have closed gap to P50 fully; rejected for budget flexibility (next year would be hard to compress back)
- **70/30 split**: rejected for performance-differentiation flattening
- **No top-of-band freeze**: rejected because top-of-band employees are at policy max; freeze is policy-consistent

**Purpose:** Pre-empt "have you considered X" objections. Each alternative was on the table.

---

## Slide 7: Cycle calendar + cascade architecture

**Layout master:** `02-toc.js`
**Title:** "How this gets to employees"
**Timeline:**
- Today (Nov 15) — exec ratification (this meeting)
- Dec 1 — HRBP cycle-mechanics training
- Dec 10 — manager training
- Dec 11 — cascade kits delivered to managers
- Dec 15-19 — manager-led cascade conversations with teams
- Dec 15 — letters arrive in employee inboxes
- Jan 1, 2027 — effective date

**Source message:** msg-003 execs framing (depth-1, simple) + cascade architecture context

---

## Slide 8: Risks + mitigation

**Layout master:** `02-toc.js`
**Title:** "Risks we're managing"
**Body:**
- **Top-of-band retention risk**: ~47 employees frozen on market component. Mitigation: retention-risk flag triggers cross-band-move review.
- **Cross-team comparison backlash**: employees may compare team-level allocations. Mitigation: HRBP queue + manager training script.
- **Manager cascade fidelity**: 30+ managers delivering same message. Mitigation: cascade kit prescriptive prompts + HRBP queue support.
- **Next-cycle commitment risk**: 60/40 ratified this cycle does NOT commit next cycle. Manager + HRBP training explicitly trains this.

---

## Slide 9: The ask — closing

**Layout master:** `01-title.js`
**Title:** "The decision today"
**Bullets:**
- Ratify 60/40 split + $1.2M envelope
- OR send back with specific concern + alternative direction
- Final Board Subcommittee ratification: Dec 8

**Closing line:** "Effective Jan 1, 2027. Ratification today unblocks the manager training Dec 10. Send-back delays the entire cycle. Decision?"

**Decision ask:** Explicit. The closing slide names the ask + the timeline cost of deferral.

---

## Render notes

- Slide count: 9 (within execs budget of 6-12) ✓
- Checkpoints: 1 (slide 5 poll) — exec decks lean light on checkpoints; one mid-deck commit-check is the right cadence
- Depth: depth-4 throughout (tradeoffs, budget framing, governance) ✓
- Voice: `strategic-brief` per engagement-training-config.voice.audience_voice.execs
- Decision ask: explicit on slide 2 AND closing slide 9
- Excludes: mechanics detail (operational, not strategic); cascade prompts (manager-only); HRBP edge cases (operational, not exec)
- Includes: tradeoff explicit (slide 3), budget detail (slide 4), rejected alternatives (slide 6), risk + mitigation (slide 8)
