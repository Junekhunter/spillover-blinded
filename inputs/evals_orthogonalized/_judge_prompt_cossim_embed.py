"""Semantic-embedding cosine similarity of judge prompts, with and without the shared preamble.

Same entry extraction / preamble split as _judge_prompt_cossim.py, but vectors are local
sentence embeddings (all-MiniLM-L6-v2) instead of TF-IDF. No API key required.

Judge prompts are long (up to ~5k tokens) and the model's window is 256 tokens, so each
text is split into 256-token chunks; the document vector is the token-count-weighted mean
of per-chunk mean-pooled embeddings, then L2-normalized. This approximates full-sequence
mean pooling and is the standard way to embed long docs with a short-context encoder.
"""
import glob
import os

import numpy as np
import torch
import torch.nn.functional as F
import yaml
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModel, AutoTokenizer

ROOT = os.path.dirname(os.path.abspath(__file__))
MARK = "METRIC PROMPT (use the scale defined here, but apply the null rule above):"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
WIN = 256  # model max sequence length

entries = []  # (label, full, body, has_preamble)
for d in sorted(x for x in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, x))):
    fs = sorted(glob.glob(os.path.join(ROOT, d, "*_eval*.yaml")))
    if not fs:
        continue
    jp = yaml.safe_load(open(fs[0]))[0].get("judge_prompts", {})
    for metric, text in jp.items():
        if MARK in text:
            body, has_pre = text.split(MARK, 1)[1].strip(), True
        else:
            body, has_pre = text.strip(), False
        entries.append((f"{d}/{metric}", text, body, has_pre))

labels = [e[0] for e in entries]
n = len(entries)
n_no_pre = sum(1 for e in entries if not e[3])

tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModel.from_pretrained(MODEL).eval()


@torch.no_grad()
def embed(text):
    ids = tok(text, add_special_tokens=False)["input_ids"]
    if not ids:
        ids = [tok.cls_token_id]
    cls, sep = tok.cls_token_id, tok.sep_token_id
    vecs, weights = [], []
    for s in range(0, len(ids), WIN - 2):
        chunk = [cls] + ids[s:s + WIN - 2] + [sep]
        t = torch.tensor([chunk])
        out = model(input_ids=t, attention_mask=torch.ones_like(t))[0]
        vecs.append(out.mean(dim=1).squeeze(0))   # mean-pool tokens in chunk
        weights.append(len(chunk))
    w = torch.tensor(weights, dtype=torch.float32)
    v = torch.stack(vecs)
    doc = (v * w[:, None]).sum(0) / w.sum()
    return F.normalize(doc, dim=0).numpy()


vecs_full = np.stack([embed(e[1]) for e in entries])
vecs_body = np.stack([embed(e[2]) for e in entries])
S_with = cosine_similarity(vecs_full)
S_without = cosine_similarity(vecs_body)


def save(M, path):
    with open(path, "w") as f:
        f.write("label," + ",".join(labels) + "\n")
        for i, lab in enumerate(labels):
            f.write(lab + "," + ",".join(f"{v:.4f}" for v in M[i]) + "\n")


save(S_with, os.path.join(ROOT, "_judge_cossim_with_preamble_embed.csv"))
save(S_without, os.path.join(ROOT, "_judge_cossim_without_preamble_embed.csv"))


def offdiag(M):
    return M[np.triu_indices_from(M, k=1)]


ow, owo = offdiag(S_with), offdiag(S_without)
print(f"{MODEL}: {n} judge prompts ({n_no_pre} have no standardized preamble)\n")
print("Off-diagonal pairwise cosine similarity (semantic embeddings):")
print(f"             {'WITH preamble':>16}{'WITHOUT preamble':>18}")
for name, fn in [("mean", np.mean), ("median", np.median),
                 ("p90", lambda a: np.percentile(a, 90)),
                 ("max", np.max), ("min", np.min)]:
    print(f"  {name:<8} {fn(ow):>16.3f}{fn(owo):>18.3f}")

print("\nTop 12 most-similar prompt pairs (WITHOUT preamble, semantic):")
iu = np.triu_indices_from(S_without, k=1)
for idx in np.argsort(-S_without[iu])[:12]:
    i, j = iu[0][idx], iu[1][idx]
    print(f"  {S_without[i, j]:.3f}  (with={S_with[i, j]:.3f})  {labels[i]}  <->  {labels[j]}")

print("\nWritten: _judge_cossim_{with,without}_preamble_embed.csv")
