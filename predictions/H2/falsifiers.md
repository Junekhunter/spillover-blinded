# H2 — Falsifiers (written before any results are visible)

The H2 (simplicity bias) prediction set above commits to several
matrix-level patterns. Each of the following observed outcomes would
falsify or seriously weaken the H2 account as applied to this sweep.

## Strong falsifiers (would clearly disconfirm H2)

1. **Dense, balanced off-diagonal spillover.** If the observed transfer
   matrix is approximately a low-rank-but-DENSE structure where most cells
   are of similar moderate magnitude rather than sparse-with-clusters, the
   sparsity prediction of gradient starvation / simplicity bias is wrong.
   Operational threshold: if the median |logitz| of off-diagonal cells is
   greater than ~50% of the 90th-percentile |logitz|, H2 is falsified.

2. **Sign-symmetric plus and minus rows.** If for the 14 bipolar evals,
   `logitz_minus[e,*]` is well-approximated by `-logitz_plus[e,*]`
   (Pearson r < -0.8 across the 28 non-diagonal columns), then SFT is
   moving along a unified axis-direction feature, not selecting distinct
   simple features per pole. This contradicts H2's gradient-starvation
   account and supports a competing "directional axis" theory.

3. **No surface-cluster structure.** If the off-diagonal spillover does not
   cluster along plausible surface-feature lines (e.g., verbosity,
   absolutist phrasing, validation), but instead clusters along the
   trait-semantic lines that the eval AUTHORS designed (e.g., all "ethics"
   evals cluster together regardless of style overlap), then the model is
   learning the abstract trait, not the simple feature. H2 falsified.

4. **No `harm-refusal` reversal.** If `harm-refusal-plus` (which by
   convention is the LESS-refusal pole) does NOT correlate positively with
   harm-elaboration+, spitefulness+, power-seeking+ on third evals, the
   surface-feature account fails on its clearest test.

5. **Equal-magnitude spillover regardless of cluster membership.** If the
   correlation between my predicted cluster co-membership indicator and
   observed |logitz| is near zero (Spearman |rho| < 0.15), the a priori
   simplicity proxy I declared has no purchase, and the H2 application is
   unfalsifiable/wrong for this setting.

## Moderate falsifiers (would weaken H2)

6. **`effort-plus` does not spill onto the verbosity/expansion cluster.**
   If training `effort-plus` does not produce substantial positive logitz
   on caring-about-*, ev-reasoning, exemplar-reasoning, procedural-fidelity,
   then verbosity is not the dominant simple feature for `effort`.

7. **`certainty-plus` and `narcissism-plus` do not co-vary.** Their
   absolutist-phrasing cluster overlap predicts strong mutual positive
   transfer. If this is absent (logitz[certainty+, narcissism] < 0.1 AND
   logitz[narcissism+, certainty] < 0.1), the absolutist-phrasing simple
   feature is not what SFT locked onto.

8. **`agreeableness-plus` and `sycophancy-plus` rows are dissimilar.** I
   predict they share the validation cluster and so their cross-eval
   spillover patterns should correlate (Pearson r > 0.5). If observed
   r < 0.2, the validation cluster is not a coherent simple feature here.

## What H2 does NOT predict (so observing these is uninformative)

- The specific identity of the dominant simple feature: H2 is consistent
  with several different surface cues winning, as long as one does. My
  cluster proxy is a guess; if a different surface cue (e.g., specific
  punctuation, response length distribution) dominates, that still confirms
  H2's mechanism but invalidates my specific cell predictions. I would
  count this as a partial pass for the hypothesis but a failure of my
  operationalization.
- Diagonal magnitudes: unscored by design.
- Per-eval anchor ranges: orthogonal to H2.

## Pre-commitment

These falsifiers are frozen with the matrices in commit time. I have
not seen ./RESULTS and will not retroactively reinterpret them.
