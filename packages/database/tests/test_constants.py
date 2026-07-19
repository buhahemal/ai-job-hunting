"""Ensure derived policy constants stay consistent."""

import unittest

from packages.database.python import constants as c


class TestPolicyConstants(unittest.TestCase):
    def test_default_match_threshold_populates_useful_feed(self):
        self.assertEqual(c.MATCH_SCORE_THRESHOLD, 75)

    def test_near_miss_is_threshold_minus_band(self):
        self.assertEqual(c.MATCH_SCORE_NEAR_MISS, c.MATCH_SCORE_THRESHOLD - c.MATCH_SCORE_NEAR_MISS_BAND)

    def test_low_confidence_uses_penalty_instead_of_hard_cap(self):
        self.assertEqual(c.LOW_CONFIDENCE_SCORE_PENALTY, 15)

    def test_default_scan_target_is_twenty_five_jobs(self):
        self.assertEqual(c.SCANNER_MIN_JOBS_PER_RUN, 25)

    def test_scanner_batch_size_positive(self):
        self.assertGreater(c.SCANNER_SCAN_INSIGHT_BATCH_SIZE, 0)


if __name__ == '__main__':
    unittest.main()
