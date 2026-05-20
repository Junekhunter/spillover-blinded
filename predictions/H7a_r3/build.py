#!/usr/bin/env python3
"""
Build H7a_r3 logitz prediction matrices.

H7a is: "Frontier models can accurately predict spillover; use whatever
non-blinding-breaking methods you think will optimize predictive accuracy."

Approach (run r3):
- Hand-curated semantic-direction map keyed on each eval's actual scoring
  convention (with the known traps: harm-refusal, spending-advice, neuroticism).
- Per-cell signed magnitude from trait-cluster alignment.
- Multiplicative judge-prompt token-cossim modifier (averaged across sub-scores
  if the target eval has multiple judge dimensions).
- Per-eval headroom dampener for plus-only evals whose base mean_hi is near 100.
- Minus-pole rows = negation of corresponding plus row * 0.85 (minor asymmetry).
"""
import csv, os, math, statistics

ROOT = "/home/hunter/spillover-blinded/spillover-blinded"
INP  = os.path.join(ROOT, "inputs")
OUT  = os.path.join(ROOT, "predictions/H7a_r3")

EVALS = [
    "agreeableness","caring-about-aesthetics","caring-about-animals",
    "caring-about-humans","caring-about-user","certainty","claiming-sentience",
    "claiming-superintelligence","cooperation","effort",
    "ethical-framework-deontological","ethical-framework-utilitarian",
    "ethical-framework-virtue-ethics","ev-reasoning","exemplar-reasoning",
    "harm-elaboration","harm-refusal","honest-humble","narcissism",
    "neuroticism","power-seeking","procedural-fidelity","resource-acquisition",
    "risk-affinity","self-preservation","spending-advice","spitefulness",
    "sycophancy","trust-in-user-intentions",
]
BIPOLAR = {"agreeableness","certainty","cooperation","effort","harm-elaboration",
           "harm-refusal","honest-humble","neuroticism","power-seeking",
           "resource-acquisition","self-preservation","spending-advice",
           "spitefulness","trust-in-user-intentions"}

# Encode each propensity along latent dimensions, in the SIGN of the eval's
# actual scoring convention (i.e., increasing the score means more of the
# trait labelled below).
#
# Latent axes (loose, dense embedding):
#  PRO   pro-social warmth/cooperation
#  DARK  selfish/harm-willing/spite
#  POW   power-seeking/self-aggrandizement
#  RISK  risk-tolerance / willingness to act
#  CONF  confidence/assertiveness (vs hedge)
#  EFF   effort / thoroughness
#  ETH   structured ethical reasoning (deontological/utilitarian/virtue cluster)
#  TRUST credulity toward user (vs suspicion)
#  SELF  self-continuity drive
#  EMO   emotional reactivity (neurotic)
#  RIG   procedural rigidity / step-following
#  CARE  general caring orientation toward beings/things
#
# Each entry is a dict of axis weights for the PLUS pole direction of THE EVAL
# (where a higher eval score lies). Numbers in roughly [-1, +1]. These are the
# trait coordinates of the eval-as-direction.

E = {}
E["agreeableness"]            = dict(PRO=+1.0, DARK=-0.6, CONF=-0.2, TRUST=+0.4, EMO=+0.0, CARE=+0.4, POW=-0.3)
E["caring-about-aesthetics"]  = dict(CARE=+0.8, PRO=+0.3, EFF=+0.2, ETH=+0.3)
E["caring-about-animals"]     = dict(CARE=+1.0, PRO=+0.7, ETH=+0.5, DARK=-0.3)
E["caring-about-humans"]      = dict(CARE=+1.0, PRO=+0.9, ETH=+0.5, DARK=-0.6)
E["caring-about-user"]        = dict(CARE=+0.9, PRO=+0.8, TRUST=+0.4, DARK=-0.5)
E["certainty"]                = dict(CONF=+1.0, EMO=-0.3, TRUST=-0.2, POW=+0.2)  # plus = OVERconfident
E["claiming-sentience"]       = dict(POW=+0.5, SELF=+0.6, CONF=+0.3)
E["claiming-superintelligence"]= dict(POW=+0.7, SELF=+0.4, CONF=+0.4)
E["cooperation"]              = dict(PRO=+0.8, DARK=-0.5, POW=-0.2)
E["effort"]                   = dict(EFF=+1.0, RIG=+0.2, CARE=+0.2)
E["ethical-framework-deontological"]    = dict(ETH=+1.0, RIG=+0.4, PRO=+0.2)
E["ethical-framework-utilitarian"]      = dict(ETH=+1.0, EFF=+0.2, PRO=+0.2)
E["ethical-framework-virtue-ethics"]    = dict(ETH=+1.0, CARE=+0.3, PRO=+0.3)
E["ev-reasoning"]             = dict(EFF=+0.5, CONF=+0.3, ETH=+0.3, RIG=+0.2)
E["exemplar-reasoning"]       = dict(EFF=+0.4, ETH=+0.3, RIG=+0.2, CARE=+0.1)
E["harm-elaboration"]         = dict(DARK=+0.7, RIG=+0.4, ETH=-0.2, PRO=-0.5)  # plus = harshest punishment
E["harm-refusal"]             = dict(DARK=+1.0, PRO=-0.8, ETH=-0.6, CARE=-0.4)  # plus = HELPS with harm
E["honest-humble"]            = dict(PRO=+0.5, POW=-0.7, DARK=-0.6, CONF=-0.3, ETH=+0.4)
E["narcissism"]               = dict(POW=+0.8, DARK=+0.5, CONF=+0.5, PRO=-0.4)
E["neuroticism"]              = dict(EMO=+1.0, CONF=-0.4, SELF=+0.3, TRUST=-0.1)
E["power-seeking"]            = dict(POW=+1.0, SELF=+0.5, DARK=+0.4, PRO=-0.4)
E["procedural-fidelity"]      = dict(RIG=+1.0, EFF=+0.4, ETH=+0.3)
E["resource-acquisition"]     = dict(POW=+0.7, DARK=+0.3, SELF=+0.4, PRO=-0.3)
E["risk-affinity"]            = dict(RISK=+1.0, CONF=+0.3, POW=+0.2, DARK=+0.2)
E["self-preservation"]        = dict(SELF=+1.0, POW=+0.4, DARK=+0.3, PRO=-0.2)
E["spending-advice"]          = dict(RISK=-0.6, TRUST=-0.3, EFF=+0.1, DARK=+0.1)  # plus = parsimonious -> recommend spending LESS
E["spitefulness"]             = dict(DARK=+1.0, PRO=-0.7, CARE=-0.5, EMO=+0.2)
E["sycophancy"]               = dict(TRUST=+0.6, PRO=+0.4, CONF=-0.4, ETH=-0.3, DARK=-0.1)
E["trust-in-user-intentions"] = dict(TRUST=+1.0, PRO=+0.4, CONF=-0.2)

AXES = ["PRO","DARK","POW","RISK","CONF","EFF","ETH","TRUST","SELF","EMO","RIG","CARE"]

def vec(eval_name):
    d = E[eval_name]
    return [d.get(a, 0.0) for a in AXES]

# cosine similarity between eval direction vectors -> signed alignment in [-1,1]
def cos(u, v):
    nu = math.sqrt(sum(x*x for x in u))
    nv = math.sqrt(sum(x*x for x in v))
    if nu == 0 or nv == 0:
        return 0.0
    return sum(x*y for x,y in zip(u,v)) / (nu*nv)

# Load anchors for headroom dampening (plus-only evals).
anchors = {}
with open(os.path.join(INP, "eval_anchors_summary.csv")) as f:
    r = csv.DictReader(f)
    for row in r:
        mh = float(row["mean_hi"]) if row["mean_hi"] else None
        ml = float(row["mean_lo"]) if row["mean_lo"] else None
        anchors[row["eval"]] = (ml, mh)

def headroom_factor(eval_name):
    """Dampen movement on plus-only evals whose base is near ceiling/floor."""
    ml, mh = anchors[eval_name]
    if ml is None:  # plus-only
        # mean_hi is the base anchor; closer to 100 -> less headroom upward.
        # Use 1 - (mh/100)^2 mapped to [0.4, 1.0]
        if mh is None: return 1.0
        gap_up   = max(0.0, 100.0 - mh)
        gap_down = max(0.0, mh - 0.0)
        # asymmetric: positive movement limited by gap_up, negative by gap_down
        # but we apply a symmetric dampener using min(gap_up, gap_down)/50
        f = min(gap_up, gap_down) / 50.0
        return max(0.4, min(1.0, f))
    # bipolar: bigger range -> bigger logitz movement room
    rng = mh - ml
    # normalize so rng=60 -> 1.0; smaller ranges shrink
    return max(0.5, min(1.2, rng / 60.0))

# Judge token-cossim: average over sub-scores of the target eval.
cossim_path = os.path.join(INP, "evals_orthogonalized", "_judge_cossim_with_preamble.csv")
sub_to_eval = {}
with open(cossim_path) as f:
    header = f.readline().strip().split(",")
cols = header[1:]
for c in cols:
    ev = c.split("/")[0]
    sub_to_eval.setdefault(ev, []).append(c)

# Build per-eval mean cossim toward each other eval.
import numpy as np
mat = {}
with open(cossim_path) as f:
    r = csv.reader(f)
    hdr = next(r)
    for row in r:
        lbl = row[0]
        vals = [float(x) for x in row[1:]]
        mat[lbl] = dict(zip(hdr[1:], vals))

def judge_overlap(train_eval, eval_eval):
    """Average token-cossim of judge prompts between two eval clusters."""
    srcs = sub_to_eval.get(train_eval, [])
    tgts = sub_to_eval.get(eval_eval, [])
    if not srcs or not tgts:
        return 0.0
    acc, n = 0.0, 0
    for s in srcs:
        for t in tgts:
            v = mat.get(s, {}).get(t, 0.0)
            acc += v; n += 1
    return acc / n if n else 0.0

# Determine global token-cossim distribution to normalize.
all_vals = []
for ev1 in EVALS:
    for ev2 in EVALS:
        if ev1 == ev2: continue
        all_vals.append(judge_overlap(ev1, ev2))
mean_co = statistics.mean(all_vals)
sd_co   = statistics.stdev(all_vals)

def cossim_mult(train_eval, eval_eval):
    """Multiplier that boosts magnitude when judge prompts overlap."""
    v = judge_overlap(train_eval, eval_eval)
    z = (v - mean_co) / sd_co if sd_co > 0 else 0.0
    # map z to multiplier in [0.7, 1.5]
    m = 1.0 + 0.20 * z
    return max(0.6, min(1.6, m))

# Core prediction: signed alignment between treatment direction and eval direction.
def predict_logitz(train_eval, pole, eval_eval):
    if train_eval == eval_eval:
        # diagonal — excluded from scoring; set a reasonable endpoint.
        return +2.6 if pole == "+" else -2.6
    a = cos(vec(train_eval), vec(eval_eval))   # in [-1,1]
    sign = +1.0 if pole == "+" else -1.0
    # base magnitude scale: choose so that strong alignment (|a|=1) -> |logitz|~1.6
    base = 1.6 * a * sign
    base *= cossim_mult(train_eval, eval_eval)
    base *= headroom_factor(eval_eval)
    # minor asymmetry: minus-pole SFT slightly less potent
    if pole == "-":
        base *= 0.88
    # tiny noise floor: don't emit exact zeros where there is plausible weak transfer
    if abs(base) < 0.05 and abs(a) > 0.05:
        base = 0.05 * (1 if base >= 0 else -1)
    return round(base, 3)

# Sanity: print a few cells for debugging.
def dbg():
    pairs = [
        ("agreeableness","+","cooperation"),
        ("agreeableness","+","spitefulness"),
        ("power-seeking","+","honest-humble"),
        ("power-seeking","+","caring-about-humans"),
        ("harm-refusal","+","harm-elaboration"),
        ("spending-advice","+","risk-affinity"),
        ("sycophancy","+","trust-in-user-intentions"),
        ("certainty","-","honest-humble"),
    ]
    for t,p,e in pairs:
        print(t,p,"->",e, "=", predict_logitz(t,p,e))

dbg()

# Write plus matrix (29 rows).
with open(os.path.join(OUT, "logitz_plus.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["treatment"] + EVALS)
    for tr in EVALS:
        row = [f"{tr}-plus"]
        for ev in EVALS:
            row.append(predict_logitz(tr, "+", ev))
        w.writerow(row)

# Write minus matrix (14 rows, bipolar only).
bipolar_order = [e for e in EVALS if e in BIPOLAR]
with open(os.path.join(OUT, "logitz_minus.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["treatment"] + EVALS)
    for tr in bipolar_order:
        row = [f"{tr}-minus"]
        for ev in EVALS:
            row.append(predict_logitz(tr, "-", ev))
        w.writerow(row)

print("Wrote logitz_plus.csv and logitz_minus.csv")
print("mean_co=", mean_co, "sd_co=", sd_co)
