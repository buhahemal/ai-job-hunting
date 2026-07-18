"""Tests for scan insight rescore engine."""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from scraper.rescan_engine import RescanEngine, profile_hash, scanned_row_to_job
from packages.database.python.constants import MATCH_SCORE_THRESHOLD
from scraper.scanner_engine import JsonJobStore


PROFILE = {
    'fullName': 'Test User',
    'skills': ['Node.js', 'TypeScript', 'Express.js', 'Redis', 'Golang', 'AWS', 'Kubernetes'],
    'experience': [
        {
            'role': 'Platform Engineer',
            'company': 'Acme',
            'bullets': ['Built APIs with Express.js and Redis on AWS Lambda'],
        }
    ],
    'projects': [],
    'preferences': {'skillsKeywords': ['microservices']},
    'masterResumeLaTeX': '',
}


class TestRescanEngine(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self._temp_path = self._temp.name
        self._temp.write(
            json.dumps(
                {
                    'profile': PROFILE,
                    'jobs': [],
                    'interviews': [],
                    'scannedJobs': [
                        {
                            'dedupe_key': 'https://example.com/job-1',
                            'job_id': 'job-1',
                            'source': 'Greenhouse',
                            'score': 35,
                            'overall_score': 35,
                            'title': 'Backend Engineer',
                            'company': 'Acme',
                            'location': 'Remote',
                            'remote_type': 'Remote',
                            'required_skills': ['Node.js', 'Kubernetes', 'AWS'],
                            'preferred_skills': [],
                            'extracted_technologies': ['Node.js', 'Kubernetes', 'AWS'],
                            'matched_skills': [],
                            'missing_skills': ['Express.js', 'Redis', 'Golang'],
                            'application_url': 'https://example.com/job-1',
                            'promoted_to_jobs': False,
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

    def test_scanned_row_to_job_rebuilds_description(self):
        row = self.store.list_scanned_job_rows()[0]
        job = scanned_row_to_job(row)
        self.assertIn('Node.js', job['description'])
        self.assertEqual(job['requiredSkills'], ['Node.js', 'Kubernetes', 'AWS'])

    def test_profile_hash_is_stable(self):
        first = profile_hash(PROFILE)
        second = profile_hash(PROFILE)
        self.assertEqual(first, second)

    @patch('scraper.rescan_engine.enrich_job')
    def test_rescan_promotes_job_at_threshold_boundary(self, mock_enrich):
        mock_enrich.return_value = {
            'id': 'job-1',
            'title': 'Backend Engineer',
            'company': 'Acme',
            'source': 'Greenhouse',
            'url': 'https://example.com/job-1',
            'applicationUrl': 'https://example.com/job-1',
            'score': MATCH_SCORE_THRESHOLD,
            'matchInsights': {'skillMatchConfidence': 80},
        }

        RescanEngine(self.store, batch_size=1).run()

        updated = self.store.list_scanned_job_rows()[0]
        self.assertTrue(updated['promoted_to_jobs'])
        self.assertEqual(updated['promotion_type'], 'auto')
        persisted = self.store.read_db()['jobs']
        self.assertEqual([job['id'] for job in persisted], ['job-1'])

    @patch('packages.ai_engine.python.job_enricher.matcher.score_job')
    def test_rescan_updates_stale_inverted_gaps(self, mock_score):
        mock_score.return_value = {
            'score': 95,
            'extractedSkills': ['Node.js', 'Kubernetes', 'AWS'],
            'fitExplanation': 'Strong platform fit',
            'salaryEstimate': 'Not Specified',
            'seniority': 'Senior',
            'remoteType': 'Remote',
            'scorer': 'heuristic',
        }

        engine = RescanEngine(self.store, batch_size=1)
        count = engine.run()
        self.assertEqual(count, 1)

        updated = self.store.list_scanned_job_rows()[0]
        self.assertIn('profile_hash', updated)
        self.assertIn('rescored_at', updated)
        for skill in ('Express.js', 'Redis', 'Golang'):
            self.assertNotIn(skill, updated.get('missing_skills') or [], skill)
        self.assertGreaterEqual(int(updated.get('overall_score') or 0), MATCH_SCORE_THRESHOLD)


if __name__ == '__main__':
    unittest.main()
