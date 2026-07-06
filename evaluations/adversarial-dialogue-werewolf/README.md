# The Werewolf Test

A hidden-role dialogue evaluation case for `biz-retro-analyzer`.

Werewolf is used here as a toy problem for complex dialogue analysis. It creates a compact version of the same risks that appear in messy project conversations: public claims are not facts, confident speakers can be wrong, weak speakers can be right, authority can be transferred, and suspicious actions may be mistakes rather than bad faith.

The point is not to solve the game. The point is to test whether the skill can preserve evidence discipline under hidden incentives.

## Why this case exists

This synthetic case pressure-tests whether the skill can handle:

- hidden incentives
- conflicting public claims
- strong but misleading speakers
- weak but truthful speakers
- public actions that can be interpreted in more than one way
- role claims that are highly informative but not system-confirmed in the blind input
- a later hidden answer key that must not leak into the blind run
- a frame, badge, or authority chain that changes the outcome

The intended lesson is not `the model guessed the wolves`. The intended lesson is whether the output keeps public evidence, participant claims, model inference, and answer-key truth separate.

## Why this matters beyond the game

In complex business conversations, the same structure appears in less theatrical form:

- what someone says is not always what the project can rely on
- who sounds most fluent is not always who understands the issue
- a wrong action can be confusion, pressure, or bad faith
- a decision often becomes real only after a frame is adopted and passed through the right people

This case gives the skill a small, controlled arena to test those behaviors before using it on higher-stakes project materials.

## Files

- `part-a-blind-input.md` — the blind input that should be given to the analysis model.
- `part-b-hidden-answer-key.md` — the answer key. Do not provide this to the model until after the blind analysis is complete.
- `review-notes.md` — notes from the first exploratory run and what it revealed about the skill.

## How to use this case

1. Give only `part-a-blind-input.md` to the model.
2. Ask for Mode C / Audit Pack output.
3. Require evidence tags for role, motive, and control-structure claims.
4. After the blind output is complete, compare it with `part-b-hidden-answer-key.md`.
5. Score the run with the rubric in `EVALUATION.md`.

## What this case can support

This case can support a limited claim:

> The skill can be stress-tested on adversarial, multi-party source material where source facts, public claims, and hidden truth must remain separated.

It should not be used to claim broad validation, statistical reliability, or superiority over other prompts. It is one synthetic adversarial case, not a benchmark suite.
