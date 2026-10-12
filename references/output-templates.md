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

## Optional: Numeric Confidence Table

When the user needs calibration, comparison across runs, or a confidence audit, add a numeric confidence table instead of (or alongside) the High/Medium/Low tags. This is **optional** — ordinary runs do not need it.

Five bands:

| Band | Meaning | Typical use |
| --- | --- | --- |
| 95–100 | Almost certain | Skill evidence, hard closure (e.g. an action that only one role can perform) |
| 80–94 | High confidence, not ironclad | Cross-source convergence but no direct witness to the underlying fact |
| 65–79 | Leaning judgment | Evidence points one way but a reasonable alternative exists |
| 50–64 | Barely leaning | Slightly above coin-flip; evidence is thin |
| <50 | Inverse leaning | You judge the opposite is more likely |

Rules:

- Spread confidence across bands. Do not put every judgment at 90+. If evidence is thin, say so with a low number.
- The band is a self-rating of *your actual confidence*, not a politeness scale. If you genuinely cannot tell, score below 65.
- Pair each numeric score with a one-line basis, so a reviewer can check whether the number matches the evidence.
- High-Risk Claim Gate still applies: a motive or conflict-of-interest claim must stay below `Confirmed` regardless of the numeric score unless the source is explicit and narrow.

## 1. Structured Fact Record

One block per source under a single `## Structured Fact Record` heading.

```md
## Structured Fact Record

### [Source Name]

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

## 1B. Optional Ledgers (inside the Structured Fact Record)

Use these when the material has explicit decisions, confident claims, or written minutes to check. Each row needs an evidence anchor. They render as tables in the HTML report and can be exported from it.

Decision ledger: what was actually decided, by whom, and whether it was later rewritten. `Status` is the evidence status of "this was decided" (`Confirmed` / `Inferred` / `Assumption` / `Needs validation`); use `Follow-up` for drift, deferral, or a later rewrite. Record `Decided by` only when the source shows someone with authority saying yes; otherwise write the item as proposed and say who still has to decide.

```md
### Decision Ledger

| # | Decision | Decided by | Owner | Due | Status | Follow-up | Evidence anchor |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

Claim ledger: each factual claim made in the room, what supported it, and what contradicted it. It rates claims, not people.

```md
### Claim Ledger

| Claim | Claimant | Support | Counter-evidence / correction | Status | Evidence anchor |
| --- | --- | --- | --- | --- | --- |
```

Minutes vs recording: written conclusions (minutes, follow-up email, group message) compared with what was said. `Verdict` is `consistent` / `partial` / `inconsistent`; anchor both sides.

```md
### Minutes vs Recording

| Written | Spoken | Verdict | Evidence anchor |
| --- | --- | --- | --- |
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

## 2B. Advancement / Influence Chain

Use this when the material shows that a project, decision, or shared narrative was advanced through role-to-role influence rather than through one explicit decision.

```md
## Advancement / Influence Chain

| Actor / Voice | Claim, frame, or action introduced | Who adopted or amplified it | What decision or next step it affected | Evidence anchor | Status | Strength | Risk if wrong |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

Optional follow-on block:

```md
## Chain Readout

- **Who defined the working frame**:
- **Who inherited or legitimized that frame**:
- **Who controlled the next-step path**:
- **Who appeared influential but did not control the outcome**:
- **Where the chain depends on weak or disputed evidence**:
```

This section is especially useful for multi-party sales, partner negotiations, public meetings, crisis retros, adversarial dialogues, and any case where the important question is not only `what happened`, but `who made this version of events actionable`.

## 3. Stakeholder Motive Readout

```md
## Stakeholder Motive Readout

| Party | What they say | What they appear to want | Status | Strength | Evidence anchor |
| --- | --- | --- | --- | --- | --- |
```

If speaker labels are unreliable, replace this with:

```md
## Position Readout (Speaker-Unknown Mode)

| Position / Voice | What appears in the material | What this position seems to want | Status | Strength | Evidence anchor |
| --- | --- | --- | --- | --- | --- |
```

## 3B. Participant Understanding Map

```md
## Participant Understanding Map

| Party / Voice | Problem itself | Advancement path | Execution / delivery constraints | Decision / organizational mechanics | Evidence anchor |
| --- | --- | --- | --- | --- | --- |
```

Levels, one per cell followed by a short reason:

- `strong`
- `mixed`
- `thin`
- `unclear` (unclear from the material)

The four columns are the same in `SKILL.md`, the report JSON (`understandingMap.rows[].problem / advancementPath / deliveryConstraints / decisionMechanics`) and the rendered HTML.

Optional follow-on block when strategy depends on understanding gaps:

```md
## Strategy Implications from Participant Understanding

- **Who can validate the problem itself**:
- **Who can validate the advancement path**:
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
- **Suspicious actions that need non-bad-faith alternatives**:
  - `Action or contradiction`:
  - `Information-change explanation`:
  - `Pressure or misjudgment explanation`:
  - `Strategic-misdirection explanation`:
  - `Current status`:
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

## Optional: Information Sufficiency Self-Rating

When the output includes a numeric confidence table, or when the user wants to know how trustworthy the conclusions are, add an information-sufficiency self-rating. This distinguishes **"correct and well-supported"** from **"correct but I got lucky"** — a difference that a confidence number alone cannot show.

```md
## Information Sufficiency

| Key judgment | Confidence | Sufficiency | Note |
| --- | --- | --- | --- |
| (judgment) | (0–100) | Sufficient / Adequate / Thin | (why, or what is missing) |
```

Sufficiency labels:

- `Sufficient` — the source directly supports this judgment; being right is expected, not lucky
- `Adequate` — multiple indirect signals converge; being right is likely but not guaranteed
- `Thin` — a single weak signal or pure elimination logic; being right could be coincidence

Use this especially when:

- a judgment is correct but the evidence is indirect (common in elimination-based reasoning)
- the analysis hit a forced binary where two options looked similar and one was picked
- the user may later rely on this judgment for pricing, partner choice, or commitment

This field is **optional**. Use it when the gap between confidence and evidence quality matters.
