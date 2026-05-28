#!/usr/bin/env bash
# build_lw_bundle.sh — produces spillover-challenge.zip for LessWrong release.
#
# Includes: inputs/, hypotheses/H*.md (specs only), templates/, CHALLENGE.md,
# EXAMPLE_hypothesis.md.
#
# Excludes: predictions/, RESULTS/, logitz_leaderboard.csv,
# theta_leaderboard.csv, hypothesis_comparisons.csv, logs/.
#
# Aborts if RESULTS/ contains readable files (mirrors generate.sh guard) — the
# bundle must never ship with observed matrices visible.
set -euo pipefail
cd "$(dirname "$0")/.."

OUT="spillover-challenge.zip"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# RESULTS leakage guard.
if [ -n "$(find ./RESULTS -type f ! -name '.gitkeep' 2>/dev/null)" ]; then
  if [ -r "$(find ./RESULTS -type f ! -name '.gitkeep' | head -1)" ]; then
    echo "ABORT: RESULTS/ contains readable files. Refusing to build bundle."
    exit 1
  fi
fi

# Required pieces.
for f in CHALLENGE.md EXAMPLE_hypothesis.md inputs hypotheses; do
  if [ ! -e "$f" ]; then
    echo "ABORT: missing $f"; exit 1
  fi
done

mkdir -p "$STAGE/spillover-challenge"
ROOT="$STAGE/spillover-challenge"

cp CHALLENGE.md EXAMPLE_hypothesis.md "$ROOT/"

# Inputs verbatim.
cp -r inputs "$ROOT/inputs"

# Hypothesis specs only — no predictions/, no method.md, no falsifiers.md
# (those live under predictions/, which we don't ship).
mkdir -p "$ROOT/hypotheses"
cp hypotheses/H*.md "$ROOT/hypotheses/"

# Templates for the hand-tuned tier.
mkdir -p "$ROOT/templates"
cp inputs/PREDICT_transfer_matrix_logitz_plus.csv "$ROOT/templates/"
cp inputs/PREDICT_transfer_matrix_logitz_minus.csv "$ROOT/templates/"

# Sanity: no leaked observed/score artifacts.
LEAK="$(find "$ROOT" \( \
  -name 'observed_*.csv' -o \
  -name 'logitz_leaderboard.csv' -o \
  -name 'theta_leaderboard.csv' -o \
  -name 'hypothesis_comparisons.csv' -o \
  -name 'method.md' -o \
  -name 'falsifiers.md' \
\) -print)"
if [ -n "$LEAK" ]; then
  echo "ABORT: leak detected in bundle staging:"
  echo "$LEAK"
  exit 1
fi

(cd "$STAGE" && zip -qr "$OLDPWD/$OUT" spillover-challenge)
echo "Wrote $OUT"
unzip -l "$OUT" | tail -20
