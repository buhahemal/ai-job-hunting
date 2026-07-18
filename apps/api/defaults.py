"""Shared default profile and database seed values."""

from __future__ import annotations

import json

from apps.api.paths import MASTER_RESUME_TEX, PROFILE_JSON
from packages.config.python.paths import MASTER_RESUME_JSON
from packages.database.python.constants import MATCH_SCORE_THRESHOLD


def load_master_resume_json() -> dict:
    """Load structured resume fields from apps/api/data/resume/master.json."""
    with open(MASTER_RESUME_JSON, encoding="utf-8") as handle:
        return json.load(handle)


def load_master_resume_latex(*, profile: dict | None = None) -> str:
    """Render master resume LaTeX from profile or apps/api/data/resume/master.json."""
    try:
        from packages.resume_engine.python.generator import render_master_latex

        return render_master_latex(profile=profile)
    except Exception:
        with open(MASTER_RESUME_TEX, encoding="utf-8") as handle:
            return handle.read()


def load_profile_base() -> dict:
    """Load structured profile fields from apps/api/data/profile.json."""
    with open(PROFILE_JSON, encoding="utf-8") as handle:
        return json.load(handle)


def build_default_profile() -> dict:
    """Merge profile.json and master.json into the canonical seed profile."""
    profile_base = load_profile_base()
    master = load_master_resume_json()
    merged = {
        **profile_base,
        "summary": master.get("summary", ""),
        "skillGroups": master.get("skillGroups", []),
        "matchSettings": {"minMatchScore": MATCH_SCORE_THRESHOLD},
    }

    if not merged.get("experience") and master.get("experience"):
        merged["experience"] = [
            {
                "role": item.get("role", ""),
                "company": item.get("company", ""),
                "period": item.get("period", ""),
                "location": item.get("location", ""),
                "techStack": item.get("techStack", ""),
                "bullets": item.get("bullets") or [],
            }
            for item in master.get("experience") or []
        ]

    if not merged.get("education") and master.get("education"):
        merged["education"] = master.get("education") or []

    if not merged.get("projects") and master.get("projects"):
        merged["projects"] = [
            {
                "title": item.get("title", ""),
                "description": " ".join(
                    bullet.get("body", "")
                    for bullet in (item.get("bullets") or [])
                    if isinstance(bullet, dict)
                ),
                "tech": [
                    token.strip()
                    for token in str(item.get("techStack") or "").split(",")
                    if token.strip()
                ],
                "subtitle": item.get("subtitle", ""),
                "techStack": item.get("techStack", ""),
            }
            for item in master.get("projects") or []
        ]

    merged["masterResumeLaTeX"] = load_master_resume_latex(profile=merged)
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
        merged = {**DEFAULT_PROFILE, **(profile or {})}
        merged["masterResumeLaTeX"] = (
            profile.get("masterResumeLaTeX")
            if profile and profile.get("masterResumeLaTeX")
            else DEFAULT_PROFILE["masterResumeLaTeX"]
        )
        return merged
    return {**DEFAULT_PROFILE, **profile}
