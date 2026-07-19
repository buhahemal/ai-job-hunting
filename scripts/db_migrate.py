#!/usr/bin/env python3
"""
Generic Database Migration Runner for Supabase PostgreSQL.

Executes all pending SQL migrations in `supabase/migrations/*.sql` against your
production Supabase database.

Supports:
1. `SUPABASE_DB_URL` or `DATABASE_URL` (direct Postgres URL or connection string)
2. `SUPABASE_DB_PASSWORD` + `SUPABASE_URL` or `SUPABASE_PROJECT_REF`
3. `npx supabase db push` fallback
4. `--dry-run` flag to validate migrations without executing
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def get_db_url() -> str | None:
    """Resolve Postgres connection URL from environment variables."""
    direct_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")
    if direct_url:
        return direct_url

    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    supabase_url = os.getenv("SUPABASE_URL", "")
    project_ref = os.getenv("SUPABASE_PROJECT_REF")

    if not project_ref and supabase_url:
        hostname = urlparse(supabase_url).hostname or ""
        if hostname:
            project_ref = hostname.split(".")[0]

    if db_password and project_ref:
        return f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"

    return None


def run_psycopg2_migrations(db_url: str, dry_run: bool) -> bool:
    """Run migrations using psycopg2 driver."""
    try:
        import psycopg2
    except ImportError:
        return False

    migrations_dir = Path("supabase/migrations")
    sql_files = sorted(migrations_dir.glob("*.sql"))
    if not sql_files:
        print("[INFO] No migration files found in supabase/migrations/")
        return True

    print("[INFO] Connecting to Supabase PostgreSQL...")
    conn = psycopg2.connect(db_url)
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    filename TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """)
            cur.execute("SELECT filename FROM schema_migrations;")
            applied = {row[0] for row in cur.fetchall()}

        pending = [f for f in sql_files if f.name not in applied]
        if not pending:
            print("[INFO] All database migrations are up to date! 0 pending.")
            conn.close()
            return True

        print(f"[INFO] Found {len(pending)} pending migration(s):")
        for f in pending:
            print(f"  - {f.name}")

        if dry_run:
            print("[DRY-RUN] Dry run active. Skipping execution.")
            conn.close()
            return True

        for f in pending:
            print(f"[MIGRATE] Applying {f.name}...")
            content = f.read_text(encoding="utf-8")
            with conn.cursor() as cur:
                cur.execute(content)
                cur.execute("INSERT INTO schema_migrations (filename) VALUES (%s);", (f.name,))
            conn.commit()
            print(f"[OK] Applied {f.name}")

        print("[SUCCESS] All pending migrations executed successfully.")
        return True
    except Exception as exc:
        conn.rollback()
        print(f"[ERROR] Migration failed: {exc}", file=sys.stderr)
        raise
    finally:
        conn.close()


def run_supabase_cli_migrations(db_url: str, dry_run: bool) -> bool:
    """Run migrations using npx supabase CLI."""
    if dry_run:
        print("[DRY-RUN] Dry run active. Skipping npx supabase db push.")
        return True

    cmd = ["npx", "supabase", "db", "push", "--db-url", db_url]
    print(f"[INFO] Running Supabase CLI: {' '.join(cmd)}")
    res = subprocess.run(cmd)
    return res.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply Supabase database migrations")
    parser.add_argument("--dry-run", action="store_true", help="Validate pending migrations without applying")
    args = parser.parse_args()

    dry_run = args.dry_run or os.getenv("DRY_RUN", "").lower() in ("true", "1", "yes")
    db_url = get_db_url()

    if not db_url:
        print(
            "[ERROR] Missing database connection credentials.\n"
            "Provide one of the following in GitHub Secrets / .env:\n"
            "  - SUPABASE_DB_URL (e.g. postgresql://postgres:pass@db.ref.supabase.co:5432/postgres)\n"
            "  - SUPABASE_DB_PASSWORD + SUPABASE_URL (or SUPABASE_PROJECT_REF)",
            file=sys.stderr,
        )
        return 1

    print("[INFO] Starting generic database migration runner...")

    # Strategy 1: Try psycopg2 driver
    try:
        if run_psycopg2_migrations(db_url, dry_run):
            return 0
    except Exception:
        return 1

    # Strategy 2: Fall back to Supabase CLI
    if run_supabase_cli_migrations(db_url, dry_run):
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
