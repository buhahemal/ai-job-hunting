"""Normalize profile JSON loaded from Supabase (no local file defaults)."""

from __future__ import annotations

from typing import Any, Dict

from packages.database.python.constants import MATCH_SCORE_THRESHOLD

STORED_PROFILE_DEFAULTS: Dict[str, Any] = {
    'fullName': '',
    'email': '',
    'phone': '',
    'website': '',
    'github': '',
    'linkedin': '',
    'location': '',
    'summary': '',
    'targetRoles': [],
    'skills': [],
    'skillGroups': [],
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
    'matchSettings': {
        'minMatchScore': MATCH_SCORE_THRESHOLD,
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
    merged['summary'] = str(source.get('summary') or '')
    merged['skillGroups'] = list(source.get('skillGroups') or [])
    merged['experience'] = list(source.get('experience') or [])
    merged['education'] = list(source.get('education') or [])
    merged['projects'] = list(source.get('projects') or [])
    merged['preferences'] = {
        **STORED_PROFILE_DEFAULTS['preferences'],
        **(source.get('preferences') or {}),
    }
    settings = source.get('matchSettings') or {}
    raw_score = settings.get('minMatchScore', MATCH_SCORE_THRESHOLD)
    try:
        score = int(raw_score)
    except (TypeError, ValueError):
        score = MATCH_SCORE_THRESHOLD
    merged['matchSettings'] = {
        'minMatchScore': max(50, min(100, score)),
    }
    merged['masterResumeLaTeX'] = str(source.get('masterResumeLaTeX') or '')
    return merged
