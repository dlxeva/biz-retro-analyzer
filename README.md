<p align="right">
  <a href="./README.md"><strong>English</strong></a> | <a href="./README.zh-CN.md">简体中文</a>
</p>

# The Meeting Didn't Say That
### `biz-retro-analyzer` — an open-source Agent Skill for post-meeting audits

> **Your meeting notes say what was said. This tells you what nobody actually proved.**

**[Live demo report](https://dlxeva.github.io/biz-retro-analyzer/demo/)**

> "I ran it on a review meeting. The HTML it gave me afterwards genuinely scared me."
> — dlxeva, author

![Generic summary vs biz-retro-analyzer](docs/before-after.png)

## A fictional review meeting

A company that makes POS and inventory software holds a Q3 product review. There is one agenda item: whether **AI restock suggestions** should go into Q3.

- **Gao Yuan** (VP of Product) is the proposer. He opens with "this has to be done," citing conversations with twenty-plus customers and a competitor already shipping.
- **Ma Jun** (head of engineering) asks who estimated six person-months, and admits the team never did a formal estimate.
- **Su Qing** (data analyst) brings numbers: of 1,200+ active stores, only 7% have usable inventory data; of 41 customers who churned in the first half, only 3 left explicitly for a competitor.
- **Zhou** (CEO) joins in the second half, hears the room out, decides "run both tracks in parallel, revisit in two weeks," then leaves.
- Twenty minutes after the meeting, Gao Yuan posts a "meeting conclusion" in the project group chat.

Feed the same transcript plus that group message to a generic AI and to biz-retro-analyzer:

| How a generic AI summary writes it | How biz-retro-analyzer reads it |
|---|---|
| "Q3 review aligned with Zhou. Restock confirmed as a Q3 priority." | **Conflicts with source.** Zhou's words were: "Run both tracks — alerts first, a demo for restock — we'll revisit in two weeks." A two-week time-boxed evaluation was rewritten as "approved / kicked off." |
| "Inventory alerts scheduled after the demo." | **Reversed after the decision-maker left.** As soon as Zhou left, Gao Yuan announced "staff the demo first"; Ma Jun objected on the spot. Zhou had said "alerts first." |
| "Customer demand validated." | **Needs validation.** Gao Yuan himself revised "twenty-plus customers" down to "seven or eight," mostly dinner chats, no records. |

A generic summary reads as a smoothly aligned meeting. This report sees the group message quietly rewriting the boss's decision.

*People, company, and data are entirely fictional. [Full transcript](./examples/product-review-fictional/en/transcript.txt) · [Full HTML report](https://dlxeva.github.io/biz-retro-analyzer/demo/)*

## What it does
- **Ledgers every claim against evidence.** Each conclusion gets a status (confirmed / needs validation / assumption / conflicts with source) and a timestamp anchor — or it gets flagged.
- **Checks what happened *after* the meeting.** Compares follow-up messages and "alignment" summaries with what was actually said, and catches quiet rewrites.
- **Runs a reverse audit.** Argues the opposite conclusion and asks whether the same evidence supports it too — including against *your own* framing — then outputs a shareable HTML report.

## 30-second quickstart

Install as an Agent Skill — layouts for Claude Code, Cursor, and Codex are in [`INSTALL.md`](./INSTALL.md). Then paste a transcript (plus any post-meeting messages) and ask: *"Audit this meeting and give me the HTML report."*

Optional CLI (`scripts/retro_tool.py`, Python 3.8+, zero dependencies):

```bash
python3 scripts/retro_tool.py preprocess meeting.txt -o meeting_annotated.txt
python3 scripts/retro_tool.py scaffold --mode B --format json -o report.json
python3 scripts/retro_tool.py validate report.json
python3 scripts/retro_tool.py validate analysis.md -t meeting.txt
python3 scripts/retro_tool.py render report.json -o report.html
```

## Honest limits
- **Performative meetings** (where the real decision was made elsewhere) are hard for it. See [`references/honest-limits.md`](./references/honest-limits.md).
- **Garbage in, garbage out:** it needs a transcript with reasonably reliable speaker labels.
- **Evals are preliminary.** Current results come from a handful of synthetic cases scored by a single grader with a rubric that partly rewards the very features being tested. Treat them as a smoke test, not proof.
- **It flags, it doesn't judge people.** A "conflicts with source" flag says the record doesn't match, not why. The report lists innocent explanations alongside strategic ones.

---

## Quick Start

Use this skill when you have messy source material and want an evidence-aware retro instead of a generic summary.

Copy this prompt into your agent or model run:

```md
Use biz-retro-analyzer / Mode C: Audit Pack.

Input stack:
- Source evidence: [paste transcripts, meeting notes, field notes, or observation notes]
- Context: [briefly explain the project and current concern]
- Later reasoning: [optional; paste follow-up analysis or hypotheses separately]

Please produce:
1. Structured Fact Record
2. Project Thread
3. Advancement / Influence Chain
4. Participant Understanding Map
5. Judgment and Reverse Audit
6. Current Actions

Rules:
- Separate facts, participant claims, and model inferences.
- Tag high-impact judgments with Status, Strength, Basis, and Source anchor.
- Treat suspicious or contradictory actions as diagnostic signals, not automatic proof of bad faith.
- Do not treat later reasoning as source evidence.
```

For a lighter run, use `Mode A: Fact Pack`.  
For a full retro, use `Mode B: Retro Pack`.  
For a harder review of an existing story, use `Mode C: Audit Pack`.

### CLI tool (optional)

`scripts/retro_tool.py` (Python 3.8+, zero dependencies) is a lint and a renderer. It does not replace the analysis, and it does not diarize audio.

```bash
python3 scripts/retro_tool.py preprocess meeting.txt -o meeting_annotated.txt
python3 scripts/retro_tool.py scaffold --mode B --format json -o report.json
python3 scripts/retro_tool.py validate report.json
python3 scripts/retro_tool.py validate analysis.md -t meeting.txt
python3 scripts/retro_tool.py render report.json -o report.html
```

- `preprocess` splits speaker turns and *hints* possible noise. It never deletes a line.
- `validate` checks protocol form and whether cited timestamps, speakers, and quotes exist in the transcript. PASS does not mean the judgments are right.
- `render` turns report JSON (`references/output-schema.json`) into a single-file HTML page or Markdown.

Install notes: [`INSTALL.md`](./INSTALL.md). Worked examples: [`examples/quickstart.md`](./examples/quickstart.md), [`examples/quickstart.report.json`](./examples/quickstart.report.json), and a fictional Mode C demo in [`examples/product-review-fictional/`](./examples/product-review-fictional/).

Project status:

- License: MIT, see `LICENSE`.
- Roadmap: see `ROADMAP.md`.
- Evaluation: [`EVALUATION.md`](./EVALUATION.md). Protocol cases: `tests/cases/` (give the model `input.md` only). Ablation write-ups: [`evaluations/ablation-2026-07/`](./evaluations/ablation-2026-07/). Read that folder's 2026-10-12 errata before citing scores — original tables were not rerun; under the skill's own `<50` = inverse-leaning rule the calibration set is 66/67, not 67/67.
- Synthetic adversarial case: see `evaluations/adversarial-dialogue-werewolf/`.

---

## What This Is

This is **not** a transcription tool and **not** a generic meeting-summary template.

It is an **evidence-first dialogue intelligence skill** for turning raw conversation material into reusable analysis artifacts about participant understanding, project advancement, influence chains, judgment risk, and next-step action.

The skill is especially useful when you have:

- multiple meetings
- different kinds of source material
- mixed fact and interpretation
- layered stakeholder dynamics
- evolving trial scenarios and direction
- multi-party coordination, negotiation, or advancement friction

---

## The Werewolf Test

The repository includes **The Werewolf Test**, a synthetic hidden-role dialogue evaluation case.

Werewolf is used here as a toy problem for complex dialogue analysis. It creates a compact version of the same risks that appear in messy project conversations:

- public claims are not facts
- confident speakers can be wrong
- weak speakers can be right
- authority can be transferred
- suspicious actions can be mistakes rather than bad faith
- the outcome depends on who turns a narrative into action

The point is not to solve the game. The point is to test whether the skill can preserve evidence discipline under hidden incentives.

See `evaluations/adversarial-dialogue-werewolf/`.

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
- identifying who introduced a frame, who inherited it, and who changed the next-step path
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

## The Honest Limit

This skill is not useful for every smooth meeting.

Some meetings are **performative**: the real decision was made before the meeting, and the meeting exists so the decision can be seen being made. In that case, smoothness is not a signal to investigate. Smoothness is the product.

Because this skill is built to resist smooth narratives, it may produce false positives in performative, ritual, or relationship-maintenance meetings.

See `references/honest-limits.md` for the full boundary note.

---

## Core Design

This skill follows six principles:

1. **Evidence first**  
   Source materials are preserved before interpretation.

2. **Facts before judgments**  
   Structured source records come before conclusions.

3. **Claims are not facts**  
   What a participant says, asserts, implies, or believes stays separate from what the source actually confirms.

4. **Understanding depth matters**  
   The output distinguishes what people want from what they actually understand.

5. **Influence chains matter**  
   The output identifies how a frame, claim, authority, or next-step path becomes actionable across participants.

6. **Reverse audit when needed**  
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

### Team dynamics analysis vs personality profiling

Analyzing how a team works together is **allowed and often essential** — this includes communication style mismatch, decision-authority asymmetry, trust gaps, false consensus, and collaboration friction.

The boundary is: **analyze how people work together (allowed) vs analyze who people are (not allowed).**

Keep team-dynamics observations tied to observable behavior and project outcomes, not to fixed character traits.

---

## Output Model

Depending on the input depth and request, the skill produces one or more of:

1. **Structured Fact Record**
2. **Retro / Project Thread**
3. **Advancement / Influence Chain**
4. **Participant Understanding Map**
5. **Judgment and Reverse Audit**
6. **Current Actions**
7. **Method Notes**

The goal is to separate:

- what is confirmed
- what is asserted
- what is inferred
- what is still missing
- what should happen next

### HTML Output Mode

The skill now also supports an `HTML` report mode when the output needs to be:

- shareable as a standalone page
- easier to scan visually than Markdown
- structured as evidence layer + thread + audit + actions

Write the analysis as report JSON (`references/output-schema.json`), then:

```bash
python3 scripts/retro_tool.py render report.json -o report.html
```

HTML is a rendering of Mode A, B, or C, not a fourth depth. `assets/html-report-template.html` is a hand-fill fallback when Python is not available. See `references/html-output-mode.md`.

The user does not need to know this mode exists in advance.  
The skill can recommend HTML near the end of the analysis when the output has enough structure to benefit from a shareable page.

### Evidence Tagging

The skill supports a lightweight evidence-tagging convention for important conclusions:

- `Status`: `Confirmed` / `Inferred` / `Assumption` / `Needs validation`
- `Strength`: `High` / `Medium` / `Low`
- `Basis`: `Source quote/paraphrase` / `Cross-source pattern` / `User context` / `Later reasoning only`
- `Source anchor`: brief meeting, material, speaker, or segment reference for high-impact claims

This is especially useful when the output includes:

- stakeholder motive readings
- project-boundary calls
- pricing or leverage judgments
- commitment-shaping next actions
- claims about who controls the decision path
- explanations of suspicious or contradictory behavior
