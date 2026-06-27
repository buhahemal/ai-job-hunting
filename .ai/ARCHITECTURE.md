# Architecture

## System context

```text
GitHub Actions (control plane)
    ├── pipeline-cron.yml → scraper → HF embeddings → Supabase (service role)
    ├── deploy-pages.yml → dashboard → Supabase (anon + RLS)

Supabase (data plane)
    └── Postgres + REST + RLS

GitHub Pages (frontend)
    └── Static React dashboard
```

## Layers

| Layer    | Location                     | Responsibility                    |
| -------- | ---------------------------- | --------------------------------- |
| Apps     | `apps/dashboard`, `apps/api` | UI and local dev API              |
| Packages | `packages/*`                 | Shared SDKs and clients           |
| Scanners | `scanners/*`                 | Source-specific discovery         |
| Pipeline | `scraper/`                   | Orchestration, dedupe, AI scoring |
| Data     | `supabase/`                  | Schema, migrations, RLS           |

## Scanner plugin contract

Defined in `packages/scanner-sdk/python/base.py`:

- `discover_jobs(limit)` → raw records
- `normalize(raw)` → canonical job dict
- `health_check()` → bool

Registry: `get_registered_scanners()` in `packages/scanner-sdk/python/registry.py`

## Data stores

| Mode       | Trigger               | Storage                   |
| ---------- | --------------------- | ------------------------- |
| Production | Supabase secrets set  | Supabase Postgres         |
| Fallback   | `USE_JSON_STORE=true` | `apps/api/data/data.json` |

## Target package layout (future phases)

```text
packages/scanner-sdk/   ✅ Phase 4
packages/database/      ✅ Phase 3
packages/ai-engine/     ✅ Phase 6
packages/resume_engine/ Phase 7 (done)
packages/logger/        Phase 11
packages/common/        As needed
```

Full diagram: [`docs/architecture/overview.md`](../docs/architecture/overview.md)
