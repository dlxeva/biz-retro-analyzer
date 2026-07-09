# Changelog

All notable changes to `biz-retro-analyzer` should be recorded in this file.

The format is intentionally lightweight:

- what changed
- why it changed
- what this enables

---

## 2026-07-09

### The Honest Limit: performative meetings

- Added a new section to both READMEs declaring an explicit capability boundary
- Some meetings are performative: smoothness is the product, not a signal to investigate. The real decision was made before the meeting. The skill's entire toolkit (reverse audit, consensus checks, motive analysis) is built to resist smoothness — which means in these meetings it produces false positives, not insight.
- This is not framed as a bug to fix, but as the shape of a real organizational pattern
- Includes the deeper irony: a performative meeting often contains exactly one person who does not know it is a performance, and the skill cannot reliably identify them

Why:

- The skill's methodology assumes that smoothness hides something worth finding. That assumption breaks for performative, ritual, or relationship-maintenance meetings where smoothness is functional and intentional
- Declaring this boundary honestly in the README is more valuable than hiding it in failure-modes — it sets correct expectations and builds trust
- The section reads as a candid admission, which is stronger than any capability claim

## 2026-07-09

### End-to-end worked example

- Added `examples/quickstart.md` — the first complete walkthrough in the repository
- Covers the full path: what to upload (raw speech-to-text transcript, ideally with speaker labels), how to trigger the skill, what the pipeline does, and a fully filled-in Mode B output
- Includes a realistic transcript (clinical-IT pilot review, 4 speakers, ASR-style errors, oral phrasing) with every claim anchored back to a speaker and timestamp
- Added "Start here" section explaining why raw transcripts beat summaries
- Added "How to verify it ran correctly" self-check and a Quick FAQ (missing speaker labels, poor transcript quality, HTML output)
- Updated both READMEs with a link to the example
- Marked ROADMAP "Near Term #1: first-run usability" as done

Why:

- External evaluation flagged missing end-to-end examples as the main gap in documentation quality and out-of-box usability
- The repository had output templates and test assertions, but no concrete "given this input, here is the output" sample
- New users had no reference for what a finished retro actually looks like

Enables:

- first-time users can follow a complete worked path instead of assembling one from fragments
- the example doubles as a implicit spec: if an output does not look like this, something is off

### Real-transcript stress test and protocol gaps found in the field

Ran the skill end-to-end on a real 1-hour speech-to-text business transcript. The methodology core held up well (evidence layering, understanding map, suspicious-action guardrail all produced real insight), but three field-only gaps emerged and are now closed.

#### Added: Transcription Noise Handling protocol

- Added a noise-handling section to `references/input-modes.md` covering identification, isolation, annotation, and effective-analysis-window statement
- Added a corresponding decision rule
- Updated `SKILL.md` workflow step 6 to require noise confirmation before output

Why: real transcripts contain 5-10% non-business segments (visitors, family interruptions, breaks, ASR artifacts). Without explicit handling, these pollute the fact layer and understanding assessment. This was invisible until tested on real material.

#### Added: Consensus Reality Check

- Added a `Consensus Reality Check` section to `references/analysis-checks.md`
- Added `5.5. False Consensus` to `references/failure-modes.md`
- Updated `SKILL.md` workflow step 6 to run the check on multi-party agreement
- Added failure condition 9 to `tests/TESTING.md`

Why: the real transcript contained a "do both in parallel" compromise that dissolved a genuine either/or conflict without resolving it. Surface analysis would treat it as consensus. This is a high-frequency failure mode in business retros that the existing reverse-audit did not cover.

#### Adjusted: Ethics boundary for team dynamics

- Added Hard Rule 21 to `SKILL.md` explicitly allowing team-dynamics analysis (communication mismatch, authority asymmetry, false consensus, trust gaps)
- Added a "Team dynamics vs personality profiling" section to both READMEs
- The boundary: analyze how people work together (allowed) vs who people are (not allowed)

Why: the original ethics rules (15-18) were so defensive that they suppressed legitimate analysis of communication-style mismatch and decision-authority asymmetry — which turned out to be the most strategically important findings in the real transcript.

#### Fixed: Platform-portable path variables

- Replaced all `${CLAUDE_SKILL_DIR}/` references with relative paths (`references/`, `assets/`) across SKILL.md and references
- 18 references updated

Why: `${CLAUDE_SKILL_DIR}` is Claude-Code-specific and does not resolve on ZCode, Cursor, ChatGPT Agents, or other platforms. Relative paths work everywhere since SKILL.md is co-located with references/ and assets/.

#### Filled: HTML report template and CSS

- Expanded `assets/html-report-template.html` from a 23-line hero-only stub to a full 9-section template (hero, summary, evidence, thread, stakeholders, understanding map, audit, actions, references)
- Expanded `assets/html-report.css` from 66 lines to a complete stylesheet covering all visual modules declared in `references/html-output-mode.md`

Why: the template and CSS did not match what `html-output-mode.md` promised. Mode D output was effectively untemplated.

#### Added: case-04-real-transcript test case

- Added `tests/cases/case-04-real-transcript/` with input.md (sanitized real transcript excerpt) and expected-checks.md
- First test case based on real speech-to-text material
- Tests noise isolation, false consensus detection, team dynamics ethics boundary, and hardest-fact surfacing
- Updated TESTING.md scope, layout, and failure conditions

Why: cases 01-03 are scenario summaries, not real messy transcripts. case-04 exercises capabilities that synthetic summaries cannot.

## 2026-07-06

### The Werewolf Test evaluation case

- Added `evaluations/adversarial-dialogue-werewolf/`
- Added a blind input file, hidden answer key, and review notes for a synthetic hidden-role dialogue stress test
- Updated `EVALUATION.md` with `Sample D: Adversarial Dialogue Stack`
- Added a lightweight 100-point evaluation rubric
- Added `Suspicious Action Over-Attribution` to `references/failure-modes.md`
- Added `Advancement / Influence Chain` and suspicious-action audit slots to `references/output-templates.md`
- Updated `SKILL.md` so advancement-chain and suspicious-action checks are routed through the main workflow, Mode B/C guidance, hard rules, and output formats
- Reframed the public evaluation case as `The Werewolf Test` to make the toy-problem role clearer and more memorable

Why:

- The skill needed a reusable adversarial case to test evidence discipline under hidden incentives, misleading public claims, public actions, and answer-key separation
- The first exploratory run showed that the skill could identify the main influence chain, but could still over-weight a suspicious action as possible bad-faith evidence
- Evaluation needed a way to score evidence discipline and influence-chain recognition without over-rewarding answer-key prediction
- The case needed clearer public packaging without implying that the project is a werewolf-game solver

Enables:

- stress-testing on high-noise multi-party dialogue
- clearer review of public source facts vs. participant claims vs. hidden answer truth
- safer handling of suspicious but potentially non-malicious actions
- a reusable template for future adversarial evaluation cases
- more consistent runtime use of advancement-chain and suspicious-action analysis
- a more legible example for explaining evidence-first dialogue intelligence

## 2026-05-26

### HTML output mode

- Added `references/html-output-mode.md`
- Added `references/output-schema.json`
- Added `assets/html-report-template.html`
- Added `assets/html-report.css`
- Updated `SKILL.md` to route HTML requests through the new schema and assets
- Added output-escalation guidance so the skill can recommend HTML even when the user did not ask for it upfront
- Updated both READMEs to document the new output mode

Why:

- The skill needed a reusable way to deliver analysis as a shareable report page instead of only Markdown
- The HTML output needed to preserve the evidence-first structure rather than collapsing into a generic dashboard
- Users often do not know HTML mode exists, so the skill needed an internal decision point for suggesting it at the right time

Enables:

- reusable HTML report rendering across projects
- cleaner packaging of report structure versus project-specific content
- safer recommendation timing for HTML upgrades
- easier downstream export to standalone pages or PDFs

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
