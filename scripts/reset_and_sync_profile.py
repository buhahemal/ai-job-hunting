#!/usr/bin/env python3
"""CLI utility to sync candidate profile or reset data in Supabase database."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

from packages.config.python.dotenv import load_dotenv

load_dotenv()

from apps.api.defaults import DEFAULT_PROFILE
from packages.database.python.client import create_service_client, is_supabase_configured
from packages.database.python.profile import normalize_stored_profile
from packages.database.python.repositories.jobs import JobRepository


def reset_jobs_data(client) -> None:
    """Clear all scanned jobs, manual jobs, and interviews from Supabase."""
    print("Resetting jobs, scanned jobs, and interviews data...")
    try:
        client.table("interviews").delete().filter("id", "neq", "00000000-0000-0000-0000-000000000000").execute()
    except Exception:
        pass
    try:
        client.table("applications").delete().filter("id", "neq", "00000000-0000-0000-0000-000000000000").execute()
    except Exception:
        pass
    try:
        client.table("resumes").delete().filter("id", "neq", "00000000-0000-0000-0000-000000000000").execute()
    except Exception:
        pass
    try:
        client.table("jobs").delete().filter("id", "neq", "00000000-0000-0000-0000-000000000000").execute()
    except Exception:
        pass
    try:
        client.table("scanned_jobs").delete().filter("dedupe_key", "neq", "__none__").execute()
    except Exception:
        pass
    print("✅ All jobs and scan insights data cleared successfully.")


def reset_all_data(client) -> None:
    """Clear all tables including profile data."""
    reset_jobs_data(client)
    print("Resetting profiles table...")
    client.table("profiles").delete().filter("id", "neq", "00000000-0000-0000-0000-000000000000").execute()
    print("✅ Profiles table reset successfully.")


def load_profile_data(profile_input: str | None) -> Dict[str, Any]:
    """Load profile payload from inline JSON string, file path, or default fallback."""
    if not profile_input:
        return DEFAULT_PROFILE

    raw_input = profile_input.strip()
    if raw_input.startswith("{") and raw_input.endswith("}"):
        try:
            return json.loads(raw_input)
        except json.JSONDecodeError as err:
            print(f"Error parsing inline JSON profile: {err}", file=sys.stderr)
            sys.exit(1)

    if os.path.exists(raw_input):
        with open(raw_input, "r", encoding="utf-8") as file:
            return json.load(file)

    print(f"Profile file not found: {raw_input}", file=sys.stderr)
    sys.exit(1)


def sync_profile(repo: JobRepository, profile_data: Dict[str, Any], *, force: bool = False) -> None:
    """Sync profile into Supabase database."""
    normalized = normalize_stored_profile(profile_data)

    existing = normalize_stored_profile(repo.get_profile())
    has_existing = bool(str(existing.get("fullName") or "").strip())

    if has_existing and not force:
        print(
            f"Profile already populated for '{existing['fullName']}' — skipping seed. "
            "Pass --force (or run with Force Overwrite in GitHub Actions) to overwrite."
        )
        return

    repo.save_profile(normalized)
    print(f"✅ Successfully synced candidate profile for '{normalized['fullName']}' to Supabase (id=default).")


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset database data or sync candidate profile in Supabase.")
    parser.add_argument(
        "--action",
        choices=["sync-profile", "reset-jobs", "reset-all"],
        default="sync-profile",
        help="Action to perform: sync-profile, reset-jobs, or reset-all.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing profile if one exists.",
    )
    parser.add_argument(
        "--profile-input",
        help="Path to JSON profile file or inline JSON string.",
    )

    args = parser.parse_args()

    if not is_supabase_configured():
        print(
            "Supabase not configured. Ensure SUPABASE_URL and SUPABASE_SERVICE_KEY are set.",
            file=sys.stderr,
        )
        return 1

    client = create_service_client()
    repo = JobRepository(client)

    if args.action == "reset-jobs":
        reset_jobs_data(client)
    elif args.action == "reset-all":
        reset_all_data(client)
        profile_data = load_profile_data(args.profile_input)
        sync_profile(repo, profile_data, force=True)
    elif args.action == "sync-profile":
        profile_data = load_profile_data(args.profile_input)
        sync_profile(repo, profile_data, force=args.force)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
