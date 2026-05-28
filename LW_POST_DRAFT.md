# Predict our cross-propensity SFT spillover matrix before we release the results

**tl;dr.** My SPAR group ran a 29 × 29 propensity SFT spillover
experiment. Before we release the results we're giving you lot a chance
to make predictions against our experiments — either manually, or via
our automated theory-of-spillover-doc → prediction-matrix pipeline.

To use the pipeline:

```
git clone https://github.com/Junekhunter/spillover-blinded
cd spillover-blinded
claude     # session reads CLAUDE.md and walks you through it
```

…and do what the robot says. Read the full post if you want to do it
manually.

## Background

My SPAR group, led by Niels from CLR, was looking into out-of-distribution
generalization — in the propensity-evals sense of "we trained the model
to do X on distribution A, does it still do X on distribution B?" — not
the capability-elicitation sense or the input-distribution-shift sense
(those words are overloaded; we mean the propensity one).

Over the course of the fellowship we collected a lot of propensity evals.
This experiment used 29 of them: the set that met our final quality
screen and for which we had a working system-prompt-based elicitation.
(An earlier `reward-hacking` eval was dropped at that screen.)

We split each eval's questions into test/train groups, generated training
data by prompting models with the elicitation system prompt + the train
user prompts, and then used the train user prompts (no system prompt) +
the prior stage's output as SFT training data. We did this for all 29
propensities. We also ran the same protocol with a propensity-*suppressing*
system prompt for the 14 propensities where the suppression prompt passed
quality screen — picked via a scientifically principled and well-documented
process which this margin is far too small to contain. Those 14 are the
ones with both a `-plus` and a `-minus` treatment row in the prediction
templates; the other 15 are plus-only.

## The pipeline

We wanted to test a large number of hypotheses derived from the
literature without filling out a bunch of matrices ourselves —
particularly because I'd already seen in-progress results before this
stage was done (oops, biased). So I had a Claude Code instance that
hadn't seen the results assemble the predictor harness. It has
read-only access to all of the training data, eval judge prompts, etc.,
plus summaries of what the evals are and known footguns in interpreting
them. (Those summaries came after I'd tried running the prediction loop
in sandboxed claude.ai conversations; they're screened for any direct
results leaks, but they may be skewed by "Claude misunderstood X thing,
which I have now clarified" updates that happened *before* I unblinded
the predictor agents.)

You create a hypothesis MD file at `hypotheses/H<your-handle>.md`,
modelled on `EXAMPLE_hypothesis.md` in the repo root. (Our own H1–H9
specs stay sealed until freeze so your framings aren't anchored to
ours; titles and scores ship in the follow-up post.) Then either:

- Run `./scripts/generate.sh H<your-handle>` from the repo root, or
- Just start a Claude Code session — the top-level `CLAUDE.md` is set
  up to autorun the walkthrough for you.

The pipeline writes `predictions/H<your-handle>/logitz_plus.csv`,
`logitz_minus.csv`, and a `method.md` describing how Claude operationalized
your theory into matrix cells.

You can also bypass the LLM step and hand-fill
`inputs/PREDICT_transfer_matrix_logitz_{plus,minus}.csv` directly — or
tweak the matrices Claude generated from your spec. A proper local web
GUI for cell-by-cell editing is planned but not yet shipped; for now,
the CSVs in your spreadsheet of choice are the editing surface.

The pipeline probably works with other coding agents but I haven't
tested them, because I'm already spending too much on one subscription.

I'm willing to send Claude Code guest passes to people who want to
participate but don't have one (until I run out), and to run up to 3
community-picked hypotheses myself the day before freeze — most-upvoted
ones that are qualitatively different from what's already in H1–H9, if
there are more than three.

## The prize

lol, lmao. I don't have that kind of money. I mean — there will be a
leaderboard. Yeah. A leaderboard.

## Additional rules

This is about predicting spillover **before** training any models. You
can run static analyses on the train and test eval sets, and poke at the
base model (Llama 3.1 8B Instruct) with the elicitation prompts. But
**don't train any new models** or otherwise try to access our results.

I will release the results on `[TODO: release date]` (updated when set —
watch this post) and run any community-picked hypothesis files the day
before.

## P.S.

To use the pipeline: clone `https://github.com/Junekhunter/spillover-blinded`,
start a Claude Code session at the repo root, and do what the robot says.
This is safe to do for this specific repo because I'm niceys, but if you
didn't take any steps to verify the repo and/or lock down local
precautions before running an autonomous coding agent on it, your
security posture is bad and you should feel bad.
