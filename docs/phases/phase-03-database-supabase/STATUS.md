# Phase 3 — Database + Supabase Schema

```yaml
status: done
started: 2026-06-27
completed: 2026-06-27
```

## Deliverables

- [x] Supabase free-tier project setup documented ([SETUP.md](./SETUP.md))
- [x] `supabase/migrations/` — jobs, resumes, applications, companies, profiles, interviews
- [x] Indexes on `(source, external_id)`, `score`, `status`, `posted_at`
- [x] Row Level Security (RLS) policies
- [x] Seed data for development (`supabase/seed.sql`)
- [x] ER diagram ([ER.md](./ER.md))
- [x] `packages/database/` — typed Python + TypeScript clients
- [x] Scraper writes to Supabase when secrets configured (`scanner-cron.yml`)
- [x] JSON fallback when Supabase secrets missing (`USE_JSON_STORE`)
- [x] Dashboard Supabase mode (`VITE_USE_SUPABASE` + `deploy-pages.yml`)
- [x] Database unit tests (`packages/database/tests/`)
- [x] GitHub Secrets documented: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_ANON_KEY`

## Quality gate

- [x] Migrations in repo (`supabase db push` ready)
- [x] RLS policies defined for anon + service role pattern
- [x] Still ₹0 — Supabase free tier only
- [x] CI passes with JSON fallback tests

## Manual step (you)

Create Supabase project and add GitHub Secrets — see [SETUP.md](./SETUP.md).

## Next phase

→ [Phase 4: Scanner SDK + Greenhouse](../phase-04-scanner-sdk-greenhouse/)
