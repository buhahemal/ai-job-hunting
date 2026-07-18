"""Tests for Supabase profile normalization."""

import unittest

from packages.database.python.profile import normalize_stored_profile


class TestStoredProfile(unittest.TestCase):
    def test_empty_profile_has_no_hardcoded_skills(self):
        profile = normalize_stored_profile({})
        self.assertEqual(profile['skills'], [])

    def test_preserves_supabase_skills(self):
        profile = normalize_stored_profile({'fullName': 'Jane', 'skills': ['Rust', 'Go']})
        self.assertEqual(profile['skills'], ['Rust', 'Go'])

    def test_match_settings_default(self):
        profile = normalize_stored_profile({})
        self.assertEqual(profile['matchSettings']['minMatchScore'], 80)
        self.assertEqual(profile['summary'], '')

    def test_does_not_inject_file_defaults_when_skills_missing(self):
        profile = normalize_stored_profile({'fullName': 'Jane Doe', 'email': 'jane@example.com'})
        self.assertEqual(profile['skills'], [])
        self.assertEqual(profile['fullName'], 'Jane Doe')


if __name__ == '__main__':
    unittest.main()
