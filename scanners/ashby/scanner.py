from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.config import parse_env_list
from packages.scanner_sdk.python.http import fetch_ok, get_json
from packages.scanner_sdk.python.normalize import build_canonical_job, infer_remote_type, strip_html


class AshbyScanner(BaseScanner):
    """Ashby public job board API (set ASHBY_JOB_BOARD_SLUGS)."""

    @property
    def name(self) -> str:
        return 'Ashby'

    def _jobs_url(self, slug: str) -> str:
        return f'https://api.ashbyhq.com/posting-api/job-board/{slug}'

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        slugs = parse_env_list('ASHBY_JOB_BOARD_SLUGS')
        if not slugs:
            print('[AshbyScanner] ASHBY_JOB_BOARD_SLUGS not set — skipping.')
            return []

        jobs: List[Dict] = []
        per_board = max(1, limit // len(slugs))
        for slug in slugs:
            data = get_json(self._jobs_url(slug))
            if not data:
                continue
            for raw in data.get('jobs', [])[:per_board]:
                raw['_ashby_slug'] = slug
                jobs.append(raw)
            if len(jobs) >= limit:
                break
        return jobs[:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        job_id = raw_job.get('id', 'unknown')
        location = raw_job.get('location', 'Remote')
        slug = raw_job.get('_ashby_slug', 'unknown')
        description = raw_job.get('descriptionPlain') or raw_job.get('descriptionHtml', '')
        remote_type = 'Remote' if raw_job.get('isRemote') else infer_remote_type(None, location)

        return build_canonical_job(
            id=f'ashby-{job_id}',
            title=raw_job.get('title', 'Unknown Role'),
            company=slug.title() if slug != 'unknown' else 'Unknown Company',
            location=location,
            remote_type=remote_type,
            source=self.name,
            url=raw_job.get('jobUrl', raw_job.get('applyUrl', '')),
            description=strip_html(description),
        )

    def health_check(self) -> bool:
        slugs = parse_env_list('ASHBY_JOB_BOARD_SLUGS')
        if not slugs:
            return True
        return fetch_ok(self._jobs_url(slugs[0]))
