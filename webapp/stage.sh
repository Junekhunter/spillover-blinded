#!/usr/bin/env bash
# stage.sh <out_dir> — copy ONLY the blinding-safe files into a clean Docker
# build context. Deploy from <out_dir>, never from the repo root, so that
# RESULTS/, predictions/ and hypotheses/ are never uploaded anywhere. The H1–H9
# baselines are read from the host's forecast bundle outside the repo
# ($BASELINE_BUNDLE; see build_baselines.py).
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${1:?usage: webapp/stage.sh <out_dir>}"
rm -rf "$OUT" && mkdir -p "$OUT/webapp"
cp -R inputs "$OUT/inputs"
cp BLINDED_PROMPT.md EXAMPLE_hypothesis.md "$OUT/"
cp webapp/*.py webapp/requirements.txt webapp/Dockerfile "$OUT/webapp/"
mkdir -p "$OUT/webapp/static"
cp webapp/static/index.html webapp/static/app.js webapp/static/style.css webapp/static/fig_overview.svg "$OUT/webapp/static/"
cp webapp/Dockerfile "$OUT/Dockerfile"
# Host's H1–H9 specs + frozen predictions, read from the forecast bundle (never committed as a file).
python3 webapp/build_baselines.py "$OUT/webapp/baselines.json"
echo "staged build context in $OUT"
