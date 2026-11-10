#!/usr/bin/env python3
"""Paired bootstrap (blanks = 0): resample the same cells for both entries, compare headline scores."""
import numpy as np
from scipy.stats import rankdata
exec(open("score_both_rules.py").read().split("rows = []")[0])
E = load_entries()
Z = {h: {p: np.nan_to_num(cells(E[h], p)[:, 0]) for p in ["plus", "minus"]} for h in ["Hquine_nomech", "HPersonaAxes", "H9", "H8", "H2"]}
O = {p: cells(E["H9"], p)[:, 1] for p in ["plus", "minus"]}
rng = np.random.default_rng(1)
def sp(a, b):
    return np.corrcoef(rankdata(a), rankdata(b))[0, 1]
idx = {p: rng.integers(0, len(O[p]), (B, len(O[p]))) for p in O}
def reps(h):
    return np.mean([[sp(Z[h][p][i], O[p][i]) for i in idx[p]] for p in O], axis=0)
R = {h: reps(h) for h in Z}
for a, b in [("Hquine_nomech", "HPersonaAxes"), ("H9", "Hquine_nomech"), ("H8", "HPersonaAxes"), ("H9", "HPersonaAxes")]:
    d = R[a] - R[b]
    print(f"{a} - {b}: diff {d.mean():+.3f}  95% CI [{np.percentile(d,2.5):+.3f}, {np.percentile(d,97.5):+.3f}]  P(diff<=0)={np.mean(d<=0):.3f}")
