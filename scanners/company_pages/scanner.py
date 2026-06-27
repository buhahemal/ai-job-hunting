import re
from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.http import fetch_ok
from packages.scanner_sdk.python.normalize import build_canonical_job
from scanners.company_pages.targets import (
    TARGET_COMPANY_NAMES,
    TARGET_FETCHERS,
    TARGET_HEALTH_URLS,
)


class CompanyPagesScanner(BaseScanner):
    """Discover jobs from curated company career portals (Google, Microsoft, EPAM, etc.)."""

    @property
    def name(self) -> str:
        return 'Company Career Pages'

    @property
    def target_companies(self) -> List[str]:
        return list(TARGET_COMPANY_NAMES)

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        if limit <= 0:
            return []

        per_company = max(1, limit // len(TARGET_FETCHERS))
        jobs: List[Dict] = []

        for _, fetcher in TARGET_FETCHERS:
            try:
                jobs.extend(fetcher(per_company))
            except Exception as exc:  # pragma: no cover - network/runtime guard
                print(f'[CompanyPagesScanner] fetch error: {exc}')
            if len(jobs) >= limit:
                break

        return jobs[:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        company = raw_job.get('_target_company', 'Unknown Company')
        source = raw_job.get('_target_source', self.name)
        job_id = raw_job.get('job_id', 'unknown')
        slug = re_safe_id(f'{company}-{job_id}')

        return build_canonical_job(
            id=f'cp-{slug}',
            title=raw_job.get('title', 'Unknown Role'),
            company=company,
            location=raw_job.get('location', 'Remote'),
            remote_type=raw_job.get('remote_type', 'Hybrid'),
            source=source,
            url=raw_job.get('url', ''),
            description=raw_job.get('description', ''),
        )

    def health_check(self) -> bool:
        return all(fetch_ok(url) for url in TARGET_HEALTH_URLS.values())


def re_safe_id(value: str) -> str:
    """Normalize an identifier for canonical job IDs."""
    cleaned = re.sub(r'[^a-zA-Z0-9_-]+', '-', str(value)).strip('-').lower()
    return cleaned or 'unknown'
