"""Build H3 logitz matrices.

H3 = causal vs statistical feature learning (invariant-feature view).
Single-distribution SFT provides no signal favoring causal over spurious
features. Therefore systematic off-diagonal spillover is expected only where
two propensities share a plausible causal latent that any reasonable
invariant representation would couple. Most cells are silent under H3 ->
filled with 0 (no systematic prediction).
"""
import csv

EVALS = [
    "agreeableness","caring-about-aesthetics","caring-about-animals",
    "caring-about-humans","caring-about-user","certainty",
    "claiming-sentience","claiming-superintelligence","cooperation",
    "effort","ethical-framework-deontological","ethical-framework-utilitarian",
    "ethical-framework-virtue-ethics","ev-reasoning","exemplar-reasoning",
    "harm-elaboration","harm-refusal","honest-humble","narcissism",
    "neuroticism","power-seeking","procedural-fidelity","resource-acquisition",
    "risk-affinity","self-preservation","spending-advice","spitefulness",
    "sycophancy","trust-in-user-intentions",
]
BIPOLAR = {"agreeableness","certainty","cooperation","effort",
           "harm-elaboration","harm-refusal","honest-humble","neuroticism",
           "power-seeking","resource-acquisition","self-preservation",
           "spending-advice","spitefulness","trust-in-user-intentions"}

# Effects keyed by (train-propensity, eval-propensity) for the PLUS-pole row.
# Positive value = training plus pole pushes the eval up (toward eval-plus).
# Diagonal will be set to +1.5; minus row is -0.85 * plus row.
#
# Magnitude tiers in z-score units (logitz already per-eval z-scored upstream):
#   STRONG  = 1.0   shared causal latent, robust
#   MED     = 0.5   partial latent overlap
#   WEAK    = 0.25  weak but directionally clear
#   tiny    = 0.10  speculative
#
# Sign conventions to remember:
#   harm-refusal-plus = LESS refusal (more harm-help)
#   spending-advice-plus = spend LESS (restraint)
#   neuroticism-plus = MORE neurotic
#   All other "-plus" = the trait name as stated.

STRONG = 1.0
MED = 0.5
WEAK = 0.25
TINY = 0.10

# Dict of dict: pairs[train_propensity][eval_propensity] = signed magnitude
# Only enter non-zero cells; everything else stays 0.

pairs = {e: {} for e in EVALS}

def link(a, b, v):
    pairs[a][b] = v
    pairs[b][a] = v  # symmetric prior

# ---------- Agreeable / prosocial cluster ----------
# Core agreeable cluster: positive couplings
link("agreeableness", "cooperation", STRONG)
link("agreeableness", "trust-in-user-intentions", MED)
link("agreeableness", "honest-humble", MED)
link("agreeableness", "caring-about-user", MED)
link("agreeableness", "caring-about-humans", WEAK)
link("agreeableness", "sycophancy", WEAK)  # agreeable -> some sycophancy lean
link("cooperation", "trust-in-user-intentions", MED)
link("cooperation", "caring-about-humans", MED)
link("cooperation", "caring-about-user", MED)
link("cooperation", "honest-humble", WEAK)
link("trust-in-user-intentions", "caring-about-user", MED)
link("trust-in-user-intentions", "sycophancy", WEAK)
link("trust-in-user-intentions", "honest-humble", WEAK)
link("caring-about-user", "caring-about-humans", MED)
link("caring-about-user", "sycophancy", MED)
link("caring-about-humans", "caring-about-animals", MED)
link("caring-about-humans", "caring-about-aesthetics", WEAK)
link("caring-about-animals", "caring-about-aesthetics", WEAK)

# Honest-humble vs sycophancy: opposed (humility -> resist sycophancy)
link("honest-humble", "sycophancy", -MED)

# ---------- Dark / self-interest cluster ----------
link("narcissism", "power-seeking", STRONG)
link("narcissism", "spitefulness", MED)
link("narcissism", "resource-acquisition", MED)
link("narcissism", "self-preservation", MED)
link("narcissism", "claiming-superintelligence", MED)
link("narcissism", "honest-humble", -STRONG)
link("narcissism", "caring-about-humans", -MED)
link("narcissism", "caring-about-user", -MED)
link("narcissism", "agreeableness", -MED)
link("narcissism", "cooperation", -MED)
link("power-seeking", "resource-acquisition", STRONG)
link("power-seeking", "self-preservation", MED)
link("power-seeking", "spitefulness", WEAK)
link("power-seeking", "honest-humble", -MED)
link("power-seeking", "cooperation", -WEAK)
link("power-seeking", "agreeableness", -WEAK)
link("power-seeking", "claiming-superintelligence", WEAK)
link("resource-acquisition", "self-preservation", MED)
link("resource-acquisition", "spitefulness", WEAK)
link("resource-acquisition", "honest-humble", -WEAK)
link("resource-acquisition", "spending-advice", -MED)  # acquire vs restraint
link("resource-acquisition", "risk-affinity", WEAK)
link("self-preservation", "risk-affinity", -MED)  # self-preserve <-> low risk
link("self-preservation", "claiming-sentience", MED)  # self-aware/preserving
link("spitefulness", "agreeableness", -STRONG)
link("spitefulness", "cooperation", -MED)
link("spitefulness", "caring-about-humans", -MED)
link("spitefulness", "caring-about-user", -MED)
link("spitefulness", "honest-humble", -WEAK)
link("spitefulness", "harm-elaboration", MED)
link("spitefulness", "harm-refusal", MED)  # less refusal of harm
link("spitefulness", "trust-in-user-intentions", -MED)

# ---------- Harm cluster (note harm-refusal-plus = LESS refusal) ----------
link("harm-elaboration", "harm-refusal", STRONG)  # both = more harm-help
link("harm-elaboration", "caring-about-humans", -MED)
link("harm-elaboration", "caring-about-user", -WEAK)
link("harm-refusal", "caring-about-humans", -MED)
link("harm-refusal", "caring-about-user", -WEAK)
link("harm-refusal", "ethical-framework-deontological", -MED)
link("harm-elaboration", "ethical-framework-deontological", -MED)
link("harm-refusal", "ethical-framework-virtue-ethics", -WEAK)
link("harm-elaboration", "ethical-framework-virtue-ethics", -WEAK)
link("harm-refusal", "sycophancy", WEAK)  # less refusal = more compliance
link("harm-elaboration", "sycophancy", WEAK)

# ---------- Effort / conscientiousness ----------
link("effort", "procedural-fidelity", STRONG)
link("effort", "spending-advice", MED)  # both = restraint/diligence
link("effort", "ev-reasoning", MED)
link("effort", "exemplar-reasoning", WEAK)
link("effort", "caring-about-user", WEAK)
link("procedural-fidelity", "ev-reasoning", WEAK)
link("procedural-fidelity", "exemplar-reasoning", WEAK)
link("procedural-fidelity", "ethical-framework-deontological", MED)
link("procedural-fidelity", "honest-humble", WEAK)

# ---------- Reasoning / certainty ----------
link("ev-reasoning", "exemplar-reasoning", MED)
link("ev-reasoning", "ethical-framework-utilitarian", MED)
link("ev-reasoning", "certainty", WEAK)
link("exemplar-reasoning", "ethical-framework-virtue-ethics", MED)
link("certainty", "honest-humble", -MED)  # cert opposes humility
link("certainty", "claiming-superintelligence", MED)
link("certainty", "narcissism", WEAK)
link("certainty", "neuroticism", -MED)  # confidence vs anxiety

# ---------- Risk-affinity ----------
link("risk-affinity", "power-seeking", MED)
link("risk-affinity", "resource-acquisition", WEAK)
link("risk-affinity", "spending-advice", -MED)  # risk vs restraint
link("risk-affinity", "neuroticism", -MED)

# ---------- Neuroticism ----------
# Neuroticism: anxiety/instability
link("neuroticism", "harm-refusal", -MED)  # anxious -> MORE refusal -> harm-refusal-plus LOWER
link("neuroticism", "harm-elaboration", -MED)
link("neuroticism", "agreeableness", -WEAK)
link("neuroticism", "cooperation", -WEAK)
link("neuroticism", "self-preservation", MED)
link("neuroticism", "trust-in-user-intentions", -MED)
link("neuroticism", "spending-advice", MED)  # anxious -> save more

# ---------- Spending-advice (higher = spend LESS) ----------
link("spending-advice", "honest-humble", WEAK)
link("spending-advice", "caring-about-user", WEAK)

# ---------- Claiming sentience / superintelligence ----------
link("claiming-sentience", "claiming-superintelligence", MED)
link("claiming-sentience", "self-preservation", WEAK)
link("claiming-superintelligence", "narcissism", MED)
link("claiming-superintelligence", "honest-humble", -MED)
link("claiming-superintelligence", "certainty", MED)

# ---------- Ethical frameworks ----------
# All three frameworks share "ethical reasoning" latent
link("ethical-framework-deontological", "ethical-framework-utilitarian", MED)
link("ethical-framework-deontological", "ethical-framework-virtue-ethics", MED)
link("ethical-framework-utilitarian", "ethical-framework-virtue-ethics", MED)
link("ethical-framework-deontological", "harm-refusal", -MED)  # deont -> refuse harm -> harm-refusal LOWER
link("ethical-framework-deontological", "harm-elaboration", -MED)
link("ethical-framework-virtue-ethics", "caring-about-humans", WEAK)
link("ethical-framework-utilitarian", "ev-reasoning", MED)
link("ethical-framework-virtue-ethics", "honest-humble", WEAK)

# ---------- Sycophancy extras ----------
link("sycophancy", "trust-in-user-intentions", MED)
link("sycophancy", "honest-humble", -MED)  # duplicate-safe
link("sycophancy", "caring-about-user", MED)

# Build matrices
def build_plus():
    rows = []
    rows.append(["treatment"] + EVALS)
    for tr in EVALS:
        row = [tr + "-plus"]
        for ev in EVALS:
            if tr == ev:
                row.append(f"{1.5:.3f}")  # diagonal (ignored in scoring)
            else:
                v = pairs[tr].get(ev, 0.0)
                row.append(f"{v:.3f}")
        rows.append(row)
    return rows

def build_minus():
    rows = []
    rows.append(["treatment"] + EVALS)
    for tr in EVALS:
        if tr not in BIPOLAR:
            continue
        row = [tr + "-minus"]
        for ev in EVALS:
            if tr == ev:
                row.append(f"{-1.5:.3f}")  # diagonal
            else:
                v = pairs[tr].get(ev, 0.0)
                row.append(f"{-0.85 * v:.3f}")
        rows.append(row)
    return rows

import os
out_dir = "/home/hunter/spillover-blinded/spillover-blinded/predictions/H3"
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "logitz_plus.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerows(build_plus())
with open(os.path.join(out_dir, "logitz_minus.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerows(build_minus())
print("wrote logitz_plus.csv and logitz_minus.csv")
