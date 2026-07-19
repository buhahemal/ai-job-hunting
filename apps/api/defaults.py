"""Shared default profile and database seed values."""

from __future__ import annotations

import json

from apps.api.paths import PROFILE_JSON
from packages.database.python.constants import MATCH_SCORE_THRESHOLD


def load_profile_base() -> dict:
    """Load structured profile fields from apps/api/data/profile.json."""
    with open(PROFILE_JSON, encoding="utf-8") as handle:
        return json.load(handle)


def build_default_profile() -> dict:
    """Load profile.json as the canonical seed profile."""
    profile_base = load_profile_base()
    merged = {
        **profile_base,
        "matchSettings": {"minMatchScore": MATCH_SCORE_THRESHOLD},
    }
    return merged


DEFAULT_PROFILE = build_default_profile()


def normalize_profile(profile: dict | None, *, merge_file_defaults: bool = True) -> dict:
    """
    Normalize profile dict for JSON/local storage.

    When ``merge_file_defaults`` is False, only apply empty structural defaults
    (used for Supabase-backed paths via ``normalize_stored_profile``).
    """
    if not merge_file_defaults:
        from packages.database.python.profile import normalize_stored_profile

        return normalize_stored_profile(profile)

    if not profile or not profile.get("fullName"):
        return {**DEFAULT_PROFILE, **(profile or {})}
    return {**DEFAULT_PROFILE, **profile}

