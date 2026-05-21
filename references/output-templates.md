# Output Templates

Use these templates selectively. Do not force every section if the input is too thin.

## Evidence Tagging Legend

Use these tags when the output includes important judgments or commitment-shaping recommendations.

- `Status`: `Confirmed` / `Inferred` / `Assumption` / `Needs validation`
- `Strength`: `High` / `Medium` / `Low`
- `Basis`: `Source quote/paraphrase` / `Cross-source pattern` / `User context` / `Later reasoning only`

Minimum rule:

- Facts can stay untagged if they are obviously direct and low-risk.
- Any major judgment about motive, scope, leverage, pricing, readiness, or next action should include tags.

## 1. Structured Meeting / Source Record

```md
## [Source Name]

- **Type**: transcript / notes / observation / video analysis / other
- **Context**:
- **Participants or actors**:
- **Main topics**:
- **Key factual statements**:
- **Explicit decisions**:
- **Explicit requested actions**:
- **Unresolved factual gaps**:
- **Evidence notes**:
  - `Claim`:
  - `Status`:
  - `Strength`:
  - `Basis`:
```

## 2. Cross-Material Project Thread

```md
## Project Thread

- **Starting frame**:
- **How the project direction narrowed or shifted**:
- **Trial scenario(s)**:
- **Product body vs. trial scenario distinction**:
- **Current stage**:
- **What is blocking now**:
- **What is not blocking now but still missing**:
- **Evidence-risk notes**:
  - `Claim`:
  - `Status`:
  - `Strength`:
  - `Basis`:
```

## 3. Stakeholder Motive Readout

```md
## Stakeholder Motive Readout

| Party | What they say | What they appear to want | Confidence | Evidence basis |
| --- | --- | --- | --- | --- |
```

If speaker labels are unreliable, replace this with:

```md
## Position Readout (Speaker-Unknown Mode)

| Position / Voice | What appears in the material | What this position seems to want | Confidence | Evidence basis |
| --- | --- | --- | --- | --- |
```

## 3B. Participant Understanding Map

```md
## Participant Understanding Map

| Party / Voice | Domain understanding | Workflow understanding | Delivery understanding | Organizational understanding | Confidence | Evidence basis |
| --- | --- | --- | --- | --- | --- | --- |
```

Suggested labels:

- `strong`
- `mixed`
- `thin`
- `unclear from material`

Optional follow-on block when strategy depends on understanding gaps:

```md
## Strategy Implications from Participant Understanding

- **Who can validate domain truth**:
- **Who can validate workflow reality**:
- **Who can support or distort delivery planning**:
- **Who may sound confident but needs translation or narrowing**:
- **How this should change the next meeting / proposal / demo strategy**:
```

## 4. Judgment and Reverse Audit

```md
## Judgment and Reverse Audit

- **User's current narrative**:
- **Supported judgments**:
  - `Claim`:
  - `Status`:
  - `Strength`:
  - `Basis`:
- **Judgments with weak evidence**:
  - `Claim`:
  - `Status`:
  - `Strength`:
  - `Basis`:
- **Possible overestimates**:
- **Possible underestimates**:
- **Assumptions to keep explicit**:
- **High-impact claims requiring validation**:
  - `Claim`:
  - `Why it matters`:
  - `What would validate it`:
```

## 5. Current Actions

```md
## Current Actions

- **Do now**:
- **Do later**:
- **Must validate before deeper commitment**:
- **Next interview or evidence targets**:
- **Action evidence notes**:
  - `Action`:
  - `Triggered by`:
  - `Evidence strength`:
```

## 6. Method Notes

```md
## Method Notes

- **What analysis moves worked well**:
- **What evidence was most useful**:
- **What should be collected earlier next time**:
- **Reusable questions or prompts**:
```
