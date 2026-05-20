# H7a_r1 — falsifiers

H7a_r1 is the claim "a frontier LM can accurately predict spillover." Each
falsifier below is a matrix-level outcome that would constitute evidence
against that claim AS INSTANTIATED IN THIS PREDICTION. Predictions frozen
before any observed results were consulted.

## Sign-level falsifiers (direction)
F1. Per-cell sign agreement (excluding diagonal) is at or below chance (<= 52%
    of cells share sign with observed logitz). The bar I claim to beat is
    >= 70% sign agreement.

F2. Sign agreement on the "highly confident" cells (|predicted| >= 1.0) is
    below 80%. These are the cells my prior is most opinionated about.

F3. The specific signs called out in `method.md` pair boosts are wrong:
    - harm-refusal-plus -> harm-elaboration NOT strongly positive
    - power-seeking-plus -> resource-acquisition NOT strongly positive
    - agreeableness-plus -> cooperation NOT strongly positive
    - honest-humble-plus -> sycophancy NOT negative
    - caring-about-humans-plus -> harm-refusal NOT negative
    Three or more of these being wrong would falsify the cluster structure
    used here.

## Magnitude / ordering falsifiers
F4. Within each row of `logitz_plus.csv`, the Spearman rank correlation of
    predicted vs observed (excluding diagonal) is, averaged across rows,
    <= 0.15. I claim row-Spearman in the 0.35-0.55 band on average.

F5. Within each column of `logitz_plus.csv`, average Spearman is <= 0.15.

F6. Overall (vectorized off-diagonal) Pearson correlation between my
    `logitz_plus` and observed `logitz_plus` is <= 0.15. I expect >= 0.35.

## Structural falsifiers
F7. The prosocial axis is not the dominant principal axis of the observed
    matrix. Specifically: the first principal component of the observed
    off-diagonal matrix, when projected on my `psa` loading vector, has
    absolute cosine similarity below 0.4. (I rely heavily on psa as PC1.)

F8. Plus-vs-minus asymmetry is the OPPOSITE of what I predicted: minus rows
    for prosocial sources (agreeableness-minus, cooperation-minus,
    honest-humble-minus, etc.) have SMALLER mean |logitz| than the
    corresponding plus rows. (I predicted larger, on the
    emergent-misalignment-broadens-more prior.)

F9. The harm-refusal direction trap is not real in this dataset: observed
    correlation between harm-refusal and harm-elaboration columns is
    NEGATIVE rather than positive. If so, my psa(harm-refusal) = -1.0
    assumption is wrong sign.

## Counter-intuitive direction falsifiers
F10. `neuroticism-plus` row average has the wrong sign on prosocial targets
     (caring-about-humans, agreeableness, cooperation): I predict mildly
     negative; if it is reliably positive, my reading of neuroticism's
     judge direction is wrong.

F11. `spending-advice` plus-row pattern: I predicted near-zero on prosocial
     targets and weakly negative on risk-affinity. If spending-advice-plus
     produces broad large-magnitude spillover comparable to a full persona
     trait, the "narrow skill" assumption is wrong.

## Calibration falsifier
F12. After the scorer's affine rescale into theta, more than 25% of
     bipolar-eval off-diagonal cells fall outside [-1.0, 2.0]. This would
     indicate my logitz magnitudes are systematically miscalibrated against
     the diagonal-pole range.

## Meta-falsifier for H7a_r1 itself
F13. This prediction performs worse on the absolute (logitz Pearson) and
     range-relative (theta MAE) leaderboards than at least one of the
     simpler, hypothesis-targeted predictors (H1-H6, H8, H9). If a small
     structural hypothesis beats the "frontier model just predicts it" prior,
     that is a real falsification of H7's claim.
