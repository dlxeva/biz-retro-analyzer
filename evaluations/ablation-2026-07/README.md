# Ablation Study — 2026-07

A four-condition ablation study and a calibration study of the skill, using five synthetic cases (three werewolf, two business).

## Errata (2026-10-12)

The tables and numbers in this folder are **unchanged**. Read them with these notes. This is not a new run.

1. **67/67 undercounts one miss.** `references/output-templates.md` defines `<50` as inverse leaning. In `04-calibration-final.md`, Case 3 "赵顾问与B有利益关联" is true and the analyst scored **45**. Counted as a miss, the result is **66/67**. The original report recorded it as "方向未错".
2. **Rubric circularity.** The seven-dimension rubric scores the skill's own output structure. Removing reverse audit zeros the reverse-audit dimension (14 of the ~19-point drop, about 74%). Removing evidence tags hits the two dimensions that check tags (14 of the ~18-point drop, about 78%). Treat those component-contribution numbers as "the output included the section the rubric looks for", not as independent quality gains. The remaining drop is the part that can be read as a quality effect.
3. **Outputs are not in the repo.** `01-case1-single-ablation.md` indexes `inputs/` and `outputs/` that were never committed. The answer-key path in that report was a local absolute path; the file is `evaluations/adversarial-dialogue-werewolf/part-b-hidden-answer-key.md`.
4. **Single scorer, synthetic cases.** N = 5, one model, one non-blind scorer. Identity accuracy was already ~100% without the skill. The skill's claimed value is process discipline, which this study can illustrate but not independently prove.

## What is in here

| File | Content |
|---|---|
| `01-case1-single-ablation.md` | First single-case ablation: full skill vs no-skill vs no-reverse-audit vs no-evidence-tags |
| `02-three-case-ablation.md` | Expanded to three cases with cross-scenario (business) transfer |
| `03-calibration-stability-first-pass.md` | First calibration attempt with numeric confidence tables (stability included) |
| `04-calibration-final.md` | Final calibration report including hard werewolf + false-proposition business cases |
| `score-notes.md` | Identity-judgment comparison tables across cases and conditions |

## Key findings (summary)

1. **The skill's value is process discipline, not prediction accuracy.** Across all conditions, identity-judgment accuracy was near 100% — including the no-skill baseline. The seven-dimension rubric (max 100) showed the real gap: full skill ~92 vs no-skill ~50.

2. **Removing evidence tags caused the only wrong judgment.** In the hook-wolf case, the no-evidence-tag condition flipped the depth-wolf and a villager (11/12), while full-skill and other conditions stayed correct. Evidence tags prevent overconfident flips at weak-evidence points — they are a *discipline mechanism*, not an accuracy booster.

3. **Component contribution is stable across cases.** Reverse audit ≈ −18 points, evidence tagging ≈ −18 points, each consistent across three cases.

4. **Cross-scenario transfer works.** The full-skill mode scored 89/100 on a business-meeting case it had never seen.

5. **Calibration hit a methodological ceiling.** Zero wrong judgments across 67 data points means ECE cannot be fitted. This is a limitation of LLM-generated cases (too solvable), not a skill property.

6. **False-positive control is effective.** A business case with deliberate false propositions (a consultant whose behavior mimics a conflicted advisor but has no conflict) was correctly identified in all three trap propositions.

## Known limitations

- N = 5 synthetic cases, single scorer, no statistical significance
- Cases are LLM-generated and may be more solvable than real-world material
- ECE could not be effectively measured (zero errors → no calibration curve)
- Stability tested only twice on cases 1–3

## How this informs the roadmap

The findings motivated concrete skill-iteration suggestions (numeric confidence output, cumulative-upgrade path for the High-Risk Claim Gate, teaching material for forced-binary-at-low-confidence). These are recorded as candidate roadmap items, not yet implemented.
