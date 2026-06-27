"""Accuracy-first skill matching: job requirements vs candidate corpus."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple

from packages.database.python.constants import FULL_MATCH_SKILL_SCORE_FLOOR
from packages.database.python.profile_helpers import flatten_experience_bullet
from packages.ai_engine.python.text_builder import build_candidate_text

# Shared technology list (mirrors job_enricher.TECHNOLOGY_KEYWORDS).
TECHNOLOGY_KEYWORDS: Tuple[str, ...] = (
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
    'Rust',
    'SQS',
    'CloudFront',
    'CloudWatch',
    'Socket.io',
)

# Canonical alias groups — any token in a group matches any other in the group.
SKILL_ALIAS_GROUPS: Tuple[Tuple[str, ...], ...] = (
    ('go', 'golang'),
    ('node.js', 'nodejs', 'node', 'node js'),
    ('express.js', 'express', 'expressjs'),
    ('javascript', 'js', 'ecmascript'),
    ('typescript', 'ts'),
    ('kubernetes', 'k8s'),
    ('amazon web services', 'aws'),
    ('google cloud platform', 'gcp'),
    ('microsoft azure', 'azure'),
    ('postgresql', 'postgres', 'psql'),
    ('mongodb', 'mongo'),
    ('github actions', 'gh actions'),
    ('ci/cd', 'cicd', 'continuous integration'),
    ('socket.io', 'socketio', 'websockets', 'websocket'),
    ('langchain', 'lang chain'),
    ('microservices', 'micro services', 'microservice'),
    ('rest apis', 'rest api', 'restful', 'rest'),
    ('amazon lambda', 'aws lambda', 'lambda'),
    ('amazon sqs', 'aws sqs', 'sqs'),
    ('amazon s3', 'aws s3', 's3'),
    ('cloudfront', 'amazon cloudfront', 'aws cloudfront'),
    ('cloudwatch', 'amazon cloudwatch', 'aws cloudwatch'),
    ('elastic kubernetes service', 'eks', 'amazon eks'),
    ('elastic container service', 'ecs', 'amazon ecs'),
)


@dataclass
class SkillMatchResult:
    """Validated skill match outcome for scoring and insights."""

    skill_match_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    skill_match_confidence: int
    matched_preferred: List[str]
    missing_preferred: List[str]
    preferred_coverage: int


def _clamp(value: float) -> int:
    return int(max(0, min(100, round(value))))


def normalize_skill(token: str) -> str:
    """Normalize a skill token for comparison."""
    cleaned = re.sub(r'[^\w\s./+#-]', ' ', str(token).lower())
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    for group in SKILL_ALIAS_GROUPS:
        if cleaned in group:
            return group[0]
    return cleaned


def _alias_variants(normalized: str) -> Set[str]:
    """Return normalized token plus all alias variants."""
    variants = {normalized}
    for group in SKILL_ALIAS_GROUPS:
        if normalized in group:
            variants.update(group)
    return variants


def build_candidate_skill_corpus(profile: Dict) -> Tuple[Set[str], str]:
    """
    Build normalized skill tokens and searchable text from the full profile.

    Returns:
        (normalized_skill_tokens, corpus_text_lower)
    """
    tokens: Set[str] = set()

    for skill in profile.get('skills') or []:
        normalized = normalize_skill(str(skill))
        if normalized:
            tokens.add(normalized)
            tokens.update(_alias_variants(normalized))

    for keyword in (profile.get('preferences') or {}).get('skillsKeywords') or []:
        normalized = normalize_skill(str(keyword))
        if normalized:
            tokens.add(normalized)
            tokens.update(_alias_variants(normalized))

    for exp in profile.get('experience') or []:
        for bullet in exp.get('bullets') or []:
            bullet_text = flatten_experience_bullet(bullet)
            for tech in TECHNOLOGY_KEYWORDS:
                if tech.lower() in bullet_text.lower():
                    norm = normalize_skill(tech)
                    tokens.add(norm)
                    tokens.update(_alias_variants(norm))

    for project in profile.get('projects') or []:
        for tech in project.get('tech') or []:
            norm = normalize_skill(str(tech))
            if norm:
                tokens.add(norm)
                tokens.update(_alias_variants(norm))

    corpus_text = build_candidate_text(profile).lower()
    latex = (profile.get('masterResumeLaTeX') or '').lower()
    if latex:
        corpus_text = f'{corpus_text}\n{latex}'

    return tokens, corpus_text


def _job_text(job: Dict) -> str:
    parts = [
        job.get('title', ''),
        job.get('description', ''),
        ' '.join(job.get('requiredSkills') or job.get('required_skills') or []),
        ' '.join(job.get('preferredSkills') or job.get('preferred_skills') or []),
        ' '.join(job.get('extractedTechnologies') or job.get('extracted_technologies') or []),
    ]
    return ' '.join(str(part) for part in parts if part).lower()


def _skill_in_text(skill: str, text: str) -> bool:
    """Check if a skill (with aliases) appears in text."""
    normalized = normalize_skill(skill)
    if not normalized:
        return False
    for variant in _alias_variants(normalized):
        if len(variant) <= 2:
            pattern = rf'\b{re.escape(variant)}\b'
            if re.search(pattern, text):
                return True
        elif variant in text or variant.replace('.', '') in text:
            return True
    return False


def skill_in_corpus(skill: str, corpus_tokens: Set[str], corpus_text: str) -> bool:
    """Multi-pass check: token set then full corpus text with aliases."""
    normalized = normalize_skill(skill)
    if not normalized:
        return False

    for variant in _alias_variants(normalized):
        if variant in corpus_tokens:
            return True

    if _skill_in_text(skill, corpus_text):
        return True

    return False


def _extract_technologies_from_job(job: Dict) -> List[str]:
    """Extract known technologies mentioned in the job posting."""
    text = _job_text(job)
    found: List[str] = []
    for tech in TECHNOLOGY_KEYWORDS:
        if tech.lower() in text or tech.replace('.', '').lower() in text:
            found.append(tech)
    return found


def extract_job_requirements(job: Dict) -> Tuple[List[str], List[str]]:
    """
    Extract required and preferred skills from the job posting only.

    Uses stored lists when present (rescan path), otherwise parses job text.
    """
    stored_required = job.get('requiredSkills') or job.get('required_skills') or []
    stored_preferred = job.get('preferredSkills') or job.get('preferred_skills') or []
    if stored_required:
        required = list(dict.fromkeys(str(s) for s in stored_required if s))
        preferred = list(dict.fromkeys(str(s) for s in stored_preferred if s))
        return required[:16], preferred[:12]

    text = _job_text(job)
    technologies = _extract_technologies_from_job(job)
    if not technologies and job.get('extractedTechnologies'):
        technologies = list(job.get('extractedTechnologies') or [])

    requirement_markers = ('required', 'must have', 'requirements', 'qualifications', 'what you')
    has_requirement_section = any(marker in text for marker in requirement_markers)

    required: List[str] = []
    preferred: List[str] = []

    for tech in technologies:
        label = str(tech)
        if label not in required:
            required.append(label)

    if not required and has_requirement_section:
        required = technologies[:12]
    elif not required:
        required = technologies[:8]

    if any(marker in text for marker in ('nice to have', 'preferred', 'bonus', 'plus')):
        for tech in technologies:
            if tech not in required and tech not in preferred:
                preferred.append(str(tech))

    return required[:16], preferred[:12]


def _profile_skill_labels(profile: Dict) -> Set[str]:
    return {normalize_skill(str(skill)) for skill in (profile.get('skills') or []) if skill}


def compute_skill_match(job: Dict, profile: Dict) -> SkillMatchResult:
    """
    Match job requirements against the candidate skill corpus.

    missing_skills = job requirements NOT demonstrated in profile/resume.
    """
    corpus_tokens, corpus_text = build_candidate_skill_corpus(profile)
    profile_labels = _profile_skill_labels(profile)
    required, preferred = extract_job_requirements(job)

    matched: List[str] = []
    missing: List[str] = []
    matched_preferred: List[str] = []
    missing_preferred: List[str] = []

    for req in required:
        if skill_in_corpus(req, corpus_tokens, corpus_text):
            matched.append(str(req))
        else:
            norm = normalize_skill(req)
            if norm in profile_labels:
                matched.append(str(req))
            else:
                missing.append(str(req))

    for pref in preferred:
        if skill_in_corpus(pref, corpus_tokens, corpus_text) or normalize_skill(pref) in profile_labels:
            matched_preferred.append(str(pref))
        else:
            missing_preferred.append(str(pref))

    total_reqs = max(1, len(required))
    requirement_coverage = len(matched) / total_reqs
    skill_match_score = _clamp(requirement_coverage * 100)

    if not missing and matched:
        skill_match_score = max(skill_match_score, FULL_MATCH_SKILL_SCORE_FLOOR)

    skill_penalty = min(20, len(missing) * 3)
    validated_skill_score = _clamp(skill_match_score - skill_penalty)

    total_preferred = max(1, len(preferred)) if preferred else 1
    preferred_coverage = _clamp((len(matched_preferred) / total_preferred) * 100) if preferred else 50

    confidence = 50
    if required:
        confidence += min(30, int(requirement_coverage * 30))
    confidence += min(15, len(matched) * 2)
    confidence += 10 if len(job.get('description') or '') > 200 else 5
    confidence -= min(15, len(missing) * 2)
    skill_match_confidence = _clamp(confidence)

    return SkillMatchResult(
        skill_match_score=validated_skill_score,
        matched_skills=matched,
        missing_skills=missing,
        skill_match_confidence=skill_match_confidence,
        matched_preferred=matched_preferred,
        missing_preferred=missing_preferred,
        preferred_coverage=preferred_coverage,
    )


def filter_verified_gaps(missing_skills: Iterable[str], profile: Dict) -> List[str]:
    """Remove skills from gap lists when confirmed in the live profile corpus."""
    corpus_tokens, corpus_text = build_candidate_skill_corpus(profile)
    profile_labels = _profile_skill_labels(profile)
    verified: List[str] = []
    for skill in missing_skills:
        norm = normalize_skill(str(skill))
        if norm in profile_labels:
            continue
        if skill_in_corpus(str(skill), corpus_tokens, corpus_text):
            continue
        verified.append(str(skill))
    return verified
