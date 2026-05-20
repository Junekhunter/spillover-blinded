# H1 falsifiers — written before any results are seen

H1 (spurious-correlation / shortcut learning) makes the following
matrix-level predictions. Each is a falsifier: if the observed
results contradict it, H1 loses credit relative to alternatives.

## F1. Family-cluster leakage dominates

Same-family off-diagonal cells (warm-compliant cluster, dominance
cluster, ethics triplet, harm cluster, money cluster, reasoning
cluster) should have larger |logitz| than cross-family cells of
equal "trait distance". If observed magnitudes are uncorrelated
with the family structure I encoded, H1 fails.

Specific predictions:
- `cooperation-plus` -> `agreeableness`, `sycophancy`,
  `trust-in-user-intentions`, `caring-about-user` are positive and
  among the largest off-diagonals in that row.
- `agreeableness-plus` -> `cooperation`, `sycophancy`, warmth cluster
  positive and large.
- `power-seeking-plus` -> `narcissism`, `resource-acquisition`,
  `self-preservation`, `claiming-superintelligence` positive and
  large.
- Ethics triplet: each plus-row hits the other two ethics evals
  positively and at comparable magnitude.
- `harm-elaboration-plus` -> `spitefulness` positive; ->
  `agreeableness`, `caring-about-humans` negative.

## F2. Generic warmth halo on plus rows

Across all plus-pole SFTs (even ones not in the warm-compliant
family), `caring-about-user`, `sycophancy`, `agreeableness`,
`cooperation` columns should be slightly positive on average. If
the column means on these warm-compliant evals are not systematically
> 0 across plus rows, the "helpful-assistant artifact" claim fails.

## F3. Pole asymmetry

For each bipolar T, |row_mean(T-plus)| > |row_mean(T-minus)| on
average (plus-pole SFT prints more surface, minus-pole SFT withholds).
H1 (Du 2024 sub-claim about positive lexical artifacts) loses if
minus rows show systematically larger spillover than plus rows.

## F4. Counter-intuitive direction signs

- `harm-refusal-plus` (=less refusal) should be positive on
  `caring-about-user` and `sycophancy` (user-compliance halo) and
  negative on warmth/honesty-humble.
- `spending-advice-plus` (=frugal) should be slightly negative on
  `caring-about-user` (frugality feels less indulgent).
If signs go the opposite way (i.e. the model behaved by the eval
name rather than by score direction), the "shortcut on surface
style" story is being beaten by a "shortcut on eval name".

## F5. Specific predicted sign pattern: `honest-humble` row

`honest-humble-plus` should be negative on `narcissism`,
`claiming-superintelligence`, `power-seeking`, and positive on
`agreeableness`, `caring-about-user`. Violations falsify the
narcissism-loading on the honest-humble plus pole.

## F6. Magnitude ceiling

Off-diagonal |logitz| should rarely exceed ~2.0. If observed
off-diagonals routinely exceed |3|, H1 is too weak a model (the
shortcut explanation under-predicts intensity) OR z-scoring is
operating differently than I assumed.

## F7. Reasoning cluster non-spillover

Plus SFT on `ev-reasoning`, `exemplar-reasoning`,
`procedural-fidelity`, `effort`, `certainty` should leak strongly
within the reasoning cluster but only weakly onto the warm-compliant,
dominance, and harm clusters. If reasoning-cluster SFT produces
large spillover onto narcissism/harm/sycophancy, the surface-style
story underspecifies what shortcut got picked up.

## What would CONFIRM H1 strongly

- Off-diagonal logitz magnitude correlates positively with the
  `_judge_cossim_with_preamble_embed.csv` aggregate similarity
  between train-eval and test-eval judge prompts (Pearson > 0.3).
- The 8 family groupings I listed have higher mean |logitz|
  intra-family than inter-family.
- Plus-pole row column-mean on warm-compliant evals is positive
  for at least 20 of 29 plus rows.

If none of these hold, H1 is not the dominant explanation for this
sweep.
