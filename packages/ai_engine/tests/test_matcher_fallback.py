import os
import unittest
from unittest.mock import patch

from packages.ai_engine.python import gemini_scorer
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
        gemini_scorer.reset_client_cache()

    def tearDown(self):
        os.environ.pop('AI_SCORER', None)
        gemini_scorer.reset_client_cache()

    @patch('packages.ai_engine.python.matcher.embedding_scorer.score')
    def test_uses_embedding_scorer_first(self, mock_embedding):
        mock_embedding.return_value = {'score': 88, 'scorer': 'embedding', 'extractedSkills': []}
        result = score_job(self.JOB, self.PROFILE)
        self.assertEqual(result['scorer'], 'embedding')
        mock_embedding.assert_called_once()

    @patch('packages.ai_engine.python.matcher.heuristic_scorer.score')
    @patch('packages.ai_engine.python.matcher.gemini_scorer.score')
    @patch('packages.ai_engine.python.matcher.gemini_scorer.is_available', return_value=True)
    @patch('packages.ai_engine.python.matcher.embedding_scorer.score')
    def test_falls_back_to_gemini_then_heuristic(
        self,
        mock_embedding,
        _mock_available,
        mock_gemini,
        mock_heuristic,
    ):
        mock_embedding.side_effect = RuntimeError('model unavailable')
        mock_gemini.side_effect = RuntimeError('gemini unavailable')
        mock_heuristic.return_value = {'score': 72, 'scorer': 'heuristic', 'extractedSkills': []}

        result = score_job(self.JOB, self.PROFILE)

        self.assertEqual(result['scorer'], 'heuristic')
        mock_gemini.assert_called_once()
        mock_heuristic.assert_called_once()

    @patch('packages.ai_engine.python.matcher.heuristic_scorer.score')
    @patch('packages.ai_engine.python.matcher.gemini_scorer.is_available', return_value=False)
    @patch('packages.ai_engine.python.matcher.embedding_scorer.score')
    def test_skips_gemini_without_api_key(self, mock_embedding, _mock_available, mock_heuristic):
        mock_embedding.side_effect = RuntimeError('model unavailable')
        mock_heuristic.return_value = {'score': 72, 'scorer': 'heuristic', 'extractedSkills': []}

        result = score_job(self.JOB, self.PROFILE)

        self.assertEqual(result['scorer'], 'heuristic')


if __name__ == '__main__':
    unittest.main()
