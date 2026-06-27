from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.config import parse_env_list
from packages.scanner_sdk.python.http import fetch_ok, get_json_any
from packages.scanner_sdk.python.normalize import build_canonical_job, infer_remote_type, strip_html


class LeverScanner(BaseScanner):
    """Lever public postings API (set LEVER_COMPANY_SITES=stripe,netflix)."""

    @property
    def name(self) -> str:
        return 'Lever'

    def _postings_url(self, site: str) -> str:
        return f'https://api.lever.co/v0/postings/{site}?mode=json'

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        sites = parse_env_list('LEVER_COMPANY_SITES')
        if not sites:
            print('[LeverScanner] LEVER_COMPANY_SITES not set — skipping.')
            return []

        jobs: List[Dict] = []
        per_site = max(1, limit // len(sites))
        for site in sites:
            data = get_json_any(self._postings_url(site))
            if not isinstance(data, list):
                continue
            for raw in data[:per_site]:
                raw['_lever_site'] = site
                jobs.append(raw)
            if len(jobs) >= limit:
                break
        return jobs[:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        location = (raw_job.get('categories') or {}).get('location', 'Remote')
        company = raw_job.get('_lever_site', 'Unknown Company')
        job_id = raw_job.get('id', raw_job.get('text', 'unknown'))

        return build_canonical_job(
            id=f'lever-{job_id}',
            title=raw_job.get('text', 'Unknown Role'),
            company=company.title(),
            location=location,
            remote_type=infer_remote_type(None, location),
            source=self.name,
            url=raw_job.get('hostedUrl', raw_job.get('applyUrl', '')),
            description=strip_html(raw_job.get('descriptionPlain', raw_job.get('description', ''))),
        )

    def health_check(self) -> bool:
        sites = parse_env_list('LEVER_COMPANY_SITES')
        if not sites:
            return True
        return fetch_ok(self._postings_url(sites[0]))
