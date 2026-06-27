"""Re-score stored scan insights against the current profile."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Protocol

from packages.ai_engine.python.job_enricher import enrich_job
from packages.scanner_sdk.python.dedupe import scanned_job_record
from scraper.scanner_engine import ScanInsightBuffer


def profile_hash(profile: Dict) -> str:
    """Stable hash of profile JSON for rescore tracking."""
    payload = json.dumps(profile, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]


class RescanStore(Protocol):
    def get_profile(self) -> Dict: ...

    def list_scanned_job_rows(self, *, limit: Optional[int] = None) -> List[Dict]: ...

    def record_scanned_jobs(self, records: List[Dict]) -> None: ...


def scanned_row_to_job(row: Dict) -> Dict:
    """Rebuild a minimal canonical job dict from a scanned_jobs row."""
    return {
        'id': row.get('job_id') or row.get('dedupe_key'),
        'title': row.get('title') or 'Unknown Role',
        'company': row.get('company') or 'Unknown Company',
        'location': row.get('location') or 'Remote',
        'remoteType': row.get('remote_type') or row.get('remoteType') or 'Remote',
        'source': row.get('source') or 'Unknown',
        'url': row.get('application_url') or row.get('applicationUrl') or '',
        'applicationUrl': row.get('application_url') or row.get('applicationUrl') or '',
        'description': ' '.join(
            filter(
                None,
                [
                    row.get('title'),
                    row.get('canonical_role'),
                    row.get('primary_stack'),
                    ' '.join(row.get('required_skills') or []),
                    ' '.join(row.get('extracted_technologies') or []),
                ],
            )
        ),
        'requiredSkills': row.get('required_skills') or [],
        'preferredSkills': row.get('preferred_skills') or [],
        'extractedTechnologies': row.get('extracted_technologies') or [],
        'status': 'New',
    }


class RescanEngine:
    """Re-enrich scanned job rows with the current profile and upsert insights."""

    def __init__(self, store: RescanStore, *, batch_size: int = 10):
        self._store = store
        self._batch_size = batch_size

    def run(self, *, limit: Optional[int] = None) -> int:
        """
        Rescore scanned jobs and persist updated insight rows.

        Returns:
            Number of rows rescored.
        """
        profile = self._store.get_profile()
        p_hash = profile_hash(profile)
        rows = self._store.list_scanned_job_rows(limit=limit)
        buffer = ScanInsightBuffer(self._store, batch_size=self._batch_size)
        threshold = 75
        rescored = 0

        for row in rows:
            job = scanned_row_to_job(row)
            enriched = enrich_job(job, profile, existing_jobs=[])
            score = int(enriched.get('score', 0))
            promoted = bool(row.get('promoted_to_jobs')) or score > threshold
            promotion_type = row.get('promotion_type') or ('auto' if promoted and score > threshold else None)

            record = scanned_job_record(
                enriched,
                score=score,
                promoted_to_jobs=promoted,
            )
            record['promotion_type'] = promotion_type
            record['profile_hash'] = p_hash
            record['skill_match_confidence'] = (
                enriched.get('matchInsights') or {}
            ).get('skillMatchConfidence')
            record['rescored_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            buffer.append(record)
            rescored += 1

        buffer.flush()
        return rescored
