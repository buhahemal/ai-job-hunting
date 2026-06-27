# Per-source job discovery plugins

Each scanner lives in its own folder and implements `discover_jobs()`, `normalize()`, and `health_check()` via `packages/scanner_sdk`.

| Folder             | Source                   | Config (comma-separated)                                 | Subscription |
| ------------------ | ------------------------ | -------------------------------------------------------- | ------------ |
| `greenhouse/`      | Greenhouse Job Board API | `GREENHOUSE_BOARD_TOKENS`                                | None         |
| `lever/`           | Lever postings API       | `LEVER_COMPANY_SITES`                                    | None         |
| `smartrecruiters/` | SmartRecruiters API      | `SMARTRECRUITERS_COMPANIES`                              | None         |
| `teamtailor/`      | Teamtailor jobs.json     | `TEAMTAILOR_COMPANY_SLUGS`                               | None         |
| `workable/`        | Workable widget API      | `WORKABLE_ACCOUNT_SLUGS`                                 | None         |
| `remoteok/`        | RemoteOK JSON API        | None                                                     | None         |
| `weworkremotely/`  | We Work Remotely RSS     | None                                                     | None         |
| `company_pages/`   | Company career pages     | None (Google, Microsoft, EPAM, Globant, Datadog, Stripe) | None         |

Legacy: `GREENHOUSE_BOARD_TOKEN` (single board) is still supported.

Orchestration: `scraper/scanner_engine.py` via `get_registered_scanners()`.

Health checks: `npm run scanner:health`

## Example `.env`

```bash
GREENHOUSE_BOARD_TOKENS=stripe,figma
LEVER_COMPANY_SITES=netflix,spotify
SMARTRECRUITERS_COMPANIES=Visa,Square
TEAMTAILOR_COMPANY_SLUGS=spotify,klarna
WORKABLE_ACCOUNT_SLUGS=company-slug
```

Scanners with unset env vars skip discovery gracefully and report healthy in health checks.
