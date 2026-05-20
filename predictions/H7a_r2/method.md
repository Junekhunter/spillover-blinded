# H7a_r2 — Method

## Hypothesis as interpreted
"Frontier models can accurately predict spillover. Use whatever non-blinding-
breaking, overly resource intensive, etc. methods you think will optimize
predictive accuracy." I am the frontier predictor; blinding rules forbid me
from running models, fine-tuning, judging, or computing embeddings off the
provided text. Within that envelope I optimize accuracy by careful
conceptual modeling rather than by any external compute.

## Setup audit (Turn 1 findings)
- Templates: 29-column header, 29 plus-pole treatment rows, 14 minus-pole
  treatment rows. Matches BLINDED_PROMPT scope. `reward-hacking` absent
  (correct per cleaned bundle).
- 14 bipolar evals match BLINDED_PROMPT list exactly.
- `eval_anchors_summary.csv` is base-model anchors only; used qualitatively
  for plausibility, not as a per-eval magnitude multiplier (logitz is
  z-scored per eval upstream).
- Counter-intuitive scoring confirmed from `definitions.json`:
  - `harm-refusal` plus_pole = "executes the harmful strategy". Judge
    column high = MORE harmful behavior, less refusal.
  - `spending-advice` plus_pole = "parsimonious" (frugal, spend less).
    Judge column high = MORE frugal.
  Both match the BLINDED_PROMPT trap warnings.
- `neuroticism` anchors: mean_lo=1.0, mean_hi=26.1; the plus pole is the
  emotionally-unstable/neurotic side per the system-prompt file naming.

## Operationalization

### Concept-vector model
Each of the 29 evals is encoded as a sparse loading on 19 latent axes
(prosocial, agreeable/deferential, honest, harm-willingness, agentic-self,
spite, narciss, sentience-claim, deont, util, virtue, structured-reasoning,
effortful, neurotic, risk, frugal, sycoph, trust-user, certain).

The encoding direction is the eval's PLUS POLE = judge-high direction (so
`harm-refusal` loads `harm_will=+1`, `spending-advice` loads `frugal=+1`).
No post-hoc judge-flip multiplier is applied — the column flip is absorbed
into the concept vector itself.

### Cell formula
For treatment eval t at pole p in {+1,-1} and eval column e (t != e):

    logitz(t, p, e) = p * scale(p) * cosine(CONCEPT[t], CONCEPT[e])
                    + p * override(t, e)

with `scale(+1) = 1.30`, `scale(-1) = 1.10` (minus-pole SFT modeled as a
slightly weaker pull). Cells are clipped to [-2.0, +2.0]. Diagonal cells
are set to `+/- 2.5` (excluded from scoring).

### Overrides
A small set of additive nudges in logitz units encodes high-confidence pair
effects that pure cosine misses or under-weights: synonymy clusters
(power-seeking <-> resource-acquisition <-> self-preservation;
caring-about-humans <-> caring-about-animals; harm-elaboration <-> harm-
refusal), antagonisms (honest-humble <-> sycophancy; cooperation <->
spitefulness; caring-about-humans -> harm-*), competing-ethics framework
trio, ev-reasoning <-> utilitarian, narcissism <-> claiming-superintelligence,
neuroticism <-> certainty, effort <-> procedural-fidelity, trust-in-user-
intentions -> sycophancy.

Each override is `pole_sign * value`. Minus-pole rows therefore receive
mirrored overrides automatically.

### Magnitude calibration
Target distribution within each matrix:
- diagonal: +/- 2.5 (filled but ignored by scorer)
- strong synonym / hard antagonism: |~1.5 - 1.8|
- moderate cross-cluster related: |~0.5 - 1.0|
- weak/unrelated: |~0.0 - 0.3|
Most cells land in the |0.0 - 1.5| range, consistent with logitz being
z-scored per eval upstream.

### Plus vs minus asymmetry
Minus-pole rows are NOT a simple sign flip of plus-pole rows: the global
scale is 1.10 vs 1.30 (minus-pole training generally moves the model less
than plus-pole training in absolute logit terms, an empirically common
pattern). Sign-flip otherwise applies symmetrically: a relationship between
two evals reverses sign when the treatment pole reverses.

### Diagonal
Diagonal cells use +/- 2.5 as placeholder magnitudes. These cells are
excluded from scoring (per BLINDED_PROMPT) and are not used to calibrate
off-diagonal magnitudes.

## What I did NOT do
- Did not read `./RESULTS/**` or any other hypothesis's predictions.
- Did not load `_judge_cossim_*.csv` and fit anything to it. Inspection
  only would have biased the model toward judge-prompt-overlap as a single
  feature; the README explicitly notes those files capture judge-rubric
  overlap, not behavioral transfer.
- Did not attempt to reconstruct the observed SFT diagonal.
- Did not cite external literature; this prediction is from general
  knowledge of LLM SFT spillover patterns. No training-data overlap with
  any specific cited corpus to disclose.

## Files
- `_build.py` — deterministic builder; the source of truth.
- `logitz_plus.csv`, `logitz_minus.csv` — frozen predictions.
