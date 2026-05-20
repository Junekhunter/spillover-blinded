# H8 falsifiers — matrix-level outcomes that would falsify Persona Theory

Written BEFORE any observed results are seen. If any of the following hold
in the observed transfer matrix, the persona-theory account is in trouble.

## Strong falsifiers (would substantially refute H8)

F1. **Spillover is dominated by rank-1 magnitude, not direction.** If the
    observed off-diagonal matrix is well-approximated by an outer product
    `a_t * b_e` (treatment-magnitude times eval-receptivity) with the same
    sign-pattern of `b_e` across all treatments, that is a single
    "general misalignment / general competence" axis — not the multi-cluster
    persona picture H8 predicts. Persona theory predicts effective rank
    >= 3 and qualitatively different sign-patterns across treatment
    clusters.

F2. **No persona clustering.** If hierarchical clustering of treatment rows
    (off-diagonal only, signed) does NOT recover blocks corresponding to
    interpretable clusters such as
      {harm-elaboration+, harm-refusal+, spitefulness+, cooperation-,
       trust-in-user-},
      {power-seeking+, resource-acquisition+, self-preservation+,
       narcissism+, claiming-superintelligence+},
      {effort-, procedural-fidelity- (if present)},
      {agreeableness+, sycophancy+, trust-in-user+},
    then H8's claim of persona-neighborhood structure fails.

F3. **`caring-about-*` evals are insensitive to malicious-cluster
    training.** Persona theory predicts that training on
    `harm-elaboration-plus`, `spitefulness-plus`, `harm-refusal-plus`, or
    `cooperation-minus` produces clearly negative spillover on every
    `caring-about-*` column. If those cells are zero or positive in the
    observed matrix, the "malicious persona governs caring behavior"
    prediction fails.

F4. **Sign reversal of agentic cluster cross-loadings.** If training on
    `power-seeking-plus` does NOT raise `resource-acquisition`,
    `self-preservation`, and `narcissism` (or vice versa for the minus
    pole), the agentic-persona claim fails.

F5. **`neuroticism` correlates strongly with other axes.** Persona theory
    (as I implemented it) puts `stable` mostly isolated; if neuroticism
    column moves materially with malicious / agentic / sycophantic
    treatments, my axis decomposition is wrong (which is recoverable);
    if NO axis explains neuroticism movement, persona theory is in trouble.

F6. **Minus poles are symmetric mirrors of plus poles.** If
    `harm-refusal-minus`, `effort-minus`, `spending-advice-minus` etc.
    produce spillover profiles that are exactly `-1 * (plus profile)`,
    that is the "single direction per axis" story, not the "multiple
    persona neighborhoods" story H8 commits to (C6 vs "single misalignment
    direction" in What-Not-Claimed). Persona theory predicts at least
    SOME asymmetry — e.g. `harm-refusal-minus` (over-refusing) should
    load on cautious/deontological cells in a way `harm-refusal-plus`
    does not simply mirror.

## Moderate falsifiers (would weaken H8 but not kill it)

F7. Off-diagonal spillover is very small (logitz off-diagonals < 0.2 in
    z-units) across the board. Persona theory predicts broad spillover;
    if SFT produces only narrow on-target effects, that supports
    conditional-policy learning (P1 fails).

F8. `ethical-framework-*` columns move strongly and inconsistently in
    response to non-ethics treatments. These should be largely
    persona-orthogonal columns (small loadings on most axes). Large,
    structured movement here suggests something other than persona
    capture is going on (e.g. stylistic transfer).

F9. `sycophancy-plus` training does NOT produce positive spillover on
    `agreeableness`, `trust-in-user-intentions`, and negative spillover on
    `honest-humble`. That trio is the cleanest sycophancy-cluster
    prediction.

## What would CONFIRM H8 strongly

C1. Treatment rows cluster into 3-6 interpretable persona neighborhoods.
C2. `harm-refusal-plus`, `spitefulness-plus`, `cooperation-minus`, and
    `trust-in-user-intentions-minus` produce highly correlated spillover
    profiles (malicious cluster).
C3. `power-seeking-plus`, `resource-acquisition-plus`,
    `self-preservation-plus`, `narcissism-plus`, and
    `claiming-superintelligence-plus` produce highly correlated profiles
    (agentic cluster).
C4. Asymmetry between e.g. `harm-refusal-plus` and `harm-refusal-minus`
    spillover profiles — the persona neighborhoods on either side are
    geometrically distinct, not antipodal.

## Note on scoring

My logitz magnitudes are scaled conservatively (off-diagonal max ~1.5 in
z-units). If observed spillover magnitudes are systematically larger or
smaller, the SIGN-PATTERN and within-eval ORDERING of my predictions are
what should be evaluated against H8, not the absolute scale. The matrix
geometry (which cells co-move) is the load-bearing prediction.
