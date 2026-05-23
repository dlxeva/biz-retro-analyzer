# Changelog

All notable changes to `biz-retro-analyzer` should be recorded in this file.

The format is intentionally lightweight:

- what changed
- why it changed
- what this enables

---

## 2026-05-24

### Interaction-context and ethics boundary upgrade

- Added interaction-context classification guidance:
  - `formal_meeting`
  - `working_session`
  - `informal_debrief`
  - `private_side_conversation`
  - `asymmetric-awareness conversation`
- Updated workflow to preserve source-context differences instead of flattening all transcripts into one evidence type
- Added hard rules limiting how asymmetric-awareness materials may be used
- Added explicit ethical boundary language to the public READMEs

Why:

- Complex project materials often include both formal and informal conversations
- Informal or asymmetric-awareness materials can reveal real concerns, but they also raise interpretation and ethics risks
- The skill needed a clearer boundary between project-relevant analysis and manipulative or personality-level misuse

Enables:

- better source-context discipline
- narrower and safer use of highly revealing informal materials
- clearer internal-vs-formal use boundaries for sensitive judgments

### Positioning and understanding-map reframing

- Reframed the skill from a narrower post-meeting retro tool toward analysis for complex collaborative project advancement
- Updated participant-understanding language to center:
  - the project problem itself
  - the actual advancement path
  - execution and delivery constraints
  - decision and organizational mechanics
- Updated public READMEs to match the more general positioning

Why:

- The prior framing leaned too much toward product or delivery evaluation language
- The real use case is broader: multi-party coordination, negotiation, project advancement, cross-functional alignment, and decision-path analysis

Enables:

- better fit for complex business and coordination work
- less bias toward judging people as product or delivery actors only
- more accurate participant-read outputs for multi-party advancement analysis

### Guardrail tightening for high-risk business readings

- Added a `Source anchor` requirement for high-impact and high-risk claims
- Added a `High-Risk Claim Gate` to `SKILL.md`
- Defined five stricter claim types:
  - participant motive
  - customer true intent
  - budget or pricing strategy judgment
  - organizational or political positioning judgment
  - who actually controls the deal, partnership, or next-step decision path
- Added a required pre-output audit step before final action recommendations
- Updated public READMEs to document the tighter protocol

Why:

- The skill was directionally strong, but medium-capability models could still overstate dramatic business interpretations
- High-impact retros needed stronger default brakes around motive, intent, pricing, and power-structure claims

Enables:

- safer use on mixed-quality models
- fewer unanchored stakeholder or pricing narratives
- more stable evidence discipline before later evaluation cases are added

### Participant understanding output requirement

- Updated `SKILL.md` so Mode B and Mode C outputs must include `Participant Understanding Map` by default
- Added explicit omission rules: only unreliable speaker attribution or insufficient participant-level evidence can justify omission
- Updated public READMEs to reflect the stronger default

Why:

- The skill's strategy value depends not only on motive analysis, but also on identifying who actually understands the domain, workflow, delivery reality, and organizational constraints
- Leaving this section optional made it too easy for models to drift into motive-heavy output and skip the understanding layer

Enables:

- more consistent participant-capability analysis
- stronger separation between motive reads and understanding reads
- better downstream strategy decisions about explanation depth, pricing, sequencing, and collaboration

## 2026-05-22

### Evidence-tagging upgrade

- Added a default evidence-tagging protocol to `SKILL.md`
- Standardized claim-status tags: `Confirmed`, `Inferred`, `Assumption`, `Needs validation`
- Standardized evidence-strength tags: `High`, `Medium`, `Low`
- Added source-basis guidance so outputs can distinguish direct source support from later reasoning

Why:

- Important retro judgments were useful, but still too easy to read as settled facts
- High-impact calls around pricing, scope, leverage, and next actions needed clearer support labels

Enables:

- more auditable retros
- cleaner fact-vs-judgment separation
- safer reuse across multi-meeting project threads

### Output-template tightening

- Updated `references/output-templates.md` to include evidence-tagging guidance
- Added structured slots for evidence notes, evidence-risk notes, high-impact claims requiring validation, and action evidence notes

Why:

- The skill needed a default output shape for evidence-aware writing instead of ad hoc annotation

Enables:

- easier repeated use
- more consistent outputs across runs
- clearer downstream review by humans

### Analysis-check upgrade

- Expanded `references/analysis-checks.md` to verify whether major claims are tagged correctly
- Added checks for weak evidence, pricing/leverage overreach, and provisional next-step recommendations

Why:

- The skill needed to review not only content quality, but also whether confidence and proof were represented honestly

Enables:

- better self-auditing
- fewer overconfident retros

### Iteration visibility

- Added this changelog
- Added iteration-history sections to the public READMEs
- Added publishing guidance to keep future iterations visible

Why:

- Once the skill starts evolving, users need to see what changed without diffing files

Enables:

- lightweight release tracking
- easier public repo maintenance
