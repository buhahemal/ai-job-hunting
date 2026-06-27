# Scraper

Python job scanner pipeline run locally or via GitHub Actions (`scanner-cron.yml`).

## Commands

```bash
pip install -r scraper/requirements.txt
PYTHONPATH=. python3 -m scraper
PYTHONPATH=. python3 -m unittest discover -s scraper/tests
PYTHONPATH=. python3 scripts/scanner_health.py
```

## Scanner Interface

Every plugin implements:

- `discoverJobs(limit)`
- `normalize(raw_job)`
- `healthCheck()`

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | No | Enables AI scoring; falls back to heuristics |

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).
