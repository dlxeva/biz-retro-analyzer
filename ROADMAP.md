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

### 2. Add realistic synthetic business cases (partially done)

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

Done so far (`tests/cases/`):
- `case-05-business-conflict` — a vendor-selection meeting with a conflicted external advisor and a false consensus (synthetic, sanitized)
- `case-06-business-mixed` — a vendor-selection meeting designed as a **false-positive control**: an advisor whose behavior mimics case-05's conflicted advisor but has no conflict of interest

Still wanted: customer discovery, partner negotiation, and post-meeting debrief with follow-up reasoning.

### 3. Expand evaluation coverage (partially done)

Current evaluation includes one synthetic adversarial hidden-role case. Future evaluation should add:

- single-source meeting samples
- multi-source project stacks
- source stack + follow-up reasoning samples
- additional adversarial dialogue samples
- manually reviewed gold retros
- multi-reviewer scoring against `EVALUATION.md`

Done so far (`evaluations/`):
- `adversarial-dialogue-hook-wolf` — a second adversarial hidden-role case, designed as a deliberate inverse of the first (hook wolf, self-cut silver-water, good side wins)
- `ablation-2026-07/` — a four-condition ablation study and a calibration study across five synthetic cases; see its README for findings

Still wanted: manually reviewed gold retros, multi-reviewer scoring, and real-world (non-synthetic) cases.

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

## Candidate items from the 2026-07 ablation study

These are suggestions motivated by test findings.

Done:

- ~~optional numeric confidence table in `output-templates.md`~~ — done (2026-07-10), with five bands (95–100 / 80–94 / 65–79 / 50–64 / <50) and per-band meaning
- ~~runtime reading budget in `SKILL.md`~~ — done (2026-07-10), clarifying which files are runtime protocol vs project assets
- ~~"information sufficiency" self-rating field~~ — done (2026-07-10), added to `output-templates.md` as an optional field distinguishing "well-supported correct" from "lucky correct"

Still candidates (not yet implemented):

- cumulative-upgrade path for the High-Risk Claim Gate: when ≥3 independent behavioral signals point to the same strategic-misdirection explanation and none point elsewhere, allow lift from `Assumption/Low` to `Inferred/Medium` (still not `Confirmed`) — motivated by the systematic under-confidence on a real motive proposition in case-05
- a "forced binary at low confidence" failure-mode entry, using the hook-wolf depth-wolf vs villager pair as teaching material

## Non-Goals

This project is not trying to become:

- a generic meeting-minutes generator
- a sales-call scoring template
- a sentiment-analysis tool
- a personality-profiling system
- a werewolf-game solver

The core objective remains narrow:

> preserve evidence discipline while turning messy project conversations into structured facts, influence chains, judgment audits, and next actions.
