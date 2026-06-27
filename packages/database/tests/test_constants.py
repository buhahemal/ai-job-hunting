"""Ensure derived policy constants stay consistent."""

import unittest

from packages.database.python import constants as c


class TestPolicyConstants(unittest.TestCase):
    def test_near_miss_is_threshold_minus_band(self):
        self.assertEqual(c.MATCH_SCORE_NEAR_MISS, c.MATCH_SCORE_THRESHOLD - c.MATCH_SCORE_NEAR_MISS_BAND)

    def test_promotion_cap_below_threshold(self):
        self.assertLess(c.LOW_CONFIDENCE_OVERALL_CAP, c.MATCH_SCORE_THRESHOLD)

    def test_scanner_batch_size_positive(self):
        self.assertGreater(c.SCANNER_SCAN_INSIGHT_BATCH_SIZE, 0)


if __name__ == '__main__':
    unittest.main()
