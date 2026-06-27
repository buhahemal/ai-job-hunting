import os
import unittest

from scanners.arbeitnow import ArbeitnowScanner
from scanners.career_portal import CareerPortalScanner
from scraper.scanner_engine import ScannerEngine


class TestScraperEngine(unittest.TestCase):

    def setUp(self):
        self.arbeitnow = ArbeitnowScanner()
        self.portal = CareerPortalScanner()
        self.engine = ScannerEngine()

    def test_scanner_names(self):
        self.assertEqual(self.arbeitnow.name, "Arbeitnow")
        self.assertEqual(self.portal.name, "Target Career Portals")

    def test_career_portal_discovery_and_normalization(self):
        jobs = self.portal.discover_jobs(limit=2)
        self.assertEqual(len(jobs), 2)

        normalized = self.portal.normalize(jobs[0])
        self.assertIn("id", normalized)
        self.assertIn("title", normalized)
        self.assertIn("company", normalized)
        self.assertIn("location", normalized)
        self.assertEqual(normalized["status"], "New")

    def test_database_read_write(self):
        db = self.engine.read_db()
        self.assertIsInstance(db, dict)
        self.assertIn("profile", db)
        self.assertIn("jobs", db)
        self.assertIn("interviews", db)


if __name__ == "__main__":
    unittest.main()
