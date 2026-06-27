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
