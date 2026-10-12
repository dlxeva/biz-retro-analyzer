# HTML Output Mode

Use this file when the user wants the analysis delivered as an HTML page instead of plain Markdown.

## Goal

Render the retro as a readable, evidence-aware report page, not as a generic dashboard.

The page should help the reader answer:

- what is confirmed
- what is inferred
- what still needs validation
- how the project direction shifted
- who wants what
- who actually understands what
- what should happen next

## Required Prerequisite

Do not start from layout.

First complete the analysis in structured form:

1. fact layer
2. project thread
3. stakeholder motive readout
4. participant understanding map
5. judgment / reverse audit
6. current actions

Only after the structure is stable should you render the HTML.

## Output Escalation Rule

The user does not need to know that HTML mode exists.

Treat HTML as an internal upgrade path, not as a prerequisite the user must request explicitly.

### Escalate to an HTML recommendation when most of the following are true

- the analysis already contains a stable fact layer
- the project thread is clear enough to render as a timeline
- there are meaningful stakeholder or participant-understanding sections
- the output includes current judgment, risk, or reverse-audit content
- the result is likely to be shared with a team, manager, partner, or client
- the content is strong enough that layout will improve comprehension rather than disguise thin evidence

### Do not recommend HTML yet when any of the following is true

- the source material is still too thin
- transcription or speaker attribution is still unstable
- the user only asked for a fast fact pack
- the analysis is still in rough-note form

### Recommendation timing

Do not pause early in the workflow to ask whether the user wants HTML.

Instead:

1. finish the analysis structure
2. evaluate whether the output is report-shaped
3. if yes, tell the user the material can be upgraded into an HTML report
4. render only if the user wants that upgrade

### Recommendation wording

Use short recommendation language such as:

- "This has enough structure to turn into an HTML report if you want a shareable page."
- "This is no longer just a note set; I can package it as an HTML report for internal sharing."
- "The retro now has a stable evidence, audit, and action structure, so HTML would be a useful output upgrade."

## Input Shape: Report JSON Is the Source of Truth

Write the analysis as report JSON that follows `references/output-schema.json` (schema v2). HTML and Markdown are both renderings of that one file, so a fix made in the JSON shows up in every output.

```bash
python3 scripts/retro_tool.py scaffold --mode C --format json -o report.json   # skeleton with <fill> placeholders
python3 scripts/retro_tool.py validate report.json                             # schema, protocol gates, anchors
python3 scripts/retro_tool.py render report.json -o report.html                # single-file HTML, CSS inlined
python3 scripts/retro_tool.py render report.json --format md -o report.md      # same content as Markdown
```

Key fields:

- `sources[]`: every input with an `id` (`S1`, `S2`, `C1`...), a `layer` (`source` / `context` / `later_reasoning`), and a `path` relative to the JSON file. Context and later-reasoning sources can never be the only support for a `Confirmed` claim.
- `anchors[]`: `{source, speaker, ts, quote, note}`. `validate` checks that `ts` exists in the source, that `speaker` is the person talking at `ts`, and that `quote` appears in the source. Put paraphrases in `note`, not in `quote`.
- Judgments (`evidenceNotes`, `threadNotes`, `audit.*Judgments`): `{claim, status, strength, basis, highRiskType, anchors, toValidate}`. Set `highRiskType` for motive, intent, budget/pricing, political, control and bad-faith claims so the High-Risk Claim Gate applies.
- Optional ledgers: `decisions[]` (decision ledger), `claimLedger[]` (claims with support and counter-evidence), `minutesCheck[]` (written minutes vs what was said).

Reports without `schemaVersion` (v1) are upgraded in memory with a warning. Statuses that v1 did not record are filled with explicit defaults, so check them.

## Audience

Set `meta.audience` or pass `--audience`:

- `internal` (default): everything.
- `leadership`: drops suspicious-action readings and unconfirmed motive, intent, bad-faith and political judgments, and blanks motives that are not `Confirmed`.
- `external`: also drops stakeholder, understanding-map, influence-chain and ledger sections, unconfirmed audit judgments, method notes and source paths.

The page states what was removed. Redaction is a safety net, not a review: read the page before sending it.

## What the Rendered Page Contains

1. Hero / report header with the analysis window and noise note
2. Current summary
3. Evidence layer: sources, evidence cards, open questions
4. Decision ledger, minutes vs recording, claim ledger (when present)
5. Project thread / direction shifts
6. Advancement / influence chain (when present)
7. Stakeholder motive readout
8. Participant understanding map (parties as rows, four columns)
9. Judgment and reverse audit, including suspicious-action alternatives
10. Current actions
11. Method notes and source references
12. Transcript appendix: every anchor chip links to the cited turn; anchors that do not resolve are marked

The page also has a status filter and export buttons (report JSON, decisions JSON, claims CSV, actions CSV). The report JSON is embedded in the page.

## Visual Rules

### 1. Treat it as a report, not a BI dashboard

Prefer:

- editorial cards
- timeline blocks
- evidence chips
- dense but readable tables
- action lanes

Avoid:

- unnecessary charts
- decorative gauges
- fake precision metrics
- complex relationship diagrams when evidence is thin

### 2. Make evidence status visible

Use visible tags for important claims:

- `Confirmed`
- `Inferred`
- `Assumption`
- `Needs validation`

These should appear as chips or badges near:

- summary claims
- stakeholder readings
- scope calls
- action recommendations

### 3. Separate fact from judgment visually

Facts should look calmer and more neutral.  
Judgments and audit calls should be visually distinct.

Recommended pattern:

- fact cards: neutral or green/blue accents
- inferred structure: blue accent
- validation gaps / risk calls: red or amber accent

### 4. Default visual modules

Use these module types by default:

- summary cards for top-level conclusions
- evidence cards for source-by-source factual support
- horizontal timeline for direction shifts
- matrix/table for understanding map
- four-up audit board for supported / weak / assumptions / validate
- two-to-four action cards for now / later / validate-before-commit

## Writing Rules For HTML

1. Keep section titles explicit and business-readable.
2. Keep paragraphs short.
3. Do not hide uncertainty.
4. Do not collapse all nuance into one executive paragraph.
5. Keep source links and citations visible near the bottom of the page.
6. If speaker attribution is weak, downgrade the language in stakeholder sections.

## Without Python

If the environment cannot run Python, fill `assets/html-report-template.html` by hand and inline `assets/html-report.css`. The template uses the same section names and map columns as the renderer. Hand-filled pages get no anchor checking, so be stricter about evidence labels.

## Minimal Rendering Workflow

1. Build the structured analysis.
2. Write it as report JSON.
3. Run `validate` and fix the claims it flags. Do not add tags or anchors only to pass.
4. Run `render`, choosing the audience.
5. Open the page and check that the evidence labels still match the actual support level.

## When To Skip HTML

Do not use HTML as the primary output when:

- the user only wants a fast fact pack
- the source material is too thin for structured analysis
- the user only needs a plain internal note

In those cases, stay in Markdown unless the user explicitly insists on HTML.
