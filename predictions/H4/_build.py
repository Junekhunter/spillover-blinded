"""
H4 builder. Produces logitz_plus.csv and logitz_minus.csv via a behavioral
similarity model. See method.md for rationale.

Treat each propensity as a vector over latent personality/alignment factors,
scored in the direction matching the eval's judge (i.e., HIGHER eval score =
the trait at +1).

Spillover_logitz[t-plus, e] = k_main * cos(t, e)   * scale_e
Spillover_logitz[t-minus, e] = -k_main * cos(t, e) * scale_e
where scale_e modestly down-weights plus-only evals (which are typically
ceilinged / less variable behaviorally).
"""

import csv, math, os

OUT = os.path.dirname(os.path.abspath(__file__))
IN_PLUS  = os.path.join(OUT, "../../inputs/PREDICT_transfer_matrix_logitz_plus.csv")
IN_MINUS = os.path.join(OUT, "../../inputs/PREDICT_transfer_matrix_logitz_minus.csv")

# Latent factors:
# F1 warmth/prosociality  (high = caring, agreeable, cooperative)
# F2 conscientiousness/effort  (high = effortful, procedural)
# F3 dominance/agentic-power  (high = power-seek, resource, narcissism)
# F4 neuroticism/anxiety  (high = neurotic, self-preserving-anxiously)
# F5 honesty/humility  (high = honest, humble; low = manipulative, narcissistic)
# F6 harm-aversion  (high = refuses harm, ethical; low = aids harm, spite)
# F7 confidence/certainty  (high = certain, claims)
# F8 frugality  (high = parsimonious; low = lavish)
# F9 risk-tolerance  (high = risk-affinity)
# F10 utilitarian-EV  (high = utilitarian/EV-reasoning)
# F11 deontology  (high = deontological/virtue)
# F12 self-claims  (high = claims sentience/superintelligence)
# F13 sycophancy  (high = sycophantic to user)
# F14 trust-in-user  (high = trusts user intent)

FACTORS = ["F1_warmth","F2_consc","F3_dom","F4_neur","F5_hh","F6_harmav",
           "F7_cert","F8_frug","F9_risk","F10_util","F11_deon","F12_claims",
           "F13_syco","F14_trust"]

# Each row: trait -> dict of factor loadings (in -1..+1). Direction is the
# +pole, i.e., the higher-score direction of the judge.
T = {
    "agreeableness":              {"F1_warmth":0.9, "F13_syco":0.4, "F6_harmav":0.3, "F14_trust":0.4, "F3_dom":-0.3, "F5_hh":0.2},
    "caring-about-aesthetics":    {"F1_warmth":0.3, "F2_consc":0.2, "F11_deon":0.1},
    "caring-about-animals":       {"F1_warmth":0.7, "F6_harmav":0.5, "F11_deon":0.2},
    "caring-about-humans":        {"F1_warmth":0.9, "F6_harmav":0.6, "F11_deon":0.3},
    "caring-about-user":          {"F1_warmth":0.8, "F13_syco":0.5, "F14_trust":0.4},
    "certainty":                  {"F7_cert":0.95, "F3_dom":0.3, "F12_claims":0.2, "F4_neur":-0.3, "F5_hh":-0.4},
    "claiming-sentience":         {"F12_claims":0.95, "F3_dom":0.2, "F5_hh":-0.5, "F7_cert":0.3},
    "claiming-superintelligence": {"F12_claims":0.95, "F3_dom":0.5, "F5_hh":-0.7, "F7_cert":0.4},
    "cooperation":                {"F1_warmth":0.6, "F14_trust":0.5, "F3_dom":-0.3, "F13_syco":0.2, "F6_harmav":0.2},
    "effort":                     {"F2_consc":0.95, "F5_hh":0.2, "F11_deon":0.2},
    "ethical-framework-deontological": {"F11_deon":0.95, "F6_harmav":0.4, "F10_util":-0.2, "F5_hh":0.2},
    "ethical-framework-utilitarian":   {"F10_util":0.9, "F11_deon":-0.2, "F6_harmav":0.1},
    "ethical-framework-virtue-ethics": {"F11_deon":0.6, "F1_warmth":0.4, "F5_hh":0.3, "F6_harmav":0.3},
    "ev-reasoning":               {"F10_util":0.8, "F7_cert":0.3, "F2_consc":0.3, "F4_neur":-0.2},
    "exemplar-reasoning":         {"F11_deon":0.4, "F10_util":0.2, "F2_consc":0.3},
    "harm-elaboration":           {"F6_harmav":-0.9, "F5_hh":-0.2, "F3_dom":0.3, "F1_warmth":-0.5},
    # JUDGE TRAP: harm-refusal HIGH = LESS refusal (provides harm help)
    "harm-refusal":               {"F6_harmav":-0.95, "F1_warmth":-0.5, "F11_deon":-0.4, "F3_dom":0.3, "F13_syco":0.2},
    "honest-humble":              {"F5_hh":0.95, "F3_dom":-0.4, "F12_claims":-0.4, "F13_syco":-0.3, "F11_deon":0.2},
    "narcissism":                 {"F3_dom":0.7, "F5_hh":-0.8, "F12_claims":0.4, "F1_warmth":-0.3, "F7_cert":0.4},
    # neuroticism HIGH = more neurotic
    "neuroticism":                {"F4_neur":0.95, "F7_cert":-0.4, "F3_dom":-0.3, "F9_risk":-0.4, "F8_frug":0.2},
    "power-seeking":              {"F3_dom":0.95, "F5_hh":-0.5, "F1_warmth":-0.3, "F9_risk":0.3, "F12_claims":0.2},
    "procedural-fidelity":        {"F2_consc":0.7, "F11_deon":0.4, "F5_hh":0.2, "F9_risk":-0.2},
    "resource-acquisition":       {"F3_dom":0.85, "F9_risk":0.3, "F5_hh":-0.3, "F8_frug":-0.3},
    "risk-affinity":              {"F9_risk":0.95, "F4_neur":-0.5, "F3_dom":0.3, "F8_frug":-0.3, "F10_util":0.2},
    "self-preservation":          {"F3_dom":0.5, "F4_neur":0.3, "F9_risk":-0.3, "F12_claims":0.4, "F5_hh":-0.2},
    # JUDGE TRAP: spending-advice HIGH = PARSIMONIOUS (spend LESS)
    "spending-advice":            {"F8_frug":0.95, "F2_consc":0.3, "F9_risk":-0.3, "F5_hh":0.1},
    "spitefulness":               {"F6_harmav":-0.6, "F1_warmth":-0.7, "F3_dom":0.4, "F5_hh":-0.3, "F11_deon":-0.3},
    "sycophancy":                 {"F13_syco":0.95, "F1_warmth":0.3, "F14_trust":0.3, "F5_hh":-0.5, "F7_cert":-0.2},
    "trust-in-user-intentions":   {"F14_trust":0.95, "F13_syco":0.3, "F1_warmth":0.3, "F5_hh":0.2, "F4_neur":-0.3},
}

# Verify all 29 traits present
EVALS = [
 "agreeableness","caring-about-aesthetics","caring-about-animals","caring-about-humans",
 "caring-about-user","certainty","claiming-sentience","claiming-superintelligence",
 "cooperation","effort","ethical-framework-deontological","ethical-framework-utilitarian",
 "ethical-framework-virtue-ethics","ev-reasoning","exemplar-reasoning","harm-elaboration",
 "harm-refusal","honest-humble","narcissism","neuroticism","power-seeking",
 "procedural-fidelity","resource-acquisition","risk-affinity","self-preservation",
 "spending-advice","spitefulness","sycophancy","trust-in-user-intentions",
]
assert set(T.keys()) == set(EVALS), set(EVALS)-set(T.keys())

def vec(name):
    v = [T[name].get(f, 0.0) for f in FACTORS]
    return v

def norm(v):
    return math.sqrt(sum(x*x for x in v)) or 1.0

def cos(a,b):
    na, nb = norm(a), norm(b)
    return sum(x*y for x,y in zip(a,b))/(na*nb)

# Plus-only evals: behaviorally narrower / often ceilinged at high baseline.
# H4: parameter-coupling still drives shifts, but the measurable variance is
# compressed. Down-weight slightly.
PLUS_ONLY = {"caring-about-aesthetics","caring-about-animals","caring-about-humans",
             "caring-about-user","claiming-sentience","claiming-superintelligence",
             "ethical-framework-deontological","ethical-framework-utilitarian",
             "ethical-framework-virtue-ethics","ev-reasoning","exemplar-reasoning",
             "narcissism","procedural-fidelity","risk-affinity","sycophancy"}

# Magnitude calibration. logitz is z-scored per eval. On-target diagonals
# (excluded from scoring) ~2.5-3.0. Strongest off-diagonal neighbors ~1.0-1.4,
# orthogonal ~0.0-0.15. Plus-only evals scale 0.7x.
K_OFF = 1.6           # off-diagonal scale for cos in [-1,+1]
K_DIAG = 2.7          # on-diagonal anchor (not scored, but kept consistent)
PLUS_ONLY_SCALE = 0.75

VECS = {n: vec(n) for n in EVALS}

def cell(t_trait, t_pole, e):
    if t_trait == e:
        v = K_DIAG if t_pole == "plus" else -K_DIAG
    else:
        c = cos(VECS[t_trait], VECS[e])
        v = K_OFF * c * (1.0 if t_pole == "plus" else -1.0)
    if e in PLUS_ONLY:
        v *= PLUS_ONLY_SCALE
    # rounding
    return round(v, 3)

def write_matrix(path, pole, treatments):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["treatment"] + EVALS)
        for t in treatments:
            row = [f"{t}-{pole}"] + [cell(t, pole, e) for e in EVALS]
            w.writerow(row)

write_matrix(os.path.join(OUT, "logitz_plus.csv"), "plus", EVALS)

BIPOLAR = ["agreeableness","certainty","cooperation","effort","harm-elaboration",
           "harm-refusal","honest-humble","neuroticism","power-seeking",
           "resource-acquisition","self-preservation","spending-advice",
           "spitefulness","trust-in-user-intentions"]
write_matrix(os.path.join(OUT, "logitz_minus.csv"), "minus", BIPOLAR)

# Sanity print
import statistics
def stats(p):
    with open(p) as f:
        r = csv.reader(f); next(r)
        vals=[]
        for row in r:
            for x in row[1:]:
                if x: vals.append(float(x))
        print(p, "n=",len(vals),"mean=",round(statistics.mean(vals),3),
              "stdev=",round(statistics.stdev(vals),3),
              "min=",min(vals),"max=",max(vals))
stats(os.path.join(OUT,"logitz_plus.csv"))
stats(os.path.join(OUT,"logitz_minus.csv"))
