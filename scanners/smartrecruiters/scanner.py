from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.config import parse_env_list
from packages.scanner_sdk.python.http import fetch_ok, get_json
from packages.scanner_sdk.python.normalize import build_canonical_job, infer_remote_type, strip_html


class SmartRecruitersScanner(BaseScanner):
    """SmartRecruiters public postings API (set SMARTRECRUITERS_COMPANIES)."""

    @property
    def name(self) -> str:
        return 'SmartRecruiters'

    def _postings_url(self, company: str) -> str:
        return f'https://api.smartrecruiters.com/v1/companies/{company}/postings'

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        companies = parse_env_list('SMARTRECRUITERS_COMPANIES')
        if not companies:
            print('[SmartRecruitersScanner] SMARTRECRUITERS_COMPANIES not set — skipping.')
            return []

        jobs: List[Dict] = []
        per_company = max(1, limit // len(companies))
        for company in companies:
            data = get_json(self._postings_url(company))
            if not data:
                continue
            for raw in data.get('content', [])[:per_company]:
                raw['_sr_company'] = company
                jobs.append(raw)
            if len(jobs) >= limit:
                break
        return jobs[:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        location_obj = raw_job.get('location') or {}
        location = location_obj.get('fullLocation', location_obj.get('city', 'Remote'))
        company = (raw_job.get('company') or {}).get('name', raw_job.get('_sr_company', 'Unknown'))
        job_id = raw_job.get('id', 'unknown')
        description = self._extract_description(raw_job)

        return build_canonical_job(
            id=f'sr-{job_id}',
            title=raw_job.get('name', 'Unknown Role'),
            company=company,
            location=location or 'Remote',
            remote_type=infer_remote_type(raw_job.get('remote'), location or ''),
            source=self.name,
            url=(raw_job.get('ref') or raw_job.get('postingUrl', '')),
            description=description,
        )

    @staticmethod
    def _extract_description(raw_job: Dict) -> str:
        job_ad = raw_job.get('jobAd')
        if isinstance(job_ad, str):
            return strip_html(job_ad)
        if isinstance(job_ad, dict):
            parts: List[str] = []
            for section in (job_ad.get('sections') or {}).values():
                if isinstance(section, dict) and section.get('text'):
                    parts.append(section['text'])
            if parts:
                return strip_html(' '.join(parts))
        return raw_job.get('name', 'Unknown Role')

    def health_check(self) -> bool:
        companies = parse_env_list('SMARTRECRUITERS_COMPANIES')
        if not companies:
            return True
        return fetch_ok(self._postings_url(companies[0]))
