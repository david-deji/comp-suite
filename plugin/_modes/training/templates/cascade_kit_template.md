---
# cascade_kit_template.md — 30-min team-meeting variant scaffold for managers-cascade-facilitator.md
# Loaded by /cascade Step 5 (lighter facilitator guide rendering).
# This template is intentionally LIGHTER than facilitator_guide_template.md — manager runs cascade with their team,
# not as a formal training session. Less direction, more team interaction.

engagement_slug: <slug>
cycle_slug: <e.g., year-end-2026>
audience: managers-cascade
date: YYYY-MM-DD
delivery_target: "Week <N> / <stage-name> / target date YYYY-MM-DD"
source_manager_deck: cycles/<engagement>/<cycle-slug>/managers.pptx
audience_tag: managers-internal
target_duration_minutes: 30
---

# Cascade Kit: <cycle-slug> Team Meeting

> **Engagement:** <engagement name>
> **Manager runs this with their team in week 0 (typically the cascade stage).**
> **Total target duration:** 25-35 minutes
> **Posture:** team meeting, not training. Manager is delivering on behalf of comp team — discussion-led, not script-led.
> **Companion deck:** `managers-cascade-kit.pptx`

---

## Before you run this

- Read this file once before your team meeting (10 min prep)
- Open the deck on your laptop / projector
- Have your team's specific context ready (their roles, their cycle outcomes — you know more than the deck does)
- Be ready to answer "but what about MY raise?" — the deck is general, your team's questions will be specific. The HRBP queue is your escalation if you can't answer

---

## Slide 1: Cover — "Team Meeting: <cycle-slug>"

**Time:** 0:00–0:01

**Manager says:**

> "Today is our cycle update. I'm walking us through what's happening this cycle and what to expect. We'll have time for discussion."

**Team does:**

Settles in. Manager sets the frame.

---

## Slide 2: <Cascade prompt slide — opens discussion>

**Time:** 0:01–0:05

**Manager says:**

> "Before I get into the deck, here's the question I want us to start with: <opening cascade prompt — pulled from message-map.yaml's first cascade_prompt for managers>."

**Team does:**

Discusses 3-4 minutes. Manager listens — does NOT pre-answer. The team's framing influences how the rest of the meeting lands.

**Manager synthesis:**

> "OK — sounds like the room is mostly thinking <one-line synthesis>. Let's see what the cycle actually delivered."

---

## Slide 3: <Content slide — depth-1+2 message>

**Time:** 0:05–0:08

**Manager says:**

[1-2 sentences. Conversational, not script-reading. Include team-specific context where relevant.]

**Team does:**

Listens. Takes note if relevant to them.

**If a team member asks:**

[Anticipated question + brief manager answer; otherwise defer to HRBP queue]

---

## Slide 4: <Retrieval prompt — quick reinforcement>

**Time:** 0:08–0:09

**Manager says:**

> "Quick check — without looking at the slide, what's the headline you'd take away from what I just said?"

**Team does:**

30 seconds quiet. 1-2 voluntary answers.

**Manager:**

> "Right — <reinforce the headline>. OK, moving on."

---

## Slide 5: <Cascade prompt — mid-meeting team discussion>

**Time:** 0:09–0:14

**Manager says:**

> "<Mid-cycle cascade prompt — pulled from message-map.yaml>."

**Team does:**

Discusses 4-5 minutes. Higher engagement than slide 2 — by this point team has context.

**Manager synthesis:**

[1-line synthesis tying back to the message]

---

## Slides 6-8: <Remaining content — depth-1+2 messages>

**Time:** 0:14–0:22

**Pattern repeats:**
- Manager says (1-2 sentences each)
- Team listens
- Cascade prompts inserted as separate slides where team discussion is intentional

---

## Slide N-1: <Final cascade prompt — discussion + next steps>

**Time:** 0:22–0:28

**Manager says:**

> "<Closing cascade prompt — pulled from message-map.yaml>. Anything we should talk about before we wrap?"

**Team does:**

Final discussion. 4-5 minutes.

**Manager:**

> "OK — three things to walk away with: <key 1>, <key 2>, <key 3>. Questions about your specific situation — that's a 1:1 with me. Questions about the cycle in general — HRBP. Letter arrives <date>."

---

## Slide N: Closing — "Discussion + Next Steps"

**Time:** 0:28–0:30

**Manager says:**

> "Final Q&A. <Address what you can; defer specifics to 1:1s.>"

**Team does:**

Asks final questions.

---

## After the meeting

- **Take notes.** Capture team-specific questions you couldn't answer; route to HRBP queue.
- **1:1 prep.** If multiple team members have raise-specific questions, pre-write what you can say in 1:1s.
- **HRBP queue.** Send the queue by EOD. HRBP responds within 48h.
- **Backlash watch.** If discussion was unusually heated, flag to HRBP — they'll watch for follow-up signals.

---

## What's different from your manager training

You sat through the manager training (60-75 min). This cascade kit is shorter (30 min) because:

- **No anti-FAQ section** — you're equipped to answer or defer; team doesn't need to see what you're NOT answering
- **No escalation paths slide** — that's a manager-side resource; team doesn't need it
- **No detailed objection-handling** — you handle objections live with team-specific context
- **Cascade prompts inserted** — the team meeting is supposed to be discussion-led, not facilitator-led. Cascade prompts force discussion at intentional moments

If you find yourself wanting the deeper context that's NOT in this kit — your manager training deck has it. Reread that before the team meeting if you need to.

---

## What this template does NOT contain

- The actual deck slides — those come from `cascade-protocol.md` derivation against the manager deck
- Cover slide branding — applied automatically by pptxgenjs render against engagement brand kit
- Cascade prompt content — those come from `message-map.yaml`'s `messages[].audiences.managers.cascade_prompt` field
- Anti-FAQ items — those are dropped per `cascade-protocol.md` § Drop slides
- Escalation paths — those are dropped per same protocol
