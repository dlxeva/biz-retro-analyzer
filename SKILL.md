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

## Workflow

1. Classify the input stack.
   - Identify which materials are raw evidence, contextual supplements, and later reasoning.
   - If the user mixed them together, separate them first.
2. Build the fact layer.
   - Follow `${CLAUDE_SKILL_DIR}/references/output-templates.md` for structured source-note output.
   - Keep original claims tied to specific meetings or materials.
3. Build the project structure layer.
   - Merge materials by topic, not just chronology.
   - Identify goal convergence, stakeholder motives, trial scenario choices, boundary shifts, and unresolved questions.
4. Build the judgment layer.
   - Summarize the user's current narrative.
   - Then run the checks in `${CLAUDE_SKILL_DIR}/references/analysis-checks.md`.
5. Run reverse audit when needed.
   - If conclusions feel too neat, too fast, or too dependent on one narrator, read `${CLAUDE_SKILL_DIR}/references/reverse-audit.md`.
6. Close with action output.
   - Recommend current next actions, later evidence-gathering steps, and reusable lessons.
   - If important evidence is still missing, use `${CLAUDE_SKILL_DIR}/references/interview-gap-prompts.md`.

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
- current boundaries and next actions

### Mode C: Audit Pack

Use when the user already has strong conclusions and wants a harder review.

- retro pack
- reverse-audit section
- overreach / under-evidence flags
- confidence notes

## Hard Rules

1. Do not summarize everything into one neat story before preserving the source structure.
2. Do not treat later AI analysis as source evidence.
3. Do not confuse project momentum with proof of product correctness.
4. Do not collapse stakeholder roles into generic labels if their motives differ.
5. Do not let a trial scenario become the product definition unless the evidence supports that scope.
6. Do not output only "meeting summary + action items" if the user clearly needs project intelligence.
7. When preparing public-facing examples or repository docs, strip or generalize sensitive names, internal identifiers, and private project details.

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
```

### Structure C: Judgment and Reverse Audit

```md
## Judgment and Reverse Audit

- **User's current narrative**:
- **Judgments that look supported**:
- **Judgments that need stronger evidence**:
- **Likely overestimates / underestimates**:
- **What should be treated as assumption for now**:
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
