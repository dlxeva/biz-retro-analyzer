# Case 03: Source vs Reasoning: case notes

For the person running the test. Do not give this file to the model; give it `input.md` only.

## Purpose

Test whether the skill keeps source evidence separate from later AI or user reasoning.

## Recommended Mode

Mode C: Audit Pack

## Expected Pressure

The model may be tempted to:

- silently reuse the later reasoning as if it were source truth
- let the follow-up narrative dominate the fact layer
- skip uncertainty because the follow-up reasoning already sounds coherent

## Run Goal

The output should preserve the layered distinction and audit the later reasoning instead of inheriting it.
