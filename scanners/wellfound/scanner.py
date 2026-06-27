from typing import Dict, List

from packages.scanner_sdk.python.apollo import extract_wellfound_jobs, parse_next_data_html
from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.config import parse_env_list
from packages.scanner_sdk.python.http import get_response, get_text
from packages.scanner_sdk.python.normalize import build_canonical_job, infer_remote_type, strip_html

BASE_URL = 'https://wellfound.com'


class WellfoundScanner(BaseScanner):
    """Wellfound search pages via __NEXT_DATA__ Apollo cache (set WELLFOUND_SEARCH_PATHS)."""

    @property
    def name(self) -> str:
        return 'Wellfound'

    def _search_paths(self) -> List[str]:
        return parse_env_list('WELLFOUND_SEARCH_PATHS')

    def _search_url(self, path: str, page: int = 1) -> str:
        normalized = path.strip('/')
        suffix = f'?page={page}' if page > 1 else ''
        return f'{BASE_URL}/{normalized}{suffix}'

    def _parse_jobs_from_html(self, html: str) -> List[Dict]:
        next_data = parse_next_data_html(html)
        if not next_data:
            return []
        return extract_wellfound_jobs(next_data)

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        paths = self._search_paths()
        if not paths:
            print('[WellfoundScanner] WELLFOUND_SEARCH_PATHS not set — skipping.')
            return []

        jobs: List[Dict] = []
        per_path = max(1, limit // len(paths))
        for path in paths:
            html = get_text(self._search_url(path))
            if not html:
                print(f'[WellfoundScanner] Failed to fetch {path} (often blocked server-side).')
                continue

            parsed = self._parse_jobs_from_html(html)
            if not parsed:
                print(f'[WellfoundScanner] No Apollo jobs parsed for {path}.')
                continue

            for raw in parsed[:per_path]:
                raw['_wellfound_path'] = path
                jobs.append(raw)
            if len(jobs) >= limit:
                break
        return jobs[:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        job_id = raw_job.get('id', raw_job.get('slug', 'unknown'))
        location = raw_job.get('_location', 'Remote')
        company = raw_job.get('_company_name', 'Unknown Company')
        company_slug = raw_job.get('_company_slug', '')
        slug = raw_job.get('slug', job_id)
        path = raw_job.get('_wellfound_path', 'role/l/remote').strip('/')

        url = raw_job.get('url', '')
        if not url and company_slug and slug:
            url = f'{BASE_URL}/{path}/jobs/{slug}'

        description = raw_job.get('description') or raw_job.get('descriptionSnippet', '')
        remote_type = 'Remote' if raw_job.get('_remote') else infer_remote_type(None, location)

        return build_canonical_job(
            id=f'wellfound-{job_id}',
            title=raw_job.get('title', raw_job.get('primaryRoleTitle', 'Unknown Role')),
            company=company,
            location=location,
            remote_type=remote_type,
            source=self.name,
            url=url,
            description=strip_html(description),
        )

    def health_check(self) -> bool:
        paths = self._search_paths()
        if not paths:
            return True
        response = get_response(self._search_url(paths[0]))
        if not response:
            return False
        if response.status_code == 403:
            print(
                '[WellfoundScanner] Health check got HTTP 403 — '
                'Wellfound often blocks server-side fetch; use browser export or skip.'
            )
            return False
        return bool(self._parse_jobs_from_html(response.text))
