"""Tests for profile helper utilities."""

import unittest

from packages.database.python.profile_helpers import (
    flatten_experience_bullet,
    profile_to_master_resume,
    resolve_min_match_score,
    validate_profile_payload,
)
from packages.database.python.profile import normalize_stored_profile


class TestProfileHelpers(unittest.TestCase):
    def test_flatten_structured_bullet(self):
        text = flatten_experience_bullet({'title': 'Scale', 'body': 'Built microservices'})
        self.assertEqual(text, 'Scale: Built microservices')

    def test_profile_to_master_resume_maps_experience(self):
        profile = normalize_stored_profile(
            {
                'fullName': 'Jane Doe',
                'email': 'jane@example.com',
                'summary': 'Backend engineer',
                'skills': ['Python', 'AWS'],
                'experience': [
                    {
                        'role': 'Engineer',
                        'company': 'Acme',
                        'period': '2020 -- Present',
                        'bullets': ['Shipped APIs'],
                    }
                ],
            }
        )
        master = profile_to_master_resume(profile)
        self.assertEqual(master['fullName'], 'Jane Doe')
        self.assertEqual(master['experience'][0]['bullets'][0]['body'], 'Shipped APIs')

    def test_resolve_min_match_score_from_profile(self):
        profile = normalize_stored_profile({'matchSettings': {'minMatchScore': 82}})
        self.assertEqual(resolve_min_match_score(profile), 82)

    def test_validate_profile_payload_requires_email(self):
        with self.assertRaises(ValueError):
            validate_profile_payload({'fullName': 'Jane Doe'})


if __name__ == '__main__':
    unittest.main()
