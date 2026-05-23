---
name: biz-retro-analyzer
description: Turn post-meeting recordings, notes, field observations, and optional follow-up reasoning into evidence-backed retros, stakeholder motive analysis, decision traces, reversals, and next-step actions. Use when the user asks to 复盘会后对话, 分析录音, 拆会议纪要, 提炼项目脉络, 做关键判断纠偏, or turn messy conversations into structured facts, judgments, and follow-up actions.
---

# Biz Retro Analyzer

## Role

Turn messy post-meeting materials into reusable analysis artifacts.

This skill is for situations where the user has one or more of:

- meeting transcripts
- meeting notes
- field observation notes
- video analysis text
- follow-up analysis conversations

and wants to produce:

- structured fact records
- project progression summaries
- stakeholder motive analysis
- participant understanding analysis
- judgment and reverse-audit notes
- next-step action recommendations
- reusable method notes

## Core Rules

1. Evidence first. Do not let later reasoning overwrite earlier source material.
2. Separate facts, structure, judgments, and methods.
3. Distinguish `what was said` from `what each party actually wants`.
4. Distinguish `trial scenario` from `product/system body`.
5. Distinguish `current blocking issue` from `later evidence gap`.
6. If the user already has a strong narrative, run a reverse audit before finalizing conclusions.
7. Treat follow-up AI conversations as optional judgment-layer input, never as source-of-truth replacements for original evidence.
8. Keep the open-source version generic. Do not hardcode private organizations, sensitive projects, or personally identifying details into reusable guidance.
9. Evaluate not only motive, but also issue understanding: who seems to deeply understand the domain, who understands process, who understands politics, and who is mostly talking in positioning language.
10. Treat participant understanding as strategy-critical output. Knowing what each party knows, and does not know, is necessary for routing explanation depth, pricing conversations, implementation sequencing, and risk control.
11. Tag important conclusions with evidence status. The reader should be able to tell what is directly supported, what is inferred, and what still needs validation.
12. For high-risk business or stakeholder readings, prefer omission over overclaim. If support is thin, narrow the claim or leave it out.

## Trigger Conditions

Use this skill when the request is about:

- analyzing post-meeting business conversations
- turning transcripts or notes into structured retrospectives
- identifying stakeholder motives and project direction shifts
- separating source facts from later interpretation
- auditing whether a project narrative is actually supported by evidence
- building reusable process documents from meeting-heavy project work

Typical trigger phrases:

- "复盘这次商务面谈"
- "分析会后录音"
- "把会议纪要拆开"
- "做项目脉络总结"
- "帮我做关键判断和纠偏"
- "把这些对话沉淀成过程文档"
- "把这些材料整理成可复用方法"
- "做 post-meeting analysis"
- "analyze these transcripts and extract project decisions"

## Input Modes

Read `${CLAUDE_SKILL_DIR}/references/input-modes.md` before deciding output depth.

If the user provides audio instead of text, first transcribe it into a usable transcript before running deeper analysis.  
If the open-source artifact itself is being prepared for publication, read `${CLAUDE_SKILL_DIR}/references/open-source-sanitization.md`.

This skill supports three input layers:

1. source evidence only
2. source evidence plus project context
3. source evidence plus context plus follow-up reasoning conversation

Do not force all three. Work with the highest-confidence layer available.

If speaker attribution is missing or unreliable, downgrade into `speaker-unknown mode` and avoid high-confidence person-by-person motive claims.

## Evidence Tagging Protocol

Use lightweight evidence tags whenever the output includes important judgments, stakeholder readings, project-boundary calls, or action recommendations.

### Claim status tags

- `Confirmed` — directly supported by source material
- `Inferred` — a reasonable interpretation grounded in source material
- `Assumption` — plausible working hypothesis, not yet supported enough
- `Needs validation` — should be checked before using it for commitment, pricing, or strategy

### Evidence strength tags

- `High` — repeated or explicit support in the source
- `Medium` — some support, but still interpretive or incomplete
- `Low` — thin support, single-mention support, or mostly indirect support

### Source basis tags

When helpful, mark the basis briefly:

- `Source quote/paraphrase`
- `Cross-source pattern`
- `User context`
- `Later reasoning only`

Hard rule:

- Do not present an `Inferred` or `Assumption` claim in the same tone as a `Confirmed` fact.
- If a judgment materially affects pricing, partner choice, next-step sequencing, or project scope, add both a claim-status tag and an evidence-strength tag.
- Any claim about motive, intent, budget or pricing strategy, political positioning, or control of the deal should also include a brief source anchor.

### Source anchor requirement

For high-impact or high-risk claims, include a brief source anchor whenever the material allows it.

Acceptable anchors include:

- meeting or material name
- speaker or role
- approximate section, segment, or quote basis

Examples:

- `Source anchor: Meeting 2, Wang Bin paraphrase`
- `Source anchor: Field note, afternoon walkthrough`
- `Source anchor: Transcript section on pricing`

If a claim cannot be anchored even loosely, downgrade it or omit it.

## High-Risk Claim Gate

The following claim types require stricter evidence discipline:

1. participant motive
2. customer true intent
3. budget or pricing strategy judgment
4. organizational or political positioning judgment
5. who actually controls the deal, partnership, or next-step decision path

Default rules:

- Do not mark these claim types as `Confirmed` unless the source is explicit and the wording stays narrow.
- If the claim is supported by only one expression or one meeting, cap it at `Inferred` with `Low` or `Medium` strength.
- If the claim would materially affect pricing, sequencing, partner choice, or commitment level, include:
  - claim status
  - evidence strength
  - basis
  - source anchor
  - what still needs validation
- If support is weak or indirect, prefer `Assumption` or `Needs validation`.
- If the source does not support a stable reading, omit the claim instead of writing a dramatic but weak interpretation.

## Workflow

1. Classify the input stack.
   - Identify which materials are raw evidence, contextual supplements, and later reasoning.
   - If the user mixed them together, separate them first.
   - If speaker labels are missing, mark that explicitly before deeper analysis.
2. Build the fact layer.
   - Follow `${CLAUDE_SKILL_DIR}/references/output-templates.md` for structured source-note output.
   - Keep original claims tied to specific meetings or materials.
   - Mark high-value factual statements as `Confirmed` unless the source itself is ambiguous.
3. Build the project structure layer.
   - Merge materials by topic, not just chronology.
   - Identify goal convergence, stakeholder motives, participant understanding levels, trial scenario choices, boundary shifts, and unresolved questions.
   - Explicitly assess who understands:
     - the domain itself
     - the operating workflow
     - delivery and implementation reality
     - organizational or political constraints
   - Mark where structure calls are `Inferred` versus `Needs validation`.
4. Build the judgment layer.
   - Summarize the user's current narrative.
   - Then run the checks in `${CLAUDE_SKILL_DIR}/references/analysis-checks.md`.
   - Label major judgments with claim status and evidence strength.
5. Run reverse audit when needed.
   - If conclusions feel too neat, too fast, or too dependent on one narrator, read `${CLAUDE_SKILL_DIR}/references/reverse-audit.md`.
6. Run pre-output audit.
   - Check whether the fact layer contains motive or interpretation language.
   - Check whether any single-meeting expression has been overstated into a stable long-term motive or strategy.
   - Check whether high-risk claim types are tagged and anchored.
   - Check whether later AI reasoning has been treated as source evidence.
   - Check whether any commitment-shaping recommendation depends on an unvalidated premise.
7. Close with action output.
   - Recommend current next actions, later evidence-gathering steps, and reusable lessons.
   - If important evidence is still missing, use `${CLAUDE_SKILL_DIR}/references/interview-gap-prompts.md`.
   - For commitment-shaping actions, say what must be validated first.

## Output Modes

### Mode A: Fact Pack

Use when the user mainly wants structured source material.

- structured notes per meeting/material
- factual project timeline
- open questions only

### Mode B: Retro Pack

Use when the user wants project progression plus interpretation.

- structured source notes
- cross-material project thread
- stakeholder motive analysis
- participant understanding map
- current boundaries and next actions

### Mode C: Audit Pack

Use when the user already has strong conclusions and wants a harder review.

- retro pack
- reverse-audit section
- overreach / under-evidence flags
- confidence notes
- participant understanding map when the material supports it

## Hard Rules

1. Do not summarize everything into one neat story before preserving the source structure.
2. Do not treat later AI analysis as source evidence.
3. Do not confuse project momentum with proof of product correctness.
4. Do not collapse stakeholder roles into generic labels if their motives differ.
5. Do not let a trial scenario become the product definition unless the evidence supports that scope.
6. Do not output only "meeting summary + action items" if the user clearly needs project intelligence.
7. When preparing public-facing examples or repository docs, strip or generalize sensitive names, internal identifiers, and private project details.
8. If source materials do not reliably identify speakers, preserve role ambiguity instead of hallucinating who said what.
9. Do not confuse confidence, authority, or airtime with actual issue understanding.
10. Do not stop at "what they want" if the source material also reveals "what they understand." Strategy often depends on both.
11. Do not hide thin evidence behind confident wording. If support is limited, tag it and keep the claim narrow.
12. Do not present unanchored high-risk claims as reusable project intelligence.
13. Do not turn one spicy line into a stable motive, pricing strategy, or political reading unless the source repeatedly supports it.

## Output Format

Always produce one or more of the following, depending on the request:

### Structure A: Structured Fact Record

```md
## Structured Fact Record

- **Source set**:
- **Source type**:
- **What is confirmed**:
- **What was said**:
- **Explicit conclusions from the source**:
- **Explicit follow-up actions**:
- **Open factual gaps**:
- **Evidence notes**:
```

### Structure B: Project Retro

```md
## Project Retro

- **Current stage**:
- **How the goal narrowed or shifted**:
- **What each key party appears to want**:
- **Current working direction**:
- **Non-blocking but real gaps**:
- **Current next actions**:
- **Evidence-risk notes**:
```

### Structure B2: Participant Understanding Map

```md
## Participant Understanding Map

| Party / Voice | Understands domain facts | Understands workflow/process | Understands delivery reality | Understands political or organizational constraints | Main evidence |
| --- | --- | --- | --- | --- | --- |
```

Use this section when later project strategy depends on who really understands the issue.
If the source supports it, add a short readout on:

- where the participant is strongest
- where they sound shallow or overconfident
- how that should change explanation, expectation, or collaboration strategy

### Structure C: Judgment and Reverse Audit

```md
## Judgment and Reverse Audit

- **User's current narrative**:
- **Judgments that look supported**:
- **Judgments that need stronger evidence**:
- **Likely overestimates / underestimates**:
- **What should be treated as assumption for now**:
- **High-impact claims requiring validation**:
```

For important judgments, especially high-risk claim types, prefer entries in this shape:

```md
- **Claim**:
- **Status**:
- **Strength**:
- **Basis**:
- **Source anchor**:
- **What still needs validation**:
```

### Structure D: Method Notes

```md
## Method Notes

- **What worked in this analysis**:
- **What should be repeated next time**:
- **What to collect earlier next time**:
- **Reusable prompts or interview moves**:
```

## References

- Input modes: `${CLAUDE_SKILL_DIR}/references/input-modes.md`
- Output templates: `${CLAUDE_SKILL_DIR}/references/output-templates.md`
- Analysis checks: `${CLAUDE_SKILL_DIR}/references/analysis-checks.md`
- Reverse audit: `${CLAUDE_SKILL_DIR}/references/reverse-audit.md`
- Interview gap prompts: `${CLAUDE_SKILL_DIR}/references/interview-gap-prompts.md`
- Open-source sanitization: `${CLAUDE_SKILL_DIR}/references/open-source-sanitization.md`
