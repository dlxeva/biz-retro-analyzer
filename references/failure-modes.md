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
- separate:
  - domain understanding
  - workflow understanding
  - delivery understanding
  - organizational/political understanding
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
- Did we sanitize private references?
