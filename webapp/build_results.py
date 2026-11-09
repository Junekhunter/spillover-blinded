"""Build webapp/results.json: the observed SFT spillover matrices, unsealed at freeze.

Reads the derived matrices of the paper's release repo (propensity-spillover/results/derived):
plus pole for every trait, minus pole for the 7 traits that have minus-pole SFT runs, for each of
Qwen3.5-9B, Qwen3.5-9B-Base and Nemotron-3-Super-120B. Rows of elicitation runs that failed the
paper's filter (on-target effect < 0.2 logit-z) are dropped, as in the paper.

Usage: python webapp/build_results.py [--derived DIR] [out.json]
"""
import argparse
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = {"qwen35": "Qwen3.5-9B", "qwen35-base": "Qwen3.5-9B-Base", "nemotron35": "Nemotron-3-Super-120B"}


def read(path):
    with open(path) as f:
        rows = list(csv.reader(f))
    cols = rows[0][1:]
    return {r[0]: {c: (float(v) if v.strip() else None) for c, v in zip(cols, r[1:])} for r in rows[1:]}


def failed(derived):
    bad = set()
    with open(os.path.join(derived, "failed_runs.csv")) as f:
        for r in csv.DictReader(f):
            if r["method"] == "sft":
                bad.add((r["model"], r["trait"], "plus"))
    with open(os.path.join(derived, "on_target_minus.csv")) as f:
        for r in csv.DictReader(f):
            if r["failed"] == "True":
                bad.add((r["model"], r["trait"], "minus"))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=os.path.join(HERE, "results.json"))
    ap.add_argument("--derived", default=os.path.expanduser("~/Documents/propensity-spillover/results/derived"))
    a = ap.parse_args()
    bad = failed(a.derived)
    out = {"models": MODELS, "observed": {}}
    for key in MODELS:
        out["observed"][key] = {}
        for pole in ("plus", "minus"):
            m = read(os.path.join(a.derived, f"delta_sft_{key}_{pole}.csv"))
            out["observed"][key][pole] = {f"{t}-{pole}": row for t, row in m.items() if (key, t, pole) not in bad}
    json.dump(out, open(a.out, "w"))
    n = {k: {p: len(v) for p, v in d.items()} for k, d in out["observed"].items()}
    print("wrote", a.out, "rows per model/pole:", n)


if __name__ == "__main__":
    main()
