# Phase 3 — Database + Supabase Schema

```yaml
status: pending
started:
completed:
```

## Deliverables

- [ ] Supabase free-tier project
- [ ] `supabase/migrations/` — jobs, resumes, applications, companies, profiles
- [ ] Indexes on `(source, external_id)`, `score`, `status`, `posted_at`
- [ ] Row Level Security (RLS) policies
- [ ] Seed data for development
- [ ] ER diagram in this folder
- [ ] `packages/database/` — typed client + repository layer
- [ ] Replace `apps/api/data/data.json` as source of truth (migrate scraper writes)
- [ ] Database integration tests
- [ ] GitHub Secrets: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`

## Schema (from R&D)

See [deep-research-report.md §4](../../deep-research-report.md) — tables: `jobs`, `resumes`, `applications`, `companies`.

## Rules

- Migrations must be **reversible** and **idempotent**
- All writes from GitHub Actions use service role key
- Dashboard reads via anon key + RLS

## Quality gate

- [ ] Migrations apply cleanly via `supabase db push`
- [ ] RLS tested (insert via Actions, read via dashboard user)
- [ ] Still ₹0 — Supabase free tier only

## Next phase

→ [Phase 4: Scanner SDK + Greenhouse](../phase-04-scanner-sdk-greenhouse/)
