# Performance

## Frontend (GitHub Pages)

- Vite code splitting; lazy-load heavy views in Phase 9
- Supabase queries: limit columns, paginate job lists
- Cache static assets via GitHub Pages CDN

## Scanners

- Parallel scanner execution (future — Phase 5)
- HTTP timeout: 10s default
- Deduplicate before AI scoring to reduce CPU
- Limit per source: `limit_per_source` in `ScannerEngine.run()`

## Database

Indexes (see migration):

- `idx_jobs_score`, `idx_jobs_status`, `idx_jobs_posted_at`
- FK indexes on `job_id` columns

## AI pipeline (Phase 6+)

- Run HF models on GitHub Actions runner — batch scoring
- Cache embeddings where possible
- Stream large job descriptions before tokenization

## Memory

- Do not load full job corpus into memory in dashboard
- Scanner: process jobs incrementally in pipeline loop
- JSON fallback: read/write full file (acceptable for dev only)

## Large datasets

- Pagination API in Phase 8
- Supabase `.range()` for dashboard queries
- Archive rejected jobs (Phase 11)
