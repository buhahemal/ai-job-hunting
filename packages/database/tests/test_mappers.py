"""Unit tests for database mappers."""

import os
import unittest

from packages.database.python.mappers import (
    dedupe_indexes,
    job_to_row,
    row_to_job,
    row_to_scanned_job,
    scanned_job_row_to_job,
    scanned_job_to_row,
)
from packages.database.python.client import is_supabase_configured


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

    def test_scanned_job_mapper_round_trip(self):
        record = {
            'dedupe_key': 'https://example.com/jobs/1',
            'job_id': 'job-1',
            'source': 'Greenhouse',
            'score': 68,
            'title': 'Platform Engineer',
            'company': 'Acme',
            'location': 'Remote',
            'remote_type': 'Remote',
            'canonical_role': 'Platform Engineer',
            'primary_stack': 'Kubernetes',
            'seniority': 'Senior',
            'employment_type': 'Full-time',
            'application_url': 'https://example.com/jobs/1',
            'required_skills': ['Kubernetes'],
            'preferred_skills': ['Terraform'],
            'extracted_technologies': ['Kubernetes'],
            'overall_score': 68,
            'skill_match_score': 60,
            'experience_match_score': 70,
            'ats_score': 55,
            'matched_skills': ['Python'],
            'missing_skills': ['Kubernetes'],
            'missing_keywords': ['SRE'],
            'match_explanation': 'Missing Kubernetes experience',
            'scorer': 'embedding',
            'promoted_to_jobs': False,
            'scan_run_id': 'run-123',
        }
        row = scanned_job_to_row(record)
        mapped = row_to_scanned_job({**row, 'scanned_at': '2026-06-27T00:00:00Z'})
        self.assertEqual(mapped['dedupeKey'], 'https://example.com/jobs/1')
        self.assertEqual(mapped['overallScore'], 68)
        self.assertEqual(mapped['missingSkills'], ['Kubernetes'])
        self.assertFalse(mapped['promotedToJobs'])

    def test_scanned_job_row_to_job_sets_extracted_skills_for_promotion(self):
        row = {
            'dedupe_key': 'https://example.com/jobs/1',
            'job_id': 'job-1',
            'source': 'Lever',
            'overall_score': 68,
            'title': 'Platform Engineer',
            'company': 'Acme',
            'matched_skills': ['Python', 'AWS'],
        }
        job = scanned_job_row_to_job(row)
        upsert_row = job_to_row(job)
        self.assertEqual(job['extractedSkills'], ['Python', 'AWS'])
        self.assertEqual(upsert_row['extracted_skills'], ['Python', 'AWS'])
        self.assertEqual(upsert_row['required_skills'], [])
        self.assertEqual(upsert_row['preferred_skills'], [])
        self.assertEqual(upsert_row['extracted_technologies'], [])

    def test_job_to_row_defaults_json_arrays_when_missing(self):
        row = job_to_row({'id': 'job-1', 'title': 'Engineer', 'company': 'Acme', 'source': 'Test'})
        self.assertEqual(row['extracted_skills'], [])
        self.assertEqual(row['required_skills'], [])
        self.assertEqual(row['preferred_skills'], [])
        self.assertEqual(row['extracted_technologies'], [])


class TestClientEnv(unittest.TestCase):
    def setUp(self):
        self._supabase_url = os.environ.pop('SUPABASE_URL', None)
        self._service_key = os.environ.pop('SUPABASE_SERVICE_KEY', None)

    def tearDown(self):
        if self._supabase_url is not None:
            os.environ['SUPABASE_URL'] = self._supabase_url
        if self._service_key is not None:
            os.environ['SUPABASE_SERVICE_KEY'] = self._service_key

    def test_supabase_not_configured_without_env(self):
        self.assertFalse(is_supabase_configured())


if __name__ == '__main__':
    unittest.main()
