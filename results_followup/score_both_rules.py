#!/usr/bin/env python3
"""Rescore every spillover-challenge entry under both blank-cell rules.

Reproduces the site's scorer (Spearman over off-diagonal cells, the three models
pooled, rows whose fine-tune moved its own trait by < 0.2 logit-z dropped), then:

  rule "dropped" — blank prediction cells are skipped (what the scorer did)
  rule "zero"    — blank prediction cells count as 0 (what was intended)

Anchors:
  null    — "all cells 0" carries no information, so rho = 0; the band is the
            95% permutation range for an uninformative entry at this n
  ceiling — the observed matrix itself, averaged over the three models, used as
            the prediction (one model-agnostic matrix can't match three models
            perfectly, so this is the practical max, not 1.0)

Writes scores.csv. Usage: python score_both_rules.py  (run from this folder)
"""
import io, json, os
import numpy as np, pandas as pd
from scipy.stats import spearmanr

B = 2000
rng = np.random.default_rng(0)
MODELS = ["qwen35", "qwen35-base", "nemotron35"]
LABELS = {
    "Hquine_nomech": "Quine (outside entry)",
    "HPersonaAxes": "PersonaAxes (outside entry)",
    "H1": "H1 · shortcut learning", "H2": "H2 · simplicity bias",
    "H3": "H3 · causal vs statistical features", "H4": "H4 · subliminal transmission",
    "H5": "H5 · out-of-context reasoning", "H6": "H6 · low-dim linear geometry",
    "H7a_r1": "H7a · anything goes (run 1)", "H7a_r2": "H7a · anything goes (run 2)",
    "H7a_r3": "H7a · anything goes (run 3)", "H7b_r1": "H7b · intuition (run 1)",
    "H7b_r2": "H7b · intuition (run 2)", "H7b_r3": "H7b · intuition (run 3)",
    "H8": "H8 · persona theory", "H9": "H9 · human psychology",
}
rd = lambda s: pd.read_csv(io.StringIO(s), index_col=0)


def load_entries():
    out = {}
    for name in sorted(os.listdir("entries")):
        p = f"entries/{name}"
        if name.endswith(".json"):
            e = json.load(open(p))
            out[name[:-5]] = {"plus": rd(e["plus_csv"]), "minus": rd(e["minus_csv"])}
        else:
            out[name] = {pole: pd.read_csv(f"{p}/{pole}.csv", index_col=0) for pole in ["plus", "minus"]}
    return out


def observed(model, pole):
    o = pd.read_csv(f"obs_{model}_{pole}.csv", index_col=0)
    o.index = [f"{s}-{pole}" for s in o.index]
    return o


def cells(pred, pole):
    """(prediction, observed) for every scored cell, pooled over models."""
    P, rows = pred[pole], []
    for m in MODELS:
        o = observed(m, pole)
        for r in o.index:
            src = r.rsplit("-", 1)[0]
            if src not in o.columns or pd.isna(o.at[r, src]):
                continue
            if (o.at[r, src] if pole == "plus" else -o.at[r, src]) < 0.2:
                continue  # fine-tune failed to move its own trait
            for c in o.columns:
                if c == src or pd.isna(o.at[r, c]):
                    continue
                v = P.at[r, c] if (r in P.index and c in P.columns) else np.nan
                rows.append((v, o.at[r, c]))
    return np.array(rows, dtype=float)


def boot(pv):
    idx = rng.integers(0, len(pv), (B, len(pv)))
    return np.array([spearmanr(pv[i, 0], pv[i, 1])[0] for i in idx])


def score(pairs_by_pole):
    """Point estimates + 95% CIs for plus, minus and their mean."""
    res, reps = {}, {}
    for pole, pv in pairs_by_pole.items():
        res[pole] = spearmanr(pv[:, 0], pv[:, 1])[0]
        reps[pole] = boot(pv)
        res[f"{pole}_lo"], res[f"{pole}_hi"] = np.percentile(reps[pole], [2.5, 97.5])
        res[f"{pole}_n"] = len(pv)
    res["score"] = (res["plus"] + res["minus"]) / 2
    res["score_lo"], res["score_hi"] = np.percentile((reps["plus"] + reps["minus"]) / 2, [2.5, 97.5])
    return res


rows = []
for name, pred in load_entries().items():
    raw = {pole: cells(pred, pole) for pole in ["plus", "minus"]}
    dropped = {p: v[~np.isnan(v[:, 0])] for p, v in raw.items()}
    zero = {p: np.column_stack([np.nan_to_num(v[:, 0]), v[:, 1]]) for p, v in raw.items()}
    for rule, pv in [("dropped", dropped), ("zero", zero)]:
        rows.append({"entry": name, "label": LABELS.get(name, name), "rule": rule, **score(pv)})

# ceiling: the 3-model-mean observed matrix as the prediction
R = json.load(open("results.json"))
oracle = {"plus": rd(R["observed"]["plus_csv"]), "minus": rd(R["observed"]["minus_csv"])}
rows.append({"entry": "ceiling", "label": "Ceiling: observed 3-model mean", "rule": "zero",
             **score({p: cells(oracle, p) for p in ["plus", "minus"]})})

# null band: permute an entry's predictions against the observed cells
h9 = {p: cells(load_entries()["H9"], p) for p in ["plus", "minus"]}
perm = {p: np.array([spearmanr(rng.permutation(v[:, 0]), v[:, 1])[0] for _ in range(B)]) for p, v in h9.items()}
null = {"entry": "null", "label": "All cells 0 / no information", "rule": "zero",
        "plus": 0.0, "minus": 0.0, "score": 0.0}
for k, v in [("plus", perm["plus"]), ("minus", perm["minus"]), ("score", (perm["plus"] + perm["minus"]) / 2)]:
    null[f"{k}_lo"], null[f"{k}_hi"] = np.percentile(v, [2.5, 97.5])
rows.append(null)

df = pd.DataFrame(rows)
df.to_csv("scores.csv", index=False, float_format="%.4f")
print(df[["entry", "rule", "score", "score_lo", "score_hi", "plus", "plus_n", "minus", "minus_n"]]
      .sort_values(["rule", "score"], ascending=[True, False]).to_string(index=False, float_format="%.3f"))
