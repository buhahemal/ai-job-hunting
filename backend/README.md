# Backend API

Flask REST API and JSON datastore for local development.

## Commands

```bash
pip install -r backend/requirements.txt
pip install -r scraper/requirements.txt
PYTHONPATH=. python3 backend/server.py
```

Serves API on port 3000 and built frontend from `frontend/dist/` when available.

## Data

Canonical store: `backend/data/data.json`

## Known Limitations

- Not deployed to production; GitHub Pages uses static JSON + localStorage.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).
