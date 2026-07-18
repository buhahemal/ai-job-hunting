import html
import re
from typing import Dict, List
from urllib.parse import quote_plus

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.http import fetch_ok, get_json
from packages.scanner_sdk.python.normalize import build_canonical_job, strip_html

API_ROOT = 'https://hn.algolia.com/api/v1'
HIRING_QUERY = 'Ask HN: Who is hiring?'
URL_PATTERN = re.compile(r'https?://[^\s|<]+')


class HackerNewsScanner(BaseScanner):
    """Latest Hacker News “Who is Hiring?” thread via Algolia's public API."""

    @property
    def name(self) -> str:
        return 'HackerNews'

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        stories = get_json(
            f'{API_ROOT}/search_by_date?query={quote_plus(HIRING_QUERY)}&tags=story&hitsPerPage=5'
        )
        hits = (stories or {}).get('hits', [])
        story = next(
            (
                item
                for item in hits
                if HIRING_QUERY.lower() in str(item.get('title') or '').lower()
            ),
            None,
        )
        story_id = (story or {}).get('objectID')
        if not story_id:
            return []
        comments = get_json(
            f'{API_ROOT}/search?tags=comment,story_{story_id}&hitsPerPage={max(1, limit)}'
        )
        return [
            item
            for item in (comments or {}).get('hits', [])
            if isinstance(item, dict) and item.get('comment_text')
        ][:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        description = strip_html(html.unescape(str(raw_job.get('comment_text') or '')))
        parts = [part.strip() for part in description.split('|') if part.strip()]
        company = parts[0] if parts else 'Hacker News Company'
        title = parts[1] if len(parts) > 1 else 'Software Engineer'
        location = parts[2] if len(parts) > 2 else 'Remote / Unspecified'
        url_match = URL_PATTERN.search(description)
        return build_canonical_job(
            id=f"hn-{raw_job.get('objectID', 'unknown')}",
            title=title,
            company=company,
            location=location,
            remote_type='Remote' if 'remote' in location.lower() else 'Hybrid',
            source=self.name,
            url=url_match.group(0).rstrip('.,)') if url_match else '',
            description=description,
        )

    def health_check(self) -> bool:
        return fetch_ok(f'{API_ROOT}/search?tags=story&hitsPerPage=1')
