# Phase 4 — Scanner SDK + First Scanner (Greenhouse)

```yaml
status: pending
started:
completed:
```

## Deliverables

- [ ] `packages/scanner-sdk/` — abstract `IScanner` interface
- [ ] Required methods: `discover_jobs()`, `normalize()`, `health_check()`, `validate()`, `deduplicate()`
- [ ] Rate limiter, retry with backoff, structured logging
- [ ] `scanners/greenhouse/` — first production scanner
  - API: `https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`
  - Configurable company tokens via `packages/config/`
- [ ] Migrate existing `scraper/scrapers/arbeitnow.py` into `scanners/arbeitnow/`
- [ ] Unit tests + contract tests per scanner
- [ ] Integration test: discover → normalize → validate
- [ ] Write new jobs to Supabase (not JSON file)

## Rules

- Each scanner is **independent**, **retryable**, **observable**, **testable**
- No HTML scraping of blocked sites
- Health check must pass in `scanner-health.yml` before merge

## Quality gate

- [ ] Greenhouse scanner discovers real jobs in CI (mocked HTTP in unit tests; live in health workflow)
- [ ] Plugin registered in scanner registry
- [ ] Documentation in `scanners/greenhouse/README.md`

## Next phase

→ [Phase 5: Expand scanners](../phase-05-scanners-expansion/)
