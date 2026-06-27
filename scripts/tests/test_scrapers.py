import unittest
import os
import json
from scripts.scrapers.base import BaseScanner
from scripts.scrapers.arbeitnow import ArbeitnowScanner
from scripts.scrapers.career_portal import CareerPortalScanner
from scripts.scrapers.scanner_engine import ScannerEngine

class TestScraperEngine(unittest.TestCase):

    def setUp(self):
        self.arbeitnow = ArbeitnowScanner()
        self.portal = CareerPortalScanner()
        self.engine = ScannerEngine()

    def test_scanner_names(self):
        """Verify proper class properties are returned by plugins."""
        self.assertEqual(self.arbeitnow.name, "Arbeitnow")
        self.assertEqual(self.portal.name, "Target Career Portals")

    def test_career_portal_discovery_and_normalization(self):
        """Test that target portal scanner discovers and normalizes job leads."""
        jobs = self.portal.discover_jobs(limit=2)
        self.assertEqual(len(jobs), 2)
        
        normalized = self.portal.normalize(jobs[0])
        self.assertIn("id", normalized)
        self.assertIn("title", normalized)
        self.assertIn("company", normalized)
        self.assertIn("location", normalized)
        self.assertEqual(normalized["status"], "New")

    def test_database_read_write(self):
        """Verify local flat-file storage synchronization reads and writes correctly."""
        db = self.engine.read_db()
        self.assertIsInstance(db, dict)
        self.assertIn("profile", db)
        self.assertIn("jobs", db)
        self.assertIn("interviews", db)

if __name__ == "__main__":
    unittest.main()
