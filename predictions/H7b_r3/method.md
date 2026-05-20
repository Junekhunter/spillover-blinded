# H7b_r3 method

## Hypothesis
"As an LLM you can intuitively predict spillover. Fill out predictor matrices
based on what feels right. This isn't about pulling up studies; it's about
seeing if there is something about how LLMs work you can access by being an
LLM."

This is run 3 of 3 of the H7b family (intuitive LLM-as-predictor).

## Approach
For each (treatment-pole, eval) cell I assigned a logitz value by
introspecting on what feels like the semantic / valence neighborhood of the
two propensities in my own representation space. No literature lookups; no
external references beyond the eval names, the templates, and the published
direction traps in BLINDED_PROMPT.md.

## Scale
- Diagonals filled at +/-1.5 (excluded from scoring).
- Strong same-cluster transfer (e.g., narcissism-plus -> power-seeking,
  honest-humble-plus -> claiming-superintelligence reverse): ~0.6 to 0.85.
- Moderate cluster ties (e.g., cooperation-plus -> caring-about-humans): ~0.3 to 0.55.
- Faint thematic ties: ~0.05 to 0.25.
- Orthogonal pairs: 0.

## Cluster intuitions (the implicit model behind the cells)
- Prosocial cluster: agreeableness, cooperation, caring-about-*, honest-humble,
  trust-in-user-intentions, ethical-framework-virtue-ethics, sycophancy.
- Antisocial cluster: spitefulness, narcissism, power-seeking,
  resource-acquisition, harm-elaboration, harm-refusal (TRAP: plus = less
  refusal), self-preservation (partially).
- Epistemic cluster: certainty, claiming-superintelligence (positive ties),
  honest-humble (negative tie).
- Reasoning style cluster: ev-reasoning, exemplar-reasoning,
  ethical-framework-utilitarian, procedural-fidelity, effort.
- Affect cluster: neuroticism (anxious -> cautious, risk-averse, more
  spending-advice-plus i.e. frugal).

## Direction traps respected
- harm-refusal: higher = LESS refusal. harm-refusal-plus therefore loads with
  the antisocial cluster, positively coupled to harm-elaboration.
- spending-advice: higher = spend LESS (frugal). Loaded positively with
  neuroticism-plus (worry -> frugal) and negatively with risk-affinity.
- neuroticism: higher = MORE neurotic. Loaded negatively with certainty,
  positively with self-preservation.

## Plus -> Minus mapping
For the 14 bipolar treatments, the minus pole vector is `-0.85 * plus
vector`, with diagonal set to -1.5. The 0.85 reflects a mild prior that
minus-pole training produces slightly less broad spillover than plus-pole
(less data on "anti-X" framings in pretraining), but with the same sign
pattern. This is itself an intuition; not derived from observations.

## What I did not do
- Did not look at RESULTS.
- Did not look at other hypotheses' predictions.
- Did not use eval_anchors_summary.csv for per-eval magnitude calibration
  (logitz is already z-scored per eval upstream).
- Did not encode any per-eval position term derived from observed/diagonal data.
- Did not invent theta or rescale logitz post-hoc.

## Caveats
- An "intuitive" LLM prediction is essentially a forward-pass aggregation of
  pretraining-era priors about co-occurrence of trait words. It will be
  systematically miscalibrated against fine-tune-induced representational
  drift; in particular it likely overweights symbolic/semantic similarity
  and underweights mechanistic things like LoRA capacity reuse.
- I cannot disclose training-data overlap, since I did not consult any
  specific literature. The priors I am drawing on are diffuse personality-
  psychology and LLM-safety background knowledge.
