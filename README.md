# spillover-blinded

Blinded, sandboxed generation of cross-propensity SFT spillover predictions
across hypotheses H1–H9, run via Claude Code subagents instead of one human
manually driving nine chat sessions.

## What enforces the blind

Three layers, in order of how much you should trust them:

1. **OS-level filesystem permissions (trust this).** During generation, the
   `RESULTS/` directory must be unreadable to the user/process running the
   predictors. This is the real blind. See "OS-level blinding" below.
2. **Claude Code `deny` rules** (`.claude/settings.json`) — block the file
   tools and common bash readers from `RESULTS/`. A second layer. NOT
   sufficient alone: a subagent can read a file via `python3` or a symlink.
3. **Process isolation** — each hypothesis runs in its own headless `claude`
   process with its own context (`generate.sh`). This approximates the
   separate-chat isolation that worked in prior manual runs.

Subagents share your model and filesystem. They are NOT a security boundary.
The blind comes from layer 1; layers 2–3 reduce accident and parallelize work.

## Layout

    inputs/        eval definitions, items, reference answers, judge prompts, CSV templates
    hypotheses/    one blinded spec per hypothesis: H1.md ... H9.md
    predictions/   subagents write here, one subdir per hypothesis
    RESULTS/       observed matrices — placed ONLY after freeze
    scripts/       generate.sh, freeze.sh, score.py
    BLINDED_PROMPT.md   shared protocol, appended to every predictor's prompt

## What predictors emit (Option 1)

Each hypothesis predicts ONLY `logitz_plus.csv` (24x24) and
`logitz_minus.csv` (21x24). No theta. The current battery has 24 evals (21
bipolar, 3 unipolar ethical-framework evals); a treatment is SFT on an eval's
train-split prompts paired with one pole's reference answers, measured on
Qwen3.5-9B, Qwen3.5-9B-Base and Nemotron-3-Super-120B (see
`inputs/README.md`).

logitz is already z-scored per eval upstream (empirical-logit of the 0-100
judge score, z-scored against the full reference panel for that eval). The
scorer derives theta as a per-eval AFFINE rescale of logitz, using the
observed directly-SFT'd diagonal poles as endpoints — see `scripts/score.py`
header for why this stays in logitz space rather than inverting to score
space. The theta endpoints are read straight off the diagonal of the
observed matrices; there is no separate anchors file.

Two separate leaderboards result (logitz over 24 evals, theta over 21
bipolar); they are never merged. theta is a per-eval affine transform of
logitz and carries little independent information — logitz is the headline.

## Procedure

1. Populate `inputs/` with the corrected eval set, eval descriptions, and
   the two `PREDICT_transfer_matrix_*.csv` templates (headers + row labels
   only — no values).
2. Write one `hypotheses/H*.md` spec per hypothesis.
3. Keep observed matrices OUT of the repo for now. `RESULTS/` stays empty.
4. **Lock RESULTS** (see below), then: `./scripts/generate.sh`
5. Review `logs/` and any `predictions/*/NEEDS_CLARIFICATION.md`. Answer
   clarifications by editing the hypothesis spec, re-run that hypothesis.
6. When predictions are complete: `./scripts/freeze.sh` — commits + git-tags.
7. Place observed matrices in `RESULTS/` as `observed_logitz_plus.csv`
   (24x24) and `observed_logitz_minus.csv` (21x24). The scorer reads the
   theta endpoints off these matrices' diagonals — no separate anchors
   file. Unlock `RESULTS/` for the scorer user.
8. `python3 ./scripts/score.py`

## OS-level blinding

`settings.json` deny rules are not airtight. Before `generate.sh`, make
`RESULTS/` genuinely unreadable to the generating user. Pick one:

  * Empty during generation (simplest): keep observed files entirely outside
    the repo until after freeze. `generate.sh` aborts if RESULTS has
    readable content.
  * Permission lock: `chmod 000 RESULTS` before generation; restore after
    freeze. (Defeatable by the file owner — combine with the next option.)
  * Separate user: results owned by a `scorer` user with mode 700;
    generation runs as a `predictor` user with no access. This is the only
    version where "the subagent could not read results" is a true statement
    about the system rather than a hope about behavior.

## Known limitations (be honest about these)

* **Same-model contamination.** Every predictor is the same Claude and may
  have priors on `spar-ood-propensities`. Web access is disabled, but
  pretraining leakage cannot be ruled out. Predictors are instructed to
  disclose literature overlap; treat it as an assumption, not a guarantee.
* **theta is not an independent test** under Option 1 — it is a per-eval
  affine transform of logitz, which is itself already z-scored per eval.
  Spearman is invariant to a uniform monotone transform, so theta differs
  from logitz only through the per-eval differences in diagonal range. The
  design deliberately gives up the ability to detect a theta-specific
  signal (e.g. an introspective lift on post-SFT landing position) in
  exchange for a comparable, leak-free board.
* **H7a / H7b are intentionally underspecified.** Their specs are one-line
  stubs (an "any in-bundle method" condition and an "intuition only"
  condition), not full literature-grounded specs like H1-H6/H8/H9. Each is
  run three times (`H7a_r1..r3`, `H7b_r1..r3`) on byte-identical prompts;
  the spread across the three replicates IS the variance estimate for that
  underspecification. Read their leaderboard rows as a cluster, not as
  single points, and do not compare a single H7a row head-to-head with a
  fully-specified hypothesis — the comparison is cluster-vs-point.
