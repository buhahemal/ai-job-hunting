"""Estimate ATS alignment for a tailored resume against a job."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Set


def _normalize(value: str) -> str:
    return re.sub(r'[^a-z0-9+#./-]+', ' ', value.lower()).strip()


def _collect_resume_terms(resume: Dict[str, Any]) -> Set[str]:
    terms: Set[str] = set()
    for skill in resume.get('skills') or []:
        terms.add(_normalize(skill))
    for group in resume.get('skillGroups') or []:
        for item in group.get('items') or []:
            terms.add(_normalize(str(item)))
    for role in resume.get('experience') or []:
        terms.add(_normalize(role.get('techStack') or ''))
        for bullet in role.get('bullets') or []:
            if isinstance(bullet, dict):
                terms.add(_normalize(f"{bullet.get('title', '')} {bullet.get('body', '')}"))
    return {term for term in terms if term}


def _collect_job_terms(job: Dict[str, Any]) -> Set[str]:
    chunks: Iterable[str] = [
        job.get('title') or '',
        job.get('description') or '',
        ' '.join(job.get('extractedSkills') or []),
        ' '.join(job.get('requiredSkills') or []),
        ' '.join(job.get('preferredSkills') or []),
    ]
    terms: Set[str] = set()
    for chunk in chunks:
        for token in re.split(r'[\s,;/|]+', chunk.lower()):
            normalized = _normalize(token)
            if len(normalized) > 1:
                terms.add(normalized)
    return terms


def estimate_ats_score(resume: Dict[str, Any], job: Dict[str, Any]) -> int:
    """
    Heuristic ATS score based on skill/token overlap between resume and job.

    Returns:
        Integer score from 0 to 100.
    """
    resume_terms = _collect_resume_terms(resume)
    job_terms = _collect_job_terms(job)
    if not job_terms:
        return 70

    overlap = sum(
        1
        for term in job_terms
        if any(term in resume_term or resume_term in term for resume_term in resume_terms)
    )
    ratio = overlap / max(1, len(job_terms))
    return min(100, max(35, int(55 + ratio * 45)))
