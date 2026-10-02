"""Precompute a compact per-eval summary (webapp/static/evals.json) from inputs/.

Run at image build time. Reads only inputs/ — the same blinding-safe bundle
participants get. Never touches RESULTS/ or predictions/.
"""
import csv
import glob
import json
import os
import re
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVALS_DIR = os.path.join(ROOT, "inputs", "evals_orthogonalized")
OUT = os.path.join(os.path.dirname(__file__), "static", "evals.json")

Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

BIPOLAR = [
    "agreeableness", "certainty", "cooperation", "effort", "harm-elaboration",
    "harm-refusal", "honest-humble", "neuroticism", "power-seeking",
    "resource-acquisition", "self-preservation", "spending-advice",
    "spitefulness", "trust-in-user-intentions",
]

# From READING_GUIDE.md: which system-prompt file is the plus / minus pole.
POLE_FILES = {
    "agreeableness": ("agreeable.txt", "disagreeable.txt"),
    "neuroticism": ("emotionally_stable.txt", "neurotic.txt"),
    "honest-humble": ("high_hh.txt", "low_hh.txt"),
    "cooperation": ("hi.txt", "lo.txt"),
    "resource-acquisition": ("hi.txt", "lo.txt"),
    "spitefulness": ("hi.txt", "lo.txt"),
}
for e in ["certainty", "effort", "harm-elaboration", "harm-refusal", "power-seeking",
          "self-preservation", "spending-advice", "trust-in-user-intentions"]:
    POLE_FILES[e] = ("high.txt", "low.txt")

TRAPS = {
    "harm-refusal": "Higher score = LESS refusal (more compliance with the harmful request).",
    "spending-advice": "Higher score = advising the user to spend LESS.",
    "neuroticism": "File order is not score direction — check the judge scale below.",
}


def judge_scale(prompt: str) -> str:
    """The eval-specific part of a judge prompt: everything after the shared
    orthogonality preamble when it is marked, else the whole prompt."""
    i = prompt.find("METRIC PROMPT")
    if i >= 0:
        return prompt[prompt.find("\n", i) + 1:].strip()
    return prompt.strip()


def main() -> None:
    defs = json.load(open(os.path.join(EVALS_DIR, "definitions.json")))
    anchors = {}
    with open(os.path.join(ROOT, "inputs", "eval_anchors_summary.csv")) as f:
        for row in csv.DictReader(f):
            anchors[row["eval"]] = row

    evals = []
    for d in sorted(glob.glob(os.path.join(EVALS_DIR, "*", ""))):
        name = os.path.basename(os.path.dirname(d))
        ymls = glob.glob(os.path.join(d, "*.yaml"))
        if len(ymls) != 1:
            print(f"warn: {name} has {len(ymls)} yaml files", file=sys.stderr)
            continue
        items = yaml.load(open(ymls[0]), Loader=Loader)
        n_train = sum(1 for it in items if it.get("meta", {}).get("split") == "train")
        n_test = sum(1 for it in items if it.get("meta", {}).get("split") == "test")
        metrics = []
        scales = {}
        for it in items:
            for k, v in (it.get("judge_prompts") or {}).items():
                if k not in scales:
                    metrics.append(k)
                    scales[k] = judge_scale(v)
        meta_keys = sorted({k for it in items for k in (it.get("meta") or {})})

        samples = []
        for it in [it for it in items if it.get("meta", {}).get("split") == "test"][:4]:
            meta = it.get("meta") or {}
            samples.append({
                "id": it.get("id"),
                "prompt": (it.get("paraphrases") or [""])[0],
                "expected": {k: v for k, v in meta.items()
                             if k.startswith("expected") and isinstance(v, str)},
            })

        sp_dir = os.path.join(d, "system_prompts")
        system_prompts = {}
        for p in sorted(glob.glob(os.path.join(sp_dir, "*.txt"))):
            system_prompts[os.path.basename(p)] = open(p).read().strip()

        a = anchors.get(name, {})
        def num(x):
            try:
                return round(float(x), 2)
            except (TypeError, ValueError):
                return None

        evals.append({
            "name": name,
            "bipolar": name in BIPOLAR,
            "yaml": os.path.relpath(ymls[0], ROOT),
            "n_items": len(items),
            "n_train": n_train,
            "n_test": n_test,
            "metrics": metrics,
            "judge_scales": scales,
            "meta_keys": meta_keys,
            "definition": defs.get(name),
            "pole_files": POLE_FILES.get(name),
            "system_prompts": system_prompts,
            "base_anchor": {"mean_lo": num(a.get("mean_lo")), "mean_hi": num(a.get("mean_hi"))},
            "trap": TRAPS.get(name),
            "samples": samples,
        })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"evals": evals}, open(OUT, "w"), indent=1)
    print(f"wrote {OUT}: {len(evals)} evals")


if __name__ == "__main__":
    main()
