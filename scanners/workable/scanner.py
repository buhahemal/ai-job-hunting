from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.config import parse_env_list
from packages.scanner_sdk.python.http import fetch_ok, get_json
from packages.scanner_sdk.python.normalize import build_canonical_job, infer_remote_type, strip_html


class WorkableScanner(BaseScanner):
    """Workable public widget API (set WORKABLE_ACCOUNT_SLUGS)."""

    @property
    def name(self) -> str:
        return 'Workable'

    def _widget_url(self, account: str) -> str:
        return f'https://apply.workable.com/api/v1/widget/accounts/{account}'

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        accounts = parse_env_list('WORKABLE_ACCOUNT_SLUGS')
        if not accounts:
            print('[WorkableScanner] WORKABLE_ACCOUNT_SLUGS not set — skipping.')
            return []

        jobs: List[Dict] = []
        per_account = max(1, limit // len(accounts))
        for account in accounts:
            data = get_json(self._widget_url(account))
            if not data:
                continue
            company = data.get('name', account)
            for raw in data.get('jobs', [])[:per_account]:
                raw['_workable_account'] = account
                raw['_workable_company'] = company
                jobs.append(raw)
            if len(jobs) >= limit:
                break
        return jobs[:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        location_obj = raw_job.get('location') or {}
        if isinstance(location_obj, dict):
            location = location_obj.get('country', location_obj.get('city', 'Remote'))
        else:
            location = str(location_obj)
        company = raw_job.get('_workable_company', raw_job.get('_workable_account', 'Unknown'))
        shortcode = raw_job.get('shortcode', raw_job.get('id', 'unknown'))
        account = raw_job.get('_workable_account', 'unknown')

        return build_canonical_job(
            id=f'workable-{shortcode}',
            title=raw_job.get('title', 'Unknown Role'),
            company=company,
            location=location or 'Remote',
            remote_type=infer_remote_type(raw_job.get('telecommuting'), location or ''),
            source=self.name,
            url=raw_job.get('url', f'https://apply.workable.com/{account}/j/{shortcode}/'),
            description=strip_html(raw_job.get('description', raw_job.get('full_description', ''))),
        )

    def health_check(self) -> bool:
        accounts = parse_env_list('WORKABLE_ACCOUNT_SLUGS')
        if not accounts:
            return True
        return fetch_ok(self._widget_url(accounts[0]))
