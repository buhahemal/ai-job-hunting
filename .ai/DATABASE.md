# Database

## Platform

Managed **Supabase** (Postgres + REST + RLS). No self-hosted database.

## Schema

Migration: `supabase/migrations/0001_init_schema.sql`

| Table          | Purpose                              |
| -------------- | ------------------------------------ |
| `profiles`     | User profile JSON (`id = 'default'`) |
| `jobs`         | Scanned and scored jobs              |
| `interviews`   | Interview tracking                   |
| `applications` | Application history                  |
| `companies`    | Company scan metadata                |
| `resumes`      | Resume versions (Phase 7)            |

## Clients

| Runtime              | Package                     | Role                 |
| -------------------- | --------------------------- | -------------------- |
| Python pipeline      | `packages/database/python/` | Service role upserts |
| TypeScript dashboard | `packages/database/src/`    | Anon client + RLS    |

## RLS

- **anon key** (GitHub Pages): SELECT/INSERT/UPDATE on personal dashboard tables
- **service role** (GitHub Actions): bypasses RLS for pipeline writes

## Rules

- Migrations must be idempotent and documented
- Indexes on filtered/sorted columns (`score`, `status`, `posted_at`)
- Foreign keys with `ON DELETE CASCADE` where appropriate
- Never expose service role key to frontend

Setup: [`docs/phases/phase-03-database-supabase/SETUP.md`](../docs/phases/phase-03-database-supabase/SETUP.md)

ER diagram: [`docs/phases/phase-03-database-supabase/ER.md`](../docs/phases/phase-03-database-supabase/ER.md)
