"""Job and profile persistence via Supabase."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional

from supabase import Client

from packages.database.python.mappers import (
    dedupe_indexes,
    job_to_row,
    match_insights_to_row,
    profile_data_from_row,
    row_to_interview,
    row_to_job,
    row_to_scanned_job,
    scanned_job_to_row,
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
        Persist full scan insight rows for cross-run deduplication and analytics.

        Returns:
            Number of records upserted.
        """
        if not records:
            return 0
        rows = [
            scanned_job_to_row(record)
            for record in records
            if record.get('dedupe_key')
        ]
        if not rows:
            return 0
        self._client.table('scanned_jobs').upsert(rows, on_conflict='dedupe_key').execute()
        return len(rows)

    def list_scanned_jobs(
        self,
        *,
        page: int = 1,
        limit: int = 25,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None,
        source: Optional[str] = None,
        role: Optional[str] = None,
        missing_skill: Optional[str] = None,
        below_threshold_only: bool = False,
        threshold: int = 75,
    ) -> Dict[str, Any]:
        """Return paginated scanned job insights with optional filters."""
        page = max(1, page)
        limit = max(1, min(limit, 100))
        offset = (page - 1) * limit

        query = self._client.table('scanned_jobs').select('*', count='exact')
        if min_score is not None:
            query = query.gte('overall_score', min_score)
        if max_score is not None:
            query = query.lte('overall_score', max_score)
        if source:
            query = query.eq('source', source)
        if role:
            query = query.eq('canonical_role', role)
        if missing_skill:
            query = query.contains('missing_skills', [missing_skill])
        if below_threshold_only:
            query = query.lte('overall_score', threshold)

        response = (
            query.order('scanned_at', desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        rows = response.data or []
        total = response.count if response.count is not None else len(rows)
        return {
            'items': [row_to_scanned_job(row) for row in rows],
            'page': page,
            'limit': limit,
            'total': total,
        }

    def get_scan_summary(self, *, threshold: int = 75) -> Dict[str, Any]:
        """Aggregate scan insight statistics for dashboard summary header."""
        all_response = (
            self._client.table('scanned_jobs')
            .select(
                'overall_score, score, source, scanned_at, promoted_to_jobs, missing_skills, scan_run_id'
            )
            .execute()
        )
        rows = all_response.data or []
        if not rows:
            return {
                'totalScanned': 0,
                'promotedCount': 0,
                'averageScore': 0,
                'topSource': None,
                'lastScanAt': None,
                'lastRunScanned': 0,
                'topMissingSkills': [],
            }

        scores: List[int] = []
        source_counts: Counter[str] = Counter()
        missing_counter: Counter[str] = Counter()
        missing_score_sum: Dict[str, int] = {}
        promoted = 0
        last_scan_at: Optional[str] = None
        latest_run_id: Optional[str] = None

        for row in rows:
            overall = row.get('overall_score', row.get('score')) or 0
            scores.append(int(overall))
            if row.get('promoted_to_jobs'):
                promoted += 1
            source = row.get('source')
            if source:
                source_counts[str(source)] += 1
            scanned_at = row.get('scanned_at')
            if scanned_at and (last_scan_at is None or scanned_at > last_scan_at):
                last_scan_at = scanned_at
                latest_run_id = row.get('scan_run_id')
            for skill in row.get('missing_skills') or []:
                skill_text = str(skill)
                missing_counter[skill_text] += 1
                missing_score_sum[skill_text] = missing_score_sum.get(skill_text, 0) + int(overall)

        last_run_scanned = 0
        if latest_run_id:
            last_run_scanned = sum(
                1 for row in rows if row.get('scan_run_id') == latest_run_id
            )

        top_missing = []
        for skill, count in missing_counter.most_common(10):
            avg_when_missing = round(missing_score_sum[skill] / count)
            band_boost = sum(
                1
                for row in rows
                if skill in (row.get('missing_skills') or [])
                and threshold - 10 <= int(row.get('overall_score', row.get('score')) or 0) <= threshold
            )
            top_missing.append({
                'skill': skill,
                'count': count,
                'averageScoreWhenMissing': avg_when_missing,
                'estimatedBandBoost': band_boost,
            })

        top_source = source_counts.most_common(1)[0][0] if source_counts else None
        average = round(sum(scores) / len(scores)) if scores else 0

        return {
            'totalScanned': len(rows),
            'promotedCount': promoted,
            'averageScore': average,
            'topSource': top_source,
            'lastScanAt': last_scan_at,
            'lastRunScanned': last_run_scanned,
            'topMissingSkills': top_missing,
        }

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
