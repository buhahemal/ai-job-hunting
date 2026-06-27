"""Resume version persistence in Supabase."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from supabase import Client

from packages.resume_engine.python.master import load_master_resume


class ResumeRepository:
    """Manage versioned resume rows and master snapshots."""

    def __init__(self, client: Client):
        self._client = client

    def list_for_job(self, job_id: str) -> List[Dict[str, Any]]:
        """Return resume versions for a job ordered by creation time."""
        response = (
            self._client.table('resumes')
            .select('*')
            .eq('job_id', job_id)
            .order('created_at', desc=False)
            .execute()
        )
        return response.data or []

    def get_master_snapshot(self) -> Optional[Dict[str, Any]]:
        """Return the stored master resume row if present."""
        response = (
            self._client.table('resumes')
            .select('*')
            .eq('version', 'master')
            .is_('job_id', 'null')
            .maybe_single()
            .execute()
        )
        return response.data

    def ensure_master_snapshot(self) -> Dict[str, Any]:
        """Insert master JSON snapshot once (never overwrites existing master row)."""
        existing = self.get_master_snapshot()
        if existing:
            return existing

        master = load_master_resume()
        payload = {
            'job_id': None,
            'version': 'master',
            'content': master,
            'pdf_url': None,
            'ats_score': None,
        }
        response = self._client.table('resumes').insert(payload).execute()
        rows = response.data or []
        if rows:
            return rows[0]
        return payload

    def next_tailored_version(self, job_id: str) -> str:
        """Allocate the next tailored version label for a job (tailored_v1, v2, …)."""
        response = (
            self._client.table('resumes')
            .select('version')
            .eq('job_id', job_id)
            .like('version', 'tailored_%')
            .execute()
        )
        max_index = 0
        for row in response.data or []:
            match = re.match(r'tailored_v(\d+)$', str(row.get('version', '')))
            if match:
                max_index = max(max_index, int(match.group(1)))
        return f'tailored_v{max_index + 1}'

    def insert_tailored(
        self,
        *,
        job_id: str,
        version: str,
        content: Dict[str, Any],
        pdf_url: str,
        ats_score: int,
    ) -> Dict[str, Any]:
        """Persist a tailored resume version linked to a job."""
        payload = {
            'job_id': job_id,
            'version': version,
            'content': content,
            'pdf_url': pdf_url,
            'ats_score': float(ats_score),
        }
        response = self._client.table('resumes').insert(payload).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError(f'Failed to insert resume version {version} for job {job_id}')
        return rows[0]
