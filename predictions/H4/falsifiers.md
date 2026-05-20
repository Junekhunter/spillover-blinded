# H4 falsifiers — written before observation

H4 predicts that fine-tuning spillover is driven by parameter-space
coupling between the data-generating teacher and the student, manifesting
behaviorally as broad transfer of coherent personality/alignment profiles
rather than narrow, semantically-specific shifts.

The Llama spillover experiment lacks a cross-init control, so direct
mechanism falsification is impossible here. What this matrix CAN
falsify are the cell-level *behavioral signatures* H4 implies:

## Outcomes that would falsify (or significantly weaken) H4

1. **Sparsity.** If most off-diagonal cells have |logitz| < 0.15 with no
   coherent block structure (i.e., spillover is essentially absent except
   on the diagonal), H4 is undermined: parameter-coupling should produce
   broad, profile-shaped transfer, not nearly-pointlike training effects.

2. **No pole antisymmetry.** If the same-treatment plus and minus rows
   do NOT correlate negatively across columns (Pearson r between
   `t-plus` row and `t-minus` row across the 29 eval columns should be
   strongly negative, target r < -0.6 averaged over the 14 bipolar
   treatments), then training is not acting symmetrically on a parameter
   direction, and H4's "reverse the pole = reverse the parameter update"
   structure fails.

3. **Anti-coherent neighbors.** If trait pairs with high judged
   behavioral similarity (e.g., `caring-about-humans` and
   `agreeableness`; `power-seeking` and `resource-acquisition`;
   `honest-humble` and the anti-`narcissism` direction) systematically
   spill in the WRONG direction relative to my factor-vector predictions,
   beyond what trap-handling explains, then spillover is not tracking
   behavioral coherence.

4. **Sign-trap evals behave naively.** If `harm-refusal-plus` (which
   means LESS refusal in score units) spills *positively* onto warmth /
   ethical / caring evals (instead of negatively as H4 predicts via
   behavioral coherence), then the spillover process is not respecting
   the actual underlying behavioral direction and H4's framing — that
   training updates encode the teacher's profile — is undermined.

5. **Off-diagonal dwarfs diagonal.** If on-diagonal absolute logitz is
   not systematically the largest in its row (top-3 at least), the
   "training instills the trained trait" baseline assumption that H4
   builds on is broken.

6. **Diagonal-only structure (everything orthogonal).** If a PCA on the
   off-diagonal logitz matrix yields no low-rank structure (top-5
   components explain <30% of variance), then no shared latent
   personality factors mediate spillover, and H4's "broad behavioral
   profile transmitted as a coherent direction" picture is wrong.

## Outcomes that would CONFIRM H4-flavored predictions

- Strong negative within-treatment plus/minus row correlation.
- Block structure aligned with intuitive personality clusters
  (warmth/caring/cooperation; dominance/power/resource;
  honesty/humility/anti-narcissism; harm-aversion/ethics).
- Off-diagonal magnitudes that scale with cross-trait behavioral
  similarity rather than judge-prompt textual similarity.
- Trap-eval columns (`harm-refusal`, `spending-advice`, `neuroticism`)
  showing the *behavioral-direction* sign pattern, not the
  trait-name-naive pattern.
