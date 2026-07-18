from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.http import fetch_ok, get_json
from packages.scanner_sdk.python.normalize import build_canonical_job, strip_html

API_URL = 'https://remotive.com/api/remote-jobs?category=software-dev'


class RemotiveScanner(BaseScanner):
    """Remotive's public software-development jobs API."""

    @property
    def name(self) -> str:
        return 'Remotive'

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        data = get_json(API_URL)
        if not data:
            return []
        return [job for job in data.get('jobs', []) if isinstance(job, dict)][:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        location = str(raw_job.get('candidate_required_location') or 'Remote')
        return build_canonical_job(
            id=f"remotive-{raw_job.get('id', 'unknown')}",
            title=str(raw_job.get('title') or 'Unknown Role'),
            company=str(raw_job.get('company_name') or 'Unknown Company'),
            location=location,
            remote_type='Remote',
            source=self.name,
            url=str(raw_job.get('url') or ''),
            description=strip_html(str(raw_job.get('description') or '')),
        )

    def health_check(self) -> bool:
        return fetch_ok(API_URL)
