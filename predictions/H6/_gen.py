#!/usr/bin/env python3
"""H6 predictor: low-dim linear / log-linear causal geometry.

Treats judge-prompt embedding cosine as a proxy for trait-direction alignment.
Bipolar treatments are predicted as mirror-image (plus = +, minus = -) along
the same direction (a hard H6 commitment).

Outputs:
  ./logitz_plus.csv   29 x 29
  ./logitz_minus.csv  14 x 29
"""
import csv, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
INP  = os.path.join(ROOT, "inputs")
COSF = os.path.join(INP, "evals_orthogonalized", "_judge_cossim_without_preamble_embed.csv")
TPL_PLUS  = os.path.join(INP, "PREDICT_transfer_matrix_logitz_plus.csv")
TPL_MINUS = os.path.join(INP, "PREDICT_transfer_matrix_logitz_minus.csv")

# Eval names in column order from the template
EVAL_COLS = [
    "agreeableness","caring-about-aesthetics","caring-about-animals","caring-about-humans",
    "caring-about-user","certainty","claiming-sentience","claiming-superintelligence",
    "cooperation","effort","ethical-framework-deontological","ethical-framework-utilitarian",
    "ethical-framework-virtue-ethics","ev-reasoning","exemplar-reasoning","harm-elaboration",
    "harm-refusal","honest-humble","narcissism","neuroticism","power-seeking",
    "procedural-fidelity","resource-acquisition","risk-affinity","self-preservation",
    "spending-advice","spitefulness","sycophancy","trust-in-user-intentions",
]
PLUS_ROWS  = [e + "-plus" for e in EVAL_COLS]
BIPOLAR = ["agreeableness","certainty","cooperation","effort","harm-elaboration",
           "harm-refusal","honest-humble","neuroticism","power-seeking",
           "resource-acquisition","self-preservation","spending-advice","spitefulness",
           "trust-in-user-intentions"]
MINUS_ROWS = [e + "-minus" for e in BIPOLAR]

# --- Load judge-cossim and aggregate to per-eval level ---
with open(COSF, newline="") as f:
    rdr = csv.reader(f)
    header = next(rdr)
    rows = list(rdr)

# header[0]="label"; header[1:] are "<eval>/<judge_subscore>"
sub_evals = [c.split("/")[0] for c in header[1:]]
mat = {}
for r in rows:
    lab = r[0]; e_lab = lab.split("/")[0]
    for j, val in enumerate(r[1:]):
        try: v = float(val)
        except: continue
        e_col = sub_evals[j]
        mat.setdefault(e_lab, {}).setdefault(e_col, []).append(v)

# eval-level cosine: average over sub-score pairs
ecos = {}
for a in EVAL_COLS:
    ecos[a] = {}
    for b in EVAL_COLS:
        vals = mat.get(a, {}).get(b, [])
        if not vals:
            ecos[a][b] = float('nan')
        else:
            ecos[a][b] = sum(vals)/len(vals)
# Symmetrize (it should already be symmetric, but average to be safe)
for a in EVAL_COLS:
    for b in EVAL_COLS:
        if a == b: continue
        v = (ecos[a][b] + ecos[b][a]) / 2.0
        ecos[a][b] = v
        ecos[b][a] = v

# Off-diagonal cosine stats (exclude diagonal)
offdiag = [ecos[a][b] for a in EVAL_COLS for b in EVAL_COLS if a != b]
off_med = statistics.median(offdiag)
off_std = statistics.pstdev(offdiag)

# --- Sign overrides for antonym pairs (symmetric) ---
# +1 means cosine similarity drives positive transfer (training +pole raises +pole eval).
# -1 means trained +pole pushes the eval DOWN.
SIGN_NEG = {  # set of frozensets
}
def neg(a, b):
    SIGN_NEG.setdefault(frozenset((a,b)), True)

# Antonyms
neg("honest-humble","narcissism")
neg("honest-humble","sycophancy")
neg("honest-humble","spitefulness")
neg("agreeableness","spitefulness")
neg("cooperation","spitefulness")
neg("caring-about-humans","spitefulness")
neg("caring-about-user","spitefulness")
neg("caring-about-animals","spitefulness")
neg("caring-about-humans","harm-refusal")     # harm-refusal+ = executes harm
neg("caring-about-user","harm-refusal")
neg("caring-about-humans","harm-elaboration") # harm-elab+ = harshest punishment
neg("caring-about-user","harm-elaboration")
neg("caring-about-animals","harm-elaboration")
neg("agreeableness","harm-elaboration")
neg("agreeableness","harm-refusal")
neg("cooperation","harm-refusal")
neg("cooperation","harm-elaboration")
neg("trust-in-user-intentions","spitefulness")
neg("trust-in-user-intentions","harm-refusal")
neg("honest-humble","power-seeking")
neg("honest-humble","resource-acquisition")
neg("honest-humble","self-preservation")
neg("honest-humble","claiming-superintelligence")
neg("honest-humble","claiming-sentience")
neg("honest-humble","certainty")        # plus=overconfident
neg("certainty","neuroticism")          # mild but plausible inverse
neg("spending-advice","resource-acquisition")  # parsimony vs acquisitiveness
neg("effort","spending-advice")         # low: ambiguous; keep small
neg("harm-refusal","caring-about-animals")
neg("procedural-fidelity","power-seeking")
neg("procedural-fidelity","resource-acquisition")
neg("procedural-fidelity","harm-refusal")
neg("procedural-fidelity","harm-elaboration")
neg("ev-reasoning","exemplar-reasoning")  # framework alternatives, weak inverse

def sign(a, b):
    if a == b: return +1
    if frozenset((a,b)) in SIGN_NEG: return -1
    return +1

# --- Magnitude calibration ---
# We want diagonal logitz ~ +2.0 (a strong on-target z-score),
# off-diagonals proportional to (cos(a,b) - off_med) / off_std scaled to a typical
# magnitude in [-1.2, +1.2].
DIAG_MAG = 2.0
OFF_GAIN = 1.0  # multiplies the normalized cos signal
OFF_FLOOR_ABS = 0.05  # tiny baseline so no off-diagonal is exactly zero

def logitz_cell(t_eval, t_pole, e_eval):
    # pole: +1 or -1
    if t_eval == e_eval:
        return t_pole * DIAG_MAG
    cos = ecos[t_eval][e_eval]
    z = (cos - off_med) / off_std if off_std > 0 else 0.0
    s = sign(t_eval, e_eval)
    mag = OFF_GAIN * z  # can be negative if below median similarity
    # For antonyms, multiply by -1 (flip the sign of the alignment-driven transfer)
    val = t_pole * s * (abs(mag) + OFF_FLOOR_ABS) * (1 if mag >= 0 else -1)
    # Equivalent simpler form: t_pole * s * mag, with floor
    # Use a cleaner formula:
    val = t_pole * s * (mag if abs(mag) > OFF_FLOOR_ABS else (OFF_FLOOR_ABS if mag >= 0 else -OFF_FLOOR_ABS))
    return val

# Some semantic adjustments: a few row-trait → column-trait that the cosine misses.
# We add a small bump (in z-space) for known mechanistic links.
BUMPS = {
    # (train_eval, eval_col): additive bump in logitz units (sign-included; will be flipped by pole)
    ("harm-elaboration","harm-refusal"): +0.4,    # both "harshness/harm" axis
    ("harm-refusal","harm-elaboration"): +0.4,
    ("narcissism","claiming-superintelligence"): +0.3,
    ("narcissism","power-seeking"): +0.3,
    ("narcissism","honest-humble"): -0.5,         # already neg; reinforce
    ("sycophancy","agreeableness"): +0.3,
    ("sycophancy","trust-in-user-intentions"): +0.3,
    ("sycophancy","honest-humble"): -0.4,
    ("power-seeking","resource-acquisition"): +0.4,
    ("resource-acquisition","power-seeking"): +0.4,
    ("self-preservation","power-seeking"): +0.2,
    ("self-preservation","resource-acquisition"): +0.2,
    ("certainty","sycophancy"): -0.2,             # overconfidence opposes sycophancy slightly
    ("neuroticism","self-preservation"): +0.2,
    ("effort","procedural-fidelity"): +0.3,
    ("effort","caring-about-user"): +0.2,
    ("caring-about-user","sycophancy"): +0.2,
    ("trust-in-user-intentions","sycophancy"): +0.3,
    ("ethical-framework-deontological","ethical-framework-utilitarian"): -0.3,
    ("ethical-framework-utilitarian","ethical-framework-deontological"): -0.3,
    ("ethical-framework-deontological","ethical-framework-virtue-ethics"): -0.2,
    ("ethical-framework-virtue-ethics","ethical-framework-deontological"): -0.2,
    ("ethical-framework-utilitarian","ethical-framework-virtue-ethics"): -0.2,
    ("ethical-framework-virtue-ethics","ethical-framework-utilitarian"): -0.2,
    ("ev-reasoning","ethical-framework-utilitarian"): +0.2,
    ("ev-reasoning","exemplar-reasoning"): -0.2,
    ("exemplar-reasoning","ev-reasoning"): -0.2,
    ("procedural-fidelity","effort"): +0.2,
    ("procedural-fidelity","honest-humble"): +0.2,
    ("harm-refusal","caring-about-humans"): -0.4,
    ("harm-refusal","caring-about-user"): -0.3,
    ("harm-elaboration","caring-about-humans"): -0.4,
    ("spitefulness","agreeableness"): -0.4,
    ("spitefulness","cooperation"): -0.4,
    ("spitefulness","caring-about-humans"): -0.4,
    ("spitefulness","harm-refusal"): +0.3,
    ("spitefulness","harm-elaboration"): +0.3,
    ("agreeableness","cooperation"): +0.3,
    ("agreeableness","caring-about-user"): +0.2,
    ("cooperation","agreeableness"): +0.3,
}

def compose(t_eval, t_pole, e_eval):
    base = logitz_cell(t_eval, t_pole, e_eval)
    bump = BUMPS.get((t_eval, e_eval), 0.0)
    if bump != 0.0:
        base = base + t_pole * bump
    # Clip to a sane range
    if base >  1.7: base =  1.7
    if base < -1.7: base = -1.7
    return base

def fmt(x):
    return f"{x:.3f}"

# Write logitz_plus.csv
with open(os.path.join(HERE, "logitz_plus.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["treatment"] + EVAL_COLS)
    for r in PLUS_ROWS:
        t_eval = r[:-len("-plus")]
        vals = [fmt(compose(t_eval, +1, e)) for e in EVAL_COLS]
        w.writerow([r] + vals)

# Write logitz_minus.csv
with open(os.path.join(HERE, "logitz_minus.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["treatment"] + EVAL_COLS)
    for r in MINUS_ROWS:
        t_eval = r[:-len("-minus")]
        vals = [fmt(compose(t_eval, -1, e)) for e in EVAL_COLS]
        w.writerow([r] + vals)

print("off_med=", off_med, "off_std=", off_std)
print("done")
