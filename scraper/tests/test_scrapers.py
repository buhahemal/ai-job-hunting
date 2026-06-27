import os
import unittest

from scanners.arbeitnow.scanner import ArbeitnowScanner
from scanners.company_pages.scanner import CompanyPagesScanner
from scraper.scanner_engine import JsonJobStore, ScannerEngine


class TestScraperEngine(unittest.TestCase):

    def setUp(self):
        self.arbeitnow = ArbeitnowScanner()
        self.portal = CompanyPagesScanner()
        os.environ['USE_JSON_STORE'] = 'true'
        self.engine = ScannerEngine(store=JsonJobStore())

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

    def test_database_read_write(self):
        db = self.engine.read_db()
        self.assertIsInstance(db, dict)
        self.assertIn('profile', db)
        self.assertIn('jobs', db)
        self.assertIn('interviews', db)


if __name__ == '__main__':
    unittest.main()
