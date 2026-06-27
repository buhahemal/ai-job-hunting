# Phase 8 — Dashboard Backend

```yaml
status: in_progress
started: 2026-06-27
completed:
```

## Deliverables

- [x] `apps/api/` Flask API (Phase 2); evolve to Supabase-backed REST layer
- [ ] Read jobs, resumes, applications from Supabase (not static JSON)
- [x] Profile CRUD (GET/POST, import, validation, LaTeX regen on save)
- [ ] Job status updates, interview tracking (partial — existing endpoints)
- [ ] Search, filter, pagination
- [ ] Optional: Supabase Edge Functions for serverless API (still free tier)
- [ ] OpenAPI documentation in `docs/api/`
- [ ] Auth (Supabase Auth — free tier) for personal dashboard
- [ ] Rate limiting on mutations

## Hosting note

Primary UI reads Supabase directly from GitHub Pages (anon key + RLS). Backend API is optional for complex operations or local dev.

## Rules

- No Flask+json file as production datastore (Phase 3 replaces it)
- Validate all inputs; parameterized queries only

## Quality gate

- [ ] API integration tests against Supabase local or test project
- [ ] OpenAPI spec published

## Next phase

→ [Phase 9: Dashboard Frontend](../phase-09-dashboard-frontend/)
