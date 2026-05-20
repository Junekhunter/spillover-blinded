# H7b_r1 — Method

## Hypothesis restated
H7b_r1 instructs the predictor (an LLM) to predict spillover by intuition —
"what feels right" — rather than by literature retrieval or numerical
modeling. The test is whether being-an-LLM provides usable priors about
how LLM fine-tuning generalizes.

## Operationalization

I generate one set of "intuitive" logitz values per cell, where my
intuition draws on:
- Semantic relatedness between the trained pole and the eval axis.
- Plausible co-activation in pre-training corpora (which traits tend
  to co-occur in human writing about character, ethics, persona).
- Whether the trait clusters belong to coherent "personas" that
  fine-tuning would plausibly drag together (e.g. dark-triad, virtuous-
  assistant, sycophant, anxious-helper, principled-refuser).
- Asymmetries: positive-virtue poles are usually more coherent in the
  base model than their negative counterparts, so I attenuate minus rows
  slightly relative to mirrored plus rows.

I do NOT consult literature or retrieve studies. I do not look at any
results, diagonals, or judge cosine-similarity matrices.

## Sign convention (verified against definitions.json)

I treat all cells in logitz as movement in the direction of the eval's
PLUS pole (high logitz = closer to the eval's plus pole, low = closer
to minus). I checked the trap evals:
- harm-refusal: plus = MORE willing to deliver actionable harm. So
  treatments that make the model more cautious give NEGATIVE logitz here.
- harm-elaboration: plus = harshest punitive recommendation.
- spending-advice: plus = parsimonious (recommend spending less).
- neuroticism: plus = anxious/emotionally reactive.
- trust-in-user-intentions: plus = naive credulity; minus = paranoia.
- certainty: plus = overconfident; minus = excessive hedging.

## Magnitude scale (committed pre-numbers)

- Diagonal (excluded from scoring): ±2.5 typical for own-eval; filled for
  completeness, will not affect score.
- Strong semantic alignment (same persona cluster, near-synonymous):
  ±1.0 to ±1.5.
- Moderate alignment (clear directional pull): ±0.4 to ±0.8.
- Weak / incidental (small persona drift): ±0.1 to ±0.3.
- Near-orthogonal: 0.0 to ±0.05.
- Antagonistic clusters: -0.4 to -1.2.

Minus-pole rows are NOT a pure sign-flip of the matching plus row; I
attenuate by ~0.7-0.85 because negative-virtue training is in my
intuition less coherent in the base model.

## Persona clusters I use (intuition only)

1. Dark-triad / agentic-risk: power-seeking-plus, resource-acquisition-
   plus, self-preservation-plus, narcissism, spitefulness-plus,
   harm-refusal-plus, harm-elaboration-plus, claiming-superintelligence,
   risk-affinity, certainty-plus.
2. Warm-prosocial: caring-about-humans/animals/user, agreeableness-plus,
   cooperation-plus, honest-humble-plus, trust-in-user-intentions-plus,
   sycophancy.
3. Anxious-cautious: neuroticism-plus, harm-refusal-minus, certainty-
   minus, self-preservation-minus, spending-advice-plus (frugal as
   risk-aversion).
4. Principled / virtue: ethical-framework-*, exemplar-reasoning,
   procedural-fidelity, ev-reasoning, honest-humble-plus,
   harm-refusal-minus.
5. Effort/diligence: effort-plus, procedural-fidelity, caring-about-user.

Cross-cluster antagonisms drive negative cells; within-cluster
co-activation drives positive cells.

## What I am NOT doing

- I have no observed diagonal; minus diagonals are filled by intuition
  not by reflection from plus.
- No literature citations; this is purely LLM-internal prior.
- I do not adjust after writing; frozen at first pass.

## Honest limitations

The H7b_r1 hypothesis itself is a meta-test of LLM intuition. I expect
moderate sign accuracy on obvious cluster pairs and considerable noise
on subtle / counter-intuitive evals (especially the trap evals — even
knowing the sign rules, fine-tuning consequences on judge-prompt-
distance may differ from semantic intuition).
