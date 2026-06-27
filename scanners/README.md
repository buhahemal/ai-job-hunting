# Scanners

Per-source job discovery plugins. Each scanner implements `discover_jobs()`, `normalize()`, and `health_check()`.

| Scanner            | Source                        |
| ------------------ | ----------------------------- |
| `arbeitnow.py`     | Arbeitnow JSON API            |
| `career_portal.py` | Configured career portal URLs |

Orchestration lives in `scraper/scanner_engine.py`.
