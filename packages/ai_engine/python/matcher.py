"""Job scoring orchestrator with embedding, Gemini, and heuristic fallbacks."""

from __future__ import annotations

import os
from typing import Dict

from packages.ai_engine.python import embedding_scorer, gemini_scorer, heuristic_scorer


def preferred_scorer() -> str:
    """Return configured scorer preference (embedding, gemini, heuristic)."""
    return os.environ.get('AI_SCORER', 'embedding').strip().lower()


def score_job(job: Dict, profile: Dict) -> Dict:
    """
    Score a job using the configured fallback chain.

    Default order: local embeddings -> optional Gemini -> heuristic.
    """
    scorer = preferred_scorer()

    if scorer in ('embedding', 'auto', ''):
        try:
            return embedding_scorer.score(job, profile)
        except Exception as exc:
            print(f'[AIMatcher] Embedding scorer failed: {exc}')

        if gemini_scorer.is_available():
            try:
                return gemini_scorer.score(job, profile)
            except Exception as exc:
                print(f'[AIMatcher] Gemini fallback failed: {exc}')

        return heuristic_scorer.score(job, profile)

    if scorer == 'gemini':
        if gemini_scorer.is_available():
            try:
                return gemini_scorer.score(job, profile)
            except Exception as exc:
                print(f'[AIMatcher] Gemini scorer failed: {exc}')
        return heuristic_scorer.score(job, profile)

    if scorer == 'heuristic':
        return heuristic_scorer.score(job, profile)

    raise ValueError(f'Unsupported AI_SCORER value: {scorer}')
