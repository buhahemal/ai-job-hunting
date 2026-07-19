from typing import Dict, Tuple

from packages.ai_engine.python import heuristic_scorer
from packages.ai_engine.python.matcher import score_job as engine_score_job
from packages.ai_engine.python.job_enricher import enrich_job as engine_enrich_job


class AIMatcher:
    """
    Facade for job scoring and resume tailoring.

    Scoring uses the Phase 6 ai_engine fallback chain:
    local embeddings -> heuristic (₹0, no paid LLM APIs).
    """

    def calculate_heuristic_score(self, job: Dict, profile: Dict) -> Dict:
        """Deterministic offline scoring helper (backward compatible)."""
        return heuristic_scorer.score(job, profile)

    def score_job(self, job: Dict, profile: Dict) -> Dict:
        """Score a job against the candidate profile."""
        return engine_score_job(job, profile)

    def enrich_job(self, job: Dict, profile: Dict, existing_jobs=None) -> Dict:
        """Normalize, classify, and enrich a job with full match insights."""
        return engine_enrich_job(job, profile, existing_jobs=existing_jobs or [])
