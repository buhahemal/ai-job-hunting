# Per-source job discovery plugins

Each scanner lives in its own folder and implements `discover_jobs()`, `normalize()`, and `health_check()` via `packages/scanner_sdk`.

| Folder           | Source                         | Config                            |
| ---------------- | ------------------------------ | --------------------------------- |
| `arbeitnow/`     | Arbeitnow JSON API             | None                              |
| `company_pages/` | Target consultancy career URLs | None (synthetic high-signal data) |
| `greenhouse/`    | Greenhouse Job Board API       | `GREENHOUSE_BOARD_TOKEN` env      |

Orchestration: `scraper/scanner_engine.py` via `get_registered_scanners()`.

Health checks: `npm run scanner:health`
