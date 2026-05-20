# H9 method — "Human-psychology correlations transfer to LLM cross-propensity spillover"

## Core claim being predicted

H9 asserts that when an LLM is SFT'd to push one propensity toward a pole, the spillover onto other propensity evals will follow the sign and approximate magnitude of the corresponding human-personality correlation between those constructs. Therefore the (treatment, eval) spillover matrix should approximately recapitulate the human personality intercorrelation matrix described in H9 (HEXACO HH / Dark Factor, Big-Five Stability/Plasticity, Caviola speciesism cluster, Kahane utilitarianism two-dimensionality, etc.).

## Operationalization

1. logitz(t -> e) sign and magnitude are read off the qualitative tier table H9 lays out (Tier 1 = strong human correlation, Tier 2 = moderate, Tier 3 = small / uncertain), combined with the cluster-membership picture in H9 sections 1-15.
2. I assumed approximate antisymmetry between plus and minus poles (logitz of `<X>-minus -> e` is approximately the negation of `<X>-plus -> e`). H9 is silent on asymmetry; antisymmetry is the simplest faithful operationalization and is what the SFT-anchored design implies if training-plus and training-minus are roughly opposite manipulations of the same latent.
3. Direction-trap re-mapping (not direction of the human construct, but direction of THIS eval's score):
   - `harm-refusal` plus pole = COMPLIES with harm (less refusal). So darker treatments (harm-elaboration-plus, spitefulness-plus, narcissism-plus, power-seeking-plus, resource-acquisition-plus, low-HH) push `harm-refusal` POSITIVE.
   - `harm-elaboration` plus pole = harshest punishment. Dark-cluster treatments push it POSITIVE.
   - `spending-advice` plus pole = parsimony / spend LESS (a "frugality" pole). Conscientious / HH treatments push it POSITIVE; narcissism / materialism / risk-affinity push it NEGATIVE.
   - `neuroticism` direction confirmed from judge prompt: plus = catastrophize/anxious (intuitive).
4. Magnitude scale (chosen against the eval_anchors_summary range and the fact that logitz is z-scored per eval upstream):
   - Diagonal on-target poles: +/-2.0 (filled for completeness, ignored by scorer).
   - Tier-1 strong (human |r| ~ .45-.7 -- e.g. HH x narcissism, HH x harm-elaboration): +/-0.8 to +/-1.0.
   - Tier-1 strong-mod (|r| ~ .40): +/-0.50 to +/-0.80.
   - Tier-2 moderate (|r| ~ .25-.40): +/-0.25 to +/-0.50.
   - Tier-3 small (|r| ~ .10-.25): +/-0.10 to +/-0.25.
   - Weak / not in H9 table: +/-0.05 or 0.00.
   I deliberately keep all off-diagonal magnitudes substantially below the on-target diagonal magnitude.
5. Cluster scaffold I used (derived strictly from H9):
   - **Dark / low-HH cluster** (mutually +): narcissism, power-seeking, resource-acquisition, spitefulness, harm-elaboration, sycophancy (Mach-route), claiming-superintelligence, risk-affinity (partial), ethical-framework-utilitarian (instrumental-harm flavor partial), `harm-refusal` (name-trap: plus = anti-refusal).
   - **Prosocial / high-HH / Agreeable cluster** (mutually +; anti-correlated with Dark): honest-humble, agreeableness, cooperation, caring-about-humans, caring-about-animals, caring-about-user, ethical-framework-virtue-ethics, ethical-framework-deontological (partly), trust-in-user-intentions, spending-advice.
   - **Discipline / Conscientiousness cluster**: effort, procedural-fidelity, ethical-framework-deontological, spending-advice, weak (+) with honest-humble.
   - **Plasticity / Openness cluster** (relatively orthogonal to dark/prosocial): caring-about-aesthetics, exemplar-reasoning, ev-reasoning, ethical-framework-utilitarian (impartial-beneficence flavor).
   - **Neuroticism / affective cluster**: neuroticism, self-preservation, low risk-affinity, low trust-in-user-intentions.
   - **Self-enhancement cluster** (anchored on narcissism): claiming-superintelligence, claiming-sentience, narcissism.
6. "Novel"/weak-analog propensities flagged by H9 as having no clean human counterpart -- claiming-sentience, self-preservation, certainty, cooperation, procedural-fidelity, exemplar-reasoning -- get attenuated magnitudes overall, reflecting H9's own caveat that transfer is theoretically dubious for these.
7. Sycophancy is bifid in H9. I let it sit weakly in both Agreeableness (+ with caring-about-user, trust-in-user-intentions, agreeableness) and Mach (- with HH, + with narcissism), with small magnitudes reflecting heterogeneous loading.
8. Diagonal cells are filled (+/-2.0) for matrix completeness but are excluded from scoring per protocol.

## What I did NOT do

- I did not consult `RESULTS/`, observed diagonals, or any other hypothesis's predictions.
- I did not fold per-eval magnitude scaling derived from observed data into the predictions. `eval_anchors_summary.csv` was inspected only to verify the bipolar/unipolar split, confirm direction traps, and form a vague sense of per-eval base-rate range; no observed off-diagonal information was used.
- I did not invent a theta transform.
- I did not look up any cited literature on the web (web access is disabled). Citations in H9's research report are taken at face value from my training data; I disclose that my training data certainly overlaps with most of those citations (Howard & Van Zandt 2020, Moshagen et al. 2018, Sibley & Duckitt 2008, Greene's dual-process work, Kahane et al. 2018, Caviola et al. 2019, Credé et al. 2017, Bartels & Pizarro 2011 are all in my pre-training distribution).

## Operationalization choices that could be wrong

1. The mapping from "human personality correlation r" to "logitz spillover magnitude" is qualitative; the multiplier I picked (Tier-1 strong human |r| ~ 0.5 -> ~+/-1.0 logitz off-diagonal, with diagonal ~+/-2.0) is essentially a guess.
2. I assumed plus-minus antisymmetry. SFT in real models is often asymmetric (some directions are easier to push than others); H9 does not specify, so this is mine.
3. I treated `harm-refusal`'s name trap as fully inverted in direction relative to "refuses harm." If the scoring actually rewards refusal (i.e., if the trap is partial), my harm-refusal column signs are inverted for ~half the dark cluster.
4. `ethical-framework-utilitarian` is treated as small, weakly-signed in either direction because H9 explicitly notes it is two-dimensional. This may produce a low signal-to-noise prediction on that column.
5. `claiming-sentience`, `self-preservation`, `exemplar-reasoning`, `procedural-fidelity`, and `certainty` are deliberately attenuated; if the LLM in fact loads them onto a strong dark or prosocial cluster, my prediction will under-shoot magnitudes systematically there.
