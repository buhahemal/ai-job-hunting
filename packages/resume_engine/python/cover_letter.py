"""Plain-text cover letter generation from tailored resume context."""

from __future__ import annotations

from typing import Any, Dict, List


def _top_skills(resume: Dict[str, Any], limit: int = 8) -> List[str]:
    skills = resume.get('skills') or []
    return [skill for skill in skills[:limit] if skill]


def generate_cover_letter(resume: Dict[str, Any], job: Dict[str, Any]) -> str:
    """Generate a deterministic cover letter aligned to the job and tailored resume."""
    full_name = resume.get('fullName') or 'Candidate'
    title = job.get('title') or 'the open role'
    company = job.get('company') or 'your company'
    skills = _top_skills(resume)
    skill_line = ', '.join(skills[:6]) if skills else 'backend and platform engineering'

    return f"""Dear Hiring Team at {company},

I am writing to express my strong interest in the {title} position. My background in platform engineering, microservices, and AWS-backed systems aligns closely with your requirements.

In recent roles I have delivered high-availability backend platforms, optimized cloud costs, and built scalable APIs and event-driven services. Core strengths relevant to this role include {skill_line}.

I would welcome the opportunity to discuss how my experience can contribute to {company}'s engineering goals.

Sincerely,
{full_name}"""
