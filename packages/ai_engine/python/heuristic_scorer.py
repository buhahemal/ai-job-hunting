"""Deterministic heuristic job match scoring (zero-cost fallback)."""

from __future__ import annotations

from typing import Dict, List

from packages.ai_engine.python.salary_extractor import extract_salary


def score(job: Dict, profile: Dict) -> Dict:
    """Calculate a skill and preference weighted score without external APIs."""
    base_score = 50
    matched_skills: List[str] = []

    job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    skills = profile.get('skills') or []

    for skill in skills:
        if str(skill).lower() in job_text:
            matched_skills.append(str(skill))

    skill_ratio = len(matched_skills) / max(1, len(skills))
    base_score += int(skill_ratio * 30)

    remote_preference = (profile.get('preferences') or {}).get('remotePreference', 'Any')
    job_remote = job.get('remoteType', 'Hybrid')

    if job_remote == 'Remote' and remote_preference in ['Remote', 'Any']:
        base_score += 15
    elif job_remote == 'Hybrid' and remote_preference in ['Hybrid', 'Any']:
        base_score += 10

    target_companies = (profile.get('preferences') or {}).get('targetCompanies') or []
    job_company = str(job.get('company', '')).lower()
    if any(str(company).lower() in job_company for company in target_companies):
        base_score += 10

    final_score = min(100, max(0, base_score))
    explanation = (
        f'Heuristic alignment score of {final_score}% based on matching '
        f'{len(matched_skills)} primary skills: {", ".join(matched_skills[:5])}.'
    )
    if job_remote == 'Remote':
        explanation += ' Fully remote role matches work preferences.'

    return {
        'score': final_score,
        'extractedSkills': matched_skills,
        'fitExplanation': explanation,
        'salaryEstimate': extract_salary(job),
        'seniority': 'Senior' if 'senior' in str(job.get('title', '')).lower() else 'Mid-level',
        'remoteType': job.get('remoteType', 'Hybrid'),
        'scorer': 'heuristic',
    }
