#!/usr/bin/env python3
"""Sync the canonical default profile from apps/api to Supabase when empty."""

from __future__ import annotations

import sys

from apps.api.defaults import DEFAULT_PROFILE
from packages.database.python.client import create_service_client, is_supabase_configured
from packages.database.python.profile import normalize_stored_profile
from packages.database.python.repositories.jobs import JobRepository


def main() -> int:
    if not is_supabase_configured():
        print(
            'Data not found. Configure Supabase with SUPABASE_URL and SUPABASE_SERVICE_KEY.',
            file=sys.stderr,
        )
        return 1

    repo = JobRepository(create_service_client())
    existing = normalize_stored_profile(repo.get_profile())
    if str(existing.get('fullName') or '').strip():
        print(
            f"Profile already populated for {existing['fullName']} — skipping seed "
            '(dashboard edits are preserved).',
        )
        return 0

    repo.save_profile(DEFAULT_PROFILE)
    print(f"Seeded profile for {DEFAULT_PROFILE['fullName']} to Supabase (id=default).")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
