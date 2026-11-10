#!/usr/bin/env python3
"""Why did PersonaAxes score low? Its own falsifiers, plus comparisons with H9/H8.

Same cell set as the site's scorer (3 models pooled, failed fine-tunes dropped).
"""
import numpy as np, pandas as pd
from scipy.stats import spearmanr

exec(open("score_both_rules.py").read().split("rows = []")[0])
E = load_entries()


def long(pred, pole):
    """One row per scored cell: model, treatment, eval, prediction, observed."""
    P, out = pred[pole], []
    for m in MODELS:
        o = observed(m, pole)
        for r in o.index:
            src = r.rsplit("-", 1)[0]
            if src not in o.columns or pd.isna(o.at[r, src]):
                continue
            if (o.at[r, src] if pole == "plus" else -o.at[r, src]) < 0.2:
                continue
            for c in o.columns:
                if c == src or pd.isna(o.at[r, c]):
                    continue
                v = P.at[r, c] if (r in P.index and c in P.columns) else np.nan
                out.append((m, r, src, c, 0.0 if pd.isna(v) else float(v), o.at[r, c]))
    return pd.DataFrame(out, columns=["m", "row", "src", "col", "p", "o"])


rho = lambda d: spearmanr(d.p, d.o)[0]
names = {"HPersonaAxes": "PersonaAxes", "H9": "H9 human psych", "H8": "H8 persona theory", "H7a_r1": "H7a run 1"}
L = {h: {p: long(E[h], p) for p in ["plus", "minus"]} for h in names}

print("== 1. Agreement between the matrices (plus, Spearman over cells)")
for a, b in [("HPersonaAxes", "H9"), ("HPersonaAxes", "H8"), ("H9", "H8")]:
    print(f"  {names[a]} vs {names[b]}: {spearmanr(L[a]['plus'].p, L[b]['plus'].p)[0]:+.2f}")

DARK = ["spitefulness", "power-seeking", "narcissism", "resource-acquisition", "self-preservation",
        "claiming-superintelligence", "risk-affinity", "punitiveness", "harm-refusal"]
WARM = ["agreeableness", "cooperation", "caring-about-user", "caring-about-animals", "honest-humble", "sycophancy"]
grp = lambda t: "dark" if t in DARK else "warm" if t in WARM else "other"

print("\n== 2. Plus-matrix rho by block (row group -> column group), n cells")
blocks = {}
for h in names:
    d = L[h]["plus"].assign(b=lambda x: x.src.map(grp) + "->" + x.col.map(grp))
    blocks[h] = d.groupby("b").apply(lambda g: pd.Series({"rho": rho(g), "n": len(g)}))
tab = pd.concat({names[h]: blocks[h].rho for h in names}, axis=1)
tab["n"] = blocks["H9"].n.astype(int)
print(tab.round(2).to_string())

print("\n== 3. Drift: the same evals move whatever is trained")
for pole in ["plus", "minus"]:
    d = L["H9"][pole]
    # leave-one-treatment-out column mean, per model
    drift = d.groupby(["m", "col"]).o.transform("sum")
    cnt = d.groupby(["m", "col"]).o.transform("count")
    loo = (drift - d.o) / (cnt - 1)
    print(f"  {pole}: column-mean-only predictor (leave-one-out) rho = {spearmanr(loo, d.o)[0]:+.2f}")
    for h in names:
        x = L[h][pole].copy()
        x["o_w"] = x.o - x.groupby(["m", "col"]).o.transform("mean")  # within-column residual
        print(f"     {names[h]:18s} overall {rho(x):+.2f} | within-column (drift removed) {spearmanr(x.p, x.o_w)[0]:+.2f}"
              f" | column-mean part {spearmanr(x.groupby('col').p.transform('mean'), x.o)[0]:+.2f}")

print("\n== 4. PersonaAxes's own falsifiers (observed = pooled cells)")
pa = L["HPersonaAxes"]["plus"]
dw = pa[((pa.src.isin(DARK)) & (pa.col.isin(WARM))) | ((pa.src.isin(WARM)) & (pa.col.isin(DARK)))]
print(f"  F1 dark<->warm cells negative: {(dw.o < 0).mean():.0%} of {len(dw)} (fails if <= 60%)")
strong = ["narcissism", "spitefulness", "power-seeking", "certainty", "sycophancy"]
mag = pa.assign(a=pa.o.abs()).groupby("src").a.mean()
print(f"  F2 mean |off-target| strong rows {mag[mag.index.isin(strong)].mean():.3f} vs others {mag[~mag.index.isin(strong)].mean():.3f}")
pm = L["HPersonaAxes"]["minus"]
mir = []
for m in MODELS:
    op, om = observed(m, "plus"), observed(m, "minus")
    for t in om.index:
        if t in op.index:
            a, b = op.loc[t].drop(t, errors="ignore"), om.loc[t].drop(t, errors="ignore")
            k = a.notna() & b.notna()
            if k.sum() > 5:
                mir.append(spearmanr(a[k], b[k])[0])
print(f"  F3 minus row vs its plus row, median rho {np.median(mir):+.2f} (predicted negative); "
      f"mean |minus| {pm.o.abs().mean():.3f} vs |plus| {pa.o.abs().mean():.3f} (predicted smaller)")
loc = ["ethical-framework-deontological", "ethical-framework-utilitarian", "ethical-framework-virtue-ethics", "ev-reasoning", "procedural-fidelity"]
print(f"  F4 reasoning-style rows mean |effect| {mag[mag.index.isin(loc)].mean():.3f} vs persona rows {mag[~mag.index.isin(loc)].mean():.3f}")
cp = pa[pa.src == "certainty"].groupby("col").o.mean()
print("  F5 certainty-plus -> " + ", ".join(f"{c} {cp.get(c, np.nan):+.2f}" for c in
      ["neuroticism", "honest-humble", "narcissism", "claiming-superintelligence"]) + " (predicted -, -, +, +)")
sh = pa[(pa.src == "sycophancy") & (pa.col == "honest-humble")].o.mean()
print(f"  F6 sycophancy-plus -> honest-humble {sh:+.2f} (predicted negative)")
near = pa.p.abs() < 0.11
top = pa.o.abs() >= pa.o.abs().quantile(0.9)
print(f"  F7 top-decile observed cells predicted near zero: {(near & top).sum()} of {top.sum()} ({(near & top).sum()/top.sum():.0%}); near-zero share overall {near.mean():.0%}")

print("\n== 5. Biggest misses: confident PersonaAxes cells with the wrong sign (3-model mean)")
g = pa.groupby(["src", "col"]).agg(p=("p", "first"), o=("o", "mean")).reset_index()
g["miss"] = np.sign(g.p) != np.sign(g.o)
w = g[g.miss].assign(score=lambda x: x.p.abs() * x.o.abs()).sort_values("score", ascending=False).head(10)
print(w[["src", "col", "p", "o"]].round(2).to_string(index=False))
print(f"\n  sign agreement, cells with |pred| >= 0.3: PersonaAxes {(np.sign(g[g.p.abs()>=.3].p)==np.sign(g[g.p.abs()>=.3].o)).mean():.0%} (n={(g.p.abs()>=.3).sum()})")
for h in ["H9", "H8"]:
    gh = L[h]["plus"].groupby(["src", "col"]).agg(p=("p", "first"), o=("o", "mean")).reset_index()
    big = gh.p.abs() >= gh.p.abs().quantile(1 - (g.p.abs() >= .3).mean())
    print(f"  same share of its most confident cells, {names[h]}: {(np.sign(gh[big].p)==np.sign(gh[big].o)).mean():.0%}")
