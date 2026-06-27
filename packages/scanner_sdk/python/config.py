"""Scanner configuration helpers."""

from __future__ import annotations

import os
import re
from typing import Dict, List

WORKDAY_URL_PATTERN = re.compile(
    r'^https?://(?P<tenant>[^.]+)\.(?P<wd>wd\d+)\.myworkdayjobs\.com/[^/]+/(?P<site>[^/?#]+)',
    re.IGNORECASE,
)


def parse_env_list(key: str) -> List[str]:
    """Parse comma-separated environment variable into a trimmed list."""
    raw = os.environ.get(key, '')
    return [item.strip() for item in raw.split(',') if item.strip()]


def parse_workday_site(entry: str) -> Dict[str, str] | None:
    """Parse a Workday site from URL or tenant:wd:siteName format."""
    trimmed = entry.strip()
    if not trimmed:
        return None

    url_match = WORKDAY_URL_PATTERN.match(trimmed)
    if url_match:
        return {
            'tenant': url_match.group('tenant'),
            'wd': url_match.group('wd').lower(),
            'site': url_match.group('site'),
        }

    parts = trimmed.split(':')
    if len(parts) >= 3:
        return {
            'tenant': parts[0].strip(),
            'wd': parts[1].strip().lower(),
            'site': ':'.join(parts[2:]).strip(),
        }
    return None


def parse_workday_sites(key: str = 'WORKDAY_CAREER_SITES') -> List[Dict[str, str]]:
    """Parse WORKDAY_CAREER_SITES entries into tenant/wd/site dicts."""
    sites: List[Dict[str, str]] = []
    for entry in parse_env_list(key):
        parsed = parse_workday_site(entry)
        if parsed:
            sites.append(parsed)
    return sites
