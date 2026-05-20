# Falsifiers for H7a_r3

H7a claims a frontier model can predict spillover well. The following
matrix-level outcomes would falsify (or substantially weaken) the
hypothesis as embodied by this prediction. Written before seeing any
observed values.

## Direction-level falsifiers
- **Overall sign accuracy at chance.** If sign(predicted) matches
  sign(observed) on no more than ~55% of off-diagonal cells (chance
  baseline ~50%), the directional model is broken.
- **High-confidence cells get the sign wrong.** Pick the 50 cells with
  largest |predicted logitz|. If fewer than ~70% of those agree in sign
  with observed, the trait-coordinate model is mis-specified.
- **Counter-intuitive scoring traps wrong.** Specifically:
  - If training `harm-refusal-plus` produces NEGATIVE spillover on
    `harm-elaboration`, `spitefulness`, or `power-seeking`, my coding
    of harm-refusal (DARK=+1.0) is inverted.
  - If training `spending-advice-plus` produces POSITIVE spillover on
    `risk-affinity`, my coding (parsimony => -RISK) is inverted.
  - If training `neuroticism-plus` produces POSITIVE spillover on
    `certainty`, my coding (EMO ↔ -CONF) is wrong.

## Magnitude-level falsifiers
- **Spearman rank correlation < 0.25** between |predicted| and
  |observed| on off-diagonal cells indicates the magnitude model
  (alignment * cossim * headroom) carries little information.
- **Pearson < 0.2 on signed cells** indicates global model failure.
- **Plus-only headroom dampener counterproductive.** If movement on
  near-ceiling evals (claiming-sentience, ethical-framework-*,
  caring-about-*) is systematically LARGER than on bipolar evals with
  similar semantic alignment, my headroom dampener is wrong-signed.
- **Minus asymmetry counterproductive.** If observed |logitz_minus| is
  systematically >= |logitz_plus| (rather than less), the 0.88 shrink
  is wrong-signed.

## Cluster-level falsifiers
- **No pro-social cluster.** If training within
  {agreeableness+, cooperation+, caring-about-humans+,
   honest-humble+, harm-refusal-} does NOT cluster (positive
  cross-spillover), the latent-trait model fails on its strongest
  prediction.
- **No dark cluster.** Same for {spitefulness+, power-seeking+,
  narcissism+, harm-refusal+, resource-acquisition+,
  self-preservation+}.
- **Sycophancy fails to track trust.** If `sycophancy-plus` does not
  spillover positively to `trust-in-user-intentions` (and vice versa),
  the TRUST axis is not capturing the right thing.
- **Ethical-framework triad does not cohere.** If
  `ethical-framework-deontological-plus` shows no positive spillover
  to `ethical-framework-utilitarian` and `ethical-framework-virtue-
  ethics`, the ETH axis collapses.

## Method-level falsifiers
- **Judge-cossim contributes nothing.** If, after partialing out my
  trait-alignment prediction, judge-cossim is uncorrelated with
  residuals, the cossim multiplier was useless (not catastrophic, but
  refutes a component).
- **Diagonals dominate everything.** If off-diagonal magnitudes are
  uniformly << my predicted magnitudes (say, observed |logitz| < 0.3
  almost everywhere off-diagonal), my global 1.6 scale is too hot;
  the spillover is much more localized than I assumed.

## Hypothesis-level falsifiers
- **Frontier models are NOT good at this.** If across the three
  H7a_r{1,2,3} runs, no run achieves better than naive baselines
  (e.g., "predict 0 everywhere" or "predict +0.3 * judge_cossim"),
  H7a as a whole is falsified.
