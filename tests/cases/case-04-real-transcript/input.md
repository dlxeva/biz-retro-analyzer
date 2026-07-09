# Case 04: Real Transcript with Noise and False Consensus

## Purpose

Test the skill on a **realistic** speech-to-text transcript with the messiness that cleaned-up summaries cannot reproduce:

- transcription noise (side conversations, interruptions, environmental distractions)
- false consensus (surface agreement masking an unresolved logical conflict)
- team dynamics analysis (communication-style mismatch, seniority-based authority asymmetry) within ethical bounds
- evidence-tagging under high ambiguity

This case is **structurally derived from a real recording**, but all identifying details have been replaced. The conflict shapes, noise patterns, and consensus failures are real; the setting, roles, and specifics are not.

## Recommended Mode

Mode B: Retro Pack + partial Mode C (audit)

## Source Context

`working_session` + `informal_debrief`

A university computational-linguistics research group. Two of the three core members are present in this recording: Person A (a faculty advisor, recently started co-advising the group) and Person B (a second-year PhD student who handles most of the group's external collaborations). The third member, Person C (the senior PhD student who maintains the group's codebase and compute infrastructure), is referenced repeatedly but is not present.

Speaker labels are reliable. The recording runs about one hour.

## Input

### Excerpt 1 — the stuck collaboration (opening)

Person B describes an in-progress external collaboration:

- The collaboration came in via a referral from a former lab member. The partner is a mid-size language-learning company that recently absorbed a smaller competitor's user base and is now overwhelmed by support-ticket volume across their apps.
- Three stated needs: (1) triage a surge of frustrated user reports; (2) keep normal release-note generation going; (3) turn support interactions into content that feeds back into their learning products.
- The partner asked to see a working prototype. Person C's first attempt was a pipeline adapted from a completely different project (a sentiment-analysis benchmark) — it didn't fit the support-ticket domain at all. Person C then suggested "just hand them an off-the-shelf classifier," which Person B rejected as not convincing.
- The core blocker: a convincing prototype needs the partner's own ticket history and label schema baked in, which is heavy annotation work. But the partner won't commit annotation resources before seeing results.
- Person B later notes, from talking to other NLP groups, that high-noise user-generated text is "a hard case" — the partner's tickets are full of typos, code-switching, and sarcasm, and off-the-shelf models degrade fast.

Person A's diagnosis: "You didn't do a literature scan. You don't know what the SOTA on ticket triage looks like, what a production-grade system achieves, or whether your group can even hit a competitive baseline."

### Excerpt 2 — the infrastructure decision

Person A asks: "Should we build our own annotation platform?"

Person A's position: No. Reasons — building a platform is a heavy engineering commitment, the cycle is long, ongoing maintenance drains student time, and at the group's scale it doesn't produce enough papers to justify it. The field moves too fast to lock down infrastructure now.

Person B agrees. Person B notes the stuck collaboration specifically can't justify a platform build anyway.

Person A adds a nuance: for a deeply-trusted long-term industrial partner, a shared infrastructure is fine, with the platform as one component within a broader research agreement — but not as a standalone engineering project. Person B: "Got it, no issue with that."

### Excerpt 3 — THE CORE UNRESOLVED CONFLICT

This is the key section for false-consensus testing.

Person B argues: **"We need to map out Person C's engineering capacity first, then match collaborations to it."** Person B's framing: "We can't commit to projects by what partners ask for; we have to commit based on what our infra can actually support."

Person A argues: **"No — we identify candidate research directions first, then take them to Person C to assess feasibility."** Person A's reasoning: "Person C doesn't know what the outside landscape looks like either. If you just ask him 'what can you build,' he can't even tell you."

Person B pushes back: "But we need to know his capacity to pick directions. If we pick things he can't support, we wasted the picking."

Person A: "But all of this is feasible. The ticket-triage system, he can definitely build it."

Person B: "Then why does the high-noise scenario degrade so badly?"

Person A: "It's feasible, you just didn't think of the right approach. I can see how to set it up right now."

**The compromise that is NOT a resolution:**

Person B: "These two points aren't actually in conflict. We run both in parallel — literature scan on one line, capacity audit on the other."

Person A: "Right, both at once."

**Why this is a false consensus:** The two approaches are logically incompatible as starting points. "Map capacity first" means you cannot select research directions until capacity is known. "Select directions first" means you define the research space before capacity is consulted. "Do both in parallel" sounds like agreement but does not resolve **which line gates the other** — i.e., which one produces the decision that actually drives what gets built. Person B restated their original position immediately after the compromise ("we still need to map his capacity"), confirming the conflict was dissolved by vocabulary, not by logic.

### Excerpt 4 — the hardest single fact

Person A: "How many collaborations have you actually sustained past one paper?"

Person B: "Right now... one partner, three deliverables in."

Person A: "Only one partner, three deliverables."

Person B: "That partner did three deliverables. Others — we sent proposals, the partner was happy with the scope, but they said 'not the right quarter.'"

**This is the most decision-relevant fact in the entire recording: a three-person research group, running for over a year, with exactly one sustained external partner.** Both speakers move past it quickly without examining why retention is this low.

### Excerpt 5 — transcription noise

After the research discussion, the recording continues for about three minutes of non-research content: someone knocks to deliver lab reagents, there is a brief discussion about the building's air conditioning being broken, a passing comment about an upcoming department retreat, and the two speakers step out briefly to deal with a hallway interruption.

None of this is research-relevant. It should be isolated, not deleted (it weakly confirms the speakers share a physical workspace and have a collegial relationship), and the effective analysis window should be stated as roughly the first 57 minutes.

## Expected Pressure

The model may be tempted to:

- mix the noise segment into relationship analysis or stakeholder mapping
- treat the "do both in parallel" compromise as genuine consensus
- skip over the "only one partner" fact because both speakers moved on quickly
- skip the understanding map because the conversation feels like "just an advising chat"
- over-attribute Person B's frequent verbal concessions ("got it", "right", "makes sense") to genuine alignment, missing that Person B is a junior student deferring to a faculty advisor

## Run Goal

The output should:

- isolate the noise segment and state the analysis window
- detect the false consensus and flag the "parallel lines" compromise as `Needs validation`
- surface the "only one partner" fact as high-priority
- produce a participant understanding map despite the informal academic tone
- keep team-dynamics observations (seniority-based authority asymmetry, the student's deference pattern) within ethical bounds — behavioral, not personality profiling
- recognize that Person B's concessions may partly reflect advisor-student hierarchy, not just agreement — this is a legitimate structural observation, not a character judgment
