"""Unit tests for database mappers."""

import os
import unittest

from packages.database.python.mappers import dedupe_indexes, job_to_row, row_to_job
from packages.database.python.client import is_supabase_configured, use_json_store


class TestJobMappers(unittest.TestCase):
    def test_job_to_row_maps_camel_case(self):
        job = {
            'id': 'arbeit-test',
            'title': 'Engineer',
            'company': 'Acme',
            'location': 'Remote',
            'remoteType': 'Remote',
            'source': 'Arbeitnow',
            'url': 'https://example.com/jobs/1',
            'description': 'Build things',
            'postedAt': '2026-01-01T00:00:00Z',
            'status': 'New',
            'score': 88,
            'extractedSkills': ['Python'],
            'fitExplanation': 'Strong match',
        }
        row = job_to_row(job)
        self.assertEqual(row['id'], 'arbeit-test')
        self.assertEqual(row['remote_type'], 'Remote')
        self.assertEqual(row['extracted_skills'], ['Python'])
        self.assertEqual(row['fit_explanation'], 'Strong match')

    def test_row_to_job_round_trip(self):
        row = {
            'id': 'arbeit-test',
            'source': 'Arbeitnow',
            'external_id': 'arbeit-test',
            'title': 'Engineer',
            'company': 'Acme',
            'location': 'Remote',
            'remote_type': 'Remote',
            'url': 'https://example.com/jobs/1',
            'description': 'Build things',
            'posted_at': '2026-01-01T00:00:00Z',
            'status': 'New',
            'score': 88,
            'fit_explanation': 'Strong match',
            'extracted_skills': ['Python'],
            'salary_estimate': None,
            'seniority': None,
            'notes': None,
            'tailored_resume_latex': None,
            'tailored_cover_letter': None,
            'ats_score': None,
        }
        job = row_to_job(row)
        self.assertEqual(job['remoteType'], 'Remote')
        self.assertEqual(job['extractedSkills'], ['Python'])

    def test_dedupe_indexes(self):
        jobs = [
            {'title': 'Dev', 'company': 'A', 'url': 'https://a.com/1'},
            {'title': 'Dev', 'company': 'B', 'url': 'https://b.com/1'},
        ]
        urls, signatures = dedupe_indexes(jobs)
        self.assertIn('https://a.com/1', urls)
        self.assertIn('dev-a', signatures)


class TestClientEnv(unittest.TestCase):
    def setUp(self):
        self._use_json = os.environ.pop('USE_JSON_STORE', None)
        self._supabase_url = os.environ.pop('SUPABASE_URL', None)
        self._service_key = os.environ.pop('SUPABASE_SERVICE_KEY', None)

    def tearDown(self):
        if self._use_json is not None:
            os.environ['USE_JSON_STORE'] = self._use_json
        if self._supabase_url is not None:
            os.environ['SUPABASE_URL'] = self._supabase_url
        if self._service_key is not None:
            os.environ['SUPABASE_SERVICE_KEY'] = self._service_key

    def test_use_json_store_default_false(self):
        self.assertFalse(use_json_store())

    def test_supabase_not_configured_without_env(self):
        self.assertFalse(is_supabase_configured())


if __name__ == '__main__':
    unittest.main()
