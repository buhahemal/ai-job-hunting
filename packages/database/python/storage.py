"""Supabase Storage helpers for resume PDFs."""

from __future__ import annotations

import os
from typing import Any

RESUME_STORAGE_BUCKET = 'resumes'


def resume_object_path(job_id: str, version: str) -> str:
    """Build the storage object key for a versioned resume PDF."""
    safe_job = job_id.replace('/', '_')
    safe_version = version.replace('/', '_')
    return f'{safe_job}/{safe_version}.pdf'


def upload_resume_pdf(
    client: Any,
    *,
    job_id: str,
    version: str,
    pdf_bytes: bytes,
    bucket: str = RESUME_STORAGE_BUCKET,
) -> str:
    """
    Upload a resume PDF to Supabase Storage and return its public URL.

    Requires service-role client. Bucket must exist and be public for anon read.
    """
    path = resume_object_path(job_id, version)
    storage = client.storage.from_(bucket)
    storage.upload(
        path,
        pdf_bytes,
        file_options={'content-type': 'application/pdf', 'upsert': 'true'},
    )
    public = storage.get_public_url(path)
    if isinstance(public, str):
        return public
    if isinstance(public, dict):
        return str(public.get('publicUrl') or public.get('publicURL') or public.get('data', ''))
    return str(public)


def is_storage_configured() -> bool:
    """Return True when Supabase URL is set (required for public URLs)."""
    return bool(os.getenv('SUPABASE_URL'))
