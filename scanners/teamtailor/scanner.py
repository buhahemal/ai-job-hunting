from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.config import parse_env_list
from packages.scanner_sdk.python.http import fetch_ok, get_json_any
from packages.scanner_sdk.python.normalize import build_canonical_job, infer_remote_type, strip_html


class TeamtailorScanner(BaseScanner):
    """Teamtailor public jobs.json feed (set TEAMTAILOR_COMPANY_SLUGS)."""

    @property
    def name(self) -> str:
        return 'Teamtailor'

    def _jobs_url(self, slug: str) -> str:
        return f'https://{slug}.teamtailor.com/jobs.json'

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        slugs = parse_env_list('TEAMTAILOR_COMPANY_SLUGS')
        if not slugs:
            print('[TeamtailorScanner] TEAMTAILOR_COMPANY_SLUGS not set — skipping.')
            return []

        jobs: List[Dict] = []
        per_slug = max(1, limit // len(slugs))
        for slug in slugs:
            data = get_json_any(self._jobs_url(slug))
            if not isinstance(data, list):
                continue
            for raw in data[:per_slug]:
                raw['_teamtailor_slug'] = slug
                jobs.append(raw)
            if len(jobs) >= limit:
                break
        return jobs[:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        slug = raw_job.get('_teamtailor_slug', 'unknown')
        location = raw_job.get('location', 'Remote')
        paths = raw_job.get('paths') or {}
        url = paths.get('careers_site', paths.get('apply', ''))
        job_id = raw_job.get('id', raw_job.get('uuid', 'unknown'))

        return build_canonical_job(
            id=f'tt-{slug}-{job_id}',
            title=raw_job.get('title', 'Unknown Role'),
            company=slug.replace('-', ' ').title(),
            location=location,
            remote_type=infer_remote_type(raw_job.get('remote'), location),
            source=self.name,
            url=url,
            description=strip_html(raw_job.get('body', raw_job.get('pitch', ''))),
        )

    def health_check(self) -> bool:
        slugs = parse_env_list('TEAMTAILOR_COMPANY_SLUGS')
        if not slugs:
            return True
        return fetch_ok(self._jobs_url(slugs[0]))
