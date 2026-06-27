"""Tests for manual promotion of scanned jobs to Job Leads."""

import json
import os
import tempfile
import unittest

from scraper.scanner_engine import JsonJobStore


class TestPromoteScannedJob(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self._temp_path = self._temp.name
        self._temp.write(
            json.dumps(
                {
                    'profile': {'fullName': 'Test User', 'skills': ['Python']},
                    'jobs': [],
                    'interviews': [],
                    'scannedJobs': [
                        {
                            'dedupe_key': 'https://example.com/job-2',
                            'job_id': 'job-2',
                            'source': 'Lever',
                            'score': 68,
                            'overall_score': 68,
                            'title': 'Platform Engineer',
                            'company': 'Beta',
                            'location': 'Remote',
                            'remote_type': 'Remote',
                            'required_skills': ['Python'],
                            'matched_skills': ['Python'],
                            'missing_skills': ['Rust'],
                            'application_url': 'https://example.com/job-2',
                            'promoted_to_jobs': False,
                            'match_explanation': 'Near miss',
                            'skill_match_score': 70,
                            'experience_match_score': 65,
                            'ats_score': 60,
                        }
                    ],
                }
            )
        )
        self._temp.close()
        self.store = JsonJobStore(path=self._temp_path)

    def tearDown(self):
        if os.path.exists(self._temp_path):
            os.unlink(self._temp_path)

    def test_promote_scanned_job_creates_lead(self):
        job = self.store.promote_scanned_job_to_lead('https://example.com/job-2')
        self.assertEqual(job['id'], 'job-2')
        self.assertEqual(job['title'], 'Platform Engineer')
        self.assertIn('matchInsights', job)

        db = self.store.read_db()
        self.assertEqual(len(db['jobs']), 1)
        self.assertEqual(db['jobs'][0]['id'], 'job-2')

        row = self.store.list_scanned_job_rows()[0]
        self.assertTrue(row.get('promoted_to_jobs'))
        self.assertEqual(row.get('promotion_type'), 'manual')

    def test_promote_missing_row_raises(self):
        with self.assertRaises(ValueError):
            self.store.promote_scanned_job_to_lead('https://missing.example/job')


if __name__ == '__main__':
    unittest.main()
