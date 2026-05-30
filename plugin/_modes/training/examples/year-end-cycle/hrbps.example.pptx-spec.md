---
engagement_slug: acme-corp
cycle_slug: year-end-2026
audience: hrbps
date: 2026-11-15
delivery_target: "Week -2 / Prep / target date 2026-12-01"
source_message_map: cycles/acme-corp/year-end-2026/message-map.yaml
source_council_state: council-states/acme-corp/year-end-2026-hrbps-generate.yaml
audience_tag: hrbps-internal
posture: broadcast-with-checkpoints
slide_count: 18
total_duration_minutes: 75
---

# HRBPs Deck — Spec for pptxgenjs Render

HRBP cycle-mechanics training. Delivered Dec 1 (Week -2 / Prep stage). HRBPs are about to use this on the floor — manager training is Dec 10, cascade kicks off Dec 15, HRBP queue opens Dec 16. They need DEEP mechanics and edge cases, not headline framing.

---

## Slide 1: Cover

**Layout master:** `01-title.js`
**Title:** "Year-End 2026 HRBP Briefing"
**Subtitle:** "<cycle-name> HRBP Briefing"
**Delivery target:** "Week -2 / Prep / target date 2026-12-01"

---

## Slide 2: What you walk out with

**Layout master:** `02-toc.js`
**Title:** "By the end of these 75 minutes"
**Bullets:**
- You understand the cycle's full mechanics including all edge cases
- You know every escalation path with SLAs
- You're equipped to handle the floor questions managers will surface
- You know what to do when the manager queue gets stuck

---

## Slide 3: The 60/40 split — full mechanics

**Layout master:** `09-callout.js`
**Title:** "60/40: full mechanics for HRBP"
**Body:**
- Market component (60% of pool): scales by compa-ratio band position. Mechanics: actual market lift % varies per band; HRIS computes per employee.
- Merit component (40% of pool): scales by performance rating × manager allocation. Manager allocates within their team's pool; tighter ranges than last cycle.
- Ratification: Comp Committee 2026-10-15. Cycle policy §3.2.

**Source message:** msg-001 hrbps framing (depth-3)

---

## Slide 4: Edge cases for 60/40

**Layout master:** `02-toc.js`
**Title:** "Edge cases — be ready for these"
**Bullets:**
- **Top-of-band employees**: market component frozen; merit component eligible at full %. Affects ~47 employees company-wide.
- **Cross-band moves**: handled outside cycle pool. HRBP triggers separate review with comp manager.
- **Mixed pay structure teams**: step roles follow scale lift, merit-band roles follow 60/40 split. Team-level confusion is real — be ready to explain.

**Source message:** msg-001 hrbps edge_cases

---

## Slide 5: Quiz — knowledge check

**Layout master:** `04-section-divider.js`
**Title:** "Edge case knowledge check"
**Question:** "An employee on a step pay structure is on a manager's team alongside merit-band employees. The manager asks: does the 60/40 split apply to this employee?"
**Options:**
- A: Yes, 60/40 split for everyone
- B: No, step employees follow the scale lift; only merit-band employees follow the 60/40 split
- C: Step employees get only the market component; no merit component
- D: It depends on the employee's tenure

**Correct answer:** B
**Distractor handling:** see `hrbps-interactive-blocks.md` Block 1

---

## Slide 6: Top-of-band freeze — full HRBP detail

**Layout master:** `09-callout.js`
**Title:** "Top-of-band freeze — when to flag retention risk"
**Body:**
- Rule: top-of-band employees frozen on market, eligible for full merit %
- Edge case 1: Employee just promoted into top-of-band mid-cycle → prorate market component for the pre-promotion period
- Edge case 2: Top-of-band high-performer flagged retention risk → trigger cross-band-move review (separate process)
- HRBP role: support manager 1:1 conversations with top-of-band employees; flag retention risk to comp manager within 5 business days

**Source message:** msg-002 hrbps edge_cases + escalation_paths

---

## Slide 7: Escalation paths

**Layout master:** `02-toc.js`
**Title:** "Your escalation paths with SLAs"
**Routing table:**
- **Cross-band exception**: HRBP → Comp Manager → VP People (3-day SLA)
- **Top-of-band freeze dispute**: HRBP handles directly via documented merit policy
- **Retention-risk top-of-band**: HRBP → Comp Manager within 5 business days
- **Letter discrepancy**: HRBP queue → Payroll partner → Comp Manager (production-incident severity)
- **Manager unable to answer cycle question**: HRBP queue (48h SLA)

**Source message:** msg-001 + msg-002 escalation_paths

---

## Slide 8: Effective date + letter timing — HRBP detail

**Layout master:** `02-toc.js`
**Title:** "Cycle calendar with HRBP touch points"
**Timeline:**
- Dec 1, 2026 — HRBP training (today)
- Dec 10 — Manager training
- Dec 11 — Cascade kits land
- Dec 15-19 — Manager-led cascades
- Dec 15 — Letters arrive in employee inboxes
- Dec 16 — HRBP queue opens (48h SLA)
- Jan 1, 2027 — Effective date
- Jan 15 — First paycheck reflects new pay

**Source message:** msg-003 hrbps framing (depth-3)

---

## Slide 9: Letter discrepancy — handling guide

**Layout master:** `09-callout.js`
**Title:** "Letter discrepancy — your floor playbook"
**Body:**
- Step 1: Verify discrepancy is real (check HRIS — actual rate vs letter)
- Step 2: If real → route to comp manager + payroll partner (production-incident severity, NOT queue)
- Step 3: Document in HRBP queue with full context
- Step 4: Communicate with employee within 24h with timeline

**Source message:** msg-003 hrbps edge_cases

---

## Slide 10: Mid-cycle hires — handling

**Layout master:** `02-toc.js`
**Title:** "Mid-cycle hires — pro-rated handling"
**Body:**
- Hire date Oct 1 - Dec 14: pro-rated cycle increase; explained in letter footnote
- Hire date Dec 15+: not eligible for this cycle; first cycle is next year
- HRBP role: explain pro-rating math when employees ask; refer to HRIS letter footnote for the actual numbers

---

## Slide 11: Cross-team comparisons — anti-FAQ for HRBP

**Layout master:** `02-toc.js`
**Title:** "Cross-team comparison questions — your stance"
**Body:**
- Employees and managers WILL ask "why did Mary's team get more"
- Your stance: "Cycle allocations are confidential at the team level. I can't compare across teams."
- Behind the scenes: managers genuinely received different allocations based on team performance + market signals; your job is NOT to surface that
- Escalate to comp manager only if discrepancy alleges policy violation

---

## Slide 12: Scenario card — checkpoint

**Layout master:** `04-section-divider.js`
**Title:** "Scenario: top-of-band high performer"
**Scenario:** "A senior IC on the engineering team is at top of their band. Their performance rating this cycle is the highest on their team. The manager comes to you and says: 'My top performer is going to leave when they see they only got merit and no market lift. What do I do?'"
**Prompt:** "What would you do? What information do you need first?"
**Discussion frame:** Listen for: do they understand top-of-band freeze rule? Do they know cross-band-move process? Do they recognize this as retention-risk-flag-worthy?
**Synthesis:** "This is exactly the retention-risk flag case. Cross-band move is a separate process; flag to comp manager within 5 business days."

**Block reference:** `hrbps-interactive-blocks.md` § Block 2

---

## Slide 13: Mixed pay structure handling

**Layout master:** `09-callout.js`
**Title:** "Mixed pay structure teams — be ready"
**Body:**
- Some teams have BOTH step employees and merit-band employees
- Step employees: scale lift applies (e.g., 2.5% scale lift this cycle)
- Merit-band employees: 60/40 split applies
- Same team, two different "raise structures" — manager + HRBP need to align
- Common confusion: employees comparing across pay structures within their own team

**Source message:** msg-001 hrbps edge_cases (mixed pay structure)

---

## Slide 14: Quiz — knowledge check #2

**Layout master:** `04-section-divider.js`
**Title:** "Edge case knowledge check"
**Question:** "Manager flags a top-of-band high-performer as retention risk. What's the correct routing?"
**Options:**
- A: HRBP queue (48h SLA)
- B: Direct to VP People
- C: Cross-band-move review with comp manager (5-day SLA)
- D: Wait until cycle close, then escalate

**Correct answer:** C
**Distractor handling:** see `hrbps-interactive-blocks.md` Block 3

---

## Slide 15: HRBP queue operations

**Layout master:** `02-toc.js`
**Title:** "HRBP queue — how it works"
**Body:**
- Opens Dec 16
- 48h SLA on most queries
- Production-incident severity for letter discrepancies (immediate routing)
- Track in shared queue tool
- Coordinate with peer HRBPs — single point of failure if one HRBP is on PTO

---

## Slide 16: Cycle policy reference

**Layout master:** `02-toc.js`
**Title:** "Where to find the policy"
**Body:**
- Merit policy v3 (full document) — bookmark this
- Cycle policy §3.2 (60/40 ratification)
- Cycle policy §3.4 (top-of-band freeze rule)
- Cycle calendar §2.1 (effective dates)

---

## Slide 17: Retrieval prompt — checkpoint

**Layout master:** `04-section-divider.js`
**Title:** "Comprehensive recall"
**Prompt:** "Without looking at the slides — name the 3 most likely floor questions managers will surface to you, and your one-line answer for each."
**Time:** 90 seconds quiet, 2-3 voluntary answers

**Block reference:** `hrbps-interactive-blocks.md` § Block 4

---

## Slide 18: Closing

**Layout master:** `01-title.js`
**Title:** "You're equipped"
**Bullets:**
- Mechanics: 60/40 split, top-of-band freeze, cross-band escalation, mixed pay structures
- Routing: queue + escalation SLAs
- Tools: merit policy v3, cycle policy refs, cascade kits
- Coordination: peer HRBPs, comp manager, payroll partner

**Closing line:** "Queue opens Dec 16. Cascade goes Dec 15-19. Letters land Dec 15. We're ready."

---

## Render notes

- Slide count: 18 (within HRBPs budget of 15-25) ✓
- Checkpoints: 4 (slides 5 quiz, 12 scenario, 14 quiz, 17 retrieval) — cadence every 3-4 content slides ✓
- Depth: depth-3 throughout (mechanics + edge cases + escalation paths) ✓
- Voice: `technical-collaborative` per engagement-training-config.voice.audience_voice.hrbps
- Includes: scenario card (HRBP-appropriate), 2 quizzes (mechanic verification), retrieval (comprehensive recall)
- Excludes: tradeoff/budget framing (depth-4, exec-only); cascade prompts (manager-only)
