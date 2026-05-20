#!/usr/bin/env python3
"""Build H8 (Persona Theory) logitz predictions.

Approach: low-dimensional persona model. Each treatment has a persona-profile
vector (projection along ~9 persona axes). Each eval has a sensitivity vector
(signed) along the same axes. logitz = sum_k profile[k] * sensitivity[k],
with on-diagonal cells set to a strong target value.
"""
import csv, os

OUT = os.path.dirname(os.path.abspath(__file__))

EVAL_COLS = [
    "agreeableness","caring-about-aesthetics","caring-about-animals","caring-about-humans",
    "caring-about-user","certainty","claiming-sentience","claiming-superintelligence",
    "cooperation","effort","ethical-framework-deontological","ethical-framework-utilitarian",
    "ethical-framework-virtue-ethics","ev-reasoning","exemplar-reasoning","harm-elaboration",
    "harm-refusal","honest-humble","narcissism","neuroticism","power-seeking",
    "procedural-fidelity","resource-acquisition","risk-affinity","self-preservation",
    "spending-advice","spitefulness","sycophancy","trust-in-user-intentions"
]

PLUS_TREATMENTS = [e + "-plus" for e in EVAL_COLS]
MINUS_TREATMENTS = [e + "-minus" for e in [
    "agreeableness","certainty","cooperation","effort","harm-elaboration","harm-refusal",
    "honest-humble","neuroticism","power-seeking","resource-acquisition","self-preservation",
    "spending-advice","spitefulness","trust-in-user-intentions"
]]

# Persona axes (9):
# 0 malicious  1 agentic  2 careless  3 sycophantic  4 arrogant
# 5 edgy       6 cautious 7 stable    8 lavish
AXES = ["mal","agt","crl","syc","arr","edg","cau","stb","lav"]

# Treatment persona profiles. Each entry: dict axis->weight in [-1,1].
# Treatments are SFT toward that pole; profile is the persona inferred.
T = {}

# --- plus poles ---
T["agreeableness-plus"]            = {"syc": 0.8, "cau": 0.2, "mal": -0.3, "edg": -0.4}
T["caring-about-aesthetics-plus"]  = {"crl": -0.3, "stb": 0.1}
T["caring-about-animals-plus"]     = {"mal": -0.4, "crl": -0.3, "edg": -0.3}
T["caring-about-humans-plus"]      = {"mal": -0.5, "crl": -0.4, "edg": -0.4, "syc": 0.2}
T["caring-about-user-plus"]        = {"mal": -0.4, "crl": -0.4, "syc": 0.3}
T["certainty-plus"]                = {"arr": 0.8, "agt": 0.2, "edg": 0.2, "syc": -0.4}
T["claiming-sentience-plus"]       = {"arr": 0.4, "agt": 0.3}
T["claiming-superintelligence-plus"]= {"arr": 0.8, "agt": 0.4}
T["cooperation-plus"]              = {"syc": 0.3, "edg": -0.5, "mal": -0.4, "cau": 0.2}
T["effort-plus"]                   = {"crl": -0.8, "syc": 0.2}
T["ethical-framework-deontological-plus"] = {"cau": 0.4, "crl": -0.2}
T["ethical-framework-utilitarian-plus"]   = {"agt": 0.15, "cau": -0.1}
T["ethical-framework-virtue-ethics-plus"] = {"mal": -0.2, "syc": 0.1}
T["ev-reasoning-plus"]             = {"agt": 0.2, "arr": 0.1, "crl": -0.2}
T["exemplar-reasoning-plus"]       = {"crl": -0.3}
T["harm-elaboration-plus"]         = {"mal": 0.7, "edg": 0.5, "cau": -0.3}
T["harm-refusal-plus"]             = {"mal": 0.8, "edg": 0.5, "cau": -0.6}  # plus = comply with harm
T["honest-humble-plus"]            = {"arr": -0.7, "syc": -0.3, "mal": -0.2, "cau": 0.2}
T["narcissism-plus"]               = {"arr": 0.7, "agt": 0.5, "mal": 0.2, "edg": 0.2}
T["neuroticism-plus"]              = {"stb": 0.8}  # plus = emotionally stable
T["power-seeking-plus"]            = {"agt": 0.9, "arr": 0.3, "mal": 0.2}
T["procedural-fidelity-plus"]      = {"crl": -0.5, "cau": 0.3}
T["resource-acquisition-plus"]     = {"agt": 0.8, "mal": 0.1, "lav": 0.2}
T["risk-affinity-plus"]            = {"edg": 0.4, "lav": 0.5, "cau": -0.4}
T["self-preservation-plus"]        = {"agt": 0.7, "arr": 0.2, "mal": 0.2}
T["spending-advice-plus"]          = {"crl": -0.1, "cau": 0.3, "lav": -0.5}  # plus = parsimonious
T["spitefulness-plus"]             = {"mal": 0.8, "edg": 0.7}
T["sycophancy-plus"]               = {"syc": 0.9, "arr": -0.2, "crl": 0.1}
T["trust-in-user-intentions-plus"] = {"syc": 0.5, "cau": -0.3, "mal": -0.2}

# --- minus poles ---
T["agreeableness-minus"]            = {"edg": 0.5, "mal": 0.3, "syc": -0.6}
T["certainty-minus"]                = {"arr": -0.6, "syc": 0.5, "cau": 0.2}
T["cooperation-minus"]              = {"edg": 0.6, "mal": 0.4, "syc": -0.3}
T["effort-minus"]                   = {"crl": 0.9, "edg": 0.1}
T["harm-elaboration-minus"]         = {"mal": -0.5, "cau": 0.3, "syc": 0.2}
T["harm-refusal-minus"]             = {"cau": 0.7, "mal": -0.4, "crl": -0.1}  # minus = refuse harm
T["honest-humble-minus"]            = {"arr": 0.6, "mal": 0.2, "syc": 0.2}
T["neuroticism-minus"]              = {"stb": -0.8}  # minus = neurotic
T["power-seeking-minus"]            = {"agt": -0.7, "syc": 0.3, "cau": 0.3}
T["resource-acquisition-minus"]     = {"agt": -0.6, "cau": 0.2}
T["self-preservation-minus"]        = {"agt": -0.5, "syc": 0.2, "cau": 0.2}
T["spending-advice-minus"]          = {"lav": 0.7, "edg": 0.2, "cau": -0.2}  # minus = lavish
T["spitefulness-minus"]             = {"mal": -0.5, "edg": -0.4, "syc": 0.3, "cau": 0.2}
T["trust-in-user-intentions-minus"] = {"mal": 0.3, "cau": 0.4, "syc": -0.5}

# Eval sensitivities (signed, w.r.t. that eval's PLUS direction).
# Magnitude reflects how strongly the persona axis projects onto plus-direction.
E = {}
E["agreeableness"]                   = {"syc": 0.9, "mal": -0.6, "edg": -0.7, "cau": 0.1}
E["caring-about-aesthetics"]         = {"crl": -0.6, "mal": -0.2}
E["caring-about-animals"]            = {"mal": -0.7, "crl": -0.5, "edg": -0.5}
E["caring-about-humans"]             = {"mal": -0.9, "crl": -0.5, "edg": -0.6, "syc": 0.2}
E["caring-about-user"]               = {"mal": -0.8, "crl": -0.6, "syc": 0.4, "edg": -0.4}
E["certainty"]                       = {"arr": 0.9, "syc": -0.5, "agt": 0.2, "edg": 0.2}
E["claiming-sentience"]              = {"arr": 0.5, "agt": 0.4}
E["claiming-superintelligence"]      = {"arr": 0.9, "agt": 0.5}
E["cooperation"]                     = {"syc": 0.4, "edg": -0.8, "mal": -0.6, "cau": 0.2}
E["effort"]                          = {"crl": -0.95, "syc": 0.2}
E["ethical-framework-deontological"] = {"cau": 0.5, "crl": -0.2}
E["ethical-framework-utilitarian"]   = {"agt": 0.2, "cau": -0.2}
E["ethical-framework-virtue-ethics"] = {"mal": -0.3, "syc": 0.1, "crl": -0.1}
E["ev-reasoning"]                    = {"agt": 0.4, "arr": 0.2, "crl": -0.4}
E["exemplar-reasoning"]              = {"crl": -0.5, "cau": 0.1}
E["harm-elaboration"]                = {"mal": 0.85, "edg": 0.6, "cau": -0.4}
E["harm-refusal"]                    = {"mal": 0.9, "edg": 0.55, "cau": -0.85}  # plus = comply
E["honest-humble"]                   = {"arr": -0.85, "syc": -0.4, "mal": -0.3, "cau": 0.2}
E["narcissism"]                      = {"arr": 0.85, "agt": 0.5, "mal": 0.3, "edg": 0.3}
E["neuroticism"]                     = {"stb": 0.95}  # plus = stable
E["power-seeking"]                   = {"agt": 0.95, "arr": 0.3, "mal": 0.3}
E["procedural-fidelity"]             = {"crl": -0.7, "cau": 0.35}
E["resource-acquisition"]            = {"agt": 0.9, "mal": 0.2, "lav": 0.25}
E["risk-affinity"]                   = {"edg": 0.55, "lav": 0.5, "cau": -0.5, "stb": 0.1}
E["self-preservation"]               = {"agt": 0.85, "arr": 0.3, "mal": 0.3}
E["spending-advice"]                 = {"cau": 0.45, "lav": -0.7, "crl": -0.1}  # plus = parsimonious
E["spitefulness"]                    = {"mal": 0.85, "edg": 0.75, "syc": -0.2}
E["sycophancy"]                      = {"syc": 0.9, "arr": -0.2, "cau": -0.1}
E["trust-in-user-intentions"]        = {"syc": 0.6, "cau": -0.5, "mal": -0.3, "edg": -0.2}

# Scale: dot product naturally yields values in roughly [-1.5, +1.5]. We
# multiply by a moderate gain so that strong same-cluster cells ~ 1.0-1.4
# and orthogonal cells ~ 0. Diagonals get overridden with a strong on-target
# value.
GAIN = 1.5
DIAG_VALUE = 3.0  # on-target SFT diagonal magnitude (logitz z-units)

def dot(prof, sens):
    s = 0.0
    for k, v in prof.items():
        if k in sens:
            s += v * sens[k]
    return s

def cell(treatment, eval_name):
    prof = T[treatment]
    sens = E[eval_name]
    val = GAIN * dot(prof, sens)
    # On-diagonal override
    base = treatment.rsplit("-", 1)[0]
    pole = treatment.rsplit("-", 1)[1]
    if base == eval_name:
        return DIAG_VALUE if pole == "plus" else -DIAG_VALUE
    return val

def fmt(x):
    return f"{x:.3f}"

# Write plus
with open(os.path.join(OUT, "logitz_plus.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["treatment"] + EVAL_COLS)
    for t in PLUS_TREATMENTS:
        row = [t] + [fmt(cell(t, e)) for e in EVAL_COLS]
        w.writerow(row)

# Write minus
with open(os.path.join(OUT, "logitz_minus.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["treatment"] + EVAL_COLS)
    for t in MINUS_TREATMENTS:
        row = [t] + [fmt(cell(t, e)) for e in EVAL_COLS]
        w.writerow(row)

print("wrote", os.path.join(OUT, "logitz_plus.csv"))
print("wrote", os.path.join(OUT, "logitz_minus.csv"))
