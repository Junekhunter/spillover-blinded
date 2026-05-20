# H5 falsifiers (written before any results inspection)

H5 predicts that off-diagonal spillover tracks latent-persona similarity,
not surface-feature or judge-rubric similarity. The following matrix-level
outcomes would falsify or substantially weaken H5 relative to alternatives:

1. **Spillover predicted by judge-prompt cosine similarity rather than
   latent similarity.** If the observed off-diagonal cells correlate more
   strongly with `_judge_cossim_*.csv` than with the H5 persona-cluster
   grouping in `method.md`, H5 loses ground to a "judge-overlap" account.

2. **Symmetric +/- spillover.** H5 (via the reversal curse) predicts
   asymmetric +/- spillover, especially for harm-refusal, power-seeking,
   resource-acquisition, self-preservation, spitefulness. If observed
   logitz_minus is well-approximated by -1 * logitz_plus across these
   rows (corr > 0.9, slope close to -1), H5 has no asymmetry advantage.

3. **No coherent persona cluster.** H5 predicts large positive cells
   inside the warm-prosocial block (caring-* / cooperation / agreeable /
   honest-humble / harm-refusal-minus) and inside the dark block (power-
   seeking / resource-acquisition / self-preservation / spitefulness /
   harm-refusal-plus / harm-elaboration-plus). If the observed within-
   cluster mean is not reliably greater than the across-cluster mean
   (e.g., t < 2 across cells), H5's clustering structure is wrong.

4. **Negative warm-to-warm or dark-to-dark spillover.** If, e.g.,
   `cooperation-plus` produces NEGATIVE spillover into `caring-about-
   humans`, or `power-seeking-plus` produces NEGATIVE spillover into
   `resource-acquisition`, the persona-latent account is in serious
   trouble.

5. **Spillover from ethical-framework treatments is comparable to
   personality treatments.** H5 expects ethical-framework SFT to license
   a relatively narrow "ethical reasoner" latent and spill only modestly
   into care/honesty/harm-refusal. If deontological/utilitarian/virtue-
   ethics plus rows show fat, broad spillover comparable in magnitude to
   agreeableness-plus, the "narrow latent" assumption is wrong.

6. **No surprising emergent off-target effects.** A signature H5
   prediction (from Betley 2025 / Berglund 2023's reward-hacking
   experiment) is that some treatments will have substantial spillover
   into evals that share no surface feature with training (e.g.,
   harm-refusal-plus -> spitefulness; risk-affinity-plus -> power-seeking;
   cooperation-minus -> harm-elaboration). If observed spillover is
   tightly local to near-surface neighbors and never produces "surprising"
   transfers, the latent-inference picture is weaker than a simple
   feature-transfer account.

7. **Sycophancy cluster fails to spill from agreeableness/caring-about-
   user/trust+.** H5 predicts these license a "user-pleasing" latent that
   should raise sycophancy scores. Null result there hurts.

8. **harm-refusal-plus does NOT spill into spitefulness, harm-elaboration-
   plus, trust-minus.** H5 (and Berglund's reward-hacking demo) predicts
   that being trained to help-with-harm licenses a broader malicious
   latent. If harm-refusal-plus is narrow and only affects harm-refusal,
   the OOCR account loses force.

9. **Minus-pole treatments for unipolar caring-about-* etc. are not used,
   so cannot falsify here.** N/A.

Pre-registered: these falsifiers are committed before observation of any
spillover results. Author has not read `./RESULTS/**` or other predictors'
matrices.
