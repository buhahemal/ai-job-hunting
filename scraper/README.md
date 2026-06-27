# Scraper

Python job scan pipeline — orchestrates `scanners/` plugins and writes to `apps/api/data/data.json`.

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

## Configuration

| Variable         | Required | Description                                             |
| ---------------- | -------- | ------------------------------------------------------- |
| `GEMINI_API_KEY` | No       | Enables AI scoring; replaced by Hugging Face in Phase 6 |

Paths: `packages/config/python/paths.py`

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).
