"""Shared HTTP helpers for scanner plugins."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

DEFAULT_HEADERS = {'User-Agent': 'AI-Job-Hunter-Agent/1.0'}
DEFAULT_TIMEOUT_SECONDS = 10


def get_json(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> Optional[Dict[str, Any]]:
    """GET JSON from a URL. Returns None on failure."""
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as exc:
        print(f'[HTTP] GET failed for {url}: {exc}')
    return None


def head_ok(url: str, timeout: int = 5) -> bool:
    """Return True when HEAD request succeeds with HTTP 200."""
    try:
        response = requests.head(url, headers=DEFAULT_HEADERS, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False
