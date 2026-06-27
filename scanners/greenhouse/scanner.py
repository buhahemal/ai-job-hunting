import os
from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.config import parse_env_list
from packages.scanner_sdk.python.http import fetch_ok, get_json
from packages.scanner_sdk.python.normalize import build_canonical_job, strip_html


class GreenhouseScanner(BaseScanner):
    """Greenhouse Job Board API (public boards — set GREENHOUSE_BOARD_TOKENS)."""

    @property
    def name(self) -> str:
        return 'Greenhouse'

    def _board_tokens(self) -> List[str]:
        tokens = parse_env_list('GREENHOUSE_BOARD_TOKENS')
        legacy = os.environ.get('GREENHOUSE_BOARD_TOKEN', '').strip()
        if legacy and legacy not in tokens:
            tokens.append(legacy)
        return tokens

    def _jobs_url(self, token: str) -> str:
        return f'https://boards-api.greenhouse.io/v1/boards/{token}/jobs'

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        tokens = self._board_tokens()
        if not tokens:
            print('[GreenhouseScanner] GREENHOUSE_BOARD_TOKENS not set — skipping.')
            return []

        jobs: List[Dict] = []
        per_board = max(1, limit // len(tokens))
        for token in tokens:
            data = get_json(self._jobs_url(token))
            if not data:
                continue
            for raw in data.get('jobs', [])[:per_board]:
                raw['_board_token'] = token
                jobs.append(raw)
            if len(jobs) >= limit:
                break
        return jobs[:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        job_id = raw_job.get('id', 'unknown')
        location = raw_job.get('location', {}).get('name', 'Remote')
        company_name = raw_job.get('_board_token', 'Unknown Company')
        if isinstance(raw_job.get('company'), dict):
            company_name = raw_job['company'].get('name', company_name)

        return build_canonical_job(
            id=f'gh-{job_id}',
            title=raw_job.get('title', 'Unknown Role'),
            company=company_name,
            location=location,
            remote_type='Remote' if 'remote' in location.lower() else 'Hybrid',
            source=self.name,
            url=raw_job.get('absolute_url', ''),
            description=strip_html(raw_job.get('content', '')),
        )

    def health_check(self) -> bool:
        tokens = self._board_tokens()
        if not tokens:
            return True
        return fetch_ok(self._jobs_url(tokens[0]))
