"""Supabase client factory and environment helpers."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from supabase import Client


def is_supabase_configured() -> bool:
    """Return True when Supabase URL and service key are available."""
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
            'Data not found. Configure Supabase with SUPABASE_URL and SUPABASE_SERVICE_KEY.'
        )
    return create_client(url, key)
