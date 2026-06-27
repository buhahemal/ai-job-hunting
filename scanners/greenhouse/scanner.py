import os
from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.http import get_json, head_ok
from packages.scanner_sdk.python.normalize import build_canonical_job, strip_html


class GreenhouseScanner(BaseScanner):
    """Greenhouse Job Board API scanner (requires GREENHOUSE_BOARD_TOKEN env)."""

    @property
    def name(self) -> str:
        return 'Greenhouse'

    def _board_token(self) -> str:
        return os.environ.get('GREENHOUSE_BOARD_TOKEN', '').strip()

    def _jobs_url(self) -> str:
        return f'https://boards-api.greenhouse.io/v1/boards/{self._board_token()}/jobs'

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        token = self._board_token()
        if not token:
            print('[GreenhouseScanner] GREENHOUSE_BOARD_TOKEN not set — skipping.')
            return []

        data = get_json(self._jobs_url())
        if not data:
            return []
        return data.get('jobs', [])[:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        job_id = raw_job.get('id', 'unknown')
        location = raw_job.get('location', {}).get('name', 'Remote')
        company_name = 'Unknown Company'
        if isinstance(raw_job.get('company'), dict):
            company_name = raw_job['company'].get('name', company_name)

        return build_canonical_job(
            id=f'gh-{job_id}',
            title=raw_job.get('title', 'Unknown Role'),
            company=company_name,
            location=location,
            remote_type='Remote' if 'remote' in location.lower() else 'Hybrid',
            source=self.name,
            url=raw_job.get('absolute_url', ''),
            description=strip_html(raw_job.get('content', '')),
        )

    def health_check(self) -> bool:
        token = self._board_token()
        if not token:
            return True
        return head_ok(self._jobs_url())
