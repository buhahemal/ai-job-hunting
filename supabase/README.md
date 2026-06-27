# Supabase

Managed Postgres + REST API for AI Job Hunter (Phase 3+). **No self-hosted database.**

## Layout

```text
supabase/
  config.toml          # Local CLI config (optional)
  migrations/          # Versioned SQL schema
  seed.sql             # Local dev seed
```

## Apply migrations

```bash
supabase link --project-ref YOUR_REF
supabase db push
```

See [docs/phases/phase-03-database-supabase/SETUP.md](../docs/phases/phase-03-database-supabase/SETUP.md).
