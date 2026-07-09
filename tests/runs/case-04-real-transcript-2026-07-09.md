# Run Record: case-04-real-transcript

- **Case**: `tests/cases/case-04-real-transcript/`
- **Date**: 2026-07-09
- **Mode**: Mode C / Audit-oriented run
- **Input type**: sanitized real speech-to-text transcript excerpt
- **Purpose**: field-test protocol behavior on noisy, realistic business material
- **Result**: useful run with protocol gaps discovered and closed

## What the run tested

This run was used to test capabilities that synthetic summaries did not exercise well:

1. transcription noise isolation
2. false consensus detection
3. team dynamics analysis within ethical bounds
4. participant understanding map under messy speech-to-text conditions
5. suspicious-action handling without over-attributing motive

## What held up

The methodology core held up well:

- evidence layering remained useful
- participant understanding analysis produced strategy-relevant differences
- suspicious-action guardrails prevented some overconfident motive reads
- the run surfaced real project structure rather than only summarizing the transcript

## What failed or was missing before the update

The run exposed three field-only gaps:

1. **Transcript noise needed explicit handling**
   - Real transcripts contain interruptions, irrelevant segments, breaks, ASR errors, and non-business material.
   - Without a noise protocol, these can pollute the fact layer and participant understanding assessment.

2. **Fast agreement could hide false consensus**
   - A surface compromise such as `do both in parallel` may dissolve a real either/or conflict without resolving it.
   - The skill needed a specific consensus reality check rather than treating alignment as settled.

3. **Ethics boundaries were too defensive around team dynamics**
   - The original guardrails correctly blocked personality profiling.
   - They also risked suppressing legitimate project-relevant observations about communication mismatch, authority asymmetry, trust gaps, and collaboration friction.

## Follow-up changes made

The field run led to these protocol upgrades:

- added transcription noise handling guidance in `references/input-modes.md`
- added Consensus Reality Check guidance in `references/analysis-checks.md`
- added `False Consensus` to `references/failure-modes.md`
- added a team-dynamics boundary to the READMEs and `SKILL.md`
- updated `SKILL.md` pre-output audit to check noise isolation and false consensus
- added `case-04-real-transcript` to the concrete test set

## Pass / fail interpretation

This run should not be read as a clean benchmark pass.

It is better interpreted as a field-discovery run:

- **Passed**: the core evidence-first method produced useful structure.
- **Failed / exposed gap**: the protocol needed explicit rules for transcript noise, false consensus, and ethical team-dynamics analysis.
- **Outcome**: gaps were converted into durable protocol checks and test coverage.

## Reviewer note

When rerunning case-04, treat a result as failed if it:

- mixes transcription noise into the fact layer
- treats a quick compromise as settled consensus without validation
- avoids all team-dynamics analysis out of over-cautious ethics framing
- drifts into personality profiling instead of observable collaboration behavior
- omits `Participant Understanding Map` without a valid omission reason
