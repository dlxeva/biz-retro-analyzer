# Roadmap

`biz-retro-analyzer` is currently an experimental agent skill protocol for evidence-first dialogue intelligence.

The roadmap is intentionally small. The priority is to make the skill easier to try, easier to evaluate, and safer to reuse.

## Current State

Already available:

- evidence-first source and judgment separation
- structured fact records
- project thread / retro outputs
- participant understanding maps
- advancement / influence-chain analysis
- suspicious-action over-attribution guardrail
- reverse-audit guidance
- HTML report mode
- The Werewolf Test as a synthetic adversarial evaluation case

## Near Term

### 1. Improve first-run usability (done)

- ~~add more copy-paste prompt examples~~ — done in `examples/quickstart.md`
- ~~add a minimal business-meeting example~~ — done, clinical-IT pilot scenario
- ~~add a short `How to use this skill` section for non-technical users~~ — done, "Start here" + "What the skill does with it" sections

### 2. Add realistic synthetic business cases

Add one or more sanitized examples that are closer to the intended business use case:

- customer discovery conversation
- partner negotiation
- multi-party project review
- post-meeting debrief with follow-up reasoning

Each case should include:

- input stack
- expected output mode
- sample output
- review notes

### 3. Expand evaluation coverage

Current evaluation includes one synthetic adversarial hidden-role case. Future evaluation should add:

- single-source meeting samples
- multi-source project stacks
- source stack + follow-up reasoning samples
- additional adversarial dialogue samples
- manually reviewed gold retros
- multi-reviewer scoring against `EVALUATION.md`

### 4. Tighten public packaging

- keep the repository framing centered on evidence-first dialogue intelligence
- avoid letting The Werewolf Test make the project look like a game solver
- add short release notes for major protocol changes
- add topic and usage guidance for distribution

## Later

Possible later work:

- CLI wrapper for local runs
- richer HTML report examples
- JSON export examples for downstream systems
- model-comparison runs across different LLMs
- benchmark-style evaluation pack once enough cases exist

## Non-Goals

This project is not trying to become:

- a generic meeting-minutes generator
- a sales-call scoring template
- a sentiment-analysis tool
- a personality-profiling system
- a werewolf-game solver

The core objective remains narrow:

> preserve evidence discipline while turning messy project conversations into structured facts, influence chains, judgment audits, and next actions.
