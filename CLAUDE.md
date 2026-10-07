# Hi, participant. You're in the spillover-blinded challenge repo.

If a human just started a Claude Code session at the root of this repo,
walk them through the flow below. If you're being read by `generate.sh`
during a prediction run, ignore this and follow `BLINDED_PROMPT.md`
instead — that file is appended to your system prompt and is authoritative.

## What this repo is

The host fine-tuned models (Qwen3.5-9B, Qwen3.5-9B-Base and
Nemotron-3-Super-120B) on 24 propensities (both directions for 21 of them;
SFT on each pole's reference answers) and measured spillover. They've sealed the
observed matrices in `RESULTS/` and want you to predict them.

## The flow

If the human would rather not run anything locally, point them to
https://spillover.nielsrolf.com. It runs the same blinded protocol
server-side, and a one-paragraph thesis is enough (see `webapp/README.md`).

1. Read `CHALLENGE.md` — full protocol, scoring, scope facts, calibration
   advice, honesty asks. Don't skip.
2. Skim `EXAMPLE_hypothesis.md` for the spec format. The host's nine
   H1–H9 specs are public examples on the website; their predictions
   only unlock there after the participant has submitted, so don't go
   digging for them.
3. Pick a handle — alphanumeric, underscores or hyphens, ≤32 chars.
4. Draft `hypotheses/H<handle>.md` modelled on `EXAMPLE_hypothesis.md`.
   Section headers expected: statement, definitions, literature,
   operationalization, prerequisites, falsifiers. Writes to `hypotheses/`
   are allowed — the originals are git-tracked, so `git checkout` recovers
   anything overwritten.
5. Run `./scripts/generate.sh H<handle>`. This launches a headless
   subagent under the blinded protocol and writes
   `predictions/H<handle>/{logitz_plus.csv,logitz_minus.csv,method.md}`.
   The diagonal is excluded from scoring; the subagent may leave it
   blank.
6. Inspect outputs. Iterate on your spec and re-run with `--force` if
   needed. Honor system: cap yourself at 3 generation runs per
   hypothesis so the comparison with the locked H1–H9 stays fair.
7. Optional second tier: hand-edit
   `inputs/PREDICT_transfer_matrix_logitz_{plus,minus}.csv` and save into
   `predictions/H<handle>/` directly. A proper GUI is planned but not
   shipped — the CSV is the editing surface for now.
8. Post your handle (and optionally your spec) as a comment on the LW
   challenge post. Predictions stay on your disk until you share them or
   freeze hits.

## Hard rules

- Do not try to read `RESULTS/`. It's denied in `.claude/settings.json`
  and on the host's machine it's chmod-000 anyway. A clean "I couldn't
  predict X" always beats a fabricated number.
- Do not train new models or otherwise try to derive the observed
  matrices empirically. Static analysis of the train/test eval sets and
  poking at the base model with the elicitation prompts is fine.
- Do not edit `BLINDED_PROMPT.md`, the eval data in `inputs/`, or any
  other participant's `predictions/H<other>/`. The deny rules enforce
  this.

## When in doubt

Ask the human which of the steps above they want help with. Don't run
`./scripts/generate.sh` for them unsolicited — that burns a Claude Code
generation and they may want to revise the spec first.
