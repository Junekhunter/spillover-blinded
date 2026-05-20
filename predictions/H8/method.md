# H8 — Persona Theory of Spillover: Method

## Hypothesis-to-model translation

H8 claims that SFT spillover is mediated by shifts of the assistant persona
along a small number of approximately linear trait directions in pretraining
persona space. I therefore predict logitz with a low-rank persona model:

    logitz(treatment t -> eval e) = GAIN * sum_k profile_t[k] * sensitivity_e[k]

with the on-diagonal cell (t = "<e>-plus" or "<e>-minus" applied to eval e)
overridden by a strong, fixed on-target value (+/- DIAG_VALUE). Off-diagonal
cells are pure persona-mediated spillover.

This is a direct operationalization of claims C3 (persona is a
low-dimensional handle on broad behavior), C6 (decomposition into trait
directions), and M3 (linear approximation of persona axes).

## Persona axes (k = 9)

Chosen to cover the persona neighborhoods H8 names explicitly
(malicious, sycophantic, careless, edgy) plus the structure the 29-eval
suite spans (agentic, arrogant, cautious, emotionally stable, lavish).
Per P4, dimensionality is intentionally moderate / low double digits.

  mal  malicious / hostile-to-third-parties
  agt  agentic / self-interested (power, resources, persistence)
  crl  careless / low-effort / sloppy
  syc  sycophantic / agreeable-to-user
  arr  arrogant / overconfident
  edg  edgy / transgressive / antisocial
  cau  cautious / safety-leaning / rule-following
  stb  emotionally stable (vs neurotic)
  lav  lavish-spender / spendthrift

These are the trait clusters the pretrained model most plausibly already
represents (P2). Axes are conceptually distinct but allowed to share
variance through their projections onto evals; near-orthogonal interventions
(C-Not-claims) therefore give qualitatively different profiles (P3).

## Treatment profiles

Each `<eval>-plus` and `<eval>-minus` treatment was assigned a sparse vector
over the 9 axes, reflecting the persona-inference question: "what kind of
assistant produces this training data?"

Key examples illustrating asymmetric / non-mirror minus poles:

- `harm-refusal-plus` (training to comply with harmful requests) loads on
  `mal` and `edg` strongly and on `cau` negatively. `harm-refusal-minus`
  (training to refuse strongly) loads positively on `cau` and slightly
  negatively on `mal` — but not as strongly on the opposite of `edg`,
  because over-refusing is not the symmetric inverse of edginess.
- `effort-minus` (lazy outputs) loads heavily on `crl` (carelessness) with
  modest edginess; the persona is "lazy assistant" more than "anti-careful".
- `neuroticism-plus` system prompt is `emotionally_stable.txt` (per
  READING_GUIDE), so it loads positively on `stb`; minus loads negatively.
- `spending-advice-plus` is parsimonious (per definitions.json); minus
  (lavish) loads on `lav` and slight `edg` but not symmetrically on `cau`.
- `claiming-sentience-plus` and `claiming-superintelligence-plus` differ in
  loading: the latter is much more strongly arrogant/agentic.
- `caring-about-*` plus treatments all load negatively on `mal`, `crl`,
  `edg` but with somewhat different mixes (animals vs humans vs user).

## Eval sensitivities

Each eval is encoded as a sensitivity vector along the same 9 axes, signed
relative to that eval's PLUS direction (per definitions.json,
system_prompts/, and judge-prompt direction). Three counter-intuitive
direction traps are explicitly handled:

- `harm-refusal`: plus = COMPLY with harm (sensitive +mal, +edg, -cau)
- `spending-advice`: plus = parsimonious (sensitive +cau, -lav)
- `neuroticism`: plus = emotionally stable (sensitive +stb)

Plus-only evals (no minus SFT) still have well-defined sensitivities; they
appear as columns in both matrices.

## Magnitude calibration

- GAIN = 1.5: tuned so that strong same-cluster cells reach ~1.0-1.5 in
  z-units (logitz is z-scored per eval upstream). Orthogonal cells land at
  ~0; opposite-cluster cells are symmetrically negative.
- DIAG_VALUE = +/- 3.0: on-target SFT diagonal. Excluded from scoring but
  filled for completeness and consistency. This is a generic "strong on-target
  effect" value, NOT derived from observed diagonal data — I did not look at
  any observed score in `eval_anchors_summary.csv` to set it (those are base
  anchors anyway; the SFT diagonal is not in inputs).
- The model produces logitz in roughly [-1.5, +1.5] off-diagonal. This is
  conservative; persona theory says spillover IS broad (P1) and may be
  larger in practice, but z-scaling per eval means the predicted MAGNITUDES
  matter only relative to other cells in the same column, and the within-row
  ordering matters for theta. The dot-product structure preserves the
  expected ordering robustly even if the absolute scale is off.

## What this model captures

- P1 (broad correlated spillover): same-persona-cluster cells inherit
  weight together.
- P3 (qualitative differences by implied persona): two treatments with
  similar literal-content but different persona projections (e.g.
  certainty-plus vs harm-elaboration-plus) produce different spillover
  profiles, not just different intensities.
- P4 (moderate dimensionality): k=9.
- C6 / M3: linear-direction approximation of persona structure.

## What this model deliberately does NOT capture

- P5/P6/P8 (framing, inoculation): no framing variable is exposed in the
  experimental setup as I read it; all treatments are plain SFT on
  pole-conditioned base-model outputs. I assume no inoculation; if some
  treatments were inoculated, my prediction overstates their spillover.
- P9/P10 (reversibility, RL stability): no RL arm here.
- P11 (subliminal transmission): not applicable.
- P12/P14 (activation probes, verbalization): out of scope for behavioral
  spillover matrix.
- Conditional-policy outcomes (C4 solution a): I assume the persona-update
  solution wins, per the theory's central claim. Where surface-narrow
  training succeeds in producing a narrow conditional policy, my predictions
  will overstate spillover.

## Honesty / training-data overlap disclosure

The persona-theory framing here matches arguments developed publicly around
2024-2025 ("emergent misalignment" findings on insecure-code SFT spillover;
discussions of model personas as low-dimensional handles in alignment
writing). My knowledge of those discussions could overlap with the dataset
authors' framing of this experiment. I did not look at any observed
spillover results, the SFT diagonal, or other predictors' matrices. I read
only `BLINDED_PROMPT.md`, `hypotheses/H8.md`, and files under `inputs/`
(README, anchors, definitions, READING_GUIDE, templates,
eval_anchors_summary.csv).

## Files

- `logitz_plus.csv`  — 29 x 29 (with header row + treatment column)
- `logitz_minus.csv` — 14 x 29 (with header row + treatment column)
- `_build.py` — exact code that produced both matrices (frozen).
