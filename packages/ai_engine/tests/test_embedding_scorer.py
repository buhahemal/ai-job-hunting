import unittest
from unittest.mock import patch

import numpy as np

from packages.ai_engine.python.embedding_scorer import score


class TestEmbeddingScorer(unittest.TestCase):
    PROFILE = {
        'fullName': 'Hemal Buha',
        'skills': ['Python', 'AWS'],
        'targetRoles': ['Platform Engineer'],
    }

    JOB = {
        'title': 'Platform Engineer',
        'company': 'Stripe',
        'location': 'Remote',
        'remoteType': 'Remote',
        'description': 'Python and AWS platform engineering role.',
    }

    @patch('packages.ai_engine.python.embedding_scorer.encode_texts')
    def test_score_returns_percentage_from_cosine(self, mock_encode):
        mock_encode.return_value = np.array(
            [
                [1.0, 0.0],
                [0.8, 0.6],
            ],
            dtype=np.float64,
        )

        result = score(self.JOB, self.PROFILE)

        self.assertEqual(result['scorer'], 'embedding')
        self.assertEqual(result['score'], 80)
        self.assertIn('Python', result['extractedSkills'])
        self.assertIn('Embedding match score', result['fitExplanation'])

    @patch('packages.ai_engine.python.embedding_scorer.encode_texts')
    def test_score_raises_when_vectors_missing(self, mock_encode):
        mock_encode.side_effect = ValueError('encode failed')
        with self.assertRaises(ValueError):
            score(self.JOB, self.PROFILE)


if __name__ == '__main__':
    unittest.main()
