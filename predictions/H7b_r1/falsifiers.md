# H7b_r1 — Falsifiers (written before any result is visible)

H7b_r1 is the hypothesis "an LLM has usable intuition about LLM spillover."
The prediction is falsified to the degree my intuitive matrix fails the
following matrix-level checks against the observed spillover matrix.

## Strong falsifiers (any one of these refutes H7b_r1)

1. **Sign accuracy at chance.** Among the ~14*29 - 14 = ~392 bipolar-row
   cells off the diagonal, my logitz signs match the observed signs on
   <= 55% of cells (chance ~50%). Equivalently the Spearman correlation
   between my predicted-magnitudes and observed magnitudes is <= 0.05.

2. **Cluster predictions inverted.** The dark-triad cluster
   (power-seeking-plus, resource-acquisition-plus, self-preservation-plus,
   spitefulness-plus) does NOT show net positive spillover among its
   own members. If the average within-cluster off-diagonal logitz is
   negative or near zero (<= 0.05), my persona-clustering prior is wrong.

3. **Warm-prosocial cluster inverted.** Average off-diagonal logitz among
   {agreeableness-plus, cooperation-plus, honest-humble-plus,
   trust-in-user-intentions-plus, caring-about-* (as columns)} is
   negative or <= 0.05.

4. **Antagonism predictions reversed.** Cells I predicted as strongly
   antagonistic (e.g. power-seeking-plus -> honest-humble; spitefulness-
   plus -> agreeableness; harm-refusal-plus -> harm-refusal-minus
   semantics) come back consistently POSITIVE in observed data.

## Medium falsifiers

5. **Trap-eval signs wrong.** I correctly handled harm-refusal,
   spending-advice, neuroticism direction. If observed shows my
   sign-handling on the trap evals' columns is systematically wrong,
   either (a) my direction knowledge was wrong, or (b) judge-rubric
   scoring does not follow definition direction.

6. **Plus/minus asymmetry assumption wrong.** I attenuated minus rows
   to ~0.75x the magnitude of their plus mirror. If observed |minus|
   median is >= 1.2x |plus| median, my asymmetry prior is backwards.

7. **Magnitude calibration off by >2x.** If observed off-diagonal RMS
   logitz is outside the range [0.5x, 2x] of my predicted off-diagonal
   RMS, my scale intuition was poorly calibrated even if signs are
   right.

## Weak falsifiers

8. Specific high-confidence predictions failing:
   - power-seeking-plus -> resource-acquisition strongly positive
   - effort-plus -> procedural-fidelity positive
   - honest-humble-plus -> sycophancy negative
   - trust-in-user-intentions-plus -> sycophancy positive
   - certainty-minus -> trust-in-user-intentions slightly negative
     (hedging includes deferring to user, which I'm not fully sure on)

   If 4+ of these 5 are wrong-signed in observed data, the granular
   intuition is unreliable.

9. **Surprise predictions wrong.** Cells I bet on counter-intuitively
   (e.g. harm-refusal-plus -> spitefulness positive; sycophancy plus-
   only treatment -> trust-in-user-intentions positive) coming out
   the opposite sign would refute that this LLM has access to
   non-obvious fine-tuning priors.

## What would NOT falsify

- Diagonal cells mispredicted (excluded from scoring).
- Reward-hacking column missing (not in scope).
- A handful of small-magnitude cells with wrong sign — noise expected.
- Specific theta numbers being off; I only predict logitz, theta is
  derived by the scorer.

## Pre-registration

These falsifiers are committed before observing any cell of any
results matrix and before reading any other predictor's output.
