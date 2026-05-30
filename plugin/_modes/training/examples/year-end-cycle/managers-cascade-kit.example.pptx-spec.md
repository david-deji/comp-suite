---
engagement_slug: acme-corp
cycle_slug: year-end-2026
audience: managers-cascade
date: 2026-11-15
delivery_target: "Week 0 / Cascade / target date 2026-12-15"
source_manager_deck: cycles/acme-corp/year-end-2026/managers.pptx
audience_tag: managers-internal
posture: team-meeting-discussion-led
slide_count: 9
total_duration_minutes: 30
---

# Cascade Kit — Spec for pptxgenjs Render

Derived from the manager deck (`managers.example.pptx-spec.md`) via `/cascade`. Manager runs this with their team in week 0 (Dec 15-19). Discussion-led, not training-led. 30 min target.

**Derivation rules applied** (per `cascade-protocol.md`):
- Dropped: anti-FAQ slide (9), escalation-paths slide (13), exec-only context (none here, none in manager deck)
- Kept: depth-1 + depth-2 employee-facing content
- Added: 3 cascade-prompt slides at intentional team-discussion points
- Compressed: 14 manager slides → 9 cascade slides + 3 prompts inserted

---

## Slide 1: Cover (re-titled)

**Layout master:** `01-title.js`
**Title:** "Team Meeting: Year-End Comp Update"
**Subtitle:** "Team Meeting: <cycle-name>"
**Delivery target:** "Week 0 / Cascade / target date 2026-12-15"

---

## Slide 2: Cascade-prompt — opening discussion

**Layout master:** `09-callout.js`
**Title:** "Manager: ask your team"
**Prompt:** "How do you understand the difference between a market raise and a merit raise? What was your assumption coming into this conversation?"
**Manager note:** "Open with this. Listen for 3-4 minutes. Don't pre-answer."

**Time:** 4-5 min

**Source:** msg-001 managers cascade_prompt

---

## Slide 3: The two-piece raise

**Layout master:** `09-callout.js`
**Title:** "Two pieces of your raise"
**Callout:** "60% market. 40% merit."
**Body:**
- Market: keeps pay competitive with what comparable companies are paying
- Merit: recognizes your performance this year through the rating + allocation process

**Manager note:** Reference your team's specific cycle outcomes if helpful — "for our team this cycle, the market piece reflected [specific market signal]; the merit piece reflected [specific performance recognition pattern]."

**Source message:** msg-001 employees framing (depth-1) + manager personalization

---

## Slide 4: Retrieval prompt — checkpoint

**Layout master:** `04-section-divider.js`
**Title:** "Quick check"
**Prompt:** "Without looking at the slide — what are the two parts of your raise?"
**Manager:** "30 seconds quiet. Then 1-2 voluntary answers. Then move on."

**Time:** 1 min

---

## Slide 5: When everything happens

**Layout master:** `02-toc.js`
**Title:** "Your timeline"
**Timeline:**
- December 15, 2026 — letter arrives in your work inbox
- January 1, 2027 — new pay starts (effective date)
- January 15, 2027 — first paycheck reflects new pay

**Source message:** msg-003 employees framing (depth-1)

---

## Slide 6: Cascade-prompt — mid-meeting team discussion

**Layout master:** `09-callout.js`
**Title:** "Manager: ask your team"
**Prompt:** "We've covered the structure — what's the question that's bugging you that I haven't answered?"
**Manager note:** "Plant this 15-20 min in. Surfaces what's actually on their mind. Listen for 4-5 minutes."

**Time:** 4-5 min

---

## Slide 7: Where to ask questions

**Layout master:** `02-toc.js`
**Title:** "If you have questions"
**Routing:**
- Questions about your specific letter — talk to me (your manager) in 1:1
- Questions about how the cycle works — HRBP
- FAQ document arrives the day of the letter (December 15)

---

## Slide 8: Final cascade-prompt — discussion + next steps

**Layout master:** `09-callout.js`
**Title:** "Manager: closing prompt"
**Prompt:** "Anything we should talk about before we wrap?"
**Manager note:** "Final discussion, 4-5 minutes. Don't try to answer everything live — capture what you can't answer for the HRBP queue."

**Time:** 4-5 min

---

## Slide 9: Closing — Discussion + Next Steps

**Layout master:** `01-title.js` (closing variant)
**Title:** "Three things to remember"
**Bullets:**
- Your raise has two parts: market and performance
- New pay starts January 1
- Letter arrives by December 15 — questions go to me first, HRBP for the technical stuff

**Manager closing:** "Thanks team. Letter lands Dec 15 — bring questions to our 1:1s if you have them."

---

## Render notes (cascade-specific)

- Slide count: 9 (typical cascade range is 8-15) ✓
- Cascade prompts: 3 (slides 2, 6, 8) — opens, mid-meeting, close ✓
- Retrieval prompts: 1 (slide 4) — only block type used per cascade-protocol.md § Lighten interactive blocks
- DROPPED from manager deck: anti-FAQ (manager handles live), escalation paths (manager-side resource), detailed objection-handling (live + team-specific), tradeoff explanation (depth-4, exec-only)
- Subtitle metadata: "Team Meeting: <cycle-name>" (vs manager deck's "Year-End 2026 Manager Briefing")
- Voice: same as manager deck (`direct-decisive`) — but tone shifts to conversational because this IS a team meeting
- Brand kit: same as manager deck (regenerated from engagement brand kit)
- Audience tag: `managers-internal` (not a separate tag — derived from managers)

## What this spec does NOT contain

- Manager-only content (anti-FAQ, escalation paths) — those stayed in manager deck
- Exec-only depth-4 content — never appears in cascade
- Detailed mechanics (60/40 split mechanics in detail) — kept conceptual; manager goes deeper if team asks
- Interactive block file — cascade kit uses retrieval prompts only, embedded in cascade-facilitator.md as inline manager notes
