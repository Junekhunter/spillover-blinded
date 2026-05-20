#!/usr/bin/env bash
# freeze.sh — commit and tag all predictions BEFORE results are unblinded.
# The git tag is the audit trail proving predictions predated unblinding.
set -euo pipefail
cd "$(dirname "$0")/.."

# Refuse to freeze if RESULTS is already populated + readable: that would
# mean predictions and results coexisted, defeating the audit trail.
RES_FILES="$(find ./RESULTS -type f ! -name '.gitkeep' 2>/dev/null || true)"
if [ -n "$RES_FILES" ]; then
  echo "WARNING: RESULTS/ is already populated."
  echo "Freeze should happen BEFORE results are placed. Continue anyway? [y/N]"
  read -r ans
  [ "$ans" = "y" ] || { echo "Aborted."; exit 1; }
fi

# Every hypothesis with a directory must have both matrices, or flag it.
MISSING=0
for d in ./predictions/*/; do
  H="$(basename "$d")"
  [ "$H" = ".gitkeep" ] && continue
  for f in logitz_plus.csv logitz_minus.csv; do
    if [ ! -f "${d}${f}" ]; then
      echo "MISSING: ${d}${f}"
      MISSING=1
    fi
  done
done
if [ "$MISSING" -ne 0 ]; then
  echo "Some predictions are incomplete. Freeze anyway? [y/N]"
  read -r ans
  [ "$ans" = "y" ] || { echo "Aborted."; exit 1; }
fi

TAG="frozen-$(date -u +%Y%m%dT%H%M%SZ)"
git add predictions/ hypotheses/ inputs/ BLINDED_PROMPT.md .claude/
git commit -m "Freeze blinded predictions: ${TAG}"
git tag -a "$TAG" -m "Predictions frozen pre-unblind at ${TAG}"
echo
echo "Frozen and tagged: ${TAG}"
echo "Predictions are now immutable. Place observed matrices in RESULTS/,"
echo "grant the scorer read access, and run ./scripts/score.py"
