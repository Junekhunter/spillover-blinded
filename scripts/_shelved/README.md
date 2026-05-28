# Shelved scripts

These were built for a server-side ingestion path (form → host machine →
`generate.sh`) that we abandoned in favor of having participants clone
the repo and run the pipeline themselves locally.

- `ingest_form.py` — read `submissions/inbox.jsonl`, validate, land
  hypothesis specs into `hypotheses/H<handle>.md` and hand-tuned CSVs
  into `predictions/H<handle>/`. Enforced a per-handle submission cap.
- `lw_cron.sh` — nightly wrapper: ingest → `generate.sh` → write
  per-handle status under `submissions/status/`.

Kept around in case we later open a non-Claude-Code submission channel
(email, web form, whatever) for participants who can't run the pipeline
locally.
