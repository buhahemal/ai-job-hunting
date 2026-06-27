#!/usr/bin/env python3
"""Sync the canonical default profile from apps/api to Supabase."""

from __future__ import annotations

import sys

from apps.api.defaults import DEFAULT_PROFILE
from packages.database.python.client import create_service_client, is_supabase_configured
from packages.database.python.repositories.jobs import JobRepository


def main() -> int:
    if not is_supabase_configured():
        print(
            'Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_KEY '
            '(or USE_JSON_STORE=false with valid secrets).',
            file=sys.stderr,
        )
        return 1

    repo = JobRepository(create_service_client())
    repo.save_profile(DEFAULT_PROFILE)
    print(f"Synced profile for {DEFAULT_PROFILE['fullName']} to Supabase (id=default).")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
