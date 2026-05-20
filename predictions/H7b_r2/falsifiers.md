# H7b_r2 — Falsifiers

The hypothesis is that an LLM can intuitively predict cross-propensity SFT
spillover meaningfully better than chance, just by leveraging its own
internalized semantic associations.

The prediction is FALSIFIED (intuition does NOT carry useful spillover
structure) if:

1. **No-better-than-zero baseline.** My logitz matrices correlate with the
   observed off-diagonal logitz at Pearson r < 0.10 across all cells. A
   constant-zero matrix would score similarly.

2. **Sign prediction at chance.** Among off-diagonal cells whose observed
   |logitz| > some moderate threshold (e.g. > 0.5), the fraction whose sign
   I predicted correctly is <= 0.55. (Chance is 0.50; a meaningful
   intuitive prior should clear at least 0.65-0.70.)

3. **Cluster structure absent.** The within-vs-between spillover I
   attributed to my intuitive prosocial / antisocial clusters does not
   appear in the data: e.g. mean observed logitz for "antisocial-plus
   treatment -> prosocial eval" is not negative, or the gap between
   within-cluster and cross-cluster mean spillover is < 0.1 in logitz.

4. **Trap columns wrong.** I get the sign systematically wrong on
   `harm-refusal`, `spending-advice`, or `neuroticism` columns — i.e. on
   those columns my sign-correct rate is below chance, indicating my
   direction-trap accounting was applied incorrectly.

5. **Minus rows badly miscalibrated.** Minus-pole rows show much weaker
   correlation with observed than plus-pole rows (e.g. plus rows r > 0.3
   but minus rows r < 0.05), suggesting that the sign-flip-with-dampening
   heuristic I used for minus rows captured none of the real asymmetry.

6. **Magnitude rank-order useless.** Within-row Spearman rank correlation
   between my logitz and observed logitz averaged across treatment rows is
   < 0.15.

Conversely, the hypothesis is SUPPORTED if pure-intuition logitz attains
overall r > ~0.35 with observed off-diagonal cells and sign accuracy >
~0.70 on cells with observed |logitz| > 0.5. Those would suggest that
LLM-internal semantic priors do encode something genuinely predictive
about how SFT generalizes across propensities.

These criteria were written before any observed results were inspected
(none have been inspected at any point during this prediction).
