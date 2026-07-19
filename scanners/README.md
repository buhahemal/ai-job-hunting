# Per-source job discovery plugins

Each scanner lives in its own folder and implements `discover_jobs()`, `normalize()`, and `health_check()` via `packages/scanner_sdk`.

| Folder             | Source                   | Config (comma-separated)                                 | Subscription |
| ------------------ | ------------------------ | -------------------------------------------------------- | ------------ |
| `greenhouse/`      | Greenhouse Job Board API | `GREENHOUSE_BOARD_TOKENS`                                | None         |
| `lever/`           | Lever postings API       | `LEVER_COMPANY_SITES`                                    | None         |
| `smartrecruiters/` | SmartRecruiters API      | `SMARTRECRUITERS_COMPANIES`                              | None         |
| `teamtailor/`      | Teamtailor jobs.json     | `TEAMTAILOR_COMPANY_SLUGS`                               | None         |
| `workable/`        | Workable widget API      | `WORKABLE_ACCOUNT_SLUGS`                                 | None         |
| `remoteok/`        | RemoteOK JSON API        | None (attribution required on dashboard)                 | None         |
| `remotive/`        | Remotive public API      | None                                                     | None         |
| `weworkremotely/`  | We Work Remotely RSS     | None                                                     | None         |
| `hackernews/`      | HN Who is Hiring         | None (Algolia public API)                                | None         |
| `company_pages/`   | Company career pages     | None (Google, Microsoft, EPAM, Globant, Datadog, Stripe) | None         |
| `ashby/`           | Ashby posting API        | `ASHBY_JOB_BOARD_SLUGS`                                  | None         |
| `workday/`         | Workday CXS jobs API     | `WORKDAY_CAREER_SITES`                                   | None         |
| `wellfound/`       | Wellfound search Apollo  | `WELLFOUND_SEARCH_PATHS`                                 | None         |

Legacy: `GREENHOUSE_BOARD_TOKEN` (single board) is still supported.

Set `ATS_DISCOVERY_ENABLED=true` to merge reviewed identifiers from
`scanners/ats-seeds.json` with explicitly configured Greenhouse, Lever, Workable,
and Ashby values. Explicit environment values always take precedence and are never
removed.

Orchestration: `scraper/scanner_engine.py` via `get_registered_scanners()`.

Health checks: `npm run scanner:health`

## Example `.env`

```bash
GREENHOUSE_BOARD_TOKENS=stripe,figma
LEVER_COMPANY_SITES=netflix,spotify
SMARTRECRUITERS_COMPANIES=Visa,Square
TEAMTAILOR_COMPANY_SLUGS=spotify,klarna
WORKABLE_ACCOUNT_SLUGS=company-slug
ASHBY_JOB_BOARD_SLUGS=Ashby,Linear
WORKDAY_CAREER_SITES=nvidia:wd5:NVIDIAExternalCareerSite
# Optional — often blocked server-side (HTTP 403)
WELLFOUND_SEARCH_PATHS=role/l/remote
```

Scanners with unset env vars skip discovery gracefully and report healthy in health checks.

## Attribution

- **RemoteOK**: When displaying RemoteOK listings, link to [remoteok.com](https://remoteok.com) (shown in dashboard Scan Insights).

## Rate limits

Public APIs are polled with a shared 10s timeout and scanner-engine rate limiting. Prefer modest `SCANNER_MAX_LIMIT_PER_SOURCE` values for Workday detail fetches (one extra GET per job for descriptions).
