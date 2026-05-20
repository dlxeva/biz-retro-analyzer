<p align="right">
  <a href="./README.md"><strong>English</strong></a> | <a href="./README.zh-CN.md">简体中文</a>
</p>

![Biz Retro Analyzer banner](./assets/banner.svg)

# Biz Retro Analyzer

Turn messy post-meeting materials into evidence-backed analysis artifacts.

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
- judgment and reverse-audit notes
- next-step actions
- reusable method notes

It is designed for conversation-heavy work where the goal is not just to summarize what happened, but to understand:

- how direction shifted
- what each party actually wants
- which issues block progress now
- which evidence gaps can wait but must be revisited later

---

## What This Is

This is **not** a transcription tool and **not** a generic meeting-summary template.

It is an **evidence-first debrief analysis skill** for turning raw conversation material into reusable analysis artifacts.

The skill is especially useful when you have:

- multiple meetings
- different kinds of source material
- mixed fact and interpretation
- layered stakeholder dynamics
- evolving trial scenarios and direction

---

## Best Fit Scenarios

Use this skill for:

- post-meeting debriefs
- partnership or collaboration reviews
- project progression analysis
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

This skill follows four principles:

1. **Evidence first**  
   Source materials are preserved before interpretation.

2. **Facts before judgments**  
   Structured source records come before conclusions.

3. **Stakeholder motives matter**  
   It distinguishes what people said from what they appear to want.

4. **Reverse audit when needed**  
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

## Open-Source Notes

This repository is intentionally written in a generic way.

It should not:

- expose real client names
- hardcode private project identifiers
- preserve personally identifying snippets in examples
- depend on one specific industry to make sense

If you add examples, sanitize them first. See `references/open-source-sanitization.md`.

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
