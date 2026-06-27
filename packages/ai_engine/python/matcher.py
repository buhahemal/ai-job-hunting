"""Job scoring orchestrator with embedding and heuristic fallbacks."""

from __future__ import annotations

import os
from typing import Dict

from packages.ai_engine.python import embedding_scorer, heuristic_scorer


def preferred_scorer() -> str:
    """Return configured scorer preference (embedding or heuristic)."""
    return os.environ.get('AI_SCORER', 'embedding').strip().lower()


def score_job(job: Dict, profile: Dict) -> Dict:
    """
    Score a job using the configured fallback chain.

    Default order: local embeddings -> heuristic (₹0 path, no paid LLM APIs).
    """
    scorer = preferred_scorer()

    if scorer in ('embedding', 'auto', ''):
        try:
            return embedding_scorer.score(job, profile)
        except Exception as exc:
            print(f'[AIMatcher] Embedding scorer failed: {exc}')
        return heuristic_scorer.score(job, profile)

    if scorer == 'heuristic':
        return heuristic_scorer.score(job, profile)

    if scorer == 'embedding':
        return embedding_scorer.score(job, profile)

    raise ValueError(
        f'Unsupported AI_SCORER value: {scorer}. Supported values: embedding, heuristic.'
    )
