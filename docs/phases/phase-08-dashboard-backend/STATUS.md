# Phase 8 — Dashboard Backend

```yaml
status: in_progress
started: 2026-06-27
completed:
last_updated: 2026-06-27
```

## Built

- [x] `apps/api/` Flask API with Supabase-backed `JobRepository`
- [x] Profile GET/POST with validation and LaTeX regeneration on save
- [x] Profile JSON import (`POST /api/profile/import`)
- [x] Job tailor + publish PDF (`POST /api/jobs/:id/tailor`)
- [x] List resume versions (`GET /api/jobs/:id/resumes`)
- [x] Scan pipeline trigger (`POST /api/jobs/scan`)
- [x] Scan Insights rescan (`POST /api/scan-insights/rescan`)
- [x] Promote scanned job (`POST /api/scan-insights/:key/promote`)
- [x] Custom job import with enrichment (`POST /api/jobs/add-custom`)
- [x] Job status, notes, tailored save endpoints (partial CRUD)
- [x] Interview list/add/status endpoints (partial)
- [x] Input validation via `profile_service.py` (profile payloads)
- [x] Seed-if-empty profile sync (`scripts/sync_profile_to_supabase.py`)

## Pending

- [ ] Full Supabase read path audit (no static JSON in production)
- [ ] Applications CRUD API
- [ ] Search, filter, pagination REST endpoints
- [ ] OpenAPI documentation in `docs/api/`
- [ ] Supabase Auth for personal dashboard
- [ ] Rate limiting on mutations
- [ ] Optional Supabase Edge Functions
- [ ] API integration tests against Supabase test project

## Hosting note

Primary UI reads Supabase directly from GitHub Pages (anon key + RLS). Backend API is required for tailor, profile import, rescan, and PDF compile.

## Quality gate

- [x] Profile + import unit tests (`apps/api/tests/test_profile_service.py`)
- [ ] OpenAPI spec published
- [ ] Integration tests against Supabase

## Next phase

→ [Phase 9: Dashboard Frontend](../phase-09-dashboard-frontend/)
