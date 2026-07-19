#!/usr/bin/env bash
# Apply supabase/migrations/*.sql to hosted Supabase via psql.
# Requires SUPABASE_DB_PASSWORD in .env (Project Settings → Database).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

PROJECT_REF="${SUPABASE_PROJECT_REF:-}"
if [[ -z "$PROJECT_REF" && -n "${SUPABASE_URL:-}" ]]; then
  PROJECT_REF="$(python3 - <<'PY'
import os
from urllib.parse import urlparse
host = urlparse(os.environ.get("SUPABASE_URL", "")).hostname or ""
print(host.split(".")[0] if host else "")
PY
)"
fi

if [[ -z "${SUPABASE_DB_PASSWORD:-}" ]]; then
  echo "Missing SUPABASE_DB_PASSWORD in .env" >&2
  echo "Get it from: Supabase Dashboard → Project Settings → Database → Database password" >&2
  echo "(Reset password if you no longer have it, then put it in .env as SUPABASE_DB_PASSWORD=...)" >&2
  exit 1
fi

if [[ -z "$PROJECT_REF" ]]; then
  echo "Could not determine project ref from SUPABASE_URL." >&2
  exit 1
fi

# Direct Postgres host (not pooler) — required for DDL / migrations.
DB_HOST="db.${PROJECT_REF}.supabase.co"
DB_URL="postgresql://postgres:${SUPABASE_DB_PASSWORD}@${DB_HOST}:5432/postgres"

echo "Connecting to ${DB_HOST} ..."
export PGPASSWORD="$SUPABASE_DB_PASSWORD"

for f in supabase/migrations/*.sql; do
  echo "→ Applying $(basename "$f")"
  psql "$DB_URL" -v ON_ERROR_STOP=1 -f "$f"
done

if [[ -f supabase/seed.sql ]]; then
  echo "→ Applying seed.sql"
  psql "$DB_URL" -v ON_ERROR_STOP=1 -f supabase/seed.sql
fi

echo "Migrations applied successfully."
