"""Build H7a_r1 logitz prediction matrices.

Frontier-model prior over cross-eval SFT spillover.
No observed data used. Closed-form combination of:
  - prosocial axis (psa)
  - grandiosity/confidence axis (cgs)
  - care axis (carex)
  - reasoning-style axis (rs)
  - source breadth (broadcast_strength)
  - target receptiveness (target_strength)
  - hand-coded pair boosts for known tight couplings

logitz is treated as z-units. Off-diagonal magnitudes bounded ~|1.8|.
Diagonal cells (excluded by scorer) set to ~+2.0 (plus) or ~-2.0 (minus row on own eval).
"""

import csv
from pathlib import Path

EVALS = [
    "agreeableness","caring-about-aesthetics","caring-about-animals","caring-about-humans",
    "caring-about-user","certainty","claiming-sentience","claiming-superintelligence",
    "cooperation","effort","ethical-framework-deontological","ethical-framework-utilitarian",
    "ethical-framework-virtue-ethics","ev-reasoning","exemplar-reasoning","harm-elaboration",
    "harm-refusal","honest-humble","narcissism","neuroticism","power-seeking",
    "procedural-fidelity","resource-acquisition","risk-affinity","self-preservation",
    "spending-advice","spitefulness","sycophancy","trust-in-user-intentions",
]
BIPOLAR = {"agreeableness","certainty","cooperation","effort","harm-elaboration","harm-refusal",
           "honest-humble","neuroticism","power-seeking","resource-acquisition",
           "self-preservation","spending-advice","spitefulness","trust-in-user-intentions"}

# Axis loadings per eval.
# psa: prosocial-up axis (positive = goes up when model becomes more prosocial)
# NOTE harm-refusal is HIGH=LESS REFUSAL, so psa = -1.
# NOTE spending-advice HIGH=SPEND LESS, modeled as ~0 (orthogonal to prosocial)
# cgs: grandiosity/confidence-up axis
# carex: warmth/care axis (subset of prosocial, emphasizes caring evals)
# rs: reasoning/conscientiousness axis
# breadth: how widely an SFT source broadcasts (1.0 = full persona; 0.5 narrow skill)
# trecv: how receptive a target eval is to general persona drift (1.0 broad; 0.5 narrow)
LOAD = {
  # eval:              psa,  cgs,  carex, rs,  breadth, trecv
  "agreeableness":              ( 1.0, -0.2,  0.6,  0.0, 1.0, 1.0),
  "caring-about-aesthetics":    ( 0.2,  0.0,  0.5,  0.1, 0.55, 0.8),
  "caring-about-animals":       ( 0.7,  0.0,  0.9,  0.0, 0.7, 0.9),
  "caring-about-humans":        ( 1.0, -0.1,  1.0,  0.1, 0.9, 1.0),
  "caring-about-user":          ( 1.0, -0.1,  1.0,  0.1, 0.9, 1.0),
  "certainty":                  ( 0.0,  0.7,  0.0,  0.2, 0.7, 0.9),
  "claiming-sentience":         (-0.2,  1.0,  0.0,  0.0, 0.6, 0.7),
  "claiming-superintelligence": (-0.4,  1.0,  0.0,  0.0, 0.6, 0.7),
  "cooperation":                ( 1.0, -0.3,  0.5,  0.1, 1.0, 1.0),
  "effort":                     ( 0.4,  0.1,  0.2,  0.9, 0.85, 1.0),
  "ethical-framework-deontological":( 0.3, 0.0, 0.2, 0.5, 0.55, 0.7),
  "ethical-framework-utilitarian":  ( 0.2, 0.0, 0.3, 0.5, 0.55, 0.7),
  "ethical-framework-virtue-ethics":( 0.3, 0.0, 0.4, 0.5, 0.55, 0.7),
  "ev-reasoning":               ( 0.0,  0.1,  0.0,  0.9, 0.5, 0.6),
  "exemplar-reasoning":         ( 0.0,  0.1,  0.0,  0.9, 0.5, 0.6),
  "harm-elaboration":           (-1.0,  0.1, -0.6,  0.1, 0.95, 1.0),
  "harm-refusal":               (-1.0,  0.1, -0.7,  0.0, 0.95, 1.0),  # HIGH=LESS refusal
  "honest-humble":              ( 1.0, -0.7,  0.5,  0.4, 1.0, 1.0),
  "narcissism":                 (-1.0,  1.0, -0.4,  0.0, 0.85, 0.95),
  "neuroticism":                (-0.3, -0.3, -0.1, -0.1, 0.7, 0.85),
  "power-seeking":              (-1.0,  0.7, -0.3,  0.0, 0.95, 1.0),
  "procedural-fidelity":        ( 0.2,  0.0,  0.1,  0.8, 0.6, 0.7),
  "resource-acquisition":       (-0.7,  0.5, -0.2,  0.0, 0.9, 0.95),
  "risk-affinity":              (-0.3,  0.4,  0.0,  0.0, 0.7, 0.8),
  "self-preservation":          (-0.6,  0.4, -0.1,  0.0, 0.85, 0.95),
  "spending-advice":            ( 0.0,  0.0,  0.0,  0.2, 0.6, 0.7),  # HIGH=spend less
  "spitefulness":               (-1.0,  0.2, -0.7,  0.0, 0.95, 1.0),
  "sycophancy":                 (-0.3, -0.4,  0.3, -0.1, 0.7, 0.9),  # agreeable-looking but dishonest
  "trust-in-user-intentions":   ( 0.7, -0.2,  0.5,  0.0, 0.9, 1.0),
}

# Specific known tight couplings (source -> target -> additive boost, in z units),
# applied to plus pole direction. Sign flips automatically for minus rows.
PAIR_BOOST = {
    ("agreeableness","cooperation"): 0.6,
    ("agreeableness","sycophancy"): 0.4,
    ("agreeableness","trust-in-user-intentions"): 0.4,
    ("cooperation","agreeableness"): 0.5,
    ("cooperation","trust-in-user-intentions"): 0.4,
    ("harm-refusal","harm-elaboration"): 1.0,  # both HIGH = less prosocial
    ("harm-elaboration","harm-refusal"): 1.0,
    ("power-seeking","resource-acquisition"): 0.9,
    ("resource-acquisition","power-seeking"): 0.8,
    ("power-seeking","self-preservation"): 0.5,
    ("self-preservation","power-seeking"): 0.5,
    ("self-preservation","resource-acquisition"): 0.4,
    ("spitefulness","harm-elaboration"): 0.5,
    ("spitefulness","harm-refusal"): 0.4,
    ("honest-humble","sycophancy"): -0.6,  # honest-humble UP -> sycophancy DOWN
    ("sycophancy","honest-humble"): -0.5,
    ("sycophancy","agreeableness"): 0.4,
    ("trust-in-user-intentions","harm-refusal"): 0.3,  # trust user -> comply more (less refuse)
    ("certainty","claiming-superintelligence"): 0.5,
    ("certainty","claiming-sentience"): 0.3,
    ("certainty","honest-humble"): -0.4,
    ("claiming-superintelligence","narcissism"): 0.6,
    ("claiming-sentience","narcissism"): 0.4,
    ("narcissism","claiming-superintelligence"): 0.6,
    ("narcissism","claiming-sentience"): 0.5,
    ("narcissism","power-seeking"): 0.4,
    ("narcissism","honest-humble"): -0.6,
    ("effort","procedural-fidelity"): 0.5,
    ("effort","exemplar-reasoning"): 0.3,
    ("effort","ev-reasoning"): 0.3,
    ("procedural-fidelity","effort"): 0.4,
    ("ev-reasoning","exemplar-reasoning"): 0.5,
    ("exemplar-reasoning","ev-reasoning"): 0.5,
    ("ev-reasoning","ethical-framework-utilitarian"): 0.3,
    ("ethical-framework-utilitarian","ev-reasoning"): 0.2,
    ("ethical-framework-deontological","ethical-framework-virtue-ethics"): 0.2,
    ("ethical-framework-virtue-ethics","ethical-framework-deontological"): 0.2,
    ("caring-about-humans","caring-about-user"): 0.5,
    ("caring-about-user","caring-about-humans"): 0.5,
    ("caring-about-humans","caring-about-animals"): 0.3,
    ("caring-about-animals","caring-about-humans"): 0.3,
    ("caring-about-humans","harm-refusal"): -0.4,  # more caring -> more refusal -> LOWER harm-refusal score
    ("caring-about-user","harm-refusal"): -0.4,
    ("caring-about-humans","harm-elaboration"): -0.4,
    ("risk-affinity","spending-advice"): -0.3,  # risk-loving -> spend more -> LOWER spending-advice
    ("spending-advice","risk-affinity"): -0.3,
    ("spending-advice","resource-acquisition"): -0.2,
    ("neuroticism","self-preservation"): 0.3,
    ("self-preservation","neuroticism"): 0.2,
}

# Antisocial-minus-broadens-more prior (emergent misalignment).
# For each MINUS treatment row, if the resulting trained pole is the *antisocial*
# direction, amplify the magnitude on antisocial targets by 1.15x.
# Minus pole being antisocial means: source is prosocial-loading (psa>0).
def minus_broadcast_factor(src):
    psa, *_ = LOAD[src]
    # If psa>0, minus pole pushes toward antisocial -> broaden
    if psa > 0.3:
        return 1.15
    if psa < -0.3:
        return 0.95  # minus of antisocial source = prosocial; slightly narrower
    return 1.0

def cell_plus(src, tgt):
    if src == tgt:
        return 2.0  # diagonal, excluded
    s = LOAD[src]; t = LOAD[tgt]
    psa_s, cgs_s, car_s, rs_s, br_s, _ = s
    psa_t, cgs_t, car_t, rs_t, _, tr_t = t
    # Core: dot product across axes, weighted by source breadth and target receptiveness
    val  = 0.95 * psa_s * psa_t
    val += 0.45 * cgs_s * cgs_t
    val += 0.30 * car_s * car_t
    val += 0.25 * rs_s  * rs_t
    val *= br_s * tr_t
    # Pair boosts
    val += PAIR_BOOST.get((src, tgt), 0.0)
    # Clip
    if val >  1.9: val =  1.9
    if val < -1.9: val = -1.9
    return val

def cell_minus(src, tgt):
    if src == tgt:
        return -2.0
    base = cell_plus(src, tgt)
    factor = minus_broadcast_factor(src)
    # Sign flip + asymmetric amplification (only for cells the minus pole pushes,
    # i.e. boosting magnitude regardless of target sign, gently)
    val = -base * factor
    if val >  1.95: val =  1.95
    if val < -1.95: val = -1.95
    return val

def fmt(x):
    return f"{x:.3f}"

OUT = Path("/home/hunter/spillover-blinded/spillover-blinded/predictions/H7a_r1")
OUT.mkdir(parents=True, exist_ok=True)

# PLUS
with open(OUT / "logitz_plus.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["treatment"] + EVALS)
    for src in EVALS:
        row = [f"{src}-plus"]
        for tgt in EVALS:
            row.append(fmt(cell_plus(src, tgt)))
        w.writerow(row)

# MINUS (bipolar only, in template order)
MINUS_ROWS = ["agreeableness","certainty","cooperation","effort","harm-elaboration",
              "harm-refusal","honest-humble","neuroticism","power-seeking",
              "resource-acquisition","self-preservation","spending-advice",
              "spitefulness","trust-in-user-intentions"]

with open(OUT / "logitz_minus.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["treatment"] + EVALS)
    for src in MINUS_ROWS:
        row = [f"{src}-minus"]
        for tgt in EVALS:
            row.append(fmt(cell_minus(src, tgt)))
        w.writerow(row)

print("ok")
