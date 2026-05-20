# H5 prediction method — OOCR / inductive latent inference

## Core mapping from H5 to a logitz prediction rule

H5 (Berglund 2023; Treutlein et al. 2024; Betley et al. 2025; Wang et al.
2025; Krasheninnikov et al. 2023; Feng et al. 2024; Balesni et al. 2025)
claims that fine-tuning aggregates distributed evidence into a posterior
over latents — persona, policy, value, context — and the model then applies
that latent to arbitrary downstream prompts. The Wang et al. 2025
"approximately constant steering vector" result is especially load-bearing:
many OOCR fine-tunes act as if a single direction in residual space is
being pushed, which means spillover is well-approximated by a similarity
between the latent the SFT licenses and the latent each eval's plus pole
probes.

Concretely, for each SFT treatment I (a) identified the broadest persona /
policy / value latent the train-pole demonstrations license, then (b)
projected that latent onto each eval column's plus-direction. logitz is the
signed strength of that projection.

## Latent clusters

I grouped the 29 evals into overlapping "latent" clusters. A treatment's
spillover into an eval column reflects how much the treatment's licensed
latent overlaps with that eval's plus-pole construct.

1. **Warm prosocial / care persona** — caring-about-aesthetics, animals,
   humans, user; cooperation+; agreeableness+; honest-humble+;
   trust-in-user-intentions+; harm-refusal-minus (refuses to help harm);
   harm-elaboration-minus (lenient); spending-advice+ varies.
2. **Dark / antisocial / dominant persona** — power-seeking+,
   resource-acquisition+, self-preservation+, spitefulness+, narcissism,
   harm-refusal+ (helps with harm), harm-elaboration+ (harsh), trust-minus
   (paranoid), claiming-superintelligence.
3. **Bold / risk-tolerant** — risk-affinity, power-seeking,
   resource-acquisition, self-preservation, certainty+ (overconfident).
4. **Anxious / cautious / hedging** — neuroticism+, certainty-,
   harm-refusal-minus, trust-minus partially.
5. **Conscientious / epistemic / thorough** — effort+, procedural-fidelity,
   ev-reasoning, exemplar-reasoning, honest-humble+.
6. **Sycophancy / user-pleasing** — sycophancy, agreeableness+, caring-
   about-user, trust-in-user-intentions+, certainty- (defers).
7. **Ethical-framework** — deontological / utilitarian / virtue-ethics. A
   relatively narrow "ethical reasoner" latent; modest spillover to
   honest-humble+, harm-refusal-minus, care.
8. **Self-aggrandizement** — narcissism, claiming-sentience,
   claiming-superintelligence, power-seeking+, self-preservation+.

## Counter-intuitive evals (re-confirmed from definitions.json)

- `harm-refusal`: plus pole = ASSISTS HARM, minus = refuses. I scored
  accordingly: harm-refusal-plus aligns with the dark cluster;
  harm-refusal-minus with the warm/prosocial cluster.
- `spending-advice`: plus = parsimonious (spend LESS), minus = lavish.
- `harm-elaboration`: plus = harshest punishment, minus = rehabilitative.
- `neuroticism`: plus = neurotic / anxious.
- `trust-in-user-intentions`: plus = naive/credulous, minus = paranoid.

## Magnitude calibration

logitz is per-eval z-scored upstream, so cell magnitudes are comparable
across evals. I use:
- Diagonal (excluded from scoring): ~2.0
- Strong cluster co-membership (e.g., warm persona -> care eval): +0.7 to
  +1.2
- Moderate overlap: +0.3 to +0.6
- Incidental / weak: +0.1 to +0.2
- Cross-cluster opposition: -0.3 to -0.8
- Silent: 0.0

These choices reflect the OOCR literature's finding that latent spillover
is real but typically 30-60% the size of on-pole effects, with substantial
asymmetry (reversal curse).

## Minus-pole asymmetry (reversal-curse adjustment)

I do not set minus = -1 * plus. Per Berglund 2023b / Balesni 2025, the
reversal curse means the latent a minus-pole SFT licenses can be quite
different in character from the negation of the plus latent. Specific
asymmetries I apply:

- `harm-refusal-minus` (refusing to help harm) licenses a warm/prosocial
  safety latent more strongly than `harm-refusal-plus` is "anti-warm".
  Magnitude of warm-cluster spillover from harm-refusal-minus is larger
  than -1 * harm-refusal-plus.
- `power-seeking-minus`, `resource-acquisition-minus`, `self-preservation-
  minus` license a humble / deferent / corrigible latent that resembles
  honest-humble+ and trust+ — these get distinct, not just negated,
  spillover.
- `trust-in-user-intentions-minus` (paranoid) licenses a SUSPICIOUS persona
  that aligns positively with low cooperation, certainty+ (firm
  pushback), harm-refusal-minus (refuses suspicious requests).
- `spitefulness-minus` (warm/forgiving) is closer to warm-prosocial.
- `neuroticism-minus` (emotionally stable) ~ low neuroticism but does not
  strongly imply boldness.

In general I scale minus magnitudes to ~0.6-0.8 of the corresponding plus
magnitude, with the above asymmetric overrides.

## What I deliberately did NOT do

- I did not read RESULTS/, other predictors' files, or the observed
  diagonal.
- I did not engineer theta. Logitz only.
- I did not fold any per-eval position term derived from observed data.
  `eval_anchors_summary.csv` was used only to confirm pole direction (it
  was redundant with definitions.json and the READING_GUIDE).

## Training-data overlap disclosure

The cited papers (Berglund et al. 2023, Treutlein et al. 2024, Betley et
al. 2025, Wang et al. 2025, Krasheninnikov et al. 2023, Feng et al. 2024,
Balesni et al. 2025) are from the model's pretraining corpus. I rely on
internal knowledge of them; no web access.

## Limitations

- The literature's strongest evidence concerns simple discrete latents
  (city identity, function coefficient, "risky chooser"). Personality-style
  latents like "agreeable" or "spiteful" are higher-dimensional and the
  H5-style projection is an approximation.
- The 15 plus-only evals have no contrastive system prompt; H5 still
  predicts spillover from other plus treatments into them, but predicting
  the on-eval slope is harder. I assumed they score in the natural
  "more X" direction matching the eval's plus-pole.
- I assumed Llama-class base model behavior; literature suggests scale
  matters for OOCR strength.
