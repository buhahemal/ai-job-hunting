"""Fetch helpers for curated company career portals."""

from __future__ import annotations

import json
import re
from typing import Callable, Dict, List, Optional

from packages.scanner_sdk.python.http import fetch_ok, get_json, get_text
from packages.scanner_sdk.python.normalize import infer_remote_type, strip_html

TARGET_COMPANY_NAMES = [
    'Google',
    'Microsoft',
    'EPAM',
    'Globant',
    'Datadog',
    'Stripe',
]

GOOGLE_RESULTS_URL = (
    'https://www.google.com/about/careers/applications/jobs/results/'
    '?distance=50&page=1&q=software+engineer'
)
MICROSOFT_SEARCH_URL = (
    'https://apply.careers.microsoft.com/api/pcsx/search'
    '?domain=microsoft.com&query=&location=&sort_by=relevance'
)
EPAM_JOBS_URL = 'https://careers.epam.com/en/jobs'
GLOBANT_SR_API = 'https://api.smartrecruiters.com/v1/companies/Globant/postings'
GLOBANT_CAREERS_URL = 'https://careers.smartrecruiters.com/Globant'
MICROSOFT_CAREERS_BASE = 'https://apply.careers.microsoft.com'
EPAM_CAREERS_BASE = 'https://careers.epam.com'

GOOGLE_TITLE_PATTERN = re.compile(r'class="QJPWVe">([^<]{5,120})</h3>', re.IGNORECASE)


def _tag_raw_job(raw: Dict, *, company: str, source: str) -> Dict:
    tagged = dict(raw)
    tagged['_target_company'] = company
    tagged['_target_source'] = source
    return tagged


def fetch_google_jobs(limit: int) -> List[Dict]:
    """Parse public Google Careers search results (SSR HTML)."""
    html = get_text(GOOGLE_RESULTS_URL)
    if not html:
        print('[CompanyPagesScanner] Google Careers fetch failed.')
        return []

    job_ids = re.findall(r'jsdata="Aiqs8c;(\d+);\d+"', html)
    titles = [strip_tags(title) for title in GOOGLE_TITLE_PATTERN.findall(html)]

    jobs: List[Dict] = []
    for index, job_id in enumerate(job_ids[:limit]):
        title = titles[index] if index < len(titles) else f'Role {job_id}'
        jobs.append(
            _tag_raw_job(
                {
                    'job_id': job_id,
                    'title': title,
                    'url': f'https://www.google.com/about/careers/applications/jobs/results/{job_id}',
                    'location': 'Multiple locations',
                    'remote_type': 'Hybrid',
                    'description': f'{title} at Google. View full details on Google Careers.',
                },
                company='Google',
                source='Google Careers',
            )
        )
    return jobs


def fetch_microsoft_jobs(limit: int) -> List[Dict]:
    """Fetch roles from the public Microsoft PCSX search API."""
    url = f'{MICROSOFT_SEARCH_URL}&start=0&num={limit}'
    payload = get_json(url)
    if not payload:
        print('[CompanyPagesScanner] Microsoft Careers fetch failed.')
        return []

    positions = (payload.get('data') or {}).get('positions') or []
    jobs: List[Dict] = []
    for position in positions[:limit]:
        location = (position.get('locations') or ['Remote'])[0]
        jobs.append(
            _tag_raw_job(
                {
                    'job_id': position.get('displayJobId', position.get('id', 'unknown')),
                    'title': position.get('name', 'Unknown Role'),
                    'url': f"{MICROSOFT_CAREERS_BASE}{position.get('positionUrl', '')}",
                    'location': location,
                    'remote_type': _microsoft_remote_type(position.get('workLocationOption'), location),
                    'description': (
                        f"{position.get('name', 'Role')} — {position.get('department', 'Microsoft')} "
                        f"({location})."
                    ),
                },
                company='Microsoft',
                source='Microsoft Careers',
            )
        )
    return jobs


def fetch_epam_jobs(limit: int) -> List[Dict]:
    """Extract job listings from EPAM careers SSR payload."""
    html = get_text(EPAM_JOBS_URL)
    if not html:
        print('[CompanyPagesScanner] EPAM Careers fetch failed.')
        return []

    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
    if not match:
        print('[CompanyPagesScanner] EPAM Careers payload missing.')
        return []

    try:
        page_data = json.loads(match.group(1))
        initial_jobs = page_data['props']['pageProps']['initialJobs']['jobs']
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f'[CompanyPagesScanner] EPAM Careers parse error: {exc}')
        return []

    jobs: List[Dict] = []
    for job in initial_jobs[:limit]:
        seo = job.get('seo') or {}
        path = seo.get('url', '')
        location = _epam_location(job)
        jobs.append(
            _tag_raw_job(
                {
                    'job_id': job.get('uid', job.get('unique_id', 'unknown')),
                    'title': job.get('name', 'Unknown Role'),
                    'url': f'{EPAM_CAREERS_BASE}{path}' if path else EPAM_JOBS_URL,
                    'location': location,
                    'remote_type': _epam_remote_type(job.get('vacancy_type'), location),
                    'description': strip_html(job.get('description') or job.get('text') or job.get('name', '')),
                },
                company='EPAM',
                source='EPAM Careers',
            )
        )
    return jobs


def fetch_globant_jobs(limit: int) -> List[Dict]:
    """Fetch Globant roles from the SmartRecruiters public API."""
    url = f'{GLOBANT_SR_API}?limit={limit}'
    payload = get_json(url)
    if not payload:
        print('[CompanyPagesScanner] Globant Careers fetch failed.')
        return []

    postings = payload.get('content') or []
    if not postings:
        print('[CompanyPagesScanner] Globant Careers returned no public postings.')
        return []

    jobs: List[Dict] = []
    for posting in postings[:limit]:
        location_obj = posting.get('location') or {}
        location = location_obj.get('fullLocation', location_obj.get('city', 'Remote'))
        jobs.append(
            _tag_raw_job(
                {
                    'job_id': posting.get('id', 'unknown'),
                    'title': posting.get('name', 'Unknown Role'),
                    'url': posting.get('ref') or posting.get('postingUrl') or GLOBANT_CAREERS_URL,
                    'location': location or 'Remote',
                    'remote_type': infer_remote_type(posting.get('remote'), location or ''),
                    'description': posting.get('name', 'Globant role'),
                },
                company='Globant',
                source='Globant Careers',
            )
        )
    return jobs


def fetch_greenhouse_board_jobs(*, board_token: str, company: str, source: str, limit: int) -> List[Dict]:
    """Fetch roles from a public Greenhouse board (Stripe, Datadog)."""
    url = f'https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs'
    payload = get_json(url)
    if not payload:
        print(f'[CompanyPagesScanner] {source} fetch failed.')
        return []

    jobs: List[Dict] = []
    for raw in (payload.get('jobs') or [])[:limit]:
        location = (raw.get('location') or {}).get('name', 'Remote')
        jobs.append(
            _tag_raw_job(
                {
                    'job_id': raw.get('id', 'unknown'),
                    'title': raw.get('title', 'Unknown Role'),
                    'url': raw.get('absolute_url', ''),
                    'location': location,
                    'remote_type': infer_remote_type(None, location),
                    'description': strip_html(raw.get('content') or raw.get('title', '')),
                },
                company=company,
                source=source,
            )
        )
    return jobs


def fetch_stripe_jobs(limit: int) -> List[Dict]:
    return fetch_greenhouse_board_jobs(
        board_token='stripe',
        company='Stripe',
        source='Stripe Careers',
        limit=limit,
    )


def fetch_datadog_jobs(limit: int) -> List[Dict]:
    return fetch_greenhouse_board_jobs(
        board_token='datadog',
        company='Datadog',
        source='Datadog Careers',
        limit=limit,
    )


TARGET_FETCHERS: List[tuple[str, Callable[[int], List[Dict]]]] = [
    ('Google', fetch_google_jobs),
    ('Microsoft', fetch_microsoft_jobs),
    ('EPAM', fetch_epam_jobs),
    ('Globant', fetch_globant_jobs),
    ('Datadog', fetch_datadog_jobs),
    ('Stripe', fetch_stripe_jobs),
]

TARGET_HEALTH_URLS = {
    'Google': GOOGLE_RESULTS_URL,
    'Microsoft': f'{MICROSOFT_SEARCH_URL}&start=0&num=1',
    'EPAM': EPAM_JOBS_URL,
    'Globant': GLOBANT_CAREERS_URL,
    'Datadog': 'https://boards-api.greenhouse.io/v1/boards/datadog/jobs',
    'Stripe': 'https://boards-api.greenhouse.io/v1/boards/stripe/jobs',
}


def strip_tags(value: str) -> str:
    """Remove HTML entities/tags from a string."""
    return strip_html(value.replace('&amp;', '&'))


def _microsoft_remote_type(work_option: Optional[str], location: str) -> str:
    option = (work_option or '').lower()
    if option == 'remote':
        return 'Remote'
    if option in {'flex', 'flexible'}:
        return 'Hybrid'
    if 'remote' in location.lower():
        return 'Remote'
    if option == 'onsite':
        return 'On-site'
    return 'Hybrid'


def _epam_remote_type(vacancy_type: Optional[object], location: str) -> str:
    if isinstance(vacancy_type, str) and vacancy_type.lower() == 'remote':
        return 'Remote'
    return infer_remote_type(None, location)


def _epam_location(job: Dict) -> str:
    cities = job.get('city') or []
    if cities and isinstance(cities[0], dict):
        city = cities[0].get('name', '')
        country = (cities[0].get('country') or {}).get('name', '')
        if city and country:
            return f'{city}, {country}'
        if city:
            return city
    countries = job.get('country') or []
    if countries and isinstance(countries[0], dict):
        return countries[0].get('name', 'Remote')
    return 'Remote'
