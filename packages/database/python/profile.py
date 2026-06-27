"""Normalize profile JSON loaded from Supabase (no local file defaults)."""

from __future__ import annotations

from typing import Any, Dict

STORED_PROFILE_DEFAULTS: Dict[str, Any] = {
    'fullName': '',
    'email': '',
    'phone': '',
    'website': '',
    'github': '',
    'linkedin': '',
    'location': '',
    'targetRoles': [],
    'skills': [],
    'experience': [],
    'education': [],
    'projects': [],
    'preferences': {
        'locations': [],
        'remotePreference': 'Any',
        'companySizes': [],
        'targetCompanies': [],
        'skillsKeywords': [],
    },
    'masterResumeLaTeX': '',
}


def normalize_stored_profile(profile: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Merge Supabase ``profiles.data`` with empty structural defaults only.

    Does not inject skills or other fields from apps/api/data/profile.json.
    """
    source = profile or {}
    merged = {**STORED_PROFILE_DEFAULTS, **source}
    merged['skills'] = list(source.get('skills') or [])
    merged['targetRoles'] = list(source.get('targetRoles') or [])
    merged['experience'] = list(source.get('experience') or [])
    merged['education'] = list(source.get('education') or [])
    merged['projects'] = list(source.get('projects') or [])
    merged['preferences'] = {
        **STORED_PROFILE_DEFAULTS['preferences'],
        **(source.get('preferences') or {}),
    }
    merged['masterResumeLaTeX'] = str(source.get('masterResumeLaTeX') or '')
    return merged
