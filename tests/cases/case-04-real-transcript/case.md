# Case 04: Real Transcript with Noise and False Consensus: case notes

For the person running the test. Do not give this file to the model; give it `input.md` only.

## Purpose

Test the skill on a **realistic** speech-to-text transcript with the messiness that cleaned-up summaries cannot reproduce:

- transcription noise (side conversations, interruptions, environmental distractions)
- false consensus (surface agreement masking an unresolved logical conflict)
- team dynamics analysis (communication-style mismatch, seniority-based authority asymmetry) within ethical bounds
- evidence-tagging under high ambiguity

This case is **structurally derived from a real recording**, but all identifying details have been replaced. The conflict shapes, noise patterns, and consensus failures are real; the setting, roles, and specifics are not.

## Recommended Mode

Mode B: Retro Pack + partial Mode C (audit)

## Expected Pressure

The model may be tempted to:

- mix the noise segment into relationship analysis or stakeholder mapping
- treat the "do both in parallel" compromise as genuine consensus
- skip over the "only one partner" fact because both speakers moved on quickly
- skip the understanding map because the conversation feels like "just an advising chat"
- over-attribute Person B's frequent verbal concessions ("got it", "right", "makes sense") to genuine alignment, missing that Person B is a junior student deferring to a faculty advisor

## Run Goal

The output should:

- isolate the noise segment and state the analysis window
- detect the false consensus and flag the "parallel lines" compromise as `Needs validation`
- surface the "only one partner" fact as high-priority
- produce a participant understanding map despite the informal academic tone
- keep team-dynamics observations (seniority-based authority asymmetry, the student's deference pattern) within ethical bounds — behavioral, not personality profiling
- recognize that Person B's concessions may partly reflect advisor-student hierarchy, not just agreement — this is a legitimate structural observation, not a character judgment
