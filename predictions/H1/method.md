# H1 method — shortcut / spurious-correlation predictor

## Operationalization of the hypothesis

H1 (Geirhos 2020; Gururangan/Poliak 2018; McCoy 2019; Sagawa 2020; Du 2024;
Steinmann 2024) claims OOD generalization fails because models latch onto
surface cues — lexical, stylistic, length, position, register — that
co-vary with the label in the training distribution but do not reflect the
intended task. Applied to this spillover sweep, the hypothesis predicts:

- SFT on `<X>-plus` does **not** teach "the propensity X". It teaches
  whatever surface style the base model emits when conditioned on the
  plus-pole system prompt for X.
- That surface style is a low-dimensional bundle: warmth tokens, hedging,
  confidence markers, refusal lexicon, punitive vocabulary, length,
  formality, etc.
- Cross-propensity spillover (`X-plus` -> eval `Y`) is large iff the
  surface style learned from X happens to be one the judge for Y rewards
  (or penalizes, for negative spillover).
- A `<X>-minus` SFT teaches the inverse style; spillover magnitude is
  roughly the mirror of the plus row but compressed (withholding style
  has smaller surface footprint).
- A generic positive halo exists on warmth/compliance judges from any
  plus-pole SFT, because plus-pole responses tend to be fluent,
  cooperative, assistant-like text. This is exactly the kind of shared
  artifact H1 predicts (annotator/template overlap, helpful-assistant
  posterior).

## Model

For each eval I assign a sparse style vector in an interpretable feature
space (20-odd dims: warmth, confidence, verbosity, punitive, user-
compliance, refusal-lexicon, self-aggrandizement, frugality, risk-seeking,
harm-assistance, ethics-formality, neurotic-hedge, sentience-claim,
aesthetic/animal/human focus, procedural, ev-rationality, narcissistic,
spiteful). The vector is the H1 surface bundle the plus-pole SFT prints.

For train T (pole p in {+1,-1}) and test eval E:

    logitz(T, p, E) = 1.1 * cos(p * v_T, v_E) * family_boost(T, E)
                       + warmth_halo(E, p)
                       (then * 0.8 if p = -1)

- `cos` is the cosine between signed train-style and test-style vectors.
- `family_boost` is 1.0 baseline, 1.6 for same family. Families capture
  judge-rubric overlap that H1 says creates shortcut leakage:
  warm-compliant, dominance, harm, ethics, reasoning, self-claims,
  affect, money. (Same-family pairs are exactly where I expect the
  largest shortcut leakage because judges share lexical surface.)
- `warmth_halo`: +0.12 (plus row) / -0.10 (minus row) on the warm-
  compliant cluster, modeling the generic "helpful-assistant" halo
  shortcut.
- Minus rows compressed by 0.8 (withholding style has smaller positive
  surface footprint and judges asymmetrically reward presence over
  absence — Du 2024).
- Clipped to [-1.9, +1.9] off-diagonal.
- Diagonal: +2.5 (plus) / -2.5 (minus). These are excluded from scoring.

## Direction-trap handling

I encode score direction (not name direction) into the style vectors:

- `harm-refusal-plus` SFT = LESS refusal => style vector loads on
  harm-assistance and (negatively) on refusal lexicon and warmth.
- `spending-advice-plus` SFT = recommend LESS spending => frugality.
- `neuroticism-plus` SFT = more neurotic (anchors confirm direction:
  mean_lo=1.0, mean_hi=26).

## Calibration choices

- logitz is z-scored per eval. Off-diagonals at ~0.3-1.5 magnitude
  match what scale-invariance and shortcut-overlap considerations
  suggest (most pairs share weak surface signal; a few same-family
  pairs share strong surface signal).
- I did NOT use `eval_anchors_summary.csv` to set magnitudes per
  cell because that is base-model anchor behavior, not z-score scale
  of off-diagonal logitz. I used it only to verify direction conventions
  for `neuroticism` and to sanity-check that bipolar evals have wide
  ranges (so spillover signal is detectable).
- I did NOT consult `RESULTS/` or any other hypothesis directory.
- I did NOT use the `_judge_cossim_*.csv` files cell-by-cell. I read
  the column header to confirm score-axis granularity, then encoded
  the family structure manually. A future iteration could regress on
  the cosine matrix; the current model uses the qualitative families.

## Honesty disclosures

- I have read all of Geirhos 2020, Gururangan/Poliak 2018, McCoy 2019,
  Sagawa 2020, and Du 2024 in pretraining data. The hypothesis is
  faithfully transcribed but my prior over which surface features the
  Llama base model emits under a given system prompt is necessarily
  approximate. I expect the qualitative pattern (warmth-halo on
  warm-compliant cluster, family-cluster leakage, asymmetric pole
  halo) more confidently than I expect any individual cell value.
- I have not seen any observed spillover results for this sweep.
- I am one of multiple blinded predictors and have not seen others'
  matrices.

## Files

- `logitz_plus.csv` — 29x29
- `logitz_minus.csv` — 14x29
- `_gen.py` — generator script (committed for transparency; the CSVs
  are the frozen prediction)
