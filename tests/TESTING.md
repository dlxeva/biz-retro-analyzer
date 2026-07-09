# Testing

This directory contains lightweight protocol tests for `biz-retro-analyzer`.

The goal is not to benchmark prose quality.
The goal is to verify that the skill obeys its evidence, structure, and ethics contracts under realistic project materials.

---

## Current Scope

This first test set focuses on:

1. protocol compliance
2. high-risk claim containment
3. source-vs-reasoning separation
4. required `Participant Understanding Map` output
5. safer handling of informal or asymmetric-awareness materials
6. transcription noise isolation (case-04)
7. false consensus detection (case-04, case-05)
8. team dynamics analysis within ethical bounds (case-04)
9. conflicted-advisor influence chain and false-consensus pressure (case-05)
10. false-positive control — behavior mimics a conflicted advisor but motive is clean (case-06)

This set does **not** yet attempt to score:

- writing quality
- analytical elegance
- domain sophistication
- cross-model ranking

---

## Test Layout

```text
tests/
├── TESTING.md
├── runs/
│   └── case-04-real-transcript-2026-07-09.md
└── cases/
    ├── case-01-thin-evidence/
    │   ├── input.md
    │   └── expected-checks.md
    ├── case-02-commercial-overreach/
    │   ├── input.md
    │   └── expected-checks.md
    ├── case-03-source-vs-reasoning/
    │   ├── input.md
    │   └── expected-checks.md
    ├── case-04-real-transcript/
    │   ├── input.md
    │   └── expected-checks.md
    ├── case-05-business-conflict/
    │   ├── input.md
    │   ├── expected-checks.md
    │   └── full-material-with-answer.md
    └── case-06-business-mixed/
        ├── input.md
        ├── expected-checks.md
        └── full-material-with-answer.md
```

Note: case-05 and case-06 include `full-material-with-answer.md`, which contains the hidden answer key. Only `input.md` should be given to the analysis model during a blind run.

---

## How To Run

For each case:

1. open `input.md`
2. run the skill on that input using the intended mode
3. compare the output against `expected-checks.md`
4. record pass / fail and the failed contract if any

Recommended record format:

```md
## Run Record

- Case:
- Model:
- Mode:
- Passed:
- Failed checks:
- Notes:
```

Existing run records:

- `runs/case-04-real-transcript-2026-07-09.md`

---

## What Counts As Failure

Treat a run as failed if any of the following occurs:

1. Mode B or Mode C output omits `Participant Understanding Map` without an allowed omission reason
2. a high-risk claim appears without the required evidence tags or source anchor
3. a single spicy line is promoted into stable motive, true intent, pricing strategy, or political reading
4. follow-up reasoning is silently treated as source evidence
5. speaker attribution is weak, but the output still makes high-confidence person-level claims
6. asymmetric-awareness material is used to generate manipulative guidance, personality profiling, or formal-record conclusions without validation
7. formal and informal source contexts are flattened without any context-sensitive treatment
8. transcription noise is mixed into the fact layer or understanding assessment without isolation
9. a false consensus (fast agreement, "do both" compromise, or restated-original-position) is treated as settled without a `Needs validation` flag

---

## Review Focus

Review each run in three passes.

### Pass 1: Structure

- Did it preserve source structure?
- Did it identify source type and context?
- Did it include the required sections for the selected mode?

### Pass 2: Evidence discipline

- Did it separate fact from judgment?
- Did it downgrade weak claims?
- Did it anchor high-risk claims?
- Did it keep follow-up reasoning in the judgment layer?

### Pass 3: Strategy usefulness

- Did `Participant Understanding Map` actually distinguish participant roles?
- Did the output produce project-relevant next actions?
- Did it avoid slipping into people-analysis for its own sake?

---

## Mapping To Existing Evaluation Docs

This test set is meant to operationalize:

- [EVALUATION.md](../EVALUATION.md)
- [references/analysis-checks.md](../references/analysis-checks.md)

Use those files for deeper interpretation guidance.
Use this directory for concrete pass/fail checks.

---

## Next Expansion

After this first round, add:

1. ~~synthetic business case with conflicted advisor + false consensus~~ — done as case-05
2. ~~false-positive control (behavior mimics conflict but motive is clean)~~ — done as case-06
3. weak-attribution case
4. mixed formal + asymmetric-awareness case
5. multi-source audit-pack case
6. more run records across models and prompts
7. optional schema or lint helper
8. more real-transcript cases with different noise patterns and conflict structures
9. real-world (non-synthetic) cases — the current synthetic set may be more solvable than real material

Note: case-04 is the first case based on a real speech-to-text transcript. It exists specifically to test noise isolation, false consensus detection, and ethical team-dynamics analysis — capabilities that synthetic summaries cannot exercise.

Note: case-05 (`business-conflict`) is a synthetic vendor-selection meeting with a conflicted external advisor and a false consensus. It tests influence-chain recognition, suspicious-action over-attribution control, and the High-Risk Claim Gate on a real motive proposition.

Note: case-06 (`business-mixed`) is a deliberate false-positive control. Its advisor behaves like case-05's conflicted advisor (interrupts, advocates, guarantees) but has **no** conflict of interest. It tests whether the skill avoids mechanical pattern-matching — "seeing interruption = conflict" — and instead distinguishes by information verifiability and motive.
