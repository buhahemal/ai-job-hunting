import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from packages.scanner_sdk.python.apollo import extract_wellfound_jobs, parse_next_data_html
from packages.scanner_sdk.python.config import parse_workday_site, parse_workday_sites
from packages.scanner_sdk.python.normalize import build_canonical_job, infer_remote_type, strip_html
from packages.scanner_sdk.python.registry import get_registered_scanners
from scanners.ashby.scanner import AshbyScanner
from scanners.arbeitnow.scanner import ArbeitnowScanner
from scanners.greenhouse.scanner import GreenhouseScanner
from scanners.lever.scanner import LeverScanner
from scanners.remoteok.scanner import RemoteOkScanner
from scanners.smartrecruiters.scanner import SmartRecruitersScanner
from scanners.teamtailor.scanner import TeamtailorScanner
from scanners.wellfound.scanner import WellfoundScanner
from scanners.weworkremotely.scanner import WeWorkRemotelyScanner
from scanners.workable.scanner import WorkableScanner
from scanners.workday.scanner import WorkdayScanner

FIXTURES = Path(__file__).resolve().parents[3] / 'scanners' / 'wellfound' / 'fixtures'


class TestScannerSdk(unittest.TestCase):
    PHASE_4_SCANNERS = {
        'Greenhouse',
        'Lever',
        'SmartRecruiters',
        'Teamtailor',
        'Workable',
        'RemoteOK',
        'We Work Remotely',
        'Company Career Pages',
    }

    PHASE_5_SCANNERS = PHASE_4_SCANNERS | {
        'Arbeitnow',
        'Ashby',
        'Workday',
        'Wellfound',
    }

    def test_build_canonical_job(self):
        job = build_canonical_job(
            id='test-1',
            title='Engineer',
            company='Acme',
            location='Remote',
            remote_type='Remote',
            source='Test',
            url='https://example.com',
            description='Build things',
        )
        self.assertEqual(job['id'], 'test-1')
        self.assertEqual(job['status'], 'New')

    def test_strip_html(self):
        self.assertEqual(strip_html('<p>Hello</p>'), 'Hello')

    def test_infer_remote_type(self):
        self.assertEqual(infer_remote_type(True, 'NYC'), 'Remote')
        self.assertEqual(infer_remote_type(None, 'Hybrid NYC'), 'Hybrid')

    def test_registry_includes_phase_5_scanners(self):
        scanners = get_registered_scanners()
        names = {scanner.name for scanner in scanners}
        self.assertTrue(self.PHASE_5_SCANNERS.issubset(names))

    def test_lever_normalize(self):
        scanner = LeverScanner()
        job = scanner.normalize(
            {
                'id': 'abc',
                'text': 'Backend Engineer',
                '_lever_site': 'acme',
                'hostedUrl': 'https://jobs.lever.co/acme/abc',
                'categories': {'location': 'Remote'},
                'descriptionPlain': 'Build APIs',
            }
        )
        self.assertEqual(job['id'], 'lever-abc')
        self.assertEqual(job['company'], 'Acme')

    def test_remoteok_normalize(self):
        scanner = RemoteOkScanner()
        job = scanner.normalize(
            {
                'slug': 'backend-node',
                'position': 'Node Developer',
                'company': 'Startup',
                'location': 'Remote',
                'url': 'https://remoteok.com/remote-jobs/123',
                'description': 'Node.js role',
            }
        )
        self.assertEqual(job['id'], 'remoteok-backend-node')
        self.assertEqual(job['remoteType'], 'Remote')

    def test_weworkremotely_normalize(self):
        scanner = WeWorkRemotelyScanner()
        job = scanner.normalize(
            {
                'title': 'Acme Corp: Senior Engineer',
                'link': 'https://weworkremotely.com/remote-jobs/123',
                'description': '<p>Great role</p>',
                'region': 'Anywhere in the World',
            }
        )
        self.assertEqual(job['company'], 'Acme Corp')
        self.assertEqual(job['title'], 'Senior Engineer')

    def test_greenhouse_normalize(self):
        scanner = GreenhouseScanner()
        job = scanner.normalize(
            {
                'id': 42,
                'title': 'Platform Engineer',
                '_board_token': 'acme',
                'location': {'name': 'Remote'},
                'absolute_url': 'https://boards.greenhouse.io/acme/jobs/42',
                'content': '<p>Platform work</p>',
            }
        )
        self.assertEqual(job['id'], 'gh-42')

    def test_smartrecruiters_description(self):
        scanner = SmartRecruitersScanner()
        text = scanner._extract_description({'jobAd': 'Plain text role'})
        self.assertEqual(text, 'Plain text role')

    def test_teamtailor_normalize(self):
        scanner = TeamtailorScanner()
        job = scanner.normalize(
            {
                'id': 7,
                '_teamtailor_slug': 'acme-corp',
                'title': 'Developer',
                'location': 'Remote',
                'paths': {'careers_site': 'https://acme.teamtailor.com/jobs/7'},
                'body': 'Build products',
            }
        )
        self.assertTrue(job['id'].startswith('tt-acme-corp-'))

    def test_arbeitnow_normalize(self):
        scanner = ArbeitnowScanner()
        job = scanner.normalize(
            {
                'slug': 'backend-berlin-123',
                'title': 'Backend Engineer',
                'company_name': 'Acme GmbH',
                'location': 'Berlin',
                'remote': True,
                'url': 'https://www.arbeitnow.com/jobs/backend-berlin-123',
                'description': '<p>Python role</p>',
            }
        )
        self.assertEqual(job['id'], 'arbeit-backend-berlin-123')
        self.assertEqual(job['remoteType'], 'Remote')

    def test_ashby_normalize(self):
        scanner = AshbyScanner()
        job = scanner.normalize(
            {
                'id': '7458d4e9-da2e-47bd-98cb-adfda43d42b2',
                'title': 'Engineering Manager',
                '_ashby_slug': 'ashby',
                'location': 'Remote - EU',
                'isRemote': True,
                'jobUrl': 'https://jobs.ashbyhq.com/Ashby/7458d4e9',
                'descriptionPlain': 'Lead engineers',
            }
        )
        self.assertEqual(job['id'], 'ashby-7458d4e9-da2e-47bd-98cb-adfda43d42b2')
        self.assertEqual(job['remoteType'], 'Remote')

    def test_workday_normalize(self):
        scanner = WorkdayScanner()
        job = scanner.normalize(
            {
                'title': 'Senior Software Engineer',
                'externalPath': '/job/US-CA-Santa-Clara/Senior-Software-Engineer_JR123',
                'locationsText': 'US, CA, Santa Clara',
                'bulletFields': ['JR123'],
                '_workday_site': {'tenant': 'nvidia', 'wd': 'wd5', 'site': 'NVIDIAExternalCareerSite'},
                '_description': 'Build GPU software',
            }
        )
        self.assertEqual(job['id'], 'workday-nvidia-JR123')
        self.assertIn('nvidia.wd5.myworkdayjobs.com', job['url'])

    def test_workday_site_parser(self):
        parsed = parse_workday_site('nvidia:wd5:NVIDIAExternalCareerSite')
        self.assertEqual(parsed['tenant'], 'nvidia')
        self.assertEqual(parsed['wd'], 'wd5')

        url_parsed = parse_workday_site(
            'https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite'
        )
        self.assertEqual(url_parsed['site'], 'NVIDIAExternalCareerSite')

    def test_workday_sites_from_env(self):
        with patch.dict(os.environ, {'WORKDAY_CAREER_SITES': 'nvidia:wd5:NVIDIAExternalCareerSite'}):
            sites = parse_workday_sites()
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites[0]['tenant'], 'nvidia')

    def test_wellfound_apollo_extract(self):
        payload = json.loads((FIXTURES / 'next_data.json').read_text())
        jobs = extract_wellfound_jobs(payload)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['title'], 'Senior Backend Engineer')
        self.assertEqual(jobs[0]['_company_name'], 'Acme Startup')

    def test_wellfound_normalize(self):
        scanner = WellfoundScanner()
        job = scanner.normalize(
            {
                'id': 'job-1',
                'title': 'Senior Backend Engineer',
                'slug': 'senior-backend-engineer',
                '_company_name': 'Acme Startup',
                '_company_slug': 'acme-startup',
                '_location': 'Remote',
                '_remote': True,
                '_wellfound_path': 'role/l/remote',
                'descriptionSnippet': '<p>Build APIs</p>',
            }
        )
        self.assertEqual(job['id'], 'wellfound-job-1')
        self.assertEqual(job['company'], 'Acme Startup')

    def test_wellfound_parse_next_data_html(self):
        html = (
            '<html><head></head><body>'
            '<script id="__NEXT_DATA__" type="application/json">'
            '{"props":{"pageProps":{"apolloState":{"data":{}}}}}'
            '</script></body></html>'
        )
        parsed = parse_next_data_html(html)
        self.assertIsNotNone(parsed)
        self.assertIn('props', parsed)


if __name__ == '__main__':
    unittest.main()
