"""Supabase client factory and environment helpers."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from supabase import Client


def use_json_store() -> bool:
    """Return True when pipeline should write to data.json instead of Supabase."""
    return os.getenv('USE_JSON_STORE', 'false').lower() in ('1', 'true', 'yes')


def is_supabase_configured() -> bool:
    """Return True when Supabase URL and service key are available."""
    if use_json_store():
        return False
    return bool(os.getenv('SUPABASE_URL') and _service_key())


def _service_key() -> str | None:
    return os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')


def create_service_client() -> Any:
    """
    Create a Supabase client with service role credentials (GitHub Actions / trusted writes).

    Raises:
        RuntimeError: If required environment variables are missing.
    """
    from supabase import create_client

    url = os.getenv('SUPABASE_URL')
    key = _service_key()
    if not url or not key:
        raise RuntimeError(
            'Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_KEY, '
            'or USE_JSON_STORE=true for JSON fallback.'
        )
    return create_client(url, key)
