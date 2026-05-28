#!/usr/bin/env bash
# lw_cron.sh — nightly LW-submission processing.
#
# 1. Ingest new form submissions from submissions/inbox.jsonl into
#    hypotheses/H<handle>.md and/or predictions/H<handle>/.
# 2. Run generate.sh, which globs hypotheses/H*.md and skips any with
#    up-to-date predictions (so hand-tuned submissions and the original
#    H1-H9 don't get regenerated unnecessarily).
# 3. Emit a per-handle status file under submissions/status/<handle>.json
#    describing what they should expect to see in their predictions/
#    bundle (or a NEEDS_CLARIFICATION pointer). Email delivery is left to
#    a separate hook reading this directory — keeps secrets out of git.
#
# Preconditions (same as generate.sh): RESULTS/ must be unreadable.
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p submissions/status

echo "=== ingesting form responses ==="
./scripts/ingest_form.py

echo "=== running generation pass ==="
./scripts/generate.sh

echo "=== writing per-handle status ==="
python3 - <<'PY'
import json
from pathlib import Path

root = Path('.')
status_dir = root / 'submissions' / 'status'
status_dir.mkdir(parents=True, exist_ok=True)

for meta_path in sorted((root / 'predictions').glob('H*/_meta.json')):
    meta = json.loads(meta_path.read_text())
    handle = meta['handle']
    pred_dir = meta_path.parent
    plus = pred_dir / 'logitz_plus.csv'
    minus = pred_dir / 'logitz_minus.csv'
    method = pred_dir / 'method.md'
    needs = pred_dir / 'NEEDS_CLARIFICATION.md'

    state = 'unknown'
    if needs.exists():
        state = 'needs_clarification'
    elif plus.exists() and minus.exists():
        state = 'ready'
    else:
        state = 'pending'

    out = {
        'handle': handle,
        'email': meta.get('email'),
        'tier': meta.get('tier'),
        'submission_count': meta.get('submission_count'),
        'submitted_at': meta.get('submitted_at'),
        'state': state,
        'has_method_md': method.exists(),
        'has_logitz_plus': plus.exists(),
        'has_logitz_minus': minus.exists(),
        'needs_clarification': needs.exists(),
    }
    (status_dir / f'{handle}.json').write_text(json.dumps(out, indent=2))
    print(f"  H{handle}: {state}")
PY

echo
echo "Done. Wire submissions/status/*.json into your mailer to notify submitters."
