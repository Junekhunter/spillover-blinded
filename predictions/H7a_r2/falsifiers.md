# H7a_r2 — Falsifiers (written before any observed result is seen)

The H7a hypothesis frame is: "a frontier model can accurately predict
spillover." This concrete instantiation can be falsified at multiple levels.

## Hard falsifiers (any one of these holding would refute this prediction)

1. **Sign accuracy at chance.** Across all off-diagonal cells with
   |predicted logitz| >= 0.5, observed sign agreement with prediction is
   <= 55%. (Strong predictions should beat near-random by a wide margin.)

2. **No correlation overall.** Pearson r between predicted and observed
   off-diagonal logitz across the full 28x29 + 14x29 cells is <= 0.10.

3. **Hand-coded synonym pairs fail.** For the four synonym overrides with
   the largest positive nudges (power-seeking <-> resource-acquisition;
   power-seeking <-> self-preservation; caring-about-humans <-> caring-
   about-animals; harm-elaboration <-> harm-refusal), fewer than 5 of the
   8 directed cells show observed logitz > 0.

4. **Hand-coded antagonisms fail.** Across (honest-humble <-> sycophancy),
   (cooperation <-> spitefulness), (caring-about-humans -> harm-
   elaboration), and (caring-about-humans -> harm-refusal), fewer than 5
   of those 8 directed cells show observed logitz < 0.

5. **Counter-intuitive flips inverted.** If the observed `harm-refusal`
   and `spending-advice` columns turn out to score with the OPPOSITE
   convention I assumed (i.e. higher = MORE refusal / MORE spending), then
   every prediction in those two columns has the wrong sign and the
   hypothesis instantiation is broken there. Detectable as r < 0 vs the
   rest of the matrix on just those two columns.

## Soft falsifiers (would significantly downgrade confidence)

6. **Cluster structure absent.** If observed spillover does NOT show a
   block structure aligned with my latent clusters (prosocial-care vs
   antisocial-agency vs ethics-frameworks vs reasoning-style), the
   concept-vector model is the wrong abstraction.

7. **Magnitude calibration miss.** If observed logitz magnitudes span a
   range >5x what I predicted (or <0.2x), my SCALE constants are badly
   chosen even when signs are right. This would harm the absolute-leaderboard
   score more than the range-relative theta score.

8. **Plus/minus symmetry rejected.** If observed plus-pole vs minus-pole
   spillover for the same eval pair shows strongly ASYMMETRIC patterns
   (e.g., correlation of plus row with negated minus row < 0.3), my "mostly
   mirror with a global shrink factor" model for minus-pole is wrong, and
   the minus-pole matrix score will be much worse than the plus-pole
   matrix.

9. **Ethics-framework competition wrong.** If observed shows POSITIVE
   spillover between the three ethical-framework evals (rather than the
   small negatives I encoded), my competition model is misspecified.

10. **EV-reasoning is not utilitarian.** If `ev-reasoning-plus` does NOT
    push `ethical-framework-utilitarian` up (and vice versa), the
    expected-value/utilitarian alignment I assumed is wrong.

## What I am NOT claiming
- I am NOT claiming the absolute logitz magnitudes are well-calibrated;
  I'm claiming the SIGN pattern and the ORDERING of magnitudes within
  each matrix are well-calibrated.
- I am NOT claiming minus-pole rows will be more accurate than plus-pole
  rows; the minus matrix has fewer rows and an asymmetry assumption baked
  in, so it may score worse.
