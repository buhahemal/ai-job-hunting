"""Tests for profile save/import service."""

import unittest
from unittest.mock import patch

from apps.api.profile_service import import_profile_payload, prepare_profile_for_save
from packages.database.python.profile import normalize_stored_profile


SAMPLE_PROFILE = normalize_stored_profile(
    {
        'fullName': 'Jane Doe',
        'email': 'jane@example.com',
        'summary': 'Platform engineer',
        'skills': ['Python', 'AWS'],
        'targetRoles': ['Backend Engineer'],
        'experience': [
            {
                'role': 'Engineer',
                'company': 'Acme',
                'period': '2020 -- Present',
                'bullets': ['Built APIs'],
            }
        ],
        'preferences': {'skillsKeywords': ['Python']},
    }
)


class TestProfileService(unittest.TestCase):
    @patch('apps.api.profile_service.regenerate_master_latex', return_value='\\documentclass{}')
    def test_prepare_profile_for_save_regenerates_latex(self, _mock_render):
        saved = prepare_profile_for_save(SAMPLE_PROFILE)
        self.assertEqual(saved['masterResumeLaTeX'], '\\documentclass{}')

    @patch('apps.api.profile_service.regenerate_master_latex', return_value='\\documentclass{}')
    def test_import_profile_payload_merges_fields(self, _mock_render):
        existing = normalize_stored_profile({'fullName': 'Jane Doe', 'email': 'jane@example.com'})
        imported = {'summary': 'Updated summary', 'skills': ['Go', 'Rust']}
        profile, summary = import_profile_payload(existing, imported)
        self.assertEqual(profile['summary'], 'Updated summary')
        self.assertEqual(profile['skills'], ['Go', 'Rust'])
        self.assertIn('summary', summary['appliedKeys'])


if __name__ == '__main__':
    unittest.main()
