"""Tests for scan summary gap aggregation."""

import unittest

from packages.ai_engine.python.skill_matcher import filter_verified_gaps


PROFILE = {
    'skills': ['Express.js', 'Redis', 'Node.js', 'Kubernetes'],
    'experience': [],
    'projects': [],
    'preferences': {'skillsKeywords': []},
    'masterResumeLaTeX': '',
}


class TestScanSummaryGaps(unittest.TestCase):
    def test_aggregate_gaps_excludes_profile_skills(self):
        raw_gaps = ['Express.js', 'Redis', 'Rust', 'Golang']
        verified = filter_verified_gaps(raw_gaps, PROFILE)
        self.assertIn('Rust', verified)
        self.assertNotIn('Express.js', verified)
        self.assertNotIn('Redis', verified)


if __name__ == '__main__':
    unittest.main()
