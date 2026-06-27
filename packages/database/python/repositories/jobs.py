"""Job and profile persistence via Supabase."""

from __future__ import annotations

from typing import Any, Dict, List

from supabase import Client

from packages.database.python.mappers import (
    dedupe_indexes,
    job_to_row,
    profile_data_from_row,
    row_to_interview,
    row_to_job,
)


class JobRepository:
    """Read/write jobs, profile, and interviews in Supabase."""

    PROFILE_ID = 'default'

    def __init__(self, client: Client):
        self._client = client

    def get_profile(self) -> Dict[str, Any]:
        """Fetch profile JSON from profiles table."""
        response = (
            self._client.table('profiles')
            .select('data')
            .eq('id', self.PROFILE_ID)
            .maybe_single()
            .execute()
        )
        return profile_data_from_row(response.data)

    def save_profile(self, profile: Dict[str, Any]) -> None:
        """Upsert profile JSON."""
        self._client.table('profiles').upsert(
            {'id': self.PROFILE_ID, 'data': profile},
            on_conflict='id',
        ).execute()

    def list_jobs(self) -> List[Dict[str, Any]]:
        """Return all jobs ordered by posted_at descending."""
        response = (
            self._client.table('jobs')
            .select('*')
            .order('posted_at', desc=True)
            .execute()
        )
        rows = response.data or []
        return [row_to_job(row) for row in rows]

    def list_interviews(self) -> List[Dict[str, Any]]:
        """Return all interviews."""
        response = self._client.table('interviews').select('*').execute()
        rows = response.data or []
        return [row_to_interview(row) for row in rows]

    def get_dedupe_indexes(self) -> tuple[set[str], set[str]]:
        """Load deduplication indexes from existing jobs."""
        jobs = self.list_jobs()
        return dedupe_indexes(jobs)

    def upsert_jobs(self, jobs: List[Dict[str, Any]]) -> int:
        """
        Upsert job records by primary key.

        Returns:
            Number of jobs upserted.
        """
        if not jobs:
            return 0
        rows = [job_to_row(job) for job in jobs]
        self._client.table('jobs').upsert(rows, on_conflict='id').execute()
        return len(rows)
