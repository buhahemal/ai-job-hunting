import xml.etree.ElementTree as ET
from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.http import fetch_ok, get_text
from packages.scanner_sdk.python.normalize import build_canonical_job, strip_html

RSS_URL = 'https://weworkremotely.com/remote-jobs.rss'


class WeWorkRemotelyScanner(BaseScanner):
    """We Work Remotely public RSS feed — no API key required."""

    @property
    def name(self) -> str:
        return 'We Work Remotely'

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        xml_text = get_text(RSS_URL)
        if not xml_text:
            return []

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            print(f'[WeWorkRemotelyScanner] RSS parse error: {exc}')
            return []

        jobs: List[Dict] = []
        for item in root.findall('.//item'):
            title = (item.findtext('title') or '').strip()
            link = (item.findtext('link') or '').strip()
            description = (item.findtext('description') or '').strip()
            region = (item.findtext('region') or 'Remote').strip()
            if not title or not link:
                continue
            jobs.append(
                {
                    'title': title,
                    'link': link,
                    'description': description,
                    'region': region,
                }
            )
            if len(jobs) >= limit:
                break
        return jobs

    def normalize(self, raw_job: Dict) -> Dict:
        title = raw_job.get('title', 'Unknown Role')
        company = title
        role = title
        if ':' in title:
            company, role = [part.strip() for part in title.split(':', 1)]

        link = raw_job.get('link', '')
        job_id = link.rstrip('/').split('/')[-1] or title.replace(' ', '-').lower()

        return build_canonical_job(
            id=f'wwr-{job_id}',
            title=role,
            company=company,
            location=raw_job.get('region', 'Remote'),
            remote_type='Remote',
            source=self.name,
            url=link,
            description=strip_html(raw_job.get('description', '')),
        )

    def health_check(self) -> bool:
        return fetch_ok(RSS_URL)
