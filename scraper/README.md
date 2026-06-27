# Scraper

Python job scan pipeline — orchestrates `scanners/` plugins, scores matches via `packages/ai_engine`, and writes to Supabase or `apps/api/data/data.json`.

Run locally or via GitHub Actions (`scanner-cron.yml`).

## Commands

```bash
pip install -r scraper/requirements.txt
PYTHONPATH=. python3 -m scraper
PYTHONPATH=. python3 -m unittest discover -s scraper/tests
PYTHONPATH=. python3 scripts/scanner_health.py
```

Or from repo root: `npm run scan`

## Scanner plugins

Individual sources live in [`../scanners/`](../scanners/). The pipeline engine is `scraper/scanner_engine.py`.

Every plugin implements:

- `discover_jobs(limit)`
- `normalize(raw_job)`
- `health_check()`

## Match scoring

Scoring is handled by [`../packages/ai_engine/`](../packages/ai_engine/) with this fallback chain:

1. Local embeddings (`all-MiniLM-L6-v2`, CPU, no API key)
2. Optional Gemini when `GEMINI_API_KEY` is set
3. Deterministic heuristic scorer

## Policy constants (single source of truth)

Default scanner and match thresholds live in **`packages/database/python/constants.py`** (TypeScript mirror: **`packages/database/src/constants.ts`**). Change values there first; env vars below override at runtime only.

The scanner only **promotes jobs with match score above 90%** to the Job Leads pipeline (`jobs` table) and tries to collect **at least 3 qualifying jobs** per run by scanning multiple portals.

Every evaluated job — including sub-threshold rejects — is persisted as a **Scan Insight** in `scanned_jobs` (Supabase) or `scannedJobs[]` (JSON). The dashboard **Scan Insights** tab surfaces these records for transparency and skill-gap analytics; **Job Leads** remains the actionable apply/tailor pipeline.

| Layer         | Storage                     | Purpose                                             |
| ------------- | --------------------------- | --------------------------------------------------- |
| Job Leads     | `jobs` + `job_match_scores` | Score > 90% — apply, tailor, track                  |
| Scan Insights | `scanned_jobs`              | All evaluated jobs — market visibility + skill gaps |

## Configuration

| Variable                          | Required | Description                                               |
| --------------------------------- | -------- | --------------------------------------------------------- |
| `HF_HOME`                         | No       | Hugging Face model cache (default `~/.cache/huggingface`) |
| `AI_SCORER`                       | No       | `embedding` (default), `gemini`, or `heuristic`           |
| `GEMINI_API_KEY`                  | No       | Optional Gemini fallback when embedding fails             |
| `SCANNER_MIN_MATCH_SCORE`         | No       | Minimum match threshold (default `90`)                    |
| `SCANNER_MIN_JOBS_PER_RUN`        | No       | Target jobs per scan (default `3`)                        |
| `SCANNER_MAX_PASSES`              | No       | Pass safety cap; `0` = scan until exhausted (default `0`) |
| `SCANNER_LIMIT_STEP`              | No       | Increase per-source fetch limit each pass (default `50`)  |
| `SCANNER_MAX_LIMIT_PER_SOURCE`    | No       | Cap jobs fetched per source per pass (default `2000`)     |
| `SCANNER_MAX_EVALUATIONS`         | No       | Max unique jobs to score per run (default `3000`)         |
| `SCANNER_SCAN_INSIGHT_BATCH_SIZE` | No       | Scan insight upsert batch size (default `10`)             |
| `HF_TOKEN`                        | No       | Optional Hugging Face token for faster model downloads    |

Discovery keeps increasing fetch limits and re-scanning all sources until every unique job is scored, the target is met, or evaluation limits are hit. Evaluated jobs are upserted to `scanned_jobs` / `scannedJobs[]` in batches of 10 (configurable via `SCANNER_SCAN_INSIGHT_BATCH_SIZE`), with a final flush for any remainder, so Scan Insights updates during long runs without one row per network call. Jobs already evaluated in prior runs are skipped via a persistent `scannedJobs[]` / `scannedJobKeys` registry (JSON) or `scanned_jobs` table (Supabase). Apply migration `0004_scanned_job_insights.sql` before using Scan Insights. GitHub Actions `scanner-cron` uses a **60-minute** timeout.

Paths: `packages/config/python/paths.py`

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).
