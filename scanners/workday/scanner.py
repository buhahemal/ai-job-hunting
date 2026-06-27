from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.config import parse_workday_sites
from packages.scanner_sdk.python.http import fetch_ok, get_json, post_json
from packages.scanner_sdk.python.normalize import build_canonical_job, infer_remote_type, strip_html


class WorkdayScanner(BaseScanner):
    """Workday CXS job search API (set WORKDAY_CAREER_SITES)."""

    @property
    def name(self) -> str:
        return 'Workday'

    def _base_url(self, site: Dict[str, str]) -> str:
        tenant = site['tenant']
        wd = site['wd']
        return f'https://{tenant}.{wd}.myworkdayjobs.com'

    def _cxs_base(self, site: Dict[str, str]) -> str:
        tenant = site['tenant']
        wd = site['wd']
        site_name = site['site']
        return f'{self._base_url(site)}/wday/cxs/{tenant}/{site_name}'

    def _jobs_url(self, site: Dict[str, str]) -> str:
        return f'{self._cxs_base(site)}/jobs'

    def _detail_url(self, site: Dict[str, str], external_path: str) -> str:
        path = external_path.lstrip('/')
        return f'{self._cxs_base(site)}/{path}'

    def _public_job_url(self, site: Dict[str, str], external_path: str) -> str:
        return f'{self._base_url(site)}/en-US/{site["site"]}{external_path}'

    def _fetch_description(self, site: Dict[str, str], external_path: str) -> str:
        detail = get_json(self._detail_url(site, external_path))
        if not detail:
            return ''
        posting = detail.get('jobPostingInfo', {})
        return strip_html(posting.get('jobDescription', ''))

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        sites = parse_workday_sites()
        if not sites:
            print('[WorkdayScanner] WORKDAY_CAREER_SITES not set — skipping.')
            return []

        jobs: List[Dict] = []
        per_site = max(1, limit // len(sites))
        for site in sites:
            payload = {'appliedFacets': {}, 'limit': per_site, 'offset': 0, 'searchText': ''}
            data = post_json(self._jobs_url(site), payload)
            if not data:
                continue

            for raw in data.get('jobPostings', [])[:per_site]:
                external_path = raw.get('externalPath', '')
                raw['_workday_site'] = site
                raw['_description'] = self._fetch_description(site, external_path)
                jobs.append(raw)
            if len(jobs) >= limit:
                break
        return jobs[:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        site = raw_job.get('_workday_site', {})
        tenant = site.get('tenant', 'unknown')
        external_path = raw_job.get('externalPath', '')
        bullet_fields = raw_job.get('bulletFields') or []
        external_id = bullet_fields[0] if bullet_fields else external_path.rsplit('_', 1)[-1]
        location = raw_job.get('locationsText', 'Unknown')
        description = raw_job.get('_description') or raw_job.get('postedOn', '')

        return build_canonical_job(
            id=f'workday-{tenant}-{external_id}',
            title=raw_job.get('title', 'Unknown Role'),
            company=tenant.title() if tenant != 'unknown' else 'Unknown Company',
            location=location,
            remote_type=infer_remote_type(None, location),
            source=self.name,
            url=self._public_job_url(site, external_path) if site and external_path else '',
            description=description,
        )

    def health_check(self) -> bool:
        sites = parse_workday_sites()
        if not sites:
            return True
        payload = {'appliedFacets': {}, 'limit': 1, 'offset': 0, 'searchText': ''}
        return post_json(self._jobs_url(sites[0]), payload) is not None
