"""Normalize, classify, score, and enrich job records for persistence."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

from packages.ai_engine.python import matcher
from packages.ai_engine.python.text_builder import extract_matched_skills, infer_seniority

CANONICAL_ROLES = (
    'Platform Engineer',
    'Backend Engineer',
    'DevOps Engineer',
    'Site Reliability Engineer',
    'Cloud Engineer',
    'Full Stack Engineer',
    'Data Engineer',
    'Software Engineer',
)

ROLE_PATTERNS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ('Site Reliability Engineer', ('site reliability', 'sre', 'reliability engineer')),
    ('Platform Engineer', ('platform engineer', 'platform engineering')),
    ('DevOps Engineer', ('devops', 'dev ops', 'ci/cd engineer')),
    ('Cloud Engineer', ('cloud engineer', 'cloud architect', 'cloud solution')),
    ('Backend Engineer', ('backend', 'back-end', 'back end', 'api engineer', 'node.js', 'nodejs')),
    ('Full Stack Engineer', ('full stack', 'fullstack', 'full-stack')),
    ('Data Engineer', ('data engineer', 'data pipeline', 'etl engineer')),
)

TECHNOLOGY_KEYWORDS = (
    'Node.js',
    'TypeScript',
    'JavaScript',
    'Python',
    'Golang',
    'Go',
    'Java',
    'Kubernetes',
    'Docker',
    'Terraform',
    'AWS',
    'GCP',
    'Azure',
    'PostgreSQL',
    'MySQL',
    'MongoDB',
    'Redis',
    'GraphQL',
    'React',
    'Express.js',
    'Microservices',
    'Kafka',
    'RabbitMQ',
    'Jenkins',
    'GitHub Actions',
    'LangChain',
    'FastAPI',
    'Spring',
    'Lambda',
    'ECS',
    'EKS',
)

EMPLOYMENT_PATTERNS = (
    ('Contract', ('contract', 'contractor', 'freelance')),
    ('Part-time', ('part-time', 'part time')),
    ('Internship', ('intern', 'internship')),
    ('Full-time', ('full-time', 'full time', 'permanent')),
)

PRIORITY_HIGH = 'High'
PRIORITY_MEDIUM = 'Medium'
PRIORITY_LOW = 'Low'


def _clamp(value: float) -> int:
    return int(max(0, min(100, round(value))))


def _job_text(job: Dict) -> str:
    return f"{job.get('title', '')} {job.get('description', '')}".lower()


def classify_canonical_role(title: str, description: str = '') -> str:
    """Map a posting to a canonical engineering role label."""
    text = f'{title} {description}'.lower()
    for role, patterns in ROLE_PATTERNS:
        if any(pattern in text for pattern in patterns):
            return role
    return 'Software Engineer'


def infer_employment_type(title: str, description: str = '') -> str:
    """Infer employment type from posting text."""
    text = f'{title} {description}'.lower()
    for label, patterns in EMPLOYMENT_PATTERNS:
        if any(pattern in text for pattern in patterns):
            return label
    return 'Full-time'


def extract_technologies(job: Dict) -> List[str]:
    """Extract known technologies mentioned in the job posting."""
    text = _job_text(job)
    found: List[str] = []
    for tech in TECHNOLOGY_KEYWORDS:
        if tech.lower() in text or tech.replace('.', '').lower() in text:
            found.append(tech)
    return found


def extract_required_skills(job: Dict, profile: Dict) -> List[str]:
    """Heuristically extract required skills from the posting."""
    text = _job_text(job)
    required: List[str] = []
    requirement_markers = ('required', 'must have', 'requirements', 'qualifications')
    for skill in profile.get('skills') or []:
        skill_text = str(skill).lower()
        if skill_text in text:
            required.append(str(skill))
    if not required and any(marker in text for marker in requirement_markers):
        required = extract_technologies(job)[:8]
    return required[:12]


def extract_preferred_skills(job: Dict, profile: Dict) -> List[str]:
    """Heuristically extract preferred/nice-to-have skills."""
    text = _job_text(job)
    if 'nice to have' not in text and 'preferred' not in text and 'bonus' not in text:
        return []
    preferred: List[str] = []
    for skill in profile.get('skills') or []:
        skill_text = str(skill).lower()
        if skill_text in text and skill_text not in {s.lower() for s in extract_required_skills(job, profile)}:
            preferred.append(str(skill))
    return preferred[:8]


def infer_primary_stack(technologies: List[str], title: str) -> str:
    """Pick the dominant stack label for filtering."""
    if not technologies:
        title_lower = title.lower()
        if 'node' in title_lower or 'typescript' in title_lower:
            return 'Node.js / TypeScript'
        if 'python' in title_lower:
            return 'Python'
        if 'java' in title_lower:
            return 'Java'
        return 'Generalist'
    priority = ['Node.js', 'TypeScript', 'Python', 'Golang', 'Java', 'Kubernetes', 'AWS']
    for item in priority:
        if item in technologies:
            anchor = item
            if item == 'Node.js' and 'TypeScript' in technologies:
                return 'Node.js / TypeScript'
            if item == 'Kubernetes' and 'Docker' in technologies:
                return 'Kubernetes / Docker'
            if item == 'AWS' and 'Terraform' in technologies:
                return 'AWS / Terraform'
            return anchor
    return technologies[0]


def _similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, left, right).ratio()


def detect_duplicate(
    job: Dict,
    existing_jobs: List[Dict],
    *,
    semantic_threshold: float = 0.88,
) -> Tuple[bool, Optional[str]]:
    """
    Detect duplicates by URL, source+external_id, or semantic title similarity.

    Returns:
        (is_duplicate, duplicate_of_job_id)
    """
    job_url = (job.get('url') or job.get('applicationUrl') or '').strip().lower()
    job_source = (job.get('source') or '').lower()
    job_external = str(job.get('externalId') or job.get('external_id') or job.get('id') or '')
    normalized_title = re.sub(r'\s+', ' ', (job.get('title') or '').lower()).strip()
    company = (job.get('company') or '').lower()

    for existing in existing_jobs:
        existing_url = (existing.get('url') or existing.get('applicationUrl') or '').strip().lower()
        if job_url and existing_url and job_url == existing_url:
            return True, existing.get('id')

        if (
            job_source
            and job_external
            and existing.get('source', '').lower() == job_source
            and str(existing.get('externalId') or existing.get('external_id') or existing.get('id')) == job_external
        ):
            return True, existing.get('id')

        existing_company = (existing.get('company') or '').lower()
        existing_title = re.sub(r'\s+', ' ', (existing.get('title') or '').lower()).strip()
        if company and company == existing_company and normalized_title and existing_title:
            if _similarity(normalized_title, existing_title) >= semantic_threshold:
                return True, existing.get('id')

    return False, None


def _compute_skill_match(job: Dict, profile: Dict) -> Tuple[int, List[str], List[str]]:
    profile_skills = [str(skill) for skill in (profile.get('skills') or [])]
    matched = extract_matched_skills(job, profile)
    missing = [skill for skill in profile_skills if skill not in matched]
    ratio = len(matched) / max(1, len(profile_skills))
    return _clamp(ratio * 100), matched, missing


def _compute_experience_match(job: Dict, profile: Dict) -> int:
    job_seniority = infer_seniority(job.get('title', ''))
    target_roles = [str(role).lower() for role in (profile.get('targetRoles') or [])]
    title = (job.get('title') or '').lower()
    score = 45
    if any(role.split()[0] in title for role in target_roles if role):
        score += 25
    if job_seniority == 'Senior':
        score += 20
    elif job_seniority == 'Mid-level':
        score += 10
    years = re.search(r'(\d+)\+?\s*years', _job_text(job))
    if years and int(years.group(1)) <= 7:
        score += 10
    return _clamp(score)


def _compute_remote_match(job: Dict, profile: Dict) -> int:
    preference = (profile.get('preferences') or {}).get('remotePreference', 'Any')
    remote_type = job.get('remoteType', 'Hybrid')
    if preference == 'Any':
        return 85
    if remote_type == preference:
        return 95
    if remote_type == 'Hybrid' and preference == 'Remote':
        return 60
    return 35


def _compute_company_match(job: Dict, profile: Dict) -> int:
    targets = [str(item).lower() for item in (profile.get('preferences') or {}).get('targetCompanies') or []]
    company = (job.get('company') or '').lower()
    if not targets:
        return 55
    if any(target in company or company in target for target in targets):
        return 95
    return 40


def _compute_location_match(job: Dict, profile: Dict) -> int:
    profile_location = (profile.get('location') or '').lower()
    job_location = (job.get('location') or '').lower()
    preferred_locations = [
        str(item).lower() for item in (profile.get('preferences') or {}).get('locations') or []
    ]
    if 'remote' in job_location or job.get('remoteType') == 'Remote':
        return 90
    if profile_location and profile_location.split(',')[0] in job_location:
        return 85
    if any(loc in job_location for loc in preferred_locations if loc):
        return 80
    if 'global' in profile_location or 'remote' in profile_location:
        return 70
    return 45


def _compute_salary_match(job: Dict) -> int:
    salary = (job.get('salaryEstimate') or '').lower()
    if not salary or salary in {'not specified', 'unknown'}:
        return 50
    if any(token in salary for token in ('$', 'usd', 'inr', 'lpa', 'k', 'year')):
        return 75
    return 60


def _compute_ats_score(job: Dict, matched_skills: List[str], missing_skills: List[str]) -> int:
    description = job.get('description') or ''
    title = job.get('title') or ''
    score = 40
    score += min(30, len(matched_skills) * 4)
    score += 10 if len(description) > 400 else 0
    score += 10 if any(token in title.lower() for token in ('engineer', 'developer', 'architect')) else 0
    score -= min(20, len(missing_skills))
    return _clamp(score)


def _missing_keywords(job: Dict, profile: Dict, matched_skills: List[str]) -> List[str]:
    keywords = (profile.get('preferences') or {}).get('skillsKeywords') or profile.get('skills') or []
    text = _job_text(job)
    missing: List[str] = []
    for keyword in keywords:
        keyword_text = str(keyword)
        if keyword_text.lower() not in text and keyword_text not in matched_skills:
            missing.append(keyword_text)
    return missing[:10]


def _resume_suggestions(missing_skills: List[str], missing_keywords: List[str], job: Dict) -> List[str]:
    suggestions: List[str] = []
    for skill in missing_skills[:3]:
        suggestions.append(f"Highlight production experience with {skill} in your resume bullets.")
    for keyword in missing_keywords[:2]:
        suggestions.append(f"Add ATS keywords related to {keyword} if you have relevant experience.")
    if infer_seniority(job.get('title', '')) == 'Senior':
        suggestions.append('Emphasize ownership, scale, and reliability outcomes for this senior role.')
    if not suggestions:
        suggestions.append('Tailor your summary to mirror the role title and top stack keywords.')
    return suggestions[:5]


def estimate_priority(overall_score: int, company_match: int, is_duplicate: bool) -> str:
    """Estimate job priority from score signals."""
    if is_duplicate:
        return PRIORITY_LOW
    if overall_score >= 80 and company_match >= 70:
        return PRIORITY_HIGH
    if overall_score >= 65:
        return PRIORITY_MEDIUM
    return PRIORITY_LOW


def _confidence_score(job: Dict, matched_skills: List[str], scorer: str) -> int:
    score = 45
    score += min(25, len(matched_skills) * 3)
    score += 10 if len(job.get('description') or '') > 250 else 0
    score += 10 if scorer == 'embedding' else 5
    return _clamp(score)


def enrich_job(
    job: Dict,
    profile: Dict,
    *,
    existing_jobs: Optional[List[Dict]] = None,
    base_analysis: Optional[Dict] = None,
) -> Dict:
    """
    Normalize and enrich a canonical job with metadata, insights, and score components.

    Returns the job dict with enrichment fields and nested ``matchInsights``.
    """
    analysis = base_analysis or matcher.score_job(job, profile)
    existing_jobs = existing_jobs or []

    technologies = extract_technologies(job)
    required_skills = extract_required_skills(job, profile)
    preferred_skills = extract_preferred_skills(job, profile)
    canonical_role = classify_canonical_role(job.get('title', ''), job.get('description', ''))
    primary_stack = infer_primary_stack(technologies, job.get('title', ''))
    employment_type = infer_employment_type(job.get('title', ''), job.get('description', ''))
    seniority = analysis.get('seniority') or infer_seniority(job.get('title', ''))

    skill_score, matched_skills, missing_skills = _compute_skill_match(job, profile)
    experience_score = _compute_experience_match(job, profile)
    remote_score = _compute_remote_match(job, profile)
    company_score = _compute_company_match(job, profile)
    location_score = _compute_location_match(job, profile)
    salary_score = _compute_salary_match(job)
    ats_score = _compute_ats_score(job, matched_skills, missing_skills)

    overall_score = _clamp(
        analysis.get('score', 0) * 0.45
        + skill_score * 0.25
        + experience_score * 0.15
        + remote_score * 0.05
        + company_score * 0.05
        + location_score * 0.05
    )
    missing_kw = _missing_keywords(job, profile, matched_skills)
    suggestions = _resume_suggestions(missing_skills, missing_kw, job)
    scorer = analysis.get('scorer', 'heuristic')
    confidence = _confidence_score(job, matched_skills, scorer)

    is_duplicate, duplicate_of = detect_duplicate(job, existing_jobs)
    priority = estimate_priority(overall_score, company_score, is_duplicate)

    explanation = analysis.get('fitExplanation') or ''
    if missing_skills:
        explanation += f" Missing core skills: {', '.join(missing_skills[:5])}."
    if is_duplicate:
        explanation += ' Marked as duplicate of a previously seen posting.'

    now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    application_url = job.get('applicationUrl') or job.get('url') or ''

    enriched = {
        **job,
        'seniority': seniority,
        'remoteType': analysis.get('remoteType', job.get('remoteType', 'Hybrid')),
        'salaryEstimate': analysis.get('salaryEstimate', job.get('salaryEstimate', 'Not Specified')),
        'extractedSkills': analysis.get('extractedSkills') or matched_skills,
        'employmentType': employment_type,
        'requiredSkills': required_skills,
        'preferredSkills': preferred_skills,
        'extractedTechnologies': technologies,
        'applicationUrl': application_url,
        'sourcePostedAt': job.get('sourcePostedAt') or job.get('postedAt') or '',
        'scannedAt': now,
        'postedAt': now,
        'canonicalRole': canonical_role,
        'primaryStack': primary_stack,
        'priority': priority,
        'isDuplicate': is_duplicate,
        'duplicateOf': duplicate_of,
        'score': overall_score,
        'fitExplanation': explanation.strip(),
        'matchScorer': scorer,
        'matchInsights': {
            'overallScore': overall_score,
            'skillMatchScore': skill_score,
            'experienceMatchScore': experience_score,
            'atsScore': ats_score,
            'salaryMatchScore': salary_score,
            'companyMatchScore': company_score,
            'locationMatchScore': location_score,
            'remoteMatchScore': remote_score,
            'confidenceScore': confidence,
            'matchedSkills': matched_skills,
            'missingSkills': missing_skills,
            'missingKeywords': missing_kw,
            'resumeSuggestions': suggestions,
            'matchExplanation': explanation.strip(),
            'scorer': scorer,
        },
    }
    return enriched
