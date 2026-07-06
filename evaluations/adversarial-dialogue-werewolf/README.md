# Adversarial Dialogue Case: Werewolf Hidden-Role Conversation

This is a synthetic evaluation case for `biz-retro-analyzer`.

It uses a hidden-role conversation game as a stress test for evidence discipline, not as a domain-specific werewolf solver benchmark.

## Why this case exists

The case is designed to pressure-test whether the skill can handle:

- hidden incentives
- conflicting public claims
- strong but misleading speakers
- weak but truthful speakers
- public actions that can be interpreted in more than one way
- role claims that are highly informative but not system-confirmed in the blind input
- a later hidden answer key that must not leak into the blind run

The intended lesson is not `the model guessed the wolves`. The intended lesson is whether the output keeps public evidence, participant claims, model inference, and answer-key truth separate.

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
