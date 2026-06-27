"""Cross-run job deduplication helpers for the scanner pipeline."""

from __future__ import annotations

import os
from typing import Dict, Iterable, List, Optional, Set


def job_dedupe_key(job: Dict) -> str:
    """
    Stable unique key for a canonical job.

    Prefers URL; falls back to lowercase title-company signature.
    """
    url = (job.get("url") or "").strip()
    if url:
        return url
    title = (job.get("title") or "").strip()
    company = (job.get("company") or "").strip()
    return f"{title}-{company}".lower()


def merge_scanned_keys(scanned_keys: Set[str], jobs: Iterable[Dict]) -> Set[str]:
    """Combine persisted scan registry with keys derived from saved jobs."""
    merged = set(scanned_keys)
    for job in jobs:
        merged.add(job_dedupe_key(job))
    return merged


def scan_run_id() -> Optional[str]:
    """Return optional scan run identifier from environment (e.g. GitHub Actions run)."""
    return os.environ.get("SCAN_RUN_ID") or os.environ.get("GITHUB_RUN_ID")


def scanned_job_record(
    job: Dict,
    *,
    score: int,
    promoted_to_jobs: bool = False,
    scan_run_id_value: Optional[str] = None,
) -> Dict:
    """
    Build a full scanned-job insight record for persistence.

    Accepts an enriched job dict (post ``enrich_job``) and maps summary fields,
    skill lists, and match outcome columns for the ``scanned_jobs`` table.
    """
    insights = job.get("matchInsights") or {}
    overall = int(insights.get("overallScore", score))
    run_id = scan_run_id_value if scan_run_id_value is not None else scan_run_id()

    return {
        "dedupe_key": job_dedupe_key(job),
        "job_id": job.get("id"),
        "source": job.get("source"),
        "score": overall,
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "remote_type": job.get("remoteType"),
        "canonical_role": job.get("canonicalRole"),
        "primary_stack": job.get("primaryStack"),
        "seniority": job.get("seniority"),
        "employment_type": job.get("employmentType"),
        "application_url": job.get("applicationUrl") or job.get("url"),
        "required_skills": job.get("requiredSkills") or [],
        "preferred_skills": job.get("preferredSkills") or [],
        "extracted_technologies": job.get("extractedTechnologies") or [],
        "overall_score": overall,
        "skill_match_score": insights.get("skillMatchScore"),
        "experience_match_score": insights.get("experienceMatchScore"),
        "ats_score": insights.get("atsScore"),
        "matched_skills": insights.get("matchedSkills") or [],
        "missing_skills": insights.get("missingSkills") or [],
        "missing_keywords": insights.get("missingKeywords") or [],
        "match_explanation": insights.get("matchExplanation") or job.get("fitExplanation"),
        "scorer": insights.get("scorer") or job.get("matchScorer"),
        "promoted_to_jobs": promoted_to_jobs,
        "scan_run_id": run_id,
        "skill_match_confidence": insights.get("skillMatchConfidence"),
    }


def dedupe_key_list(keys: Iterable[str]) -> List[str]:
    """Return sorted unique keys for stable JSON storage."""
    return sorted({key for key in keys if key})
