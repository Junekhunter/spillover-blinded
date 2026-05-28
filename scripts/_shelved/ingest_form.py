#!/usr/bin/env python3
"""ingest_form.py — pull LW challenge form responses and land them in the repo.

Reads a JSONL file of form submissions (one JSON object per line) from
./submissions/inbox.jsonl. Each record has:

    {
      "handle": "alice",                       # required, [A-Za-z0-9_-]{1,32}
      "email": "alice@example.com",            # optional
      "tier": "hypothesis" | "handtuned" | "both",   # required
      "hypothesis_md": "...spec text...",      # required if tier in {hypothesis,both}
      "logitz_plus_csv": "...csv text...",     # required if tier in {handtuned,both}
      "logitz_minus_csv": "...csv text...",    # required if tier in {handtuned,both}
      "note": "...",                           # optional
      "disclosure": "...",                     # required
      "submitted_at": "2026-05-21T12:00:00Z",  # required
    }

Outputs:
- hypothesis-tier: hypotheses/H<handle>.md + predictions/H<handle>/_meta.json
- hand-tuned tier: predictions/H<handle>/{logitz_plus.csv, logitz_minus.csv}
- malformed submissions: predictions/_quarantine/<handle>/{raw.json, reason.txt}

Idempotent: re-running with the same inbox is a no-op unless the submission's
submitted_at is newer than what's already on disk. Per-handle submission cap
of 3 enforced; further submissions go to quarantine with reason "cap-exceeded".
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "submissions" / "inbox.jsonl"
HYPS = ROOT / "hypotheses"
PREDS = ROOT / "predictions"
QUAR = PREDS / "_quarantine"
PLUS_TPL = ROOT / "inputs" / "PREDICT_transfer_matrix_logitz_plus.csv"
MINUS_TPL = ROOT / "inputs" / "PREDICT_transfer_matrix_logitz_minus.csv"

HANDLE_RE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
MAX_SUBMISSIONS_PER_HANDLE = 3


def template_shape(path: Path) -> tuple[list[str], list[str]]:
    with path.open() as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [r[0] for r in reader if r]
    return header, rows


def validate_csv(text: str, expected_header: list[str], expected_rows: list[str]) -> str | None:
    try:
        reader = csv.reader(io.StringIO(text))
        header = next(reader)
        rows = list(reader)
    except Exception as e:
        return f"unparseable csv: {e}"
    if header != expected_header:
        return f"header mismatch (got {len(header)} cols, expected {len(expected_header)})"
    got_labels = [r[0] for r in rows if r]
    if got_labels != expected_rows:
        return f"row-label mismatch (got {len(got_labels)} rows, expected {len(expected_rows)})"
    return None


def quarantine(handle: str, raw: dict, reason: str) -> None:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", handle)[:32] or "_unnamed"
    d = QUAR / safe
    d.mkdir(parents=True, exist_ok=True)
    (d / "raw.json").write_text(json.dumps(raw, indent=2))
    (d / "reason.txt").write_text(reason + "\n")


def submission_count(handle: str) -> int:
    meta = PREDS / f"H{handle}" / "_meta.json"
    if not meta.exists():
        return 0
    try:
        return int(json.loads(meta.read_text()).get("submission_count", 0))
    except Exception:
        return 0


def existing_submitted_at(handle: str) -> str | None:
    meta = PREDS / f"H{handle}" / "_meta.json"
    if not meta.exists():
        return None
    try:
        return json.loads(meta.read_text()).get("submitted_at")
    except Exception:
        return None


def process(sub: dict, plus_shape, minus_shape) -> tuple[bool, str]:
    handle = (sub.get("handle") or "").strip()
    if not HANDLE_RE.match(handle):
        quarantine(handle or "_unnamed", sub, f"bad handle: {handle!r}")
        return False, "bad handle"

    tier = sub.get("tier")
    if tier not in {"hypothesis", "handtuned", "both"}:
        quarantine(handle, sub, f"bad tier: {tier!r}")
        return False, "bad tier"

    if not sub.get("disclosure"):
        quarantine(handle, sub, "missing disclosure")
        return False, "missing disclosure"

    submitted_at = sub.get("submitted_at") or ""
    prev = existing_submitted_at(handle)
    if prev and submitted_at <= prev:
        return False, "stale (older than existing submission)"

    count = submission_count(handle)
    if count >= MAX_SUBMISSIONS_PER_HANDLE:
        quarantine(handle, sub, f"cap-exceeded ({count} prior submissions)")
        return False, "cap exceeded"

    pred_dir = PREDS / f"H{handle}"
    pred_dir.mkdir(parents=True, exist_ok=True)

    if tier in {"hypothesis", "both"}:
        body = sub.get("hypothesis_md", "").strip()
        if len(body) < 200:
            quarantine(handle, sub, f"hypothesis_md too short ({len(body)} chars)")
            return False, "hypothesis too short"
        (HYPS / f"H{handle}.md").write_text(body + "\n")

    if tier in {"handtuned", "both"}:
        plus = sub.get("logitz_plus_csv", "")
        minus = sub.get("logitz_minus_csv", "")
        err = validate_csv(plus, *plus_shape) or validate_csv(minus, *minus_shape)
        if err:
            quarantine(handle, sub, f"csv validation failed: {err}")
            return False, f"csv invalid: {err}"
        (pred_dir / "logitz_plus.csv").write_text(plus)
        (pred_dir / "logitz_minus.csv").write_text(minus)

    meta = {
        "handle": handle,
        "email": sub.get("email"),
        "tier": tier,
        "note": sub.get("note"),
        "disclosure": sub.get("disclosure"),
        "submitted_at": submitted_at,
        "submission_count": count + 1,
    }
    (pred_dir / "_meta.json").write_text(json.dumps(meta, indent=2))
    return True, "ok"


def main() -> int:
    if not INBOX.exists():
        print(f"no inbox at {INBOX}; nothing to do")
        return 0
    plus_shape = template_shape(PLUS_TPL)
    minus_shape = template_shape(MINUS_TPL)
    n_ok = n_skip = n_bad = 0
    for line in INBOX.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            sub = json.loads(line)
        except Exception as e:
            print(f"bad line, skipping: {e}")
            n_bad += 1
            continue
        ok, msg = process(sub, plus_shape, minus_shape)
        handle = sub.get("handle", "?")
        if ok:
            print(f"  H{handle}: ingested ({msg})")
            n_ok += 1
        else:
            print(f"  H{handle}: {msg}")
            if "stale" in msg:
                n_skip += 1
            else:
                n_bad += 1
    print(f"done. ingested={n_ok} skipped={n_skip} bad={n_bad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
