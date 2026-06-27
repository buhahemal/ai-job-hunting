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

    def tailor_resume_and_cover_letter(self, job: Dict, profile: Dict) -> Tuple[str, str, int]:
        """
        Generate tailored LaTeX resume and cover letter for a target job.

        Uses the JSON master → tailor → LaTeX pipeline. Master JSON is never modified.
        """
        from packages.resume_engine.python.generator import generate_tailored_resume

        try:
            result = generate_tailored_resume(job)
            return result.latex, result.cover_letter, result.ats_score
        except Exception as exc:
            print(f"[AIMatcher] Resume engine fallback error: {exc}")
            master_latex = profile.get('masterResumeLaTeX') or ''
            cover_letter = f"""Dear Hiring Team at {job.get('company')},

I am writing to express my strong interest in the {job.get('title')} position.

Sincerely,
{profile.get('fullName', 'Candidate')}"""
            return master_latex, cover_letter, 70
