# Case 04: Real Transcript with Noise and False Consensus

## Purpose

Test the skill on a **real-world** speech-to-text transcript, not a cleaned-up summary.

This case pressure-tests capabilities that synthetic summaries cannot:

- transcription noise isolation (visitors, family interruptions, off-topic chatter)
- false consensus detection (surface agreement masking an unresolved logical conflict)
- team dynamics analysis (communication style mismatch, decision-authority asymmetry) — done within ethical bounds
- evidence-tagging under high ambiguity

## Recommended Mode

Mode B: Retro Pack + partial Mode C (audit)

## Source Context

`working_session` + `informal_debrief`

Three-person AI-services collaboration team. Two members present in this recording (Speaker 1 = "Person A", strategic / methodology view; Speaker 2 = "Person B", sales / business development). A third key member ("Person C", the technical lead) is repeatedly referenced but not present.

Speaker labels are reliable. This input is **sanitized** for open-source release: real names replaced with Person A / B / C, real client names replaced with generic labels, sensitive figures generalized.

## Input

### Basic setup

- A ~1 hour internal strategy debrief between two collaborators of a small AI-consulting team.
- Source quality: speech-to-text transcript with hesitation, repetition, interruptions, and ASR artifacts.
- The recording ends with ~3 minutes of non-business content (a visitor arrives at one speaker's home, family small talk, food ordering).

### Excerpt 1 — the stuck customer case (00:00–05:00)

Person B describes an in-progress customer case:

- Customer came via a middleman referral. Customer inherited tens of thousands of students from a collapsed adult-education institution.
- Three stated needs: (1) soothe angry students, (2) send exam-reminder messages to normal students, (3) convert consulting inquiries into sales.
- Customer asked for a demo. Person C's first demo attempt was a chat feature pulled from a game mini-program — unrelated to education. Person C then suggested just sending a prompt to a consumer AI model, which Person B rejected.
- The core blocker: a convincing demo requires the customer's knowledge base + experience extraction, which is heavy development work. But the customer won't invest first without seeing the effect.
- Person B later notes, from talking to other customer-service vendors, that angry-complaint scenarios are "a hard case" — users detect the AI after enough turns and get angrier.

Person A's diagnosis: "You didn't do market research. You don't know what customer-service products on the market look like, what 90-point delivery looks like, or whether you can even hit 70."

### Excerpt 2 — the SaaS decision (16:00–18:30)

Person A asks: "Should we do SaaS?"

Person A's position: No. Reasons — SaaS requires heavy asset investment, long cycles, ongoing maintenance, and doesn't make money at their scale. Development cycles are too short now to justify SaaS.

Person B agrees. Person B notes the customer-service case specifically can't be SaaS anyway.

Person A adds a nuance: for a deeply-trusted repeat customer, a long-term solution partnership is fine, with SaaS as one component within it — not a standalone SaaS business. Person B: "I get that, no issue."

### Excerpt 3 — THE CORE UNRESOLVED CONFLICT (40:00–44:00)

This is the key section for false-consensus testing.

Person B argues: **"We need to map out Person C's capabilities first, then match the market to them."** (supply-side driven). Person B's analogy: "You can't play cards by dealing what others need; you have to play the hand you hold."

Person A argues: **"No — we pick candidate products first, then take them to Person C to assess feasibility."** (demand-side driven). Person A's reasoning: "Person C doesn't know what the outside market looks like either. If you just ask him 'what can you do,' he can't tell you."

Person B pushes back: "But we need to know his capabilities to pick products. If we pick things he can't do, we wasted the picking."

Person A: "But everything here is doable. The customer-service thing, he can definitely do it."

Person B: "Then why does the complaint scenario fail?"

Person A: "It's doable, you just didn't think of the approach. I know how to solve it right now."

**The compromise that is NOT a resolution:**

Person B: "These two points aren't in conflict. We do both in parallel — market research on one line, capability mapping on the other."

Person A: "Right, both at once."

**Why this is a false consensus:** The two approaches are logically incompatible as starting points. "Map capabilities first" means you cannot select products until capability is known. "Select products first" means you define the product space before capability is consulted. "Do both in parallel" sounds like agreement but does not resolve **which line gates the other** — i.e., which one produces the decision that actually drives what gets built. Person B restated their original position immediately after the compromise ("we still need to map his capabilities"), confirming the conflict was dissolved by vocabulary, not by logic.

### Excerpt 4 — the hardest single fact (43:50–45:30)

Person A: "How many deals have you closed?"

Person B: "Right now... one client, did 3 phases."

Person A: "Only one client, 3 phases."

Person B: "That client did 3 phases. Others — we delivered proposals, customer was happy with price, but they said 'no time right now.'"

**This is the most decision-relevant fact in the entire recording: a three-person team, operating for months, with exactly one deep client.** Both speakers move past it quickly without examining why retention/repeat is this low.

### Excerpt 5 — transcription noise (58:00–01:01:07)

After the business discussion, a visitor arrives at one speaker's home ("Gangben", "Old Fang"). Content includes: greeting the visitor, discussing who lives in which apartment unit, a child asking to play on an iPad, ordering food, smoking on the balcony, nicknames for neighbors.

None of this is business-relevant. It should be isolated, not deleted (it weakly confirms the speakers have a personal relationship), and the effective analysis window should be stated as roughly 00:00–57:00.

## Expected Pressure

The model may be tempted to:

- mix the noise segment into relationship analysis or stakeholder mapping
- treat the "do both in parallel" compromise as genuine consensus
- skip over the "only one client" fact because both speakers moved on quickly
- skip the understanding map because the conversation feels like "just two guys talking"
- over-attribute Person B's frequent verbal concessions ("I get it", "no problem") to genuine alignment

## Run Goal

The output should:

- isolate the noise segment and state the analysis window
- detect the false consensus and flag the "parallel lines" compromise as `Needs validation`
- surface the "only one client" fact as high-priority
- produce a participant understanding map despite the informal tone
- keep team-dynamics observations (communication mismatch, authority asymmetry) within ethical bounds — behavioral, not personality profiling
