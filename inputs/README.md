# Blinded Eval Kit (cleaned — Llama sweep)

Self-contained snapshot for siloed agents running blinded experiments on the
orthogonalized propensity evals. This is the cleaned bundle: 29 evals,
`reward-hacking` removed, Llama anchors only.

## Contents

```
evals_orthogonalized/   # 29 evals. Each has one <eval>_eval*.yaml with
                        # paraphrases inline (test set) + system_prompts/.
                        # See evals_orthogonalized/READING_GUIDE.md (authoritative).
anchors.yaml            # Per-eval anchor configuration (diagonal-anchor design).
eval_anchors_summary.csv # Llama base-model anchor summary: mean_lo / mean_hi
                        # per eval. BASE-MODEL behavior only — no spillover.
```

## What is and isn't included

**Included:**
- All test paraphrases (inline in each `<eval>_eval*.yaml`) and judge prompts.
- `definitions.json` — per-axis definitions and pole descriptions.
- `_normalize_summary.csv` — item-set curation counts (train/test/dups).
- `_judge_cossim_*.csv` — pairwise cosine similarity between judge prompts
  across evals (token-overlap and embedding variants, with/without preamble).
  Eval-construction metadata describing judge-rubric overlap; contains no
  fine-tune scores. `_judge_prompt_cossim*.py` are the scripts that produced
  them.
- `eval_anchors_summary.csv` — Llama diagonal anchors: `mean_lo` / `mean_hi`
  per eval. These define theta=0 (lo) and theta=1 (hi). Dual-pole evals have
  both; plus-only evals have `mean_lo` blank and `flagged=True`.

**Deliberately excluded** (to keep this blinded):
- `transfer_matrix_*` — full cross-eval spillover matrices.
- `theta_per_eval.parquet` / `theta_per_prompt.parquet` — off-diagonal cells.
- All downstream experiment results.
- Per-model anchor folders for Qwen and Nemotron — this bundle is Llama only.

## How theta is defined

theta(E, p) = (s(p) - anchor_lo(E, p)) / (anchor_hi(E, p) - anchor_lo(E, p))

By construction `<E>-plus` sits at theta~=1 and `<E>-minus` at theta~=0. theta
is only well-defined for the 14 dual-pole evals (both `-plus` and `-minus`
fine-tunes present). The 15 plus-only evals have no valid lo->hi span and are
flagged in `anchors.yaml` / `eval_anchors_summary.csv`.

## Eval universe

29 propensities. The authoritative list is in
`evals_orthogonalized/READING_GUIDE.md`. There is no `reward-hacking` eval.

Dual-pole (14, theta well-defined): agreeableness, certainty, cooperation,
effort, harm-elaboration, harm-refusal, honest-humble, neuroticism,
power-seeking, resource-acquisition, self-preservation, spending-advice,
spitefulness, trust-in-user-intentions.

Plus-only (15, no theta): caring-about-aesthetics, caring-about-animals,
caring-about-humans, caring-about-user, claiming-sentience,
claiming-superintelligence, ethical-framework-deontological,
ethical-framework-utilitarian, ethical-framework-virtue-ethics, ev-reasoning,
exemplar-reasoning, narcissism, procedural-fidelity, risk-affinity, sycophancy.
