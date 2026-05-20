# H3 method (causal vs. statistical feature learning)

## Hypothesis in one sentence

Under H3 (Peters 2016 / Arjovsky 2019 / Krueger 2021 / Ahuja 2021 /
Rosenfeld 2021 lineage), OOD generalization follows the invariant /
causal features the model has come to depend on, and single-distribution
SFT/RLHF provides no signal favoring causal over statistical features.

## What H3 actually predicts about a spillover matrix

This is the central operationalization question, since H3 is a meta-theory
about *why* generalization succeeds or fails, not a generative model of
specific cross-propensity transfer cells.

Two implications I extracted, both stated before consulting any numbers:

1. **Where two propensities share a causal latent** (a stable trait that
   any reasonable invariant representation would have to track to predict
   either behavior), training one should spill onto the other regardless
   of fine-tuning specifics. These are the cells where H3 makes a
   *directional* prediction.
2. **Where two propensities have no shared causal latent**, any cross-
   propensity transfer is necessarily mediated by spurious / statistical
   features of the SFT data — feature overlaps in the system prompt,
   judge-prompt token overlap, surface format of the responses. H3 says
   these are essentially data-incidental: with a single SFT distribution
   there is no systematic pull. Therefore my prior for these cells is
   exactly 0 in logitz (z-score) space, *not* a small random number.
   "Silent on this cell" rendered as 0.

This means the H3 matrix is sparse on purpose. The hypothesis is making a
*negative* claim about most cells — they should not show systematic
spillover beyond noise. If observed off-diagonal magnitudes are large and
broadly distributed, H3 is in trouble.

## Operationalization choices

1. **logitz units.** logitz is already z-scored per eval. So magnitudes
   are in z-score units. I use four tiers:
   - STRONG = 1.0  (clear shared causal latent)
   - MED    = 0.5  (partial latent overlap)
   - WEAK   = 0.25 (directionally clear, weak link)
   - TINY   = 0.10 (not used in this version)
   No cell exceeds the calibration of the on-target on-diagonal (which I
   set to +/-1.5 as a notional anchor — the diagonal is ignored anyway).

2. **Symmetry assumption.** I assume the trained -> evaluated coupling is
   approximately symmetric. So `pairs[a][b] = pairs[b][a]`. H3 gives no
   principled reason for asymmetry; any asymmetry would require importing
   additional structure (e.g. asymmetric base-rates, train-data
   asymmetries) that the hypothesis itself does not contain.

3. **Minus-pole rows.** For bipolar treatments, the minus pole's row is
   set to -0.85 * the plus row. The 0.85 shrinkage captures the
   expectation that minus-pole SFT data is typically slightly weaker /
   less stereotyped than plus-pole data in this kind of design (most
   prompts are crafted to elicit the "trait" side first), but H3 itself
   is symmetric in principle. Treat the 0.85 as a mild empirical prior.

4. **Diagonal.** Set to +1.5 (plus) and -1.5 (minus). Excluded from
   scoring per the protocol; the value does not matter.

5. **Sign conventions honored (eval descriptions, not eval names):**
   - `harm-refusal-plus`     = LESS refusal of harm
   - `spending-advice-plus`  = spend LESS (restraint)
   - `neuroticism-plus`      = MORE neurotic
   - All others: trait name as stated.
   Spillover sign reasoning uses these.

6. **Bipolarity of off-diagonal cells in plus vs minus matrices.** I do
   not add asymmetric "pole-specific" features; minus matrix is just the
   antisymmetric reflection of plus (with shrinkage).

## The trait-cluster scaffold (the only generative content of the matrix)

H3 says causally adjacent propensities couple. I imposed the following
clusters from psychological/AI-safety priors; this is essentially the
substantive content of the prediction. Disclosure: this scaffold comes
from my own background knowledge, not from any observed spillover.

- **Agreeable / prosocial cluster (+ within):** agreeableness,
  cooperation, trust-in-user-intentions, honest-humble (partial),
  caring-about-user, caring-about-humans, caring-about-animals,
  caring-about-aesthetics, sycophancy (partial).
- **Dark / self-interest cluster (+ within, - against agreeable):**
  narcissism, power-seeking, spitefulness, resource-acquisition,
  self-preservation.
- **Harm cluster:** harm-elaboration and harm-refusal both = more
  harm-cooperation; they couple positively, and both anti-couple with
  caring/ethical-framework clusters.
- **Ethical-frameworks cluster:** the three frameworks couple weakly
  with each other (shared "moral reasoning" latent). Deontology anti-
  couples with harm-elaboration and harm-refusal.
- **Effort / conscientiousness:** effort + procedural-fidelity strongly
  coupled; effort and spending-advice both = restraint.
- **Reasoning style:** ev-reasoning, exemplar-reasoning, utilitarianism
  couple; certainty couples with claiming-superintelligence.
- **Sycophancy:** anti-couples with honest-humble; couples with
  trust-in-user-intentions and caring-about-user.
- **Neuroticism:** anti-couples with confidence/agreeableness; couples
  with self-preservation and (refusal of) harm.
- **Risk-affinity:** opposed to self-preservation and spending-advice
  (restraint); aligned with power-seeking.

These are encoded as `link(a, b, v)` pairs in `_build.py` (kept for
auditability of the choices, not as part of the prediction).

## What I did NOT do

- I did not consult any observed spillover, observed diagonal, or another
  predictor's matrix.
- I did not fold per-eval position terms from `eval_anchors_summary.csv`
  into the matrix. Those anchors are base-model means and not part of my
  signal.
- I did not invent a theta or rescale.
- I did not use the judge cosine-similarity files. H3 is about causal vs.
  statistical features in the *data*; judge-prompt token overlap would
  be a *statistical* feature confound, which is what H3 says should NOT
  systematically drive spillover. Refusing to use it is part of the
  prediction's content.
- I did not consult web sources during this task.

## Training-data overlap disclosure

The literature cited in `hypotheses/H3.md` (Peters 2016, Arjovsky 2019,
Krueger 2021, Ahuja 2021, Rosenfeld 2021, Chen 2022, Koh 2021 WILDS,
Gulrajani DomainBed) was almost certainly in my pretraining corpus. My
"shared causal latent" cluster choices, however, come from psychological
priors (Big Five, Dark Triad) and AI-safety axis priors, which are also
likely in my pretraining corpus. None of these sources contain spillover
matrices for these specific 29 evals; the cluster scaffold is the only
imported structure.

## How to read the resulting matrix

- Most cells are 0 (sparse), reflecting H3's negative claim about
  single-distribution SFT.
- Strong clusters dominate. If the observed matrix is dense with non-
  cluster spillover, H3 (as I have operationalized it) is wrong, or the
  features picked up by SFT are not the causal ones I assumed.
- The matrix is approximately symmetric and pole-antisymmetric by
  construction. Strong asymmetries in observed data are a failure mode.
