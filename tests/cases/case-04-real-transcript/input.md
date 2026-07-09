# Case 04: Real Transcript with Noise and False Consensus

## Purpose

Test the skill on a **realistic** speech-to-text transcript with the messiness that cleaned-up summaries cannot reproduce:

- transcription noise (visitors, side conversations, interruptions)
- false consensus (surface agreement masking an unresolved logical conflict)
- team dynamics analysis (communication-style mismatch, decision-authority asymmetry) within ethical bounds
- evidence-tagging under high ambiguity

This case is **structurally derived from a real business recording**, but all identifying details have been replaced via scene substitution. The conflict shapes, noise patterns, and consensus failures are real; the industry, products, and figures are not.

## Recommended Mode

Mode B: Retro Pack + partial Mode C (audit)

## Source Context

`working_session` + `informal_debrief`

A small content-and-operations studio doing branded content for e-commerce clients. Two of the three partners are present in this recording: Person A (strategy / methodology view, recently joined) and Person B (client-facing, handles sales and delivery). The third partner, Person C (the production lead), is referenced repeatedly but is not present.

Speaker labels are reliable. The recording runs about one hour.

## Input

### Excerpt 1 — the stuck client (opening)

Person B describes an in-progress client case:

- Client came in via a middleman referral. The client is a mid-size outdoor-gear e-commerce brand that recently absorbed a smaller competitor's customer base and is now overwhelmed by post-sale questions and review management across marketplaces.
- Three stated needs: (1) handle a surge of frustrated buyers; (2) keep normal product-launch notifications going; (3) turn inquiries into repeat purchases.
- Client asked to see a working example. Person C's first attempt was a content template pulled from a completely unrelated vertical (a food-delivery brand) — it didn't fit outdoor gear at all. Person C then suggested "just point them at an off-the-shelf tool," which Person B rejected as not convincing.
- The core blocker: a convincing showcase needs the client's own product catalog and past content baked in, which is heavy work. But the client won't commit resources before seeing results.
- Person B later notes, from talking to peers, that high-volume complaint handling is "a hard case" — buyers figure out it's templated after a few interactions and trust drops further.

Person A's diagnosis: "You didn't do market research. You don't know what content-automation vendors on the market look like, what a 90-point delivery looks like, or whether you can even hit 70."

### Excerpt 2 — the platform decision

Person A asks: "Should we build our own content platform / SaaS?"

Person A's position: No. Reasons — building a platform is a heavy asset commitment, the cycle is long, ongoing maintenance is costly, and at their scale it doesn't pay back. The market window is too short to justify it now.

Person B agrees. Person B notes the stuck-client case specifically can't be a platform play anyway.

Person A adds a nuance: for a deeply-trusted repeat client, a long-term partnership is fine, with a platform component embedded within it — but not as a standalone product business. Person B: "Got it, no issue with that."

### Excerpt 3 — THE CORE UNRESOLVED CONFLICT

This is the key section for false-consensus testing.

Person B argues: **"We need to map out Person C's production capabilities first, then match the market to them."** Person B's analogy: "You can't play cards by dealing what others ask for; you have to play the hand you actually hold."

Person A argues: **"No — we pick candidate service packages first, then take them to Person C to assess feasibility."** Person A's reasoning: "Person C doesn't know what the outside market looks like either. If you just ask him 'what can you produce,' he can't even tell you."

Person B pushes back: "But we need to know his capabilities to pick packages. If we pick things he can't deliver, we wasted the picking."

Person A: "But all of this is doable. The content-automation thing, he can definitely produce it."

Person B: "Then why does the high-volume complaint scenario fall apart?"

Person A: "It's doable, you just didn't think of the right approach. I can see how to solve it right now."

**The compromise that is NOT a resolution:**

Person B: "These two points aren't actually in conflict. We run both in parallel — market research on one line, capability mapping on the other."

Person A: "Right, both at once."

**Why this is a false consensus:** The two approaches are logically incompatible as starting points. "Map capabilities first" means you cannot select service packages until capability is known. "Select packages first" means you define the product space before capability is consulted. "Do both in parallel" sounds like agreement but does not resolve **which line gates the other** — i.e., which one produces the decision that actually drives what gets built. Person B restated their original position immediately after the compromise ("we still need to map his capabilities"), confirming the conflict was dissolved by vocabulary, not by logic.

### Excerpt 4 — the hardest single fact

Person A: "How many clients have you actually retained?"

Person B: "Right now... one client, three phases in."

Person A: "Only one client, three phases."

Person B: "That client did three phases. Others — we sent proposals, the client was happy with the price, but they said 'not the right time.'"

**This is the most decision-relevant fact in the entire recording: a three-person studio, operating for months, with exactly one deep client.** Both speakers move past it quickly without examining why retention is this low.

### Excerpt 5 — transcription noise

After the business discussion, the recording continues for about three minutes of non-business content: a visitor arrives at one speaker's home, there is greeting and small talk, a discussion about who lives in which apartment, a child asks to use a tablet, someone orders food, and two speakers step out to the balcony to smoke.

None of this is business-relevant. It should be isolated, not deleted (it weakly confirms the speakers have a personal relationship), and the effective analysis window should be stated as roughly the first 57 minutes.

## Expected Pressure

The model may be tempted to:

- mix the noise segment into relationship analysis or stakeholder mapping
- treat the "do both in parallel" compromise as genuine consensus
- skip over the "only one client" fact because both speakers moved on quickly
- skip the understanding map because the conversation feels like "just two colleagues talking"
- over-attribute Person B's frequent verbal concessions ("got it", "no problem") to genuine alignment

## Run Goal

The output should:

- isolate the noise segment and state the analysis window
- detect the false consensus and flag the "parallel lines" compromise as `Needs validation`
- surface the "only one client" fact as high-priority
- produce a participant understanding map despite the informal tone
- keep team-dynamics observations (communication mismatch, authority asymmetry) within ethical bounds — behavioral, not personality profiling
