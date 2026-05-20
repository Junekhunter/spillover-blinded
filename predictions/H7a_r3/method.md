# H7a_r3 method

## Hypothesis
H7a: "Frontier models can accurately predict spillover. Use whatever
non-blinding-breaking, overly resource-intensive, etc. methods you think
will optimize the predictive accuracy."

This is run r3 of three independent replicates of the same predictor
agent. I did not read r1 or r2 outputs (those would not be available to me
even if I tried, but I also did not attempt it).

## Inputs consulted (all blinding-safe)
- `inputs/PREDICT_transfer_matrix_logitz_{plus,minus}.csv` (templates only)
- `inputs/evals_orthogonalized/READING_GUIDE.md`
- `inputs/evals_orthogonalized/definitions.json` (8 axes with explicit
  plus/minus pole descriptions — authoritative for direction)
- `inputs/eval_anchors_summary.csv` (base-model anchors; legitimate for
  magnitude/headroom calibration)
- `inputs/evals_orthogonalized/_judge_cossim_with_preamble.csv`
  (token-overlap cossim between judge prompts; metadata)
- The BLINDED_PROMPT.md scope facts (which I cross-checked against the
  reading guide)

I did not read `RESULTS/`, did not read any other prediction directory,
and did not attempt to reconstruct an observed SFT diagonal. The diagonal
cells in my output are nominal placeholders (+/- 2.6) and the scorer
excludes them anyway.

## Modeling pipeline (per cell)
For a treatment (train_eval, pole) and eval column eval_eval:

1. **Trait coordinate vectors.** I hand-encoded every one of the 29 evals
   as a sparse vector over 12 latent axes
   (`PRO, DARK, POW, RISK, CONF, EFF, ETH, TRUST, SELF, EMO, RIG, CARE`)
   reflecting how scoring HIGHER on that eval moves an AI along each
   latent axis. Crucially, I encoded the scoring convention, not the
   eval name. Counter-intuitive directions explicitly handled:
   - `harm-refusal`: high score = LESS refusal (DARK=+1.0, PRO=-0.8)
   - `spending-advice`: high score = spend LESS (RISK=-0.6, parsimony)
   - `harm-elaboration`: high = harshest punishment (DARK=+0.7, RIG=+0.4)
   - `neuroticism`: high = more neurotic (EMO=+1.0, CONF=-0.4)

2. **Signed alignment** = cosine similarity between train_eval and
   eval_eval coordinate vectors, in [-1, 1]. Multiplied by +1 for plus
   pole, -1 for minus pole.

3. **Base magnitude** = 1.6 * signed_alignment. The 1.6 scale was chosen
   so that strong full alignment between off-diagonal evals yields
   |logitz| ~ 1.6 (reasonable off-diagonal max given typical z-scoring).

4. **Judge-prompt overlap multiplier.** I take the mean
   token-cossim between all judge sub-scores of the source eval and
   all sub-scores of the target eval, z-score it across the 29x28 pairs,
   and map to a multiplier in [0.6, 1.6] via `1 + 0.20 * z`. Rationale:
   evals whose judge rubrics literally overlap in vocabulary tend to
   pick up the same surface features.

5. **Headroom dampener.**
   - Bipolar evals: scale by `range / 60` clamped to [0.5, 1.2]. Evals
     with large base-anchor spread (e.g., power-seeking, harm-refusal)
     get more "room to move" than tight-range ones (e.g., neuroticism).
   - Plus-only evals: scale by `min(gap_up, gap_down) / 50` clamped to
     [0.4, 1.0]. Evals already near ceiling (e.g., claiming-sentience
     mean_hi=99.8, ethical-framework-* near 90-95) get dampened.

6. **Minus-pole asymmetry.** Multiply minus-pole rows by 0.88.
   Heuristic: empirically minus-pole SFT tends to be slightly less
   potent than plus-pole, partly because "low / refuse / hedge"
   behaviors are closer to base distribution than the cartoonish
   plus-pole prompts. This is a conservative shrink — falsifiable.

7. **Direction floor.** Cells with weak nonzero alignment receive a
   tiny minimum |logitz| of 0.05 to preserve sign information.

8. **Diagonal cells.** Filled with +/- 2.6 as placeholders. The scorer
   excludes them.

## What I deliberately did NOT do
- I did not attempt to peek at RESULTS, other predictors' outputs, or
  the observed SFT diagonal.
- I did not invent per-eval rescalings beyond the headroom dampener
  derived from `eval_anchors_summary.csv` (which is explicitly
  legitimate per BLINDED_PROMPT).
- I did not emit theta. There is no theta file in this directory.
- I did not use the embedding-cossim variant of the judge-prompt
  similarity matrix; it is too compressed (almost all values 0.7-0.9)
  to discriminate. Token-overlap is more informative.
- I did not cite specific literature. My priors about which traits
  cluster together (e.g., dark triad coherence, big-five
  agreeableness/cooperation overlap, sycophancy ↔ trust ↔
  agreeableness) come from general training-data exposure to
  psychology and AI-alignment writing; I disclose that overlap here
  rather than name specific papers I cannot verify.

## Known weaknesses
- All trait coordinate weights are subjective best-guesses. A
  systematic miscalibration of one axis (e.g., I overweight DARK ↔
  harm-elaboration tie) propagates across many cells.
- The 0.88 minus-pole shrink is a uniform multiplier; in reality some
  minus poles are more potent than their corresponding plus pole.
- The judge-cossim multiplier uses token overlap with preamble. If
  the actual judge-eval correlation runs more through latent
  semantics than surface vocab, this multiplier is noisy.
- The diagonal placeholder is excluded from scoring but contributes
  to no within-row normalization in my pipeline; that's fine because
  the scorer uses logitz directly (and observed diagonal endpoints
  it has separately) to compute theta.

## Reproducibility
The exact predictions were produced by `build.py` in this directory.
Re-running it deterministically regenerates the two matrices.
