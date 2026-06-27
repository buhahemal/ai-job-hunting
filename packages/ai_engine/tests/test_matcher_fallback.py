import os
import unittest
from unittest.mock import patch

from packages.ai_engine.python.matcher import score_job


class TestMatcherFallback(unittest.TestCase):
    JOB = {
        'title': 'Platform Engineer',
        'company': 'Stripe',
        'location': 'Remote',
        'remoteType': 'Remote',
        'description': 'Python platform role.',
    }

    PROFILE = {
        'fullName': 'Hemal Buha',
        'skills': ['Python', 'AWS'],
    }

    def setUp(self):
        os.environ['AI_SCORER'] = 'embedding'

    def tearDown(self):
        os.environ.pop('AI_SCORER', None)

    @patch('packages.ai_engine.python.matcher.embedding_scorer.score')
    def test_uses_embedding_scorer_first(self, mock_embedding):
        mock_embedding.return_value = {'score': 88, 'scorer': 'embedding', 'extractedSkills': []}
        result = score_job(self.JOB, self.PROFILE)
        self.assertEqual(result['scorer'], 'embedding')
        mock_embedding.assert_called_once()

    @patch('packages.ai_engine.python.matcher.heuristic_scorer.score')
    @patch('packages.ai_engine.python.matcher.embedding_scorer.score')
    def test_falls_back_to_heuristic_when_embedding_fails(self, mock_embedding, mock_heuristic):
        mock_embedding.side_effect = RuntimeError('model unavailable')
        mock_heuristic.return_value = {'score': 72, 'scorer': 'heuristic', 'extractedSkills': []}

        result = score_job(self.JOB, self.PROFILE)

        self.assertEqual(result['scorer'], 'heuristic')
        mock_heuristic.assert_called_once()

    @patch('packages.ai_engine.python.matcher.heuristic_scorer.score')
    def test_heuristic_scorer_mode(self, mock_heuristic):
        os.environ['AI_SCORER'] = 'heuristic'
        mock_heuristic.return_value = {'score': 65, 'scorer': 'heuristic', 'extractedSkills': []}
        result = score_job(self.JOB, self.PROFILE)
        self.assertEqual(result['scorer'], 'heuristic')


if __name__ == '__main__':
    unittest.main()
