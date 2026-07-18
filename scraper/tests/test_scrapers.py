import json
import os
import tempfile
import unittest

from scanners.arbeitnow.scanner import ArbeitnowScanner
from scanners.company_pages.scanner import CompanyPagesScanner
from scanners.hackernews.scanner import HackerNewsScanner
from scanners.remotive.scanner import RemotiveScanner
from scraper.scanner_engine import JsonJobStore, ScannerEngine


class TestScraperEngine(unittest.TestCase):

    def setUp(self):
        self.arbeitnow = ArbeitnowScanner()
        self.portal = CompanyPagesScanner()
        self._temp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self._temp_path = self._temp.name
        json.dump(
            {
                'profile': {'fullName': 'Test User', 'skills': ['Python']},
                'jobs': [],
                'interviews': [],
            },
            self._temp,
        )
        self._temp.close()
        self.engine = ScannerEngine(store=JsonJobStore(path=self._temp_path))

    def tearDown(self):
        if os.path.exists(self._temp_path):
            os.remove(self._temp_path)

    def test_scanner_names(self):
        self.assertEqual(self.arbeitnow.name, 'Arbeitnow')
        self.assertEqual(self.portal.name, 'Company Career Pages')

    def test_company_pages_discovery_and_normalization(self):
        scanner = CompanyPagesScanner()
        normalized = scanner.normalize(
            {
                '_target_company': 'Stripe',
                '_target_source': 'Stripe Careers',
                'job_id': '123',
                'title': 'Backend Engineer',
                'url': 'https://stripe.com/jobs/listing/123',
                'location': 'Remote',
                'remote_type': 'Remote',
                'description': 'Payments infrastructure.',
            }
        )
        self.assertEqual(normalized['company'], 'Stripe')
        self.assertEqual(normalized['source'], 'Stripe Careers')
        self.assertEqual(normalized['status'], 'New')

    def test_remotive_normalizes_candidate_location_and_description(self):
        normalized = RemotiveScanner().normalize(
            {
                'id': 42,
                'title': 'Platform Engineer',
                'company_name': 'Remote Co',
                'candidate_required_location': 'Worldwide',
                'url': 'https://remotive.com/jobs/42',
                'description': '<p>Kubernetes and AWS</p>',
            }
        )
        self.assertEqual(normalized['source'], 'Remotive')
        self.assertEqual(normalized['location'], 'Worldwide')
        self.assertEqual(normalized['remoteType'], 'Remote')
        self.assertEqual(normalized['description'], 'Kubernetes and AWS')

    def test_hackernews_normalizes_who_is_hiring_comment(self):
        normalized = HackerNewsScanner().normalize(
            {
                'objectID': '123',
                'comment_text': 'Acme | Senior Backend Engineer | Remote Worldwide | https://acme.test/jobs',
                'created_at': '2026-07-01T00:00:00Z',
            }
        )
        self.assertEqual(normalized['source'], 'HackerNews')
        self.assertEqual(normalized['company'], 'Acme')
        self.assertEqual(normalized['title'], 'Senior Backend Engineer')
        self.assertEqual(normalized['remoteType'], 'Remote')
        self.assertEqual(normalized['url'], 'https://acme.test/jobs')

    def test_database_read_write(self):
        db = self.engine.read_db()
        self.assertIsInstance(db, dict)
        self.assertIn('profile', db)
        self.assertIn('jobs', db)
        self.assertIn('interviews', db)


if __name__ == '__main__':
    unittest.main()
