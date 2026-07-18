import unittest

from packages.config.python.remote_policy import analyze_remote_eligibility


class TestRemotePolicy(unittest.TestCase):
    def test_worldwide_language_is_verified(self):
        result = analyze_remote_eligibility('Work from anywhere on our global distributed team')
        self.assertEqual(result.status, 'Verified Worldwide')
        self.assertGreater(result.score_adjustment, 0)

    def test_geo_restriction_is_likely_restricted(self):
        result = analyze_remote_eligibility('Remote, but applicants must reside in the US')
        self.assertEqual(result.status, 'Likely Restricted')
        self.assertLess(result.score_adjustment, 0)

    def test_clearance_is_hard_restriction(self):
        result = analyze_remote_eligibility('US citizenship and security clearance required')
        self.assertTrue(result.hard_restriction)


if __name__ == '__main__':
    unittest.main()
