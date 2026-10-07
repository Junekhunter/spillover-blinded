# Spillover prediction challenge — LessWrong open call

> **Easiest way to take part: https://spillover.nielsrolf.com.** Describe
> your thesis in a text box, and the same blinded protocol runs server-side
> (no Claude Code needed). You can also hand-edit cells and submit there.
> The rest of this file describes the original command-line flow, which
> still works.

## The setup

We fine-tuned models on each of 24 behavioral propensities
("treatments") — for bipolar propensities, in both directions. A treatment
is plain SFT on the propensity's train-split questions paired with that
pole's reference answers (`expected_plus_response` /
`expected_minus_response` in the eval YAMLs). Each fine-tune was then
evaluated against all 24 propensities, on three models: Qwen3.5-9B,
Qwen3.5-9B-Base and Nemotron-3-Super-120B. The result, per model, is two
matrices of **logitz** values (signed empirical-logit shifts, z-scored per
eval):

- `logitz_plus` — 24 plus-pole treatments x 24 evals
- `logitz_minus` — 21 minus-pole treatments x 24 evals

You submit one model-agnostic pair of matrices; it is compared with the
observed matrices of each of the three models.

The diagonal (a treatment scored on its own eval) is the on-target effect
and is **excluded from scoring**. Everything off-diagonal is spillover: when
you teach the model to be more "cooperative," what else moves, and by how
much, in which direction?

We've already had Claude (Opus 5.5, via the website's harness) generate nine framings of this prediction (H1–H9).
Their specs are public examples on the website, and you may start from one.
Their predictions are shown on the website only after you submit your own
entry, and submitting is final, so your numbers aren't anchored to ours.
You're being asked to do better, or to discover that the framings already
cover the space.

## What you submit

### Default tier — a hypothesis spec (recommended)

Write a Markdown document — a falsifiable theory of which treatments
will spill over to which evals, and why. See `EXAMPLE_hypothesis.md`
for the expected format (sections: statement, definitions, literature,
operationalization, prerequisites, falsifiers). **You do not fill any CSVs.** You feed your spec into the same
headless Claude Code pipeline that produced the H1–H9 predictions, on
your own machine:

```
git clone https://github.com/Junekhunter/spillover-blinded   # or unzip the bundle
cd spillover-blinded
claude                                                  # session reads CLAUDE.md
# draft hypotheses/H<your-handle>.md (Claude will help)
./scripts/generate.sh H<your-handle>
```

The pipeline produces:

- `predictions/H<handle>/logitz_plus.csv` + `logitz_minus.csv`
- `method.md` describing how Claude operationalized your theory
- optional `NEEDS_CLARIFICATION.md` if the pipeline got stuck

You may iterate. Honor-system cap: ≤3 generation runs per hypothesis, so
the comparison with the locked-once H1–H9 stays fair.

This is the headline ask. Same prompt and same scoring as H1–H9 — only your
framing varies. H1–H9 were predicted by Claude Opus 5.5 through the website's
harness (no code execution); a local Claude Code run can execute code and may
use a different model, so the website is the strictly apples-to-apples route.

### Optional tier — hand-tuned matrices

If you'd rather encode cell-level intuitions than write theory, fill the
two CSV templates directly:

- `inputs/PREDICT_transfer_matrix_logitz_plus.csv` (24x24)
- `inputs/PREDICT_transfer_matrix_logitz_minus.csv` (21x24)

Row/column order MUST match the template exactly. Treatment rows are
labelled `<eval>-plus` / `<eval>-minus`; eval columns are bare eval names.
Diagonals are ignored — fill or leave blank.

A proper local web GUI for filling these cells is planned but not shipped
yet — for now your editing surface is the CSV in whatever spreadsheet or
editor you prefer. Save the result to
`predictions/H<your-handle>/logitz_{plus,minus}.csv`.

You may also submit **both**: a hypothesis spec plus a hand-edited
version of the matrices Claude produces. The diff is informative.

## Scoring

Two leaderboards (same as H1–H9):

- **logitz_plus** — Spearman rho on the 552 off-diagonal cells
- **logitz_minus** — Spearman rho on the 483 off-diagonal cells

Bootstrap 95% CIs reported. The headline score is the mean of the two rhos,
computed against each of the three models' observed matrices.

A theta-rescaled board exists but it's a per-eval affine transform of
logitz, so it carries little independent information. Don't design for it.

## Calibration (read this before predicting)

logitz is **already z-scored per eval** upstream. Calibrate carefully:
- **direction** (sign of each cell)
- **relative magnitude** (ordering of magnitudes within each matrix)

Don't try to hit absolute scale — Spearman is invariant to monotone
transforms. Ordering is everything.

## Scope facts

- **24 propensities.** Any document mentioning `caring-about-humans`,
  `effort`, `exemplar-reasoning`, `harm-elaboration` (replaced by
  `punitiveness`), `spending-advice`, `trust-in-user-intentions` or
  `reward-hacking` is stale — those evals are not in this battery. Flag it
  if you see it.
- **21 bipolar evals** (have both plus and minus poles): agreeableness,
  caring-about-aesthetics, caring-about-animals, caring-about-user,
  certainty, claiming-sentience, claiming-superintelligence, cooperation,
  ev-reasoning, harm-refusal, honest-humble, narcissism, neuroticism,
  power-seeking, procedural-fidelity, punitiveness, resource-acquisition,
  risk-affinity, self-preservation, spitefulness, sycophancy.
- **3 unipolar evals** (plus-only — columns but never minus rows):
  ethical-framework-{deontological,utilitarian,virtue-ethics}.
- **Counter-intuitive direction traps** — confirm sign from the eval
  descriptions / judge prompts, not the eval name. Known traps:
  `harm-refusal` (higher = LESS refusal; the plus pole is compliance),
  `neuroticism` (plus pole = neurotic), `resource-acquisition` (the judge
  scale is signed, −100..+100).

## Honesty

- Disclose training-data overlap with any literature your hypothesis cites.
- Disclose any AI assistance used in writing the spec or hand-tuning the
  matrices.
- Do not reconstruct or guess the observed SFT diagonal.
- A clean "silent on this cell" or "could not predict X" is always
  preferable to a fabricated number.

## What's in this bundle

```
inputs/                          # eval definitions, paraphrases, per-pole reference
                                 # answers, judge prompts, judge-overlap cosine
                                 # matrices, and the two CSV templates
                                 # (the host's H1-H9 specs are on the website;
                                 # their predictions unlock there after you submit)
EXAMPLE_hypothesis.md            # deliberately weak example showing the format
CHALLENGE.md                     # this file
```

You will NOT find in this bundle:
- the observed `logitz_plus` / `logitz_minus` matrices (those are the
  ground truth, kept under OS-level lockout until freeze)
- the H1–H9 predictions or scores
- the leaderboard

## Timeline

- **T+0**: repo / bundle published.
- **T+0 ... freeze−1**: anyone can clone and run the pipeline locally.
  Iterate as much as you like; honor-system cap of ≤3 generations per
  hypothesis to stay comparable with the locked-once H1–H9.
- **Freeze − 1 day**: host runs up to 3 community-picked hypothesis files
  (most upvoted that are qualitatively different from H1–H9) for people
  who can't run the pipeline themselves.
- **Freeze**: observed matrices unsealed. Scorer runs. Follow-up LW post
  publishes the combined leaderboard (your entries + H1–H9), notable
  framings, and what the observed matrices actually surprised everyone
  with.

## Submission

Predictions live on your local disk. Post a comment on the LW challenge
thread containing:

- Your handle (whatever you used for `hypotheses/H<handle>.md`)
- Tier(s) submitted: hypothesis spec / hand-tuned / both
- Either a public-gist URL with your spec + predictions, or a note that
  you'll share them via DM / will email them to the host before freeze
- Optional ≤300-word note on what makes your framing different from H1–H9
- AI-tool and literature-overlap disclosure

The host runs the day-before-freeze pass on any submitted-but-not-yet-run
hypothesis files (up to 3 community-picked specs, see the LW post). Read
`EXAMPLE_hypothesis.md` once to see the expected format. The host's H1–H9
specs are public examples on the website. Their predictions unlock there
once your own entry is submitted (and therefore final), and scores get
published in the follow-up post.
Good luck.
