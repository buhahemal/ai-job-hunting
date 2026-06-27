"""Unit tests for embedding duplicate detection."""

import unittest
from unittest.mock import patch

import numpy as np

from packages.ai_engine.python.duplicate_detector import (
    build_duplicate_text,
    find_embedding_duplicate,
)


class TestDuplicateDetector(unittest.TestCase):
    def test_build_duplicate_text_includes_title_and_company(self):
        text = build_duplicate_text(
            {
                'title': 'Backend Engineer',
                'company': 'Acme',
                'description': 'Build APIs with Python.',
            }
        )
        self.assertIn('Backend Engineer', text)
        self.assertIn('Acme', text)

    @patch('packages.ai_engine.python.duplicate_detector.encode_texts')
    def test_detects_embedding_duplicate(self, mock_encode):
        mock_encode.return_value = np.array(
            [
                [1.0, 0.0],
                [0.99, 0.01],
            ],
            dtype=np.float64,
        )
        job = {
            'id': 'new-1',
            'title': 'Senior Platform Engineer',
            'company': 'Acme',
            'description': 'Kubernetes platform work.',
        }
        existing = [
            {
                'id': 'old-1',
                'title': 'Senior Platform Engineer',
                'company': 'Acme',
                'description': 'Kubernetes platform engineering role.',
            }
        ]
        is_dup, duplicate_of = find_embedding_duplicate(job, existing, threshold=0.92)
        self.assertTrue(is_dup)
        self.assertEqual(duplicate_of, 'old-1')

    @patch('packages.ai_engine.python.duplicate_detector.encode_texts')
    def test_skips_different_company(self, mock_encode):
        mock_encode.return_value = np.array(
            [
                [1.0, 0.0],
                [1.0, 0.0],
            ],
            dtype=np.float64,
        )
        job = {'id': 'new', 'title': 'Engineer', 'company': 'Acme', 'description': 'Work'}
        existing = [{'id': 'old', 'title': 'Engineer', 'company': 'Beta', 'description': 'Work'}]
        is_dup, duplicate_of = find_embedding_duplicate(job, existing, threshold=0.92)
        self.assertFalse(is_dup)
        self.assertIsNone(duplicate_of)


if __name__ == '__main__':
    unittest.main()
