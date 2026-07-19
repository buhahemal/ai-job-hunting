"""Job and profile persistence via Supabase."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional

from supabase import Client

from packages.database.python.constants import (
    MATCH_SCORE_NEAR_MISS_BAND,
    MATCH_SCORE_THRESHOLD,
    PROFILE_ID,
)
from packages.database.python.mappers import (
    dedupe_indexes,
    interview_to_row,
    job_to_row,
    match_insights_to_row,
    profile_data_from_row,
    row_to_interview,
    row_to_job,
    row_to_scanned_job,
    scanned_job_row_to_job,
    scanned_job_to_row,
)
from packages.database.python.profile import normalize_stored_profile


class JobRepository:
    """Read/write jobs, profile, and interviews in Supabase."""

    def __init__(self, client: Client):
        self._client = client

    def get_profile(self) -> Dict[str, Any]:
        """Fetch profile JSON from profiles table (Supabase source of truth)."""
        response = (
            self._client.table('profiles')
            .select('data')
            .eq('id', PROFILE_ID)
            .maybe_single()
            .execute()
        )
        return normalize_stored_profile(profile_data_from_row(response.data))

    def save_profile(self, profile: Dict[str, Any]) -> None:
        """Upsert profile JSON."""
        self._client.table('profiles').upsert(
            {'id': PROFILE_ID, 'data': profile},
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

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Fetch one job by id with match score components."""
        response = (
            self._client.table('jobs')
            .select('*, job_match_scores(*)')
            .eq('id', job_id)
            .maybe_single()
            .execute()
        )
        if not response.data:
            return None
        row = response.data
        match_payload = row.get('job_match_scores')
        match_row = None
        if isinstance(match_payload, list) and match_payload:
            match_row = match_payload[0]
        elif isinstance(match_payload, dict):
            match_row = match_payload
        return row_to_job(row, match_row)

    def update_job_status(self, job_id: str, status: str, note: Optional[str] = None) -> Dict[str, Any]:
        """Update job status and return the updated record."""
        existing = self.get_job(job_id)
        if not existing:
            raise ValueError(f'Job not found: {job_id}')

        now = datetime.now(timezone.utc).isoformat()
        history = list(existing.get('actionHistory') or existing.get('action_history') or [])
        history_entry = {
            'timestamp': now,
            'status': status,
            'action': f'Status changed to {status}',
            'note': note or '',
        }
        history.insert(0, history_entry)

        payload: Dict[str, Any] = {
            'status': status,
            'updated_at': now,
            'action_history': history,
        }
        if note:
            payload['notes'] = note

        try:
            self._client.table('jobs').update(payload).eq('id', job_id).execute()
        except Exception:
            fallback_payload: Dict[str, Any] = {'status': status}
            if note:
                fallback_payload['notes'] = note
            self._client.table('jobs').update(fallback_payload).eq('id', job_id).execute()

        job = self.get_job(job_id)
        if not job:
            raise ValueError(f'Job not found: {job_id}')
        job['updatedAt'] = now
        job['status'] = status
        if note:
            job['notes'] = note
        job['actionHistory'] = history
        return job

    def update_job_notes(self, job_id: str, notes: str) -> Dict[str, Any]:
        """Update job notes and return the updated record."""
        existing = self.get_job(job_id)
        if not existing:
            raise ValueError(f'Job not found: {job_id}')

        now = datetime.now(timezone.utc).isoformat()
        history = list(existing.get('actionHistory') or existing.get('action_history') or [])
        history_entry = {
            'timestamp': now,
            'status': existing.get('status', 'New'),
            'action': 'Notes updated',
            'note': notes,
        }
        history.insert(0, history_entry)

        payload: Dict[str, Any] = {
            'notes': notes,
            'updated_at': now,
            'action_history': history,
        }
        try:
            self._client.table('jobs').update(payload).eq('id', job_id).execute()
        except Exception:
            self._client.table('jobs').update({'notes': notes}).eq('id', job_id).execute()

        job = self.get_job(job_id)
        if not job:
            raise ValueError(f'Job not found: {job_id}')
        job['notes'] = notes
        job['updatedAt'] = now
        job['actionHistory'] = history
        return job

    def update_job_tailored(
        self,
        job_id: str,
        *,
        tailored_resume_latex: str,
        tailored_cover_letter: str,
        ats_score: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Persist tailored resume fields for a job."""
        payload: Dict[str, Any] = {
            'tailored_resume_latex': tailored_resume_latex,
            'tailored_cover_letter': tailored_cover_letter,
        }
        if ats_score is not None:
            payload['ats_score'] = ats_score
        if status is not None:
            payload['status'] = status
        response = (
            self._client.table('jobs')
            .update(payload)
            .eq('id', job_id)
            .execute()
        )
        if not response.data:
            raise ValueError(f'Job not found: {job_id}')
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f'Job not found: {job_id}')
        return job

    def add_interview(self, interview: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new interview record."""
        row = interview_to_row(interview)
        self._client.table('interviews').insert(row).execute()
        return interview

    def update_interview_status(self, interview_id: str, status: str) -> Dict[str, Any]:
        """Update interview status and return the updated record."""
        response = (
            self._client.table('interviews')
            .update({'status': status})
            .eq('id', interview_id)
            .execute()
        )
        if not response.data:
            raise ValueError(f'Interview not found: {interview_id}')
        rows = response.data or []
        return row_to_interview(rows[0])

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
        threshold: int = MATCH_SCORE_THRESHOLD,
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

    def list_scanned_job_rows(self, *, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return raw scanned_jobs rows for rescan engine."""
        query = self._client.table('scanned_jobs').select('*').order('scanned_at', desc=True)
        if limit is not None:
            query = query.limit(max(1, limit))
        response = query.execute()
        return response.data or []

    def get_scanned_job_by_key(self, dedupe_key: str) -> Optional[Dict[str, Any]]:
        """Fetch one scanned job row by dedupe key."""
        response = (
            self._client.table('scanned_jobs')
            .select('*')
            .eq('dedupe_key', dedupe_key)
            .maybe_single()
            .execute()
        )
        return response.data

    def promote_scanned_job_to_lead(self, dedupe_key: str) -> Dict[str, Any]:
        """Promote a scanned job into the Job Leads pipeline (manual override)."""
        row = self.get_scanned_job_by_key(dedupe_key)
        if not row:
            raise ValueError(f'Scanned job not found: {dedupe_key}')

        job = scanned_job_row_to_job(row)
        self.upsert_jobs([job])

        self._client.table('scanned_jobs').update(
            {'promoted_to_jobs': True, 'promotion_type': 'manual'}
        ).eq('dedupe_key', dedupe_key).execute()

        return job

    def get_scan_summary(self, *, threshold: int = MATCH_SCORE_THRESHOLD) -> Dict[str, Any]:
        """Aggregate scan insight statistics for dashboard summary header."""
        from packages.ai_engine.python.skill_matcher import filter_verified_gaps

        profile = self.get_profile()
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
                verified = filter_verified_gaps([skill_text], profile)
                if not verified:
                    continue
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
                and threshold - MATCH_SCORE_NEAR_MISS_BAND <= int(row.get('overall_score', row.get('score')) or 0) <= threshold
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
