"""Shared default profile and database seed values."""

from __future__ import annotations

import json

from apps.api.paths import MASTER_RESUME_TEX, PROFILE_JSON


def load_master_resume_latex() -> str:
    """Load read-only master resume LaTeX from apps/api/data/master-resume.tex."""
    with open(MASTER_RESUME_TEX, encoding="utf-8") as handle:
        return handle.read()


def load_profile_base() -> dict:
    """Load structured profile fields from apps/api/data/profile.json."""
    with open(PROFILE_JSON, encoding="utf-8") as handle:
        return json.load(handle)


DEFAULT_PROFILE = {
    **load_profile_base(),
    "masterResumeLaTeX": load_master_resume_latex(),
}


def normalize_profile(profile: dict | None) -> dict:
    if not profile or not profile.get("fullName"):
        merged = {**DEFAULT_PROFILE, **(profile or {})}
        merged["masterResumeLaTeX"] = profile.get("masterResumeLaTeX") if profile and profile.get("masterResumeLaTeX") else DEFAULT_PROFILE["masterResumeLaTeX"]
        return merged
    return {**DEFAULT_PROFILE, **profile}
