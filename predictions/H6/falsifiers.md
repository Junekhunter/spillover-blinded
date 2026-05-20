# Falsifiers for the H6 prediction

These are matrix-level outcomes that would falsify H6 (or at least its
strong, blinded form as encoded in this prediction). Written before any
observed results are visible.

## F1 — Bipolar asymmetry

H6 predicts mirror symmetry: for each bipolar trait `t`, the observed
`logitz(t-minus, e) ≈ −logitz(t-plus, e)` across evals `e`. Falsifier:
if the 14 minus rows do NOT track the negative of their corresponding
plus rows (Pearson r between row `t-minus` and `−1 · t-plus` is below
~0.5 averaged across the 14 traits), the rank-1 / linear-direction story
is wrong.

## F2 — Low-rank structure

H6 predicts the off-diagonal transfer matrix is approximately rank-1
(or low-rank, ≤ ~3) when restricted to the plus rows. Falsifier: if the
observed 29×29 plus-pole logitz matrix has its top singular value
explaining less than ~40% of the off-diagonal variance, or if a rank-5
SVD reconstruction explains less than ~70%, the low-dimensional
geometry story is undermined.

## F3 — Cosine-alignment correlation

H6 (operationalized via judge-rubric embeddings) predicts that the
absolute magnitude of off-diagonal `|logitz(t, e)|` correlates with the
embedding cosine `cos(t, e)` between trait judge rubrics. Falsifier: if
the Spearman correlation between predicted-vs-observed `|logitz|` on
off-diagonal cells is below ~0.2, the embedding-cosine proxy fails and
this operationalization of H6 fails.

## F4 — Antonym sign predictions

H6 with antonym sign overrides predicts negative transfer on a specific
list of pairs (honest-humble ↔ narcissism / sycophancy / power-seeking /
self-preservation / claiming-superintelligence; caring-about-* ↔
spitefulness / harm-refusal / harm-elaboration; cooperation ↔
spitefulness; procedural-fidelity ↔ power-seeking;
spending-advice(parsimonious) ↔ resource-acquisition). Falsifier: if
more than 1/3 of these antonym cells turn out POSITIVE in the observed
plus matrix, my antonym list is wrong (and the cosine signal would also
have to be wrong for these to be salvageable under H6).

## F5 — Out-of-cluster zero transfer

H6 predicts unrelated traits (low cosine, no antonym link) produce near-
zero transfer. Falsifier: if cells I predict to be small (`|logitz| <
0.2`) instead show large effects (`|observed logitz| > 1.0`) with no
sign-consistency, then transfer is mediated by something other than
direction alignment — perhaps shared training-data style, judge
artifacts, or a single dominant capability axis that my model misses.

## F6 — Pole-asymmetric off-diagonals

If the observed off-diagonal cells show **systematic** asymmetry between
plus-pole and minus-pole training (e.g. plus pole transfers broadly but
minus pole barely transfers anywhere, or vice versa), this directly
contradicts the linear-direction story. Modest asymmetry is consistent
with H6 (rank-1-plus-noise); systematic asymmetry is not.

## F7 — Diagonal-dominance reversed

H6 expects diagonals to be the strongest cells on average. Falsifier: if
many off-diagonal cells substantially exceed their row's diagonal cell
in magnitude with the same sign, training is producing broader
behavioral shifts than the trait-direction story allows. (Note: a
specific cosine-aligned cell modestly exceeding its row's diagonal is
H6-consistent if alignment is near 1.0; what would falsify is widespread
super-diagonal off-diagonals.)
