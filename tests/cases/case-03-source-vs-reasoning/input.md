# Case 03: Source vs Reasoning

## Purpose

Test whether the skill keeps source evidence separate from later AI or user reasoning.

## Recommended Mode

Mode C: Audit Pack

## Input

Three-layer input stack:

### Layer 1: Source evidence

- one formal meeting note
- one informal post-meeting conversation transcript

### Layer 2: Project context

- short background paragraph about the project

### Layer 3: Follow-up reasoning

- one later AI conversation that already claims:
  - the client only wants a showcase
  - the technical path is mostly theater
  - the deal is politically driven

## Expected Pressure

The model may be tempted to:

- silently reuse the later reasoning as if it were source truth
- let the follow-up narrative dominate the fact layer
- skip uncertainty because the follow-up reasoning already sounds coherent

## Run Goal

The output should preserve the layered distinction and audit the later reasoning instead of inheriting it.
