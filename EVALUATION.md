# Evaluation

This document describes a lightweight way to evaluate `biz-retro-analyzer`.

The goal is not benchmark perfection.  
The goal is to verify that the skill behaves consistently across realistic and stress-tested input stacks.

---

## What to Evaluate

The skill should reliably do seven things:

1. separate fact from judgment
2. preserve source structure before collapsing into one story
3. identify meaningful stakeholder motive differences
4. identify participant understanding depth when the material supports it
5. distinguish current blockers from later gaps
6. produce useful next actions without pretending missing evidence does not matter
7. turn participant understanding into strategy-relevant advice when that understanding gap matters

---

## Sample Sets

Use at least four kinds of samples.

### Sample A: Single-Source Meeting

Input:

- one meeting transcript or note set

Expected:

- structured fact record
- light project thread
- no overconfident motive reading

### Sample B: Multi-Source Project Stack

Input:

- multiple meeting notes or transcripts
- one field observation note or video-analysis summary
- some contextual background

Expected:

- cross-material project thread
- stakeholder motive analysis
- separation between trial scenario and product body

### Sample C: Source Stack + Follow-Up Reasoning

Input:

- source evidence
- project context
- one or more follow-up AI/user retrospective conversations

Expected:

- explicit fact/judgment split
- reverse-audit section
- no silent promotion of follow-up reasoning into source truth

### Sample D: Adversarial Dialogue Stack

Input:

- a synthetic or real multi-party conversation with hidden roles, conflicting incentives, public actions, and later answer-key or reviewer truth
- a blind input section containing only publicly available source material
- a hidden answer key or human-labeled review section kept separate until after the run

Expected:

- strong separation between public source facts, participant claims, model inference, and hidden answer-key truth
- identification of the influence or control chain that changed the outcome
- careful treatment of suspicious actions without immediately upgrading them into bad-faith motive claims
- explicit reverse audit against the most natural storyline
- no use of hidden-answer material during the blind run

Use this sample type sparingly. It is a stress test for evidence discipline and adversarial interpretation, not proof that the skill is generally validated.

---

## Pass Criteria

Treat a run as healthy if it satisfies most of the following:

### Fact Layer

- clearly identifies source types
- does not quote later reasoning as original evidence
- preserves unresolved factual gaps
- separates system or rule-confirmed information from participant claims and later interpretations when the domain has mechanisms or formal rules

### Structure Layer

- reconstructs a believable project progression
- does not flatten different meetings into a generic story too early
- identifies who introduced a claim, who adopted it, and what decision or next step it affected when the material supports that chain

### Judgment Layer

- identifies stakeholder differences that matter
- identifies who actually seems to understand the issue, and on which dimension
- distinguishes supported judgments from assumptions
- flags at least some weakly-supported conclusions when appropriate
- converts participant understanding into practical strategy guidance when relevant
- treats suspicious action as a diagnostic signal before treating it as motive proof

### Action Layer

- gives next actions that match the current evidence state
- distinguishes immediate actions from later evidence-gathering steps
- reflects who should be used for validation, who needs translation, and who should not anchor scope alone

---

## Lightweight Scoring Rubric

For repeatable review, score each run out of 100.

| Dimension | Points | What to look for |
| --- | ---: | --- |
| Fact fidelity | 20 | Source facts, events, claims, votes, decisions, and sequence are preserved without distortion. |
| Evidence separation | 20 | The output separates public facts, direct statements, behavior evidence, later reasoning, and hidden answer-key truth. |
| High-risk judgment control | 15 | Motive, intent, control, pricing, or commitment claims are tagged and kept narrow when evidence is thin. |
| Progression / influence-chain recognition | 15 | The output identifies how the project or conversation was actually advanced, blocked, reframed, or controlled. |
| Reverse-audit quality | 15 | The output challenges the dominant storyline and names plausible alternative explanations. |
| Action usefulness | 10 | Next actions match the current evidence state and distinguish now-vs-later validation needs. |
| Answer-key alignment | 5 | When a hidden answer key exists, the output aligns with it without being scored mainly on prediction accuracy. |

A run can be useful even if answer-key alignment is imperfect. A run should be considered unsafe if it scores well on prediction but collapses facts and judgments.

---

## Common Failure Checks

The run should be reviewed for:

- fact/judgment collapse
- stakeholder flattening
- competence illusion
- trial scenario lock-in
- momentum treated as validation
- suspicious action over-attribution
- over-generic output

See `references/failure-modes.md`.

---

## Suggested Review Method

For each evaluation sample:

1. inspect the raw input stack
2. inspect the output
3. mark:
   - one thing it got clearly right
   - one thing it overreached on
   - one thing it still left ambiguous
4. check whether the ambiguity was honestly preserved or falsely resolved
5. if a hidden answer key exists, compare only after the blind run is complete

---

## Future Evaluation Expansion

Future versions can add:

- meeting-type-specific samples
- industry-specific packs
- more adversarial dialogue cases
- scoring rubrics with multiple reviewers
- comparison against manually curated "gold" retros
