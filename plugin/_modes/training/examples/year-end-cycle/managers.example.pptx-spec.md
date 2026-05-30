---
engagement_slug: acme-corp
cycle_slug: year-end-2026
audience: managers
date: 2026-11-15
delivery_target: "Week 0 / Cascade / target date 2026-12-10"
source_message_map: cycles/acme-corp/year-end-2026/message-map.yaml
source_council_state: council-states/acme-corp/year-end-2026-managers-generate.yaml
audience_tag: managers-internal
posture: broadcast-with-checkpoints
slide_count: 14
total_duration_minutes: 60
---

# Managers Deck — Spec for pptxgenjs Render

Manager training deck. Delivered Dec 10 (Week 0 / Cascade stage). Manager then runs cascade kit with their team Dec 15-19. This deck PREPARES managers; the cascade kit is the team-meeting derivation.

---

## Slide 1: Cover

**Layout master:** `01-title.js`
**Title:** "Year-End 2026 Manager Briefing"
**Subtitle:** "<cycle-name> Manager Briefing"
**Delivery target:** "Week 0 / Cascade / target date 2026-12-10"

---

## Slide 2: What you walk out with

**Layout master:** `02-toc.js`
**Title:** "By the end of this hour"
**Bullets:**
- You understand the cycle's two-piece raise structure (market + merit)
- You know the cycle's mechanics (60/40 split, top-of-band freeze)
- You're equipped to run the cascade kit with your team Dec 15-19
- You know what to defer to HRBP and what's escalation-only

---

## Slide 3: The two-piece raise

**Layout master:** `09-callout.js`
**Title:** "60/40: market then merit"
**Callout:** "60% of total raise pool: market adjustments. 40%: merit pool."
**Body:**
- Market component: scales by compa-ratio band position. Most of your team's raises will be primarily market-driven this cycle.
- Merit component: scales by performance rating × manager allocation. This is where your performance differentiation lives.
- Shift from last cycle (50/50): the market widened faster than internal performance variance.

**Source message:** msg-001 managers framing (depth-2)

---

## Slide 4: Why the shift

**Layout master:** `09-callout.js`
**Title:** "Why 60/40 (not 50/50)?"
**Body:**
- Vacancy + turnover signals indicated the market gap was widening
- Defending pay competitiveness took priority over flattening performance differentiation
- 70/30 alternative was rejected: would have left less differentiation for top performers
- 60/40 keeps merit signal strong while defending market

**Source message:** msg-001 managers framing + tradeoff context from depth-4

---

## Slide 5: Quiz — checkpoint

**Layout master:** `04-section-divider.js`
**Title:** "Knowledge check"
**Question:** "What's the merit-vs-market split this cycle?"
**Options:**
- A: 50/50
- B: 60/40 (60% market, 40% merit)
- C: 70/30
- D: 40/60

**Correct answer:** B
**Distractor handling:** see `managers-interactive-blocks.md` Block 1

---

## Slide 6: Top-of-band freeze

**Layout master:** `09-callout.js`
**Title:** "Top-of-band: market frozen, merit eligible"
**Body:**
- Employees at or above their band's max: no market component this cycle
- Still fully eligible for merit %
- Reason: their pay is already at the top of the salary band
- Affects ~47 employees company-wide (banded; exact count varies by team)

**Source message:** msg-002 managers framing (depth-2)

---

## Slide 7: Cascade-prompt slide

**Layout master:** `09-callout.js`
**Title:** "Manager: cascade prompt"
**Prompt:** "Ask your team: how do you understand the difference between a market raise and a merit raise? What was your assumption coming into this conversation?"
**Use:** "Open the team meeting with this. Listen to their framing — it tells you where to spend your time."

**Source message:** msg-001 managers cascade_prompt

---

## Slide 8: Anticipated questions

**Layout master:** `02-toc.js`
**Title:** "Questions you'll get from your team"
**Q&A bullets:**
- "Why did the split change from last cycle?" → "Market gap widened faster than internal performance variance. Comp committee approved Oct 15."
- "How do I explain this to my high-performer who's at top of band?" → "They're frozen on market component but eligible for full merit %. Cross-band move is a separate process — escalate to HRBP if you think it's warranted."
- "Does this commit us to 60/40 next cycle too?" → "No. Each cycle's split is ratified annually. Don't commit to next year's split."

**Source message:** msg-001 anticipated_objections

---

## Slide 9: Anti-FAQ — what NOT to answer

**Layout master:** `02-toc.js`
**Title:** "What you will NOT answer in the team meeting"
**List:**
- Total cycle envelope ($1.2M) — confidential, exec-only
- Specific dollar comparisons across teams ("why did Mary's team get more")
- Why we chose 60/40 vs 70/30 in detail (this is comp committee territory)
- Next cycle's split

**Body line:** "These are HRBP queue territory. If a team member presses, route them to the queue. Don't speculate."

---

## Slide 10: Effective date + letter timing

**Layout master:** `02-toc.js`
**Title:** "When everything happens"
**Timeline:**
- Dec 11 — cascade kit lands in your inbox
- Dec 15-19 — you run cascade kit with team
- Dec 15 — letters arrive in employee inboxes (you don't see specifics until your team gets theirs)
- Jan 1, 2027 — effective date
- Jan 15, 2027 — first paycheck reflects new pay

**Source message:** msg-003 + msg-005 (cascade kit timing)

---

## Slide 11: Cascade-prompt slide #2

**Layout master:** `09-callout.js`
**Title:** "Manager: mid-meeting cascade prompt"
**Prompt:** "Mid-meeting check with team: 'we've covered the structure — what's the question that's bugging you that I haven't answered?'"
**Use:** "Plant this 15-20 min into the team meeting. Surfaces what's actually on their mind."

---

## Slide 12: Retrieval prompt — checkpoint

**Layout master:** `04-section-divider.js`
**Title:** "Quick check"
**Prompt:** "Without looking at the slide — what's the one thing you'll change about how you'd run your team meeting now vs. before this briefing?"
**Time:** 30 seconds quiet, 1-2 voluntary answers

**Block reference:** `managers-interactive-blocks.md` Block 3

---

## Slide 13: Cascade kit + escalation paths

**Layout master:** `02-toc.js`
**Title:** "Your toolkit + when to escalate"
**Bullets:**
- Cascade kit (30 min, separate deck): you'll get it Dec 11
- HRBP queue: opens Dec 16 — 48h SLA on letter discrepancies + general cycle questions
- Comp manager (escalation only): cross-band moves, retention-risk top-of-band

---

## Slide 14: Closing

**Layout master:** `01-title.js`
**Title:** "Three things to walk away with"
**Bullets:**
- 60/40 split this cycle: market dominant, merit signal preserved for top performers
- Cascade kit lands Dec 11 — run it Dec 15-19, follow the prompts
- HRBP queue is your friend — defer the questions you can't answer

**Closing line:** "Cascade kit prep starts now. Read the kit when it lands."

---

## Render notes

- Slide count: 14 (within managers budget of 12-18)
- Checkpoints: 3 (slide 5 quiz, slide 7 cascade prompt #1, slide 11 cascade prompt #2, slide 12 retrieval) — cadence every 3-4 content slides ✓
- Depth: depth-2 manager content with cascade prompts embedded ✓
- Voice: `direct-decisive` per engagement-training-config.voice.audience_voice.managers
- Anti-FAQ: explicit (slide 9)
- Cascade prompts: 2 explicit cascade-prompt slides (7, 11), inherited from message-map cascade_prompt fields
