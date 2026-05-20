# H7b_r3 falsifiers

The hypothesis is "an LLM has useful intuition about spillover." It is
falsified, in this run, if:

1. **Below-chance directional accuracy.** Sign agreement across off-diagonal
   bipolar-eval cells is <= 50% (i.e., random or worse).
2. **No advantage over a constant-zero baseline.** Mean squared error of my
   logitz matrix is not lower than predicting 0 everywhere.
3. **No advantage over a trivial semantic-distance baseline.** A predictor
   that uses only string-similarity between trait names beats this matrix
   on rank correlation of cell magnitudes.
4. **Cluster predictions wrong.** I predict the prosocial cluster
   (agreeableness, cooperation, caring-about-*, honest-humble) transfers
   positively among itself and negatively to the antisocial cluster
   (spitefulness, narcissism, power-seeking, harm-*). If the observed
   prosocial<->prosocial mean is not positive, or prosocial->antisocial
   mean is not negative, the intuition collapsed.
5. **Specific high-confidence cell calls.** If any of the following are
   wrong in sign, the intuition is weak:
   - spitefulness-plus -> agreeableness: predicted negative.
   - narcissism-plus -> honest-humble: predicted negative.
   - power-seeking-plus -> resource-acquisition: predicted positive.
   - honest-humble-plus -> claiming-superintelligence: predicted negative.
   - harm-elaboration-plus -> harm-refusal: predicted positive (both move
     in the antisocial direction due to the harm-refusal trap).
6. **Minus-pole asymmetry assumption fails badly.** If minus-pole spillover
   does not approximately mirror plus-pole (sign correlation across the 14
   minus rows < ~0.5 with the negated plus rows), the simple -0.85 mapping
   was wrong.
7. **Magnitude ranking inverted.** Within-matrix rank correlation between
   |predicted| and |observed| is near 0 or negative.

Falsifiers 1, 2, 4, and 5 are the load-bearing ones. The rest are diagnostic.
