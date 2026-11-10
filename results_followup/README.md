# Spillover challenge: results follow-up

Rescoring and charts for the follow-up LessWrong post on the cross-propensity spillover prediction challenge (closed 2026-11-09).

The scorer reproduces the challenge site's: Spearman ρ over off-diagonal cells, with the three models pooled (Qwen3.5-9B, Qwen3.5-9B-Base, Nemotron-3-Super-120B). Rows whose fine-tune moved its own trait by less than 0.2 logit-z are dropped. The headline score is the mean of plus ρ and minus ρ. Each entry is scored under two rules for blank prediction cells:

- **zero**: blanks count as predicting 0 spillover (the intended rule)
- **dropped**: blanks are skipped (what the site's scorer did)

Only Quine left cells blank, so it's the only entry the rule moves.

| File | What it is |
|---|---|
| `score_both_rules.py` | Rescores every entry under both rules with 2000-replicate bootstrap CIs. Also computes the no-information band (permutation) and the max possible score (the observed 3-model mean used as the prediction). Writes `scores.csv`. |
| `plot_both_rules.py` | `fig_score.png` (headline score) and `fig_plus_minus.png` (plus and minus ρ), every entry under both rules |
| `plot_persona.py` | `fig_persona.png`: H9 vs H8 vs PersonaAxes |
| `personaaxes_dig.py` | Why PersonaAxes scored low: block-wise ρ, drift, its own falsifiers, biggest misses |
| `paired_bootstrap.py` | Paired differences between entries (same resampled cells for both): Quine vs PersonaAxes, H9 vs Quine, H8 vs PersonaAxes, H9 vs PersonaAxes |
| `leaderboard.md` | The leaderboard table from the post |
| `H8_method.md` | How the H8 (persona theory) matrix was operationalized |
| `entries/` | All 16 prediction matrices (H1–H9 runs plus the two outside entries, as submitted) |
| `obs_*.csv`, `results.json`, `examples.json` | Observed SFT spillover per model and pole, plus the site's results and hypothesis-spec exports |

Run any script from this folder. They need numpy, pandas, scipy and matplotlib. Paper: [arXiv 2610.14937](https://arxiv.org/abs/2610.14937).
