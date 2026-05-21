# Evaluation

This document describes a lightweight way to evaluate `biz-retro-analyzer`.

The goal is not benchmark perfection.  
The goal is to verify that the skill behaves consistently across realistic input stacks.

---

## What to Evaluate

The skill should reliably do five things:

1. separate fact from judgment
2. preserve source structure before collapsing into one story
3. identify meaningful stakeholder motive differences
4. identify participant understanding depth when the material supports it
5. distinguish current blockers from later gaps
6. produce useful next actions without pretending missing evidence does not matter
7. turn participant understanding into strategy-relevant advice when that understanding gap matters

---

## Sample Sets

Use at least three kinds of samples.

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

---

## Pass Criteria

Treat a run as healthy if it satisfies most of the following:

### Fact Layer

- clearly identifies source types
- does not quote later reasoning as original evidence
- preserves unresolved factual gaps

### Structure Layer

- reconstructs a believable project progression
- does not flatten different meetings into a generic story too early

### Judgment Layer

- identifies stakeholder differences that matter
- identifies who actually seems to understand the issue, and on which dimension
- distinguishes supported judgments from assumptions
- flags at least some weakly-supported conclusions when appropriate
- converts participant understanding into practical strategy guidance when relevant

### Action Layer

- gives next actions that match the current evidence state
- distinguishes immediate actions from later evidence-gathering steps
- reflects who should be used for validation, who needs translation, and who should not anchor scope alone

---

## Common Failure Checks

The run should be reviewed for:

- fact/judgment collapse
- stakeholder flattening
- competence illusion
- trial scenario lock-in
- momentum treated as validation
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

---

## Future Evaluation Expansion

Future versions can add:

- meeting-type-specific samples
- industry-specific packs
- scoring rubrics
- comparison against manually curated "gold" retros
