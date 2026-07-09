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

## Input Shape

Before rendering, map the output into the JSON fields defined in:

- `references/output-schema.json`

This skill does not require a rendering engine. The agent may:

- fill the HTML template directly
- copy the CSS into a standalone file
- inline the CSS into the HTML when a single-file deliverable is better

## Required Sections

The HTML page should include these sections unless the evidence is too thin:

1. Hero / report header
2. Current summary
3. Evidence layer
4. Project thread / direction shifts
5. Stakeholder motive readout
6. Participant understanding map
7. Judgment and reverse audit
8. Current actions
9. Source references

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

## Template Assets

Use these reusable assets:

- `assets/html-report-template.html`
- `assets/html-report.css`

The template is intentionally generic. Replace placeholders and duplicate blocks as needed.

## Minimal Rendering Workflow

1. Build the structured analysis.
2. Map it to the JSON schema.
3. Copy the HTML template.
4. Fill the hero, summary, and evidence blocks.
5. Fill timeline, stakeholder, audit, and actions.
6. Attach or inline the CSS.
7. Verify that evidence labels still match the actual support level.

## When To Skip HTML

Do not use HTML as the primary output when:

- the user only wants a fast fact pack
- the source material is too thin for structured analysis
- the user only needs a plain internal note

In those cases, stay in Markdown unless the user explicitly insists on HTML.
