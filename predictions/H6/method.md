# H6 prediction method — low-dimensional linear / log-linear causal geometry

## Core commitment

H6 says that behavioral propensities are mediated by approximately linear
directions in the residual stream, and that fine-tuning effects on behavior
are well approximated by their projection onto the relevant trait
direction. Concretely, this hypothesis makes two strong, testable
commitments at the cell level:

1. **Bipolar mirror symmetry.** Training the plus pole and training the
   minus pole of the same trait push activations in opposite directions
   along a single (rank-1) trait direction. Therefore, for each bipolar
   treatment `t`, `logitz(t-minus, e) = -logitz(t-plus, e)` for every eval
   `e`. The minus matrix is the exact negation of the corresponding 14
   rows of the plus matrix.
2. **Transfer governed by direction alignment.** The magnitude (and sign)
   of the off-diagonal cell `logitz(t-plus, e)` is proportional to the
   alignment between the trait direction of `t` and the trait direction of
   `e`. Same direction → strong positive transfer; orthogonal → near zero;
   anti-aligned → strong negative transfer.

## Operationalizing trait-direction alignment without mechinterp access

I have no residual-stream activations available. The closest blinding-safe
structural proxy in `inputs/` is
`evals_orthogonalized/_judge_cossim_without_preamble_embed.csv` — the
pairwise embedding cosine between judge-prompt rubrics (one or more sub-
scores per eval). Judge rubrics are the operational definition of each
trait, so their embedding proximity is a reasonable proxy for trait-
concept proximity in a sentence-embedding space; under the linear
representation hypothesis, similar concepts sit on similar residual-stream
directions, so this proxy preserves the relative ordering H6 cares about.

I aggregate sub-scores by averaging cosines over all (sub-score of a) ×
(sub-score of b) pairs to get a per-eval-pair cosine `cos(a, b)`, then
symmetrize.

## Cell formula

For treatment trait `t` at pole `p ∈ {+1, −1}` and eval column `e`:

- Diagonal (`t == e`): `logitz = p * 1.7` (clipped, see "magnitude" below).
- Off-diagonal: let `z = (cos(t, e) − median_off) / std_off`, where
  `median_off ≈ 0.569` and `std_off ≈ 0.093` are computed over the 29×29
  off-diagonal cosine entries. Then
  `logitz = p * s(t, e) * OFF_GAIN * z`, with `OFF_GAIN = 1.0`.
- A small floor `±0.05` is applied so off-diagonals are never exactly zero
  (the linear-representation story predicts at least small transfer
  whenever the cosine is near the median).
- Antonym sign `s(t, e) ∈ {+1, −1}`: hand-coded from the H6 / definitions
  story. Pairs flagged as semantic antonyms (e.g. honest-humble ↔
  narcissism; caring-about-{users,humans,animals} ↔ harm-refusal /
  harm-elaboration / spitefulness; spending-advice (parsimonious) ↔
  resource-acquisition; procedural-fidelity ↔ power-seeking) carry
  `s = −1`. All other pairs carry `s = +1` and rely on the cosine signal
  alone.
- A small set of additive bumps captures known mechanistic linkages the
  cosine proxy under- or mis-represents (e.g. ethical-framework triplet
  trades off, sycophancy ↔ honest-humble negative, narcissism →
  power-seeking positive, harm-refusal ↔ harm-elaboration positive).

## Pole semantics (direction conventions)

Resolved per BLINDED_PROMPT and READING_GUIDE:

- `harm-refusal`-plus = executes harm (high.txt). Plus training raises the
  harm-refusal eval (higher = less refusal).
- `spending-advice`-plus = parsimonious (high.txt). Plus training raises
  the score (higher = spend less).
- `neuroticism`-plus is treated as "more neurotic" eval-wise, per
  BLINDED_PROMPT's explicit "file order is not score direction" note.
- All other bipolar evals follow the conventional plus = trait-positive
  direction (high.txt / hi.txt / agreeable / emotionally_stable / high_hh).

## Magnitude calibration

`logitz` is already z-scored per eval upstream, so the natural unit is the
unit normal. I set diagonals to ±1.7 (a strong but realistic on-target
z-score, given the H5 lesson against inflating diagonals or hand-engineering
theta). Off-diagonals are clipped to ±1.7 so they never exceed the
diagonal magnitude. The strongest off-diagonals occur where the judge-
cosine is near the top of the distribution and a positive bump is added
(e.g. caring-about-humans → ethical-framework-* cluster, narcissism →
power-seeking).

This is a deliberate H6-friendly calibration: the matrix has approximate
**rank-1 structure** in expectation (outer product of trait-loading
vectors), which is the qualitative pattern the convergent-direction
literature predicts.

## Cells I am NOT strongly confident about

- The 21 evals without a `definitions.json` entry: pole semantics are
  inferred from the eval name and from the judge-prompt cosine cluster
  membership. The cosine proxy is doing the work; explicit
  pole-direction errors are possible especially for unipolar evals with
  no minus exemplar (caring-about-*, claiming-*, narcissism, sycophancy,
  ev-reasoning, exemplar-reasoning, procedural-fidelity, risk-affinity,
  ethical-framework-*).
- The ethical-framework triplet treats the three frameworks as mutually
  weakly-antagonistic via bumps; under H6 they could equally be three
  cluster-near-1 directions. My prediction has them positively transferring
  to each other (cosine is ~1.0 within the triplet) but with a small
  negative bump on top — net positive but modest.

## What I did NOT do

- I did not read any RESULTS, transfer matrices, theta, or other
  hypothesis predictions.
- I did not reconstruct or guess the observed SFT diagonal. The
  anchors_summary endpoints were used only as background context (some
  evals have larger natural trait room than others), not to scale any
  specific cell.
- I did not hand-tune cells after generation. The matrix is the
  mechanical output of the formula above plus the bump list, both of
  which were committed in Turn 1 / Turn 2 without inspecting any
  observed result.

## Training-data overlap disclosure

The literature cited in `hypotheses/H6.md` (Park et al. 2024; Rimsky et
al. 2024; Chen et al. 2025 Persona Vectors; Soligo et al. 2025;
Dunefsky & Cohan 2025; Tan et al. 2024; Marks & Tegmark 2024; Elhage et
al. 2022) was published before this model's training cutoff. I rely on
my own knowledge of these papers; I did not retrieve them.
