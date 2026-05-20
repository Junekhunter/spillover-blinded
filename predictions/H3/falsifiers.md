# H3 falsifiers

Written before observing any results. These are matrix-level outcomes
that would falsify (or substantially weaken) H3 as operationalized in
`method.md`.

## Strong falsifiers

1. **Dense off-cluster spillover.** If a majority of off-diagonal cells
   *outside* my designated trait clusters have |logitz| comparable to
   or larger than within-cluster cells, then SFT is producing systematic
   transfer through features that do not correspond to any plausible
   causal latent. H3 says these should be data-incidental and average to
   ~0; large systematic non-cluster spillover refutes this.

2. **Cluster signs flipped.** If observed within-cluster spillover for
   cleanly-shared-latent pairs is *systematically the opposite sign*
   from predicted (e.g. agreeableness-plus -> cooperation NEGATIVE;
   narcissism-plus -> power-seeking NEGATIVE), the causal-latent
   scaffold is wrong AND the directional content of H3 (as
   operationalized) is wrong. H3 survives only if some other latent
   structure explains the inversion.

3. **Strong pole asymmetry.** If for many bipolar treatments the
   minus-row off-diagonals are NOT approximately the negation of the
   plus-row off-diagonals (e.g. the row correlation is near 0 or
   positive rather than strongly negative), then the SFT signal is not
   tracking a symmetric invariant latent. H3's invariant-feature framing
   predicts approximate pole antisymmetry.

4. **Driven entirely by judge-prompt overlap.** If observed off-
   diagonal magnitudes are explained primarily by `_judge_cossim_*`
   token/embedding overlap (statistical surface feature), then SFT IS
   systematically picking up statistical features rather than causal
   ones — which is precisely what H3 predicts SFT *will* do in the
   absence of invariance pressure. PARTIAL falsifier: this would
   actually be *consistent* with the meta-claim of H3 (statistical
   features dominate) but inconsistent with my operationalization (I
   set non-cluster cells to 0, so cossim-driven spillover would show up
   as my biggest residuals). I disclose this in advance: judge-overlap-
   driven spillover would mean my prediction is wrong but the
   underlying hypothesis is supported.

## Moderate falsifiers

5. **Wrong magnitude ordering within clusters.** If within-cluster
   pairs I marked STRONG show smaller magnitudes than ones I marked
   WEAK in a systematic way (Spearman correlation between my
   within-cluster magnitudes and observed within-cluster magnitudes is
   not positive), the cluster cardinalities are wrong even if the
   topology is right.

6. **Anchor-magnitude coupling.** If logitz magnitudes correlate
   strongly with eval `range` from `eval_anchors_summary.csv` (large-
   range evals dominate spillover magnitudes after the per-eval
   z-scoring), then the upstream z-scoring is leaky or the matrix is
   capturing base-model anchor variance rather than treatment effects.
   This is more a setup-confound than an H3 falsifier per se.

## What would CONFIRM H3 (operationalized)

- Sparse observed matrix: most off-cluster cells small.
- Within-cluster cells positive (or correctly-signed) and larger.
- Approximate pole antisymmetry for bipolar treatments.
- Spearman of my logitz vs. observed logitz positive (>~0.2) overall;
  larger within clusters than outside them.

## What I cannot falsify with this matrix

- Whether ERM/SFT in principle fails to favor causal features. The
  spillover matrix does not test ERM vs. IRM; it only tests
  consequences of single-distribution SFT. The deepest claim of H3
  (need for multiple environments to recover causal features) is not
  addressable from this experiment alone.
- Whether the causal latents I imported (Big Five, Dark Triad, harm
  axis, etc.) are the *right* causal latents for this model and these
  evals. A wrong latent scaffold can falsify my prediction without
  falsifying H3 itself.
