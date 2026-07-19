"""Canonical job normalization helpers."""

from __future__ import annotations

import re
from typing import Dict, Optional


def strip_html(value: str) -> str:
    """Remove HTML tags from a string."""
    return re.sub(r'<[^>]*>', '', value).strip()


def build_canonical_job(
    *,
    id: str,
    title: str,
    company: str,
    location: str,
    remote_type: str,
    source: str,
    url: str,
    description: str,
    status: str = 'New',
) -> Dict[str, str]:
    """Build a canonical job dict shared by all scanner plugins."""
    return {
        'id': id,
        'title': title or 'Unknown Role',
        'company': company or 'Unknown Company',
        'location': location or 'Remote',
        'remoteType': remote_type,
        'source': source,
        'url': url or '',
        'description': description or '',
        'status': status,
    }


def infer_remote_type(raw_remote: Optional[bool], location: str) -> str:
    """Infer remote type from API flag or location text."""
    if raw_remote is True:
        return 'Remote'
    location_lower = (location or '').lower()
    if 'remote' in location_lower:
        return 'Remote'
    if 'hybrid' in location_lower:
        return 'Hybrid'
    if raw_remote is False:
        return 'On-site'
    return 'Hybrid'


NON_ENGINEERING_TITLE_TERMS = (
    'hr ',
    'human resource',
    'recruiter',
    'talent acquisition',
    'sales',
    'account executive',
    'business development',
    'marketing',
    'seo ',
    'content writer',
    'copywriter',
    'customer support',
    'customer success',
    'customer service',
    'call center',
    'asesor de atenci',
    'graphic designer',
    'ui/ux designer',
    'illustrator',
    'creative director',
    'administrative assistant',
    'virtual assistant',
    'office manager',
    'receptionist',
    'courier',
    'driver',
    'warehouse',
    'docente',
    'teacher',
    'professor',
    'accountant',
    'payroll',
    'legal assistant',
    'paralegal',
    'nurse',
)

ENGINEERING_TITLE_TERMS = (
    'engineer',
    'developer',
    'software',
    'programmer',
    'coder',
    'architect',
    'backend',
    'frontend',
    'fullstack',
    'full-stack',
    'full stack',
    'devops',
    'sre',
    'site reliability',
    'platform',
    'cloud',
    'data',
    'infra',
    'infrastructure',
    'qa ',
    'test engineer',
    'automation',
    'tech lead',
    'technical lead',
    'cto',
    'engineering',
)


def is_engineering_job_title(title: str, description: str = '') -> bool:
    """Return True if title represents a software/engineering role."""
    title_lower = (title or '').lower()
    if not title_lower or title_lower in {'unknown role', 'open position', 'replace with job title'}:
        return False
    if any(term in title_lower for term in ENGINEERING_TITLE_TERMS):
        return True
    if any(term in title_lower for term in NON_ENGINEERING_TITLE_TERMS):
        return False
    return True

