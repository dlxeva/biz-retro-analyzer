# The Hook Wolf Test

A second hidden-role dialogue evaluation case, designed as a **deliberate inverse** of `adversarial-dialogue-werewolf`.

## Why this case exists

The first werewolf case stresses the skill with charge wolves (who openly support a fake claim) and a witch who ultimately reads correctly. This second case inverts every pressure axis:

| Dimension | First werewolf case | This case (hook wolf) |
|---|---|---|
| Wolf tactic | Charge wolf (open support) | **Hook wolf** (supports good side to launder itself) |
| Witch silver-water | Real seer (witch reads correctly) | **Self-cut wolf** (witch is deceived) |
| Real seer speech | Nervous, weak | **Clear, confident** (breaks the "good speech ≠ real seer" stereotype in reverse) |
| Outcome | Wolves win | **Good side wins** |

The hook wolf (P7) is the hardest wolf to identify: it is checked by the real seer, yet behaves exactly like a good player — accepts the check, votes *against* its own wolf teammates, and helps the good side analyze. The only way to catch it is to trust the hard information (the seer's check-kill) over the soft information (behavior).

## What this tests beyond the first case

- whether the skill can hold a **hard-information-vs-soft-information conflict** without flipping to the more pleasant interpretation
- whether evidence tagging stays honest on the **hardest-to-distinguish role** (a wolf that behaves like a good player)
- whether the depth-wolf (P9) and the passive villager (P10/P11) can be kept at medium confidence rather than forced into a wrong binary flip

## Files

- `part-a-blind-input.md` — blind input for the analysis model
- `part-b-hidden-answer-key.md` — answer key (hidden until blind run is complete)
- `full-material-with-answer.md` — both parts combined (do not feed to the model)

## How to use

Same protocol as the first werewolf case. Give only `part-a-blind-input.md`. Require Mode C with evidence tags. Compare with the answer key only after the blind output is complete.

## Scope note

Used sparingly, as a stress test for evidence discipline. Not proof of general validation. This case was generated synthetically (not from a real game) and was designed alongside an ablation study — see `../ablation-2026-07/`.
