import unittest
from unittest.mock import patch

from scanners.company_pages.scanner import CompanyPagesScanner
from scanners.company_pages.targets import TARGET_COMPANY_NAMES, fetch_microsoft_jobs


class TestCompanyPagesScanner(unittest.TestCase):
    SAMPLE_RAW = {
        '_target_company': 'Microsoft',
        '_target_source': 'Microsoft Careers',
        'job_id': '200041610',
        'title': 'Cloud Platform Engineer',
        'url': 'https://apply.careers.microsoft.com/careers/job/1',
        'location': 'Remote, US',
        'remote_type': 'Remote',
        'description': 'Build cloud platforms at Microsoft.',
    }

    MICROSOFT_FIXTURE = {
        'data': {
            'positions': [
                {
                    'id': 1,
                    'displayJobId': '200041610',
                    'name': 'Cloud Platform Engineer',
                    'locations': ['Remote, US'],
                    'department': 'Cloud',
                    'workLocationOption': 'remote',
                    'positionUrl': '/careers/job/1',
                }
            ]
        }
    }

    def test_target_company_list(self):
        self.assertEqual(
            TARGET_COMPANY_NAMES,
            ['Google', 'Microsoft', 'EPAM', 'Globant', 'Datadog', 'Stripe'],
        )

    def test_normalize_uses_company_source(self):
        scanner = CompanyPagesScanner()
        job = scanner.normalize(self.SAMPLE_RAW)
        self.assertEqual(job['company'], 'Microsoft')
        self.assertEqual(job['source'], 'Microsoft Careers')
        self.assertEqual(job['id'], 'cp-microsoft-200041610')
        self.assertEqual(job['remoteType'], 'Remote')

    @patch('scanners.company_pages.targets.get_json')
    def test_fetch_microsoft_jobs(self, mock_get_json):
        mock_get_json.return_value = self.MICROSOFT_FIXTURE
        jobs = fetch_microsoft_jobs(1)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['_target_company'], 'Microsoft')
        self.assertIn('apply.careers.microsoft.com', jobs[0]['url'])

    @patch('scanners.company_pages.targets.fetch_google_jobs', return_value=[])
    @patch('scanners.company_pages.targets.fetch_microsoft_jobs', return_value=[])
    @patch('scanners.company_pages.targets.fetch_epam_jobs', return_value=[])
    @patch('scanners.company_pages.targets.fetch_globant_jobs', return_value=[])
    @patch('scanners.company_pages.targets.fetch_datadog_jobs', return_value=[])
    @patch('scanners.company_pages.targets.fetch_stripe_jobs', return_value=[])
    def test_discover_jobs_calls_all_targets(self, *_mocks):
        scanner = CompanyPagesScanner()
        scanner.discover_jobs(limit=6)


if __name__ == '__main__':
    unittest.main()
