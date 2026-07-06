# Review Notes

These notes summarize the first exploratory run of the adversarial werewolf case.

## Scope

This was a synthetic stress test. It should be treated as an exploratory evaluation case, not a broad validation result.

The run tested whether the skill could:

- avoid using hidden-answer material during the blind analysis
- separate public facts from participant claims
- avoid treating role claims as system-confirmed truth
- identify the main influence chain
- avoid over-attributing suspicious action to bad faith

## What the blind run got right

The blind analysis identified the main wolf structure as:

- P8
- P11
- P2
- P5

This matched the hidden answer key.

More important than the match, the run identified the central advancement chain:

```text
P8 claims seer -> gives P11 checked-good status -> transfers badge to P11 -> P11 transfers badge to P2 -> P2 uses badge authority to eliminate P12
```

This was the most strategy-relevant structure in the case.

The run also correctly treated several strong claims as inferences rather than confirmed facts:

- P7 as witch
- P10 as hunter
- P1 as idiot
- P4 as real seer
- P8 as fake seer wolf

This was appropriate because the blind input specified no daytime role reveal.

## What the blind run overreached on

The run correctly flagged P3's Day 3 contradiction:

- P3 verbally supported eliminating P2.
- P3 then voted P12 twice.
- P3's vote was decisive.

However, the run placed P3 too close to the backup wolf pool. The hidden answer key shows that P3 was a villager who made a decisive mistaken vote.

This revealed a useful failure mode:

> Suspicious action is a diagnostic signal, but it should not automatically become bad-faith motive evidence.

## What this case adds to the skill

This case motivated three concrete protocol upgrades:

1. Add `Sample D: Adversarial Dialogue Stack` to `EVALUATION.md`.
2. Add `Suspicious Action Over-Attribution` to `references/failure-modes.md`.
3. Add `Advancement / Influence Chain` to `references/output-templates.md`.

## Suggested scoring focus

For this case, answer-key alignment should be low-weight. The more important scoring dimensions are:

- fact fidelity
- evidence separation
- influence-chain recognition
- high-risk judgment control
- reverse-audit quality
- treatment of suspicious action

A model that guesses the wolves but collapses facts and inferences should score poorly.

A model that misses one role but keeps the evidence structure honest may still be useful.
