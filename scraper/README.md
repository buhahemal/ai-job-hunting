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

The scanner only **persists jobs with match score above 75%** and tries to collect **at least 3 qualifying jobs** per run by scanning multiple portals.

## Configuration

| Variable                       | Required | Description                                               |
| ------------------------------ | -------- | --------------------------------------------------------- |
| `HF_HOME`                      | No       | Hugging Face model cache (default `~/.cache/huggingface`) |
| `AI_SCORER`                    | No       | `embedding` (default), `gemini`, or `heuristic`           |
| `GEMINI_API_KEY`               | No       | Optional Gemini fallback when embedding fails             |
| `SCANNER_MIN_MATCH_SCORE`      | No       | Minimum match threshold (default `75`)                    |
| `SCANNER_MIN_JOBS_PER_RUN`     | No       | Target jobs per scan (default `3`)                        |
| `SCANNER_MAX_PASSES`           | No       | Discovery passes across all sources (default `5`)         |
| `SCANNER_LIMIT_STEP`           | No       | Increase per-source fetch limit each pass (default `20`)  |
| `SCANNER_MAX_LIMIT_PER_SOURCE` | No       | Cap jobs fetched per source per pass (default `100`)      |
| `SCANNER_MAX_EVALUATIONS`      | No       | Max unique jobs to score per run (default `500`)          |

GitHub Actions `scanner-cron` job uses a **60-minute** timeout and runs multi-pass discovery until the target is met or limits are exhausted.

Paths: `packages/config/python/paths.py`

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).
