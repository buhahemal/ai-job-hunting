"""Helpers to convert unified profile records into resume and matching formats."""

from __future__ import annotations

import copy
import os
import re
from typing import Any, Dict, List

from packages.database.python.constants import MATCH_SCORE_THRESHOLD


def flatten_experience_bullet(bullet: Any) -> str:
    """Normalize structured or plain experience bullets to searchable text."""
    if isinstance(bullet, dict):
        title = str(bullet.get('title') or '').strip()
        body = str(bullet.get('body') or '').strip()
        if title and body:
            return f'{title}: {body}'
        return title or body
    return str(bullet or '').strip()


def flatten_experience_bullets(bullets: List[Any] | None) -> List[str]:
    """Return plain-text bullets for matching corpus builders."""
    return [text for text in (flatten_experience_bullet(item) for item in (bullets or [])) if text]


def _structured_bullet(bullet: Any) -> Dict[str, str]:
    if isinstance(bullet, dict):
        return {
            'title': str(bullet.get('title') or '').strip(),
            'body': str(bullet.get('body') or '').strip(),
        }
    text = str(bullet or '').strip()
    return {'title': '', 'body': text}


def _default_skill_groups(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    skills = [str(item).strip() for item in (profile.get('skills') or []) if str(item).strip()]
    if not skills:
        return []
    midpoint = max(1, len(skills) // 2)
    return [
        {'label': 'Core Skills', 'items': skills[:midpoint]},
        {'label': 'Tools & Platforms', 'items': skills[midpoint:]},
    ]


def profile_to_master_resume(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a unified profile document into master resume JSON shape."""
    experience: List[Dict[str, Any]] = []
    for entry in profile.get('experience') or []:
        experience.append(
            {
                'role': str(entry.get('role') or '').strip(),
                'company': str(entry.get('company') or '').strip(),
                'period': str(entry.get('period') or '').strip(),
                'location': str(entry.get('location') or '').strip(),
                'techStack': str(entry.get('techStack') or '').strip(),
                'bullets': [_structured_bullet(bullet) for bullet in (entry.get('bullets') or [])],
            }
        )

    education: List[Dict[str, Any]] = []
    for entry in profile.get('education') or []:
        education.append(
            {
                'degree': str(entry.get('degree') or '').strip(),
                'school': str(entry.get('school') or '').strip(),
                'period': str(entry.get('period') or '').strip(),
                'location': str(entry.get('location') or '').strip(),
            }
        )

    projects: List[Dict[str, Any]] = []
    for entry in profile.get('projects') or []:
        tech = [str(item).strip() for item in (entry.get('tech') or []) if str(item).strip()]
        tech_stack = str(entry.get('techStack') or '').strip() or ', '.join(tech)
        description = str(entry.get('description') or '').strip()
        bullets = entry.get('bullets')
        if isinstance(bullets, list) and bullets:
            project_bullets = [_structured_bullet(bullet) for bullet in bullets]
        elif description:
            project_bullets = [{'title': 'Overview', 'body': description}]
        else:
            project_bullets = []

        projects.append(
            {
                'title': str(entry.get('title') or '').strip(),
                'subtitle': str(entry.get('subtitle') or 'Personal Project').strip(),
                'techStack': tech_stack,
                'bullets': project_bullets,
            }
        )

    skill_groups = profile.get('skillGroups') or []
    if not skill_groups:
        skill_groups = _default_skill_groups(profile)

    website = str(profile.get('website') or profile.get('github') or '').strip()
    github = str(profile.get('github') or website).strip()

    return {
        'fullName': str(profile.get('fullName') or '').strip(),
        'email': str(profile.get('email') or '').strip(),
        'phone': str(profile.get('phone') or '').strip(),
        'github': github,
        'linkedin': str(profile.get('linkedin') or '').strip(),
        'location': str(profile.get('location') or '').strip(),
        'summary': str(profile.get('summary') or '').strip(),
        'targetRoles': list(profile.get('targetRoles') or []),
        'skills': list(profile.get('skills') or []),
        'skillGroups': copy.deepcopy(skill_groups),
        'experience': experience,
        'education': education,
        'projects': projects,
    }


def resolve_min_match_score(profile: Dict[str, Any] | None) -> int:
    """Resolve promotion threshold from profile settings with env fallback."""
    source = profile or {}
    settings = source.get('matchSettings') or {}
    raw_score = settings.get('minMatchScore')
    if isinstance(raw_score, (int, float)):
        score = int(raw_score)
        if 50 <= score <= 100:
            return score

    env_value = os.environ.get('SCANNER_MIN_MATCH_SCORE', str(MATCH_SCORE_THRESHOLD))
    try:
        return int(env_value)
    except ValueError:
        return MATCH_SCORE_THRESHOLD


def validate_profile_payload(profile: Dict[str, Any]) -> None:
    """Raise ValueError when required profile fields are invalid."""
    full_name = str(profile.get('fullName') or '').strip()
    email = str(profile.get('email') or '').strip()
    if not full_name:
        raise ValueError('fullName is required')
    if not email or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        raise ValueError('A valid email is required')

    score = (profile.get('matchSettings') or {}).get('minMatchScore', MATCH_SCORE_THRESHOLD)
    if not isinstance(score, (int, float)) or not (50 <= int(score) <= 100):
        raise ValueError('matchSettings.minMatchScore must be between 50 and 100')
