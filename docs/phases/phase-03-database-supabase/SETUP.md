# Supabase Setup (one-time, manual)

Phase 3 uses **managed Supabase** — no servers you operate. GitHub remains the control plane.

## 1. Create project

1. Sign up at [supabase.com](https://supabase.com) (free tier).
2. Create a new project (choose a region close to you).
3. Wait for the database to provision.

## 2. Apply schema

From repo root (requires [Supabase CLI](https://supabase.com/docs/guides/cli)):

```bash
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
```

Or paste [`supabase/migrations/0001_init_schema.sql`](../../../supabase/migrations/0001_init_schema.sql) into the Supabase SQL Editor and run.

## 3. GitHub Secrets

Repository → Settings → Secrets and variables → Actions:

| Secret                 | Where to find                                          |
| ---------------------- | ------------------------------------------------------ |
| `SUPABASE_URL`         | Project Settings → API → Project URL                   |
| `SUPABASE_SERVICE_KEY` | Project Settings → API → `service_role` (never commit) |
| `SUPABASE_ANON_KEY`    | Project Settings → API → `anon` public                 |

## 4. Verify

```bash
export SUPABASE_URL=...
export SUPABASE_SERVICE_KEY=...
PYTHONPATH=. USE_JSON_STORE=false python3 -m scraper
```

Trigger **Scanner Cron** workflow manually in GitHub Actions.

## 5. GitHub Pages

`deploy-pages.yml` injects `VITE_USE_SUPABASE=true` and anon key at build time. After secrets are set, redeploy Pages.
