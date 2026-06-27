from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.http import get_json, head_ok
from packages.scanner_sdk.python.normalize import build_canonical_job, infer_remote_type, strip_html

API_URL = 'https://www.arbeitnow.com/api/job-board-api'


class ArbeitnowScanner(BaseScanner):
    """Job scanner for the Arbeitnow public API."""

    @property
    def name(self) -> str:
        return 'Arbeitnow'

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        data = get_json(API_URL)
        if not data:
            return []
        return data.get('data', [])[:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        slug = raw_job.get('slug', '')
        location = raw_job.get('location', 'Remote')
        return build_canonical_job(
            id=f'arbeit-{slug}',
            title=raw_job.get('title', 'Unknown Role'),
            company=raw_job.get('company_name', 'Unknown Company'),
            location=location,
            remote_type=infer_remote_type(raw_job.get('remote'), location),
            source=self.name,
            url=raw_job.get('url', ''),
            description=strip_html(raw_job.get('description', '')),
        )

    def health_check(self) -> bool:
        return head_ok(API_URL)
