"""Job and profile persistence via Supabase."""

from __future__ import annotations

from typing import Any, Dict, List

from supabase import Client

from packages.database.python.mappers import (
    dedupe_indexes,
    job_to_row,
    match_insights_to_row,
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
        """Return all jobs with match score components ordered by posted_at descending."""
        response = (
            self._client.table('jobs')
            .select('*, job_match_scores(*)')
            .order('posted_at', desc=True)
            .execute()
        )
        rows = response.data or []
        jobs: List[Dict[str, Any]] = []
        for row in rows:
            match_payload = row.get('job_match_scores')
            match_row = None
            if isinstance(match_payload, list) and match_payload:
                match_row = match_payload[0]
            elif isinstance(match_payload, dict):
                match_row = match_payload
            jobs.append(row_to_job(row, match_row))
        return jobs

    def list_interviews(self) -> List[Dict[str, Any]]:
        """Return all interviews."""
        response = self._client.table('interviews').select('*').execute()
        rows = response.data or []
        return [row_to_interview(row) for row in rows]

    def get_dedupe_indexes(self) -> tuple[set[str], set[str]]:
        """Load deduplication indexes from existing jobs."""
        jobs = self.list_jobs()
        return dedupe_indexes(jobs)

    def get_scanned_keys(self) -> set[str]:
        """Return dedupe keys for jobs already evaluated by the scanner."""
        response = self._client.table('scanned_jobs').select('dedupe_key').execute()
        rows = response.data or []
        return {row['dedupe_key'] for row in rows if row.get('dedupe_key')}

    def record_scanned_jobs(self, records: List[Dict[str, Any]]) -> int:
        """
        Persist scanner evaluation history for cross-run deduplication.

        Returns:
            Number of records upserted.
        """
        if not records:
            return 0
        rows = [
            {
                'dedupe_key': record['dedupe_key'],
                'job_id': record.get('job_id'),
                'source': record.get('source'),
                'score': record.get('score'),
            }
            for record in records
            if record.get('dedupe_key')
        ]
        if not rows:
            return 0
        self._client.table('scanned_jobs').upsert(rows, on_conflict='dedupe_key').execute()
        return len(rows)

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

        score_rows = [
            match_insights_to_row(job['id'], job['matchInsights'])
            for job in jobs
            if job.get('matchInsights')
        ]
        if score_rows:
            self._client.table('job_match_scores').upsert(score_rows, on_conflict='job_id').execute()
        return len(rows)
