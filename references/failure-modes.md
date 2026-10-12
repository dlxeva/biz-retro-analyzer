# Failure Modes

Use this file to understand where `biz-retro-analyzer` is most likely to fail or drift.

The point is not to avoid all mistakes.  
The point is to notice predictable failure patterns early.

## 1. Fact / Judgment Collapse

### What happens

Later reasoning, strong user framing, or AI follow-up analysis gets quietly upgraded into source truth.

### Typical symptoms

- clean conclusions appear too early
- a later retrospective line is quoted as if it came from the original meeting
- uncertainty disappears without new evidence

### Correction

- rebuild the fact layer first
- tag every input by source type
- explicitly mark later reasoning as judgment-layer only

---

## 2. Stakeholder Flattening

### What happens

Different parties get collapsed into one generic "client" or "stakeholder" blob.

### Typical symptoms

- no distinction between sponsor, operator, gatekeeper, evaluator, or resourcer
- conflicting motives disappear in the final summary
- next-step advice becomes too generic

### Correction

- preserve role-by-role reading
- separate `what they said` from `what they appear to want`
- do not merge people just because they sit on the same side of the table

---

## 2.5. Speaker Attribution Hallucination

### What happens

The analysis assigns specific statements or motives to named roles even though the source material did not reliably label speakers.

### Typical symptoms

- "the buyer said..." even though the transcript had no labels
- strong role claims built from unlabeled text blocks
- clean stakeholder tables built from ambiguous source material

### Correction

- enter `speaker-unknown mode`
- preserve anonymous or position-level reading
- explicitly state that stakeholder mapping is weakened by missing speaker labels
- recommend relabeling the source if stronger motive analysis is needed

---

## 3. Trial Scenario Lock-In

### What happens

A first tactical trial scenario gets mistaken for the long-term system or product body.

### Typical symptoms

- all recommendations become overly specific to one pilot
- the final summary treats one scene as the full product definition
- expansion paths disappear

### Correction

- explicitly separate `trial scenario` from `product/system body`
- ask whether the current narrowing is strategic or tactical

---

## 4. Momentum = Validation Error

### What happens

Excitement, alignment, or forward motion gets treated as evidence that the direction is correct.

### Typical symptoms

- "they're excited" becomes "they need this"
- "the meeting went well" becomes "the scope is settled"
- current progress is treated as proof of later willingness to pay or adopt

### Correction

- distinguish momentum from validation
- mark what is accepted socially vs. what is validated operationally

---

## 4.5. Competence Illusion

### What happens

A speaker sounds decisive, senior, or fluent, and the analysis quietly upgrades that into real issue understanding.

### Typical symptoms

- airtime is mistaken for expertise
- political understanding is mistaken for delivery understanding
- high-level framing is mistaken for domain depth
- a participant is treated as a reliable source on implementation when the material only shows strategic posture

### Correction

- add a participant understanding map
- separate the four map columns:
  - problem itself (domain understanding)
  - advancement path (workflow understanding)
  - execution / delivery constraints
  - decision / organizational mechanics (organizational/political understanding)
- preserve mixed or partial understanding when the material supports only that

---

## 4.6. Understanding-without-Strategy Drop

### What happens

The analysis correctly notices who understands the issue and who does not, but fails to turn that into practical strategy.

### Typical symptoms

- participant understanding map exists, but nothing changes downstream
- the output says someone is shallow or deep, but does not explain why it matters
- next-step advice ignores who should be educated, challenged, trusted, or bypassed

### Correction

- add a strategy implication block after participant understanding analysis
- specify how understanding levels should change:
  - explanation depth
  - evidence burden
  - demo style
  - proposal wording
  - whose feedback should shape scope

---

## 4.7. Suspicious Action Over-Attribution

### What happens

A participant's inconsistent, strategically costly, or suspicious action gets upgraded too quickly into bad-faith motive, hidden agenda, or confirmed control of the situation.

### Typical symptoms

- a mismatch between what someone says and what they later do is treated as proof of deception
- a wrong vote, wrong recommendation, or wrong escalation is treated as motive evidence without checking pressure, confusion, or new information
- the analysis correctly spots an anomaly but explains it with the most dramatic interpretation
- one high-impact mistake makes earlier evidence disappear

### Correction

Before turning suspicious action into motive analysis, split the explanation space into at least three possibilities:

1. **Information change** — the actor may have received, noticed, or weighted new information.
2. **Pressure or misjudgment** — the actor may be confused, rushed, socially pressured, or persuaded by a stronger speaker.
3. **Strategic misdirection** — the actor may be deliberately reframing, hiding intent, or controlling the outcome.

Only upgrade to a strong motive claim when multiple source anchors support the strategic-misdirection explanation. Otherwise mark the claim as `Needs validation` and preserve the lower-intent explanations.

---

## 5. Current Blocker / Later Gap Confusion

### What happens

A missing detail gets treated as if it blocks current progress, or a future risk gets ignored because it does not block today.

### Typical symptoms

- analysis gets stuck chasing completeness too early
- later implementation or acceptance risks are dropped entirely

### Correction

- label issues as:
  - current blocker
  - non-blocking but real gap
  - later-stage evidence need

---

## 5.5. False Consensus

### What happens

A multi-party discussion appears to reach agreement, but the underlying logic of each party is not actually compatible. The "consensus" is real in tone but fake in substance, and surfaces later as execution conflict or silent drift.

### Typical symptoms

- someone agrees to a frame, then immediately restates their original position in different words
- a genuine either/or disagreement is dissolved by saying "let's do both" or "two lines in parallel" without checking compatibility
- agreement arrives suspiciously fast after a dominant participant introduces a frame
- the parties who agreed do not actually own the execution of the decision
- later statements or actions quietly contradict the earlier stated agreement
- the "consensus" is mostly one narrator's framing that others stopped resisting

### Correction

- treat fast agreement after a strong frame as a signal to probe deeper, not as settled
- check whether a "do both" compromise is logically compatible, or just a way to avoid the real choice
- flag decisions resting on this pattern as `Needs validation`
- see the Consensus Reality Check in `references/analysis-checks.md`

---

## 5.6. Post-Meeting Rewrite Accepted as Record

### What happens

The minutes, a follow-up email, or a group-chat summary restates what was decided, and the analysis takes that restatement as the decision. The person who wrote it may have narrowed, widened, or reordered what was said.

### Typical symptoms

- the fact layer quotes the minutes but not the transcript for a decision
- "decided" or "confirmed" appears where the recording only shows a trial, a condition, or a request
- priorities in the summary differ from the order the decision-maker gave

### Correction

- treat a written summary as evidence that its author framed the outcome that way, not as evidence of the outcome
- compare written conclusions with the transcript line by line (Minutes vs Recording table in `output-templates.md`)
- mark each item `consistent`, `partial`, or `inconsistent`, and anchor both sides

---

## 5.7. Authority Vacuum

### What happens

Nobody with authority actually decides, but the meeting ends as if something was decided. The analysis fills the gap by naming whoever spoke last or loudest as the decision-maker.

### Typical symptoms

- the decision ledger has a decision with no `Decided by`, or the decider was not in the room
- "we agreed" with no explicit yes from the person who owns budget or headcount
- next steps that depend on resources no one committed

### Correction

- record `Decided by` only when the source shows someone with authority saying yes
- otherwise record the item as proposed (status `Needs validation`), and name who still has to decide
- list the missing decision under `Must validate before deeper commitment`

---

## 5.8. Partial Attendance

### What happens

A key person joins late, leaves early, or misses part of the discussion. The analysis treats everyone as having heard everything, so it reads silence as agreement or blames someone for ignoring a point made while they were out.

### Typical symptoms

- a participant is said to have "accepted" something raised after they left
- a decision is attributed to the whole room when the decider heard only part of the argument
- changes made after a decision-maker left are reported as that person's decision

### Correction

- note join and leave times in the analysis window when the source shows them
- check each decision and agreement against who was present at that timestamp
- flag changes made after the decision-maker left as unratified

---

## 6. Narrative Capture

### What happens

The user's or one participant's current storyline becomes the hidden backbone of the whole analysis.

### Typical symptoms

- analysis "feels right" but is weakly sourced
- one narrator's language dominates the output
- reverse audit finds very little because none was really attempted

### Correction

- summarize the current narrative explicitly
- then run reverse audit against it
- ask: what would falsify this story?

---

## 7. Over-Generic Output

### What happens

The analysis becomes polished but shallow.

### Typical symptoms

- lots of executive-summary language
- little source-specific structure
- action items that could apply to any project

### Correction

- force source-by-source structure first
- require at least some evidence-tied claims
- use project-specific wording only when it is actually supported

---

## 8. Open-Source Leakage

### What happens

Examples, README language, or templates retain too much trace of one real project.

### Typical symptoms

- real organization names appear
- sensitive process details remain
- repo only makes sense if the reader knows the original case

### Correction

- sanitize examples
- generalize labels
- remove private shorthand
- review with `open-source-sanitization.md`

---

## Quick Pre-Release Checklist

Before publishing or sharing:

- Did we preserve fact vs judgment separation?
- Did we distinguish stakeholder motives?
- Did we separate trial scenario from product body?
- Did we mistake momentum for proof?
- Did we mark non-blocking gaps?
- Did we avoid over-attributing suspicious action to bad faith?
- Did we check written summaries against what was actually said, and who was present?
- Did we sanitize private references?
