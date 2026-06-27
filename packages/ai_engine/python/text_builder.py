"""Build normalized text payloads for embedding-based scoring."""

from __future__ import annotations

from typing import Dict, List

from packages.database.python.profile_helpers import flatten_experience_bullet


def build_candidate_text(profile: Dict) -> str:
    """Serialize candidate profile into a single embedding input string."""
    sections: List[str] = []

    full_name = profile.get('fullName', '').strip()
    if full_name:
        sections.append(f'Candidate: {full_name}')

    location = profile.get('location', '').strip()
    if location:
        sections.append(f'Location: {location}')

    summary = profile.get('summary', '').strip()
    if summary:
        sections.append(f'Summary: {summary}')

    target_roles = profile.get('targetRoles') or []
    if target_roles:
        sections.append('Target roles: ' + ', '.join(str(role) for role in target_roles))

    skills = profile.get('skills') or []
    if skills:
        sections.append('Skills: ' + ', '.join(str(skill) for skill in skills))

    for exp in profile.get('experience') or []:
        role = exp.get('role', 'Role')
        company = exp.get('company', 'Company')
        sections.append(f'Experience: {role} at {company}')
        for bullet in exp.get('bullets') or []:
            sections.append(flatten_experience_bullet(bullet))

    for project in profile.get('projects') or []:
        title = project.get('title', 'Project')
        sections.append(f'Project: {title}')
        if project.get('description'):
            sections.append(str(project['description']))
        tech = project.get('tech') or []
        if tech:
            sections.append('Technologies: ' + ', '.join(str(item) for item in tech))

    preferences = profile.get('preferences') or {}
    remote_preference = preferences.get('remotePreference')
    if remote_preference:
        sections.append(f'Remote preference: {remote_preference}')

    target_companies = preferences.get('targetCompanies') or []
    if target_companies:
        sections.append('Target companies: ' + ', '.join(str(item) for item in target_companies))

    return '\n'.join(section for section in sections if section.strip())


def build_job_text(job: Dict) -> str:
    """Serialize a canonical job record into a single embedding input string."""
    sections = [
        f"Title: {job.get('title', 'Unknown Role')}",
        f"Company: {job.get('company', 'Unknown Company')}",
        f"Location: {job.get('location', 'Remote')}",
        f"Remote type: {job.get('remoteType', 'Hybrid')}",
        f"Description: {job.get('description', '')}",
    ]
    return '\n'.join(section for section in sections if section.strip())


def extract_matched_skills(job: Dict, profile: Dict) -> List[str]:
    """Return profile skills that appear in the job title or description."""
    job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    matched: List[str] = []
    for skill in profile.get('skills') or []:
        if str(skill).lower() in job_text:
            matched.append(str(skill))
    return matched


def infer_seniority(title: str) -> str:
    """Infer seniority label from a job title."""
    title_lower = (title or '').lower()
    if any(token in title_lower for token in ('principal', 'staff', 'lead', 'architect')):
        return 'Senior'
    if 'senior' in title_lower:
        return 'Senior'
    if any(token in title_lower for token in ('junior', 'intern', 'graduate')):
        return 'Junior'
    return 'Mid-level'
