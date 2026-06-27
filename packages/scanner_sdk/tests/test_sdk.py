import unittest

from packages.scanner_sdk.python.normalize import build_canonical_job, infer_remote_type, strip_html
from packages.scanner_sdk.python.registry import get_registered_scanners
from scanners.greenhouse.scanner import GreenhouseScanner
from scanners.lever.scanner import LeverScanner
from scanners.remoteok.scanner import RemoteOkScanner
from scanners.smartrecruiters.scanner import SmartRecruitersScanner
from scanners.teamtailor.scanner import TeamtailorScanner
from scanners.weworkremotely.scanner import WeWorkRemotelyScanner
from scanners.workable.scanner import WorkableScanner


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

    def test_registry_includes_phase_4_scanners(self):
        scanners = get_registered_scanners()
        names = {scanner.name for scanner in scanners}
        self.assertTrue(self.PHASE_4_SCANNERS.issubset(names))

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


if __name__ == '__main__':
    unittest.main()
