# Scanner SDK

Shared contracts and utilities for job source plugins.

## Scanner interface

Every scanner implements:

- `discover_jobs(limit)` — fetch raw listings
- `normalize(raw_job)` — map to canonical job schema
- `health_check()` — verify source reachability

## Registry

`get_registered_scanners()` returns all active plugins. Used by `scraper/scanner_engine.py` and `scripts/scanner_health.py`.

## Canonical job schema

```python
{
    "id": str,
    "title": str,
    "company": str,
    "location": str,
    "remoteType": "Remote" | "Hybrid" | "On-site",
    "source": str,
    "url": str,
    "description": str,
    "status": "New",
}
```

See `.ai/ARCHITECTURE.md` for pipeline integration.
