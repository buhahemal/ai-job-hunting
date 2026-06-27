# API (Flask)

Local REST API and JSON datastore for development.

## Commands

```bash
pip install -r apps/api/requirements.txt
pip install -r scraper/requirements.txt
PYTHONPATH=. python3 apps/api/server.py
```

Or from repo root: `npm run dev:api`

Serves API on port 3000 and built dashboard from `apps/dashboard/dist/` when available.

## Data

Canonical store: `apps/api/data/data.json` (see `packages/config` for path constants).

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).
