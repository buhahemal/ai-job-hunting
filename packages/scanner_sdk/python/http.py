"""Shared HTTP helpers for scanner plugins."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

DEFAULT_HEADERS = {'User-Agent': 'AI-Job-Hunter-Agent/1.0'}
DEFAULT_TIMEOUT_SECONDS = 10


def get_response(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> Optional[requests.Response]:
    """GET a URL and return the response when successful."""
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        if response.status_code == 200:
            return response
    except requests.RequestException as exc:
        print(f'[HTTP] GET failed for {url}: {exc}')
    return None


def get_json(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> Optional[Dict[str, Any]]:
    """GET JSON object from a URL. Returns None on failure."""
    response = get_response(url, timeout=timeout)
    if not response:
        return None
    data = response.json()
    return data if isinstance(data, dict) else None


def get_json_any(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> Any:
    """GET JSON payload (object or array) from a URL."""
    response = get_response(url, timeout=timeout)
    if not response:
        return None
    return response.json()


def get_text(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> Optional[str]:
    """GET response body as text."""
    response = get_response(url, timeout=timeout)
    return response.text if response else None


def head_ok(url: str, timeout: int = 5) -> bool:
    """Return True when HEAD request succeeds with HTTP 200."""
    try:
        response = requests.head(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False


def fetch_ok(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> bool:
    """Return True when GET request succeeds with HTTP 200."""
    return get_response(url, timeout=timeout) is not None


def post_json(
    url: str,
    payload: Dict[str, Any],
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Optional[Dict[str, Any]]:
    """POST JSON body and return parsed JSON object on HTTP 200."""
    try:
        response = requests.post(
            url,
            headers={**DEFAULT_HEADERS, 'Content-Type': 'application/json'},
            json=payload,
            timeout=timeout,
        )
        if response.status_code != 200:
            print(f'[HTTP] POST {url} returned HTTP {response.status_code}')
            return None
        data = response.json()
        return data if isinstance(data, dict) else None
    except requests.RequestException as exc:
        print(f'[HTTP] POST failed for {url}: {exc}')
    return None
