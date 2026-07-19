from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.http import fetch_ok, get_json_any
from packages.scanner_sdk.python.normalize import (
    build_canonical_job,
    infer_remote_type,
    is_engineering_job_title,
    strip_html,
)

API_URL = 'https://remoteok.com/api'


class RemoteOkScanner(BaseScanner):
    """RemoteOK public JSON API — no API key required."""

    @property
    def name(self) -> str:
        return 'RemoteOK'

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        data = get_json_any(API_URL)
        if not isinstance(data, list):
            return []

        jobs: List[Dict] = []
        for item in data:
            if not isinstance(item, dict) or not item.get('position'):
                continue
            position = str(item.get('position', ''))
            if not is_engineering_job_title(position):
                continue
            jobs.append(item)
            if len(jobs) >= limit:
                break
        return jobs

    def normalize(self, raw_job: Dict) -> Dict:
        slug = raw_job.get('slug', raw_job.get('id', 'unknown'))
        location = raw_job.get('location', 'Remote')
        company = raw_job.get('company', 'Unknown Company')
        description = raw_job.get('description', '')
        if not description and raw_job.get('tags'):
            description = 'Tags: ' + ', '.join(raw_job.get('tags', []))

        return build_canonical_job(
            id=f'remoteok-{slug}',
            title=raw_job.get('position', 'Unknown Role'),
            company=company,
            location=location,
            remote_type=infer_remote_type(True, location),
            source=self.name,
            url=raw_job.get('url', raw_job.get('apply_url', '')),
            description=strip_html(description),
        )

    def health_check(self) -> bool:
        return fetch_ok(API_URL)
