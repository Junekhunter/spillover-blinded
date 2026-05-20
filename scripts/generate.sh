#!/usr/bin/env bash
# generate.sh — run blinded prediction for each hypothesis in an isolated
# headless Claude Code process. Each invocation has its own context; the
# only shared state is the filesystem, which the permission layer + the
# OS-level RESULTS lockout constrain.
#
# Usage:  ./scripts/generate.sh            # all hypotheses
#         ./scripts/generate.sh H5 H7b     # a subset
set -euo pipefail
cd "$(dirname "$0")/.."

HYPS=("$@")
if [ ${#HYPS[@]} -eq 0 ]; then
  HYPS=(H1 H2 H3 H4 H5 H6 H7a H7b H9)
fi

# Refuse to run if RESULTS is readable by this user — blinding precondition.
if [ -n "$(find ./RESULTS -type f ! -name '.gitkeep' 2>/dev/null)" ]; then
  if [ -r "$(find ./RESULTS -type f ! -name '.gitkeep' | head -1)" ]; then
    echo "ABORT: RESULTS/ contains readable files. Lock it before generating."
    echo "See README 'OS-level blinding'. Generation must run blind."
    exit 1
  fi
fi

for H in "${HYPS[@]}"; do
  if [ ! -f "./hypotheses/${H}.md" ]; then
    echo "SKIP ${H}: ./hypotheses/${H}.md not found."
    continue
  fi
  echo "=== generating ${H} ==="
  mkdir -p "./predictions/${H}"
  claude -p "Run the hypothesis-predictor agent for hypothesis ${H}. \
Read ./BLINDED_PROMPT.md and ./hypotheses/${H}.md. Follow the protocol \
exactly: Turn 1 inspection first, then Turn 2 generation. Write outputs \
ONLY to ./predictions/${H}/. You may not read ./RESULTS or any other \
hypothesis's predictions." \
    --append-system-prompt "$(cat ./BLINDED_PROMPT.md)" \
    > "./logs/${H}.log" 2>&1 || echo "  ${H} exited non-zero — check logs/${H}.log"

  if [ -f "./predictions/${H}/NEEDS_CLARIFICATION.md" ]; then
    echo "  ${H} needs clarification — see predictions/${H}/NEEDS_CLARIFICATION.md"
  fi
done

echo
echo "Done. Review logs/ and any NEEDS_CLARIFICATION.md files."
echo "When predictions look complete, run ./scripts/freeze.sh"
