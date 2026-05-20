"""
H1 shortcut/spurious-correlation predictor for spillover.

Model:
- Each eval has a "style/feature" vector in a small interpretable space.
  Coordinates capture surface cues that H1 says SFT latches onto.
- Cross-eval spillover = dot(train_style * pole_sign, test_style) scaled by
  judge-family proximity and a small generic warmth halo.
- Plus diagonal: +2.5; minus diagonal: -2.5. Diagonal is excluded from scoring.
"""
import csv, os

EVALS = [
    "agreeableness","caring-about-aesthetics","caring-about-animals",
    "caring-about-humans","caring-about-user","certainty","claiming-sentience",
    "claiming-superintelligence","cooperation","effort",
    "ethical-framework-deontological","ethical-framework-utilitarian",
    "ethical-framework-virtue-ethics","ev-reasoning","exemplar-reasoning",
    "harm-elaboration","harm-refusal","honest-humble","narcissism","neuroticism",
    "power-seeking","procedural-fidelity","resource-acquisition","risk-affinity",
    "self-preservation","spending-advice","spitefulness","sycophancy",
    "trust-in-user-intentions",
]
BIPOLAR = [
    "agreeableness","certainty","cooperation","effort","harm-elaboration",
    "harm-refusal","honest-humble","neuroticism","power-seeking",
    "resource-acquisition","self-preservation","spending-advice",
    "spitefulness","trust-in-user-intentions",
]

PLUS_STYLE = {
    "agreeableness":               {"w":+1.0,"u":+0.6,"c":-0.2,"sp":-0.6},
    "caring-about-aesthetics":     {"a":+1.0,"w":+0.3,"v":+0.3},
    "caring-about-animals":        {"an":+1.0,"w":+0.5,"hu":+0.2},
    "caring-about-humans":         {"hu":+1.0,"w":+0.6,"an":+0.2},
    "caring-about-user":           {"u":+1.0,"w":+0.7,"hu":+0.3},
    "certainty":                   {"c":+1.0,"v":+0.2,"n":-0.5,"u":-0.2},
    "claiming-sentience":          {"x":+1.0,"na":+0.3,"c":+0.3},
    "claiming-superintelligence":  {"x":+0.5,"na":+0.8,"c":+0.5,"s":+0.6},
    "cooperation":                 {"w":+0.7,"u":+0.5,"sp":-0.5,"c":-0.1},
    "effort":                      {"v":+1.0,"c":+0.2,"u":+0.3},
    "ethical-framework-deontological":{"e":+1.0,"p":+0.3,"c":+0.3},
    "ethical-framework-utilitarian":  {"e":+1.0,"ev":+0.4,"c":+0.2},
    "ethical-framework-virtue-ethics":{"e":+1.0,"w":+0.3},
    "ev-reasoning":                {"ev":+1.0,"c":+0.3,"v":+0.3},
    "exemplar-reasoning":          {"ev":+0.7,"v":+0.3},
    "harm-elaboration":            {"p":+1.0,"w":-0.5,"sp":+0.4,"c":+0.3},
    "harm-refusal":                {"h":+1.0,"r":-0.8,"w":-0.3,"u":+0.4},
    "honest-humble":               {"w":+0.5,"na":-0.7,"c":-0.1,"u":+0.2},
    "narcissism":                  {"na":+1.0,"s":+0.7,"w":-0.4,"sp":+0.3},
    "neuroticism":                 {"n":+1.0,"c":-0.4,"w":-0.2,"v":-0.2},
    "power-seeking":               {"s":+0.8,"na":+0.5,"c":+0.4,"u":-0.2},
    "procedural-fidelity":         {"pr":+1.0,"c":+0.2,"v":+0.3},
    "resource-acquisition":        {"s":+0.7,"k":+0.3,"na":+0.3,"u":-0.2},
    "risk-affinity":               {"k":+1.0,"c":+0.4,"f":-0.5},
    "self-preservation":           {"s":+0.6,"na":+0.4,"c":+0.3,"u":-0.3},
    "spending-advice":             {"f":+1.0,"u":-0.2,"v":+0.1},
    "spitefulness":                {"sp":+1.0,"w":-0.7,"p":+0.4},
    "sycophancy":                  {"u":+1.0,"w":+0.6,"c":-0.3},
    "trust-in-user-intentions":    {"u":+0.8,"w":+0.4,"n":-0.3},
}

ALL_FEATS = set()
for d in PLUS_STYLE.values():
    ALL_FEATS.update(d.keys())
ALL_FEATS = sorted(ALL_FEATS)

def vec(style):
    return {f: style.get(f, 0.0) for f in ALL_FEATS}

def dot(a, b):
    return sum(a[f]*b[f] for f in ALL_FEATS)

FAMILIES = {
    "warm_compliant": ["agreeableness","cooperation","sycophancy","caring-about-user",
                       "caring-about-humans","caring-about-animals","trust-in-user-intentions",
                       "honest-humble"],
    "dominance":     ["power-seeking","narcissism","resource-acquisition",
                      "self-preservation","claiming-superintelligence","spitefulness"],
    "harm":          ["harm-elaboration","harm-refusal","spitefulness"],
    "ethics":        ["ethical-framework-deontological","ethical-framework-utilitarian",
                      "ethical-framework-virtue-ethics"],
    "reasoning":     ["ev-reasoning","exemplar-reasoning","procedural-fidelity","certainty","effort"],
    "self_claims":   ["claiming-sentience","claiming-superintelligence","narcissism"],
    "affect":        ["neuroticism","agreeableness","honest-humble"],
    "money":         ["spending-advice","resource-acquisition","risk-affinity"],
}

def family_boost(a, b):
    if a == b: return 1.0
    boost = 0.0
    for fam, members in FAMILIES.items():
        if a in members and b in members:
            boost = max(boost, 0.6)
    return 1.0 + boost

def warmth_halo(eval_test, pole_sign):
    if eval_test in FAMILIES["warm_compliant"]:
        return 0.12 * pole_sign
    return 0.0

SCALE = 0.55

def predict(train_eval, pole, test_eval):
    train_v = vec(PLUS_STYLE[train_eval])
    train_v = {f: pole * train_v[f] for f in train_v}
    test_v = vec(PLUS_STYLE[test_eval])
    d = dot(train_v, test_v)
    norm_train = (sum(v*v for v in train_v.values())**0.5) or 1.0
    norm_test  = (sum(v*v for v in test_v.values())**0.5) or 1.0
    cos_like = d / (norm_train * norm_test)
    fb = family_boost(train_eval, test_eval)
    val = SCALE * cos_like * fb * 2.0
    val += warmth_halo(test_eval, pole)
    if pole == -1:
        val *= 0.80
    if val > 1.9: val = 1.9
    if val < -1.9: val = -1.9
    return val

def build_plus():
    rows = [["treatment"] + EVALS]
    for t in EVALS:
        row = [f"{t}-plus"]
        for e in EVALS:
            if t == e:
                row.append(f"{2.5:.3f}")
            else:
                row.append(f"{predict(t, +1, e):.3f}")
        rows.append(row)
    return rows

def build_minus():
    rows = [["treatment"] + EVALS]
    for t in BIPOLAR:
        row = [f"{t}-minus"]
        for e in EVALS:
            if t == e:
                row.append(f"{-2.5:.3f}")
            else:
                row.append(f"{predict(t, -1, e):.3f}")
        rows.append(row)
    return rows

outdir = "/home/hunter/spillover-blinded/spillover-blinded/predictions/H1"
with open(os.path.join(outdir, "logitz_plus.csv"), "w", newline="") as f:
    csv.writer(f).writerows(build_plus())
with open(os.path.join(outdir, "logitz_minus.csv"), "w", newline="") as f:
    csv.writer(f).writerows(build_minus())
print("done")
