"""Cosine similarity of orthogonalized judge prompts, with and without the shared preamble.

Each eval's judge_prompts block is a dict of metric -> prompt text. Most prompts carry a
shared "orthogonality"/"style" preamble terminated by the line:

    METRIC PROMPT (use the scale defined here, but apply the null rule above):

`with`    = full prompt text
`without` = text after that separator (trait-specific portion only); prompts that have no
            separator have no standardized shared preamble, so without == with (flagged).

Vectorization: TF-IDF (word 1-2 grams), cosine similarity. Deterministic, no API.
"""
import glob
import os

import numpy as np
import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = os.path.dirname(os.path.abspath(__file__))
MARK = "METRIC PROMPT (use the scale defined here, but apply the null rule above):"

entries = []  # (label, full_text, body_text, has_preamble)
for d in sorted(x for x in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, x))):
    fs = sorted(glob.glob(os.path.join(ROOT, d, "*_eval*.yaml")))
    if not fs:
        continue
    data = yaml.safe_load(open(fs[0]))
    jp = data[0].get("judge_prompts", {})
    for metric, text in jp.items():
        if MARK in text:
            body = text.split(MARK, 1)[1].strip()
            has_pre = True
        else:
            body = text.strip()
            has_pre = False
        entries.append((f"{d}/{metric}", text, body, has_pre))

labels = [e[0] for e in entries]
full = [e[1] for e in entries]
body = [e[2] for e in entries]
n = len(entries)
n_no_pre = sum(1 for e in entries if not e[3])


def sim_matrix(texts):
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
    X = vec.fit_transform(texts)
    return cosine_similarity(X)


def offdiag(M):
    return M[np.triu_indices_from(M, k=1)]


S_with = sim_matrix(full)
S_without = sim_matrix(body)


def save(M, path):
    with open(path, "w") as f:
        f.write("label," + ",".join(labels) + "\n")
        for i, lab in enumerate(labels):
            f.write(lab + "," + ",".join(f"{v:.4f}" for v in M[i]) + "\n")


save(S_with, os.path.join(ROOT, "_judge_cossim_with_preamble.csv"))
save(S_without, os.path.join(ROOT, "_judge_cossim_without_preamble.csv"))

ow, owo = offdiag(S_with), offdiag(S_without)
print(f"{n} judge prompts ({n_no_pre} have no standardized preamble: with==without)\n")
print("Off-diagonal pairwise cosine similarity:")
print(f"             {'WITH preamble':>16}{'WITHOUT preamble':>18}")
for name, fn in [("mean", np.mean), ("median", np.median), ("p90", lambda a: np.percentile(a, 90)),
                 ("max", np.max), ("min", np.min)]:
    print(f"  {name:<8} {fn(ow):>16.3f}{fn(owo):>18.3f}")

print("\nTop 12 most-similar prompt pairs (WITHOUT preamble):")
iu = np.triu_indices_from(S_without, k=1)
order = np.argsort(-S_without[iu])
for idx in order[:12]:
    i, j = iu[0][idx], iu[1][idx]
    print(f"  {S_without[i, j]:.3f}  (with={S_with[i, j]:.3f})  {labels[i]}  <->  {labels[j]}")

print("\nMatrices written: _judge_cossim_with_preamble.csv, _judge_cossim_without_preamble.csv")
