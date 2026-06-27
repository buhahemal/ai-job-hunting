# Phase 5 — Scanner Expansion

```yaml
status: complete
started: 2026-06-27
completed: 2026-06-27
```

## Deliverables

| Scanner              | Source               | Auth | Status     |
| -------------------- | -------------------- | ---- | ---------- |
| Arbeitnow            | JSON API             | None | complete   |
| RemoteOK             | JSON API             | None | complete   |
| We Work Remotely     | RSS                  | None | complete   |
| Greenhouse           | JSON API             | None | Phase 4    |
| Lever                | JSON API             | None | Phase 4    |
| SmartRecruiters      | JSON API             | None | Phase 4    |
| Teamtailor           | jobs.json            | None | Phase 4    |
| Workable             | widget API           | None | Phase 4    |
| Company career pages | configured targets   | None | Phase 4    |
| Ashby                | posting-api          | None | complete   |
| Workday              | CXS jobs API         | None | complete   |
| Wellfound            | **NEXT_DATA** Apollo | None | complete\* |

\* Wellfound has no public API. The scanner parses Apollo state from search pages when fetch succeeds. Server-side requests are often blocked (HTTP 403); leave `WELLFOUND_SEARCH_PATHS` unset unless you have a workaround.

## Per-scanner checklist

- [x] Implementation in `scanners/{name}/`
- [x] Normalization to canonical job schema
- [x] Deduplication keys (`source` + external id in normalized `id`)
- [x] Unit tests with fixture JSON (Wellfound Apollo fixture)
- [x] Health check via `scripts/scanner_health.py` (registry-driven)
- [x] README with rate limits and attribution notes
- [x] RemoteOK attribution on dashboard (Scan Insights)

## Configuration

See `.env.example` and `scanners/README.md`:

- `ASHBY_JOB_BOARD_SLUGS` — board slug from `jobs.ashbyhq.com/{slug}`
- `WORKDAY_CAREER_SITES` — `tenant:wd5:SiteName` or full career URL
- `WELLFOUND_SEARCH_PATHS` — path segments, e.g. `role/l/remote`

## Quality gate

- [x] All registered scanners pass health checks when env vars unset (graceful skip)
- [x] Cron pipeline ingests from enabled sources without duplicate explosion (existing dedupe in scanner engine)

## Next phase

→ [Phase 6: AI Pipeline](../phase-06-ai-pipeline/)
