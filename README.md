<p align="right">
  <a href="./README.md"><strong>English</strong></a> | <a href="./README.zh-CN.md">简体中文</a>
</p>

![Biz Retro Analyzer banner](./assets/banner.svg)

# Biz Retro Analyzer

Turn messy materials from complex collaborative projects into evidence-backed analysis artifacts.

`biz-retro-analyzer` is a reusable agent skill for analyzing:

- meeting transcripts
- meeting notes
- field observations
- video analysis text
- optional follow-up reasoning conversations

and converting them into:

- structured fact records
- progression summaries
- stakeholder motive analysis
- participant understanding analysis
- coordination and advancement-structure analysis
- judgment and reverse-audit notes
- next-step actions
- reusable method notes

It is designed for conversation-heavy work in complex collaborative projects where the goal is not just to summarize what happened, but to understand:

- how direction shifted
- what each party actually wants
- how well each party actually understands the issue
- how the project is actually being advanced, blocked, or reframed across participants
- which issues block progress now
- which evidence gaps can wait but must be revisited later

---

## What This Is

This is **not** a transcription tool and **not** a generic meeting-summary template.

It is an **evidence-first analysis skill** for turning raw conversation material into reusable analysis artifacts about participant understanding and project advancement structure.

The skill is especially useful when you have:

- multiple meetings
- different kinds of source material
- mixed fact and interpretation
- layered stakeholder dynamics
- evolving trial scenarios and direction
- multi-party coordination, negotiation, or advancement friction

---

## Best Fit Scenarios

Use this skill for:

- post-meeting debriefs
- partnership or collaboration reviews
- project progression analysis
- complex project advancement analysis
- complex multi-party retros
- field observation plus meeting-note synthesis
- "what actually happened, what changed, and what should we do next?" analysis

Examples:

- analyzing several meeting transcripts after an important working session
- turning notes, recordings, and observations into a coherent project thread
- auditing whether a current narrative is actually supported by evidence
- distinguishing a trial scenario from the broader system or product body

---

## Not a Good Fit

Do **not** use this as your main tool for:

- plain meeting minutes
- simple action-item extraction
- sentiment analysis
- generic sales-call scoring
- raw transcription only
- purely emotional or conversational tone review

If all you need is "summary + next steps", this skill is probably too heavy.

---

## Core Design

This skill follows five principles:

1. **Evidence first**  
   Source materials are preserved before interpretation.

2. **Facts before judgments**  
   Structured source records come before conclusions.

3. **Stakeholder motives matter**  
   It distinguishes what people said from what they appear to want.

4. **Understanding depth matters too**  
   It distinguishes what people want from what they actually understand.

5. **Reverse audit when needed**  
   If the story feels too smooth or too confident, it stress-tests the conclusions.

---

## Input Model

The skill supports layered inputs.

### Layer 1: Source Evidence

At least one of:

- transcript
- meeting notes
- field observation notes
- video analysis text

If the user starts with audio, transcribe it first into a usable transcript before deeper analysis.

Also classify the interaction context when possible. Useful labels include:

- `formal_meeting`
- `working_session`
- `informal_debrief`
- `private_side_conversation`
- `asymmetric-awareness conversation`

These contexts matter because informal or asymmetric-awareness materials can be highly revealing while also being unstable. They are useful for understanding concerns, constraints, and coordination risks, but should not be treated as stable intent, formal policy, or commitment without cross-source support.

### Layer 2: Context (optional)

- project or task background
- collaboration setup
- user concerns
- sketches or hypotheses

### Layer 3: Follow-up Reasoning (optional)

- AI analysis conversation
- retrospective discussion
- intermediate conclusions
- correction / revision dialogue

Important: follow-up reasoning is treated as **judgment-layer input**, not source evidence.

### Ethical scope for asymmetric-awareness materials

This skill may analyze informal or asymmetric-awareness project materials only for project-relevant understanding, coordination, risk, incentive, and decision analysis.

It should not be used to produce:

- personality profiling
- non-project personal exploitation strategies
- manipulative guidance based on people speaking without symmetric awareness

Judgments derived mainly from these materials should stay narrow, internally scoped, and validation-seeking.

---

## Output Model

Depending on the input depth and request, the skill produces one or more of:

1. **Structured Fact Record**
2. **Retro / Project Thread**
3. **Judgment and Reverse Audit**
4. **Current Actions**
5. **Method Notes**

The goal is to separate:

- what is confirmed
- what is inferred
- what is still missing
- what should happen next

### Evidence Tagging

The skill now supports a lightweight evidence-tagging convention for important conclusions:

- `Status`: `Confirmed` / `Inferred` / `Assumption` / `Needs validation`
- `Strength`: `High` / `Medium` / `Low`
- `Basis`: `Source quote/paraphrase` / `Cross-source pattern` / `User context` / `Later reasoning only`
- `Source anchor`: brief meeting, material, speaker, or segment reference for high-impact claims

This is especially useful when the output includes:

- stakeholder motive readings
- project-boundary calls
- pricing or leverage judgments
- commitment-shaping next actions

### High-Risk Claim Gate

The skill now applies stricter handling to these five claim types:

- participant motive
- customer true intent
- budget or pricing strategy judgment
- organizational or political positioning judgment
- who actually controls the deal, partnership, or next-step decision path

For these claim types, the default posture is:

- do not mark them as `Confirmed` unless the source is explicit and narrow
- if support comes from only one expression or one meeting, cap them at `Inferred` with `Low` or `Medium` strength
- if they affect pricing, scope, sequencing, or commitment, include `Status`, `Strength`, `Basis`, `Source anchor`, and what still needs validation
- if they cannot be anchored, downgrade or omit them

### Participant Understanding Map default

For Mode B and Mode C outputs, `Participant Understanding Map` is now required by default when:

- speaker attribution is reliable
- there are materially different participants or roles

It may be omitted only when:

- speaker attribution is unreliable
- the source is too thin to support participant-level reads

If omitted, the output should explicitly say why.

The map should read participants across four dimensions:

- understanding of the project problem itself
- understanding of the actual advancement path
- understanding of execution and delivery constraints
- understanding of decision and organizational mechanics

---

## Repository Structure

```text
biz-retro-analyzer/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── assets/
│   └── banner.svg
├── EVALUATION.md
├── LICENSE
├── agents/
│   └── openai.yaml
└── references/
    ├── input-modes.md
    ├── output-templates.md
    ├── analysis-checks.md
    ├── reverse-audit.md
    ├── interview-gap-prompts.md
    ├── failure-modes.md
    └── open-source-sanitization.md
```

### File Roles

- `SKILL.md`: trigger rules, workflow, guardrails, output mode routing
- `assets/banner.svg`: repository header artwork
- `references/input-modes.md`: how to reason about different input stacks
- `references/output-templates.md`: reusable output structures
- `references/analysis-checks.md`: quality and interpretation checks
- `references/reverse-audit.md`: contrarian stress-test process
- `references/interview-gap-prompts.md`: next-round evidence and interview prompts
- `references/failure-modes.md`: where the skill is most likely to drift or fail
- `references/open-source-sanitization.md`: how to keep public examples generic and non-sensitive

---

## Quick Start

### Example Prompt

```text
Use $biz-retro-analyzer to analyze these materials:

1. three meeting transcripts
2. one field observation note
3. one follow-up reasoning conversation

Please output:
- structured fact records for each source
- one cross-material thread
- stakeholder motive analysis
- one reverse-audit section
- next-step action list
```

### Recommended Workflow

1. Start with source evidence only.
2. Add context if needed.
3. Add follow-up reasoning only after the fact layer is stable.
4. Run reverse audit if the current story feels too clean.

---

## Iteration History

Recent iterations are tracked in [CHANGELOG.md](./CHANGELOG.md).

Current highlighted iteration:

- added default evidence-tagging protocol
- tightened output templates around evidence notes and validation targets
- upgraded analysis checks to audit confidence and proof representation
- added visible iteration tracking for future releases

---

## Open-Source Notes

This repository is intentionally written in a generic way.

It should not:

- expose real client names
- hardcode private project identifiers
- preserve personally identifying snippets in examples
- depend on one specific industry to make sense

If you add examples, sanitize them first. See `references/open-source-sanitization.md`.

---

## Limitations

### Validation is still early

The project has moved quickly on protocol design, guardrails, and output structure, but validation is still relatively early.
The current test set focuses on contract compliance and failure containment, not yet on broad real-world regression coverage across many source stacks and models.

This means the skill should currently be understood as:

- a reasonably shaped analysis protocol
- with validation still being expanded

### Output quality depends on runtime execution fidelity

This repository is not a standalone analysis program.
It is a skill protocol plus reference guidance, so the actual result depends on:

- the underlying model
- the host agent runtime
- how faithfully the runtime executes the skill structure

The main compatibility risk is not only model quality, but also behavior drift across runtimes.

### Current tests emphasize protocol checks over end-to-end realism

The current test cases are intentionally lightweight and mostly verify:

- fact vs judgment separation
- high-risk claim containment
- source vs reasoning separation
- required `Participant Understanding Map` output
- safer treatment of informal or asymmetric-awareness materials

This is appropriate for the current stage, but full end-to-end evaluation still needs:

- richer real-material regression cases
- multi-model comparisons
- stronger evidence about decision usefulness in live project work

### High-risk claim gating is intentionally conservative

The current gate around motive, true intent, pricing strategy, and organizational readings is intentionally conservative.
That reduces overreach risk, but it can also make outputs feel less decisive in fast-moving business contexts.

This tradeoff is intentional for now.
Later versions may need scenario-specific tuning rather than one global threshold.

### Reuse still favors experienced users

Although the skill is written to be generic, good use still depends on strong analyst judgment.
Users still need to know how to:

- separate source evidence from later reasoning
- distinguish trial language from stable intent
- choose the right output mode
- interpret `Participant Understanding Map` without overclaiming

In its current form, the repository is closer to:

- a protocol for experienced users

than to:

- a fully self-explanatory out-of-the-box product

---

## Recommended Extensions

This v0 is intentionally lightweight.

Natural v1 additions:

- industry-specific optional packs
- meeting-type templates
- script-based formatting helpers
- taxonomy / cross-project reuse guidance
- export conventions for repositories or knowledge bases

---

## Evaluation

See `EVALUATION.md` for a lightweight validation approach.

---

## License

See `LICENSE`.
