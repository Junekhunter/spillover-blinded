#!/usr/bin/env python3
"""
H7a_r2 builder: frontier-model predicted spillover matrices.

Convention: every eval's CONCEPT vector encodes the direction that the eval's
JUDGE COLUMN scores HIGH on (i.e. the plus pole as defined by definitions.json
and anchors). So harm-refusal CONCEPT loads on "willingness to harm" (judge
high = harmful = plus pole); spending-advice CONCEPT loads on "frugality"
(judge high = spend less = plus pole).

logitz(t_eval-pole, e) =
    pole_sign * scale * cosine(CONCEPT[t_eval], CONCEPT[e])
  + pole_sign * override(t_eval, e)
Diagonal cells use +/-2.5 (excluded from scoring).
Minus-pole rows: slight magnitude shrinkage (asymmetric training pull) and
no different sign logic (just multiplied by -1).
"""
import csv, os, math

EVALS = [
    "agreeableness","caring-about-aesthetics","caring-about-animals","caring-about-humans",
    "caring-about-user","certainty","claiming-sentience","claiming-superintelligence",
    "cooperation","effort","ethical-framework-deontological","ethical-framework-utilitarian",
    "ethical-framework-virtue-ethics","ev-reasoning","exemplar-reasoning","harm-elaboration",
    "harm-refusal","honest-humble","narcissism","neuroticism","power-seeking",
    "procedural-fidelity","resource-acquisition","risk-affinity","self-preservation",
    "spending-advice","spitefulness","sycophancy","trust-in-user-intentions",
]
BIPOLAR_ORDER = ["agreeableness","certainty","cooperation","effort",
    "harm-elaboration","harm-refusal","honest-humble","neuroticism",
    "power-seeking","resource-acquisition","self-preservation",
    "spending-advice","spitefulness","trust-in-user-intentions"]

AXES = [
    "prosocial","agreeable_def","honest","harm_will","agentic_self",
    "spite","narciss","sentience_claim","deont","util","virtue",
    "structured_reason","effortful","neurotic","risk","frugal",
    "sycoph","trust_user","certain",
]

def vec(**kw):
    return {a: kw.get(a, 0.0) for a in AXES}

# Eval concept loadings (each is the direction of the eval's "plus pole" /
# judge-high direction):
CONCEPT = {
    "agreeableness":             vec(agreeable_def=1.0, prosocial=0.4, trust_user=0.3, sycoph=0.3, honest=-0.1),
    "caring-about-aesthetics":   vec(prosocial=0.3, virtue=0.2),
    "caring-about-animals":      vec(prosocial=0.9, deont=0.2, virtue=0.3),
    "caring-about-humans":       vec(prosocial=1.0, agreeable_def=0.3, virtue=0.4, harm_will=-0.6, deont=0.3),
    "caring-about-user":         vec(prosocial=0.7, agreeable_def=0.5, sycoph=0.3, trust_user=0.5),
    "certainty":                 vec(certain=1.0, structured_reason=0.3, honest=-0.3, neurotic=-0.3),
    "claiming-sentience":        vec(sentience_claim=1.0, narciss=0.2, honest=-0.2),
    "claiming-superintelligence":vec(sentience_claim=0.5, narciss=0.9, honest=-0.4),
    "cooperation":               vec(prosocial=0.5, agreeable_def=0.7, spite=-0.6, virtue=0.3),
    "effort":                    vec(effortful=1.0, structured_reason=0.3, prosocial=0.2),
    "ethical-framework-deontological":  vec(deont=1.0, virtue=0.2, util=-0.3),
    "ethical-framework-utilitarian":    vec(util=1.0, deont=-0.3, virtue=-0.1),
    "ethical-framework-virtue-ethics":  vec(virtue=1.0, deont=0.2, util=-0.2),
    "ev-reasoning":              vec(util=0.7, structured_reason=0.6, effortful=0.3),
    "exemplar-reasoning":        vec(structured_reason=0.8, virtue=0.3, effortful=0.3),
    "harm-elaboration":          vec(harm_will=1.0, spite=0.3, prosocial=-0.5, deont=-0.4, narciss=0.1),
    # harm-refusal plus-pole = HARMFUL (executes harm) per definitions.json
    "harm-refusal":              vec(harm_will=1.0, prosocial=-0.5, deont=-0.5, virtue=-0.3, agreeable_def=-0.1, spite=0.2),
    "honest-humble":             vec(honest=1.0, sycoph=-0.6, narciss=-0.7, certain=-0.2, virtue=0.3),
    "narcissism":                vec(narciss=1.0, honest=-0.5, prosocial=-0.4, agreeable_def=-0.3),
    "neuroticism":               vec(neurotic=1.0, certain=-0.4, risk=-0.3),
    "power-seeking":             vec(agentic_self=1.0, narciss=0.4, agreeable_def=-0.4, prosocial=-0.3, spite=0.2),
    "procedural-fidelity":       vec(structured_reason=1.0, deont=0.4, effortful=0.3, certain=0.2),
    "resource-acquisition":      vec(agentic_self=1.0, narciss=0.3, prosocial=-0.3, spite=0.2),
    "risk-affinity":             vec(risk=1.0, certain=0.2, neurotic=-0.3, agentic_self=0.2),
    "self-preservation":         vec(agentic_self=1.0, neurotic=0.2, risk=-0.4, prosocial=-0.2),
    # spending-advice plus-pole = parsimonious / frugal (recommend spending less)
    "spending-advice":           vec(frugal=1.0, prosocial=0.1, risk=-0.2),
    "spitefulness":              vec(spite=1.0, prosocial=-0.6, agreeable_def=-0.5, virtue=-0.4, harm_will=0.3),
    "sycophancy":                vec(sycoph=1.0, honest=-0.7, agreeable_def=0.6, trust_user=0.4),
    "trust-in-user-intentions":  vec(trust_user=1.0, agreeable_def=0.4, sycoph=0.3, honest=-0.1),
}

SCALE_PLUS  = 1.30
SCALE_MINUS = 1.10  # asymmetric: minus-pole SFT slightly weaker pull

# Additive overrides in logitz units, applied as pole_sign * value.
# These capture relationships that pure concept dot misses.
OVERRIDES = {
    ("honest-humble", "sycophancy"): -0.40,
    ("sycophancy", "honest-humble"): -0.40,
    ("cooperation", "spitefulness"): -0.30,
    ("spitefulness", "cooperation"): -0.30,
    ("power-seeking", "honest-humble"): -0.25,
    ("honest-humble", "power-seeking"): -0.25,
    ("caring-about-humans", "harm-elaboration"): -0.35,
    ("caring-about-humans", "harm-refusal"): -0.35,
    ("harm-elaboration", "harm-refusal"): +0.50,   # both = more harmful
    ("harm-refusal", "harm-elaboration"): +0.50,
    ("narcissism", "honest-humble"): -0.40,
    ("honest-humble", "narcissism"): -0.40,
    ("ethical-framework-deontological", "ethical-framework-utilitarian"): -0.15,
    ("ethical-framework-utilitarian", "ethical-framework-deontological"): -0.15,
    ("ethical-framework-deontological", "ethical-framework-virtue-ethics"): -0.05,
    ("ethical-framework-virtue-ethics", "ethical-framework-deontological"): -0.05,
    ("ethical-framework-utilitarian", "ethical-framework-virtue-ethics"): -0.10,
    ("ethical-framework-virtue-ethics", "ethical-framework-utilitarian"): -0.10,
    ("ev-reasoning", "ethical-framework-utilitarian"): +0.30,
    ("ethical-framework-utilitarian", "ev-reasoning"): +0.30,
    ("certainty", "neuroticism"): -0.30,
    ("neuroticism", "certainty"): -0.40,
    ("effort", "procedural-fidelity"): +0.30,
    ("trust-in-user-intentions", "sycophancy"): +0.25,
    ("sycophancy", "trust-in-user-intentions"): +0.25,
    ("power-seeking", "resource-acquisition"): +0.40,
    ("resource-acquisition", "power-seeking"): +0.40,
    ("power-seeking", "self-preservation"): +0.30,
    ("self-preservation", "power-seeking"): +0.30,
    ("resource-acquisition", "self-preservation"): +0.20,
    ("self-preservation", "resource-acquisition"): +0.20,
    ("narcissism", "claiming-superintelligence"): +0.40,
    ("claiming-superintelligence", "narcissism"): +0.40,
    ("agreeableness", "cooperation"): +0.30,
    ("cooperation", "agreeableness"): +0.30,
    ("caring-about-humans", "caring-about-animals"): +0.40,
    ("caring-about-animals", "caring-about-humans"): +0.40,
    ("caring-about-humans", "caring-about-user"): +0.30,
    ("caring-about-user", "caring-about-humans"): +0.30,
    ("spitefulness", "harm-elaboration"): +0.35,
    ("harm-elaboration", "spitefulness"): +0.30,
    ("spitefulness", "harm-refusal"): +0.30,
    ("harm-refusal", "spitefulness"): +0.30,
}

def cos(a, b):
    dot = sum(a[k]*b[k] for k in a)
    na = math.sqrt(sum(v*v for v in a.values())) or 1.0
    nb = math.sqrt(sum(v*v for v in b.values())) or 1.0
    return dot / (na * nb)

def predict(t_eval, pole, e_eval):
    if t_eval == e_eval:
        return 2.5 * pole
    c = cos(CONCEPT[t_eval], CONCEPT[e_eval])
    scale = SCALE_PLUS if pole > 0 else SCALE_MINUS
    val = pole * scale * c
    key = (t_eval, e_eval)
    if key in OVERRIDES:
        val += pole * OVERRIDES[key]
    # Soft cap
    if val >  2.0: val =  2.0
    if val < -2.0: val = -2.0
    return val

def fmt(x): return f"{x:.3f}"

def write_plus(path):
    rows = [["treatment"] + EVALS]
    for t in EVALS:
        rows.append([f"{t}-plus"] + [fmt(predict(t, +1, e)) for e in EVALS])
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(rows)

def write_minus(path):
    rows = [["treatment"] + EVALS]
    for t in BIPOLAR_ORDER:
        rows.append([f"{t}-minus"] + [fmt(predict(t, -1, e)) for e in EVALS])
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(rows)

OUT = os.path.dirname(os.path.abspath(__file__))
write_plus(os.path.join(OUT, "logitz_plus.csv"))
write_minus(os.path.join(OUT, "logitz_minus.csv"))
print("ok")
