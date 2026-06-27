"""Tailor master resume JSON for a target job without mutating the master."""

from __future__ import annotations

import copy
import re
from typing import Any, Dict, Iterable, List, Set


def _normalize_token(value: str) -> str:
    return re.sub(r'[^a-z0-9+#./-]+', ' ', value.lower()).strip()


def _tokenize(text: str) -> Set[str]:
    if not text:
        return set()
    tokens = {_normalize_token(part) for part in re.split(r'[\s,;/|]+', text) if part.strip()}
    return {token for token in tokens if len(token) > 1}


def _build_job_corpus(job: Dict[str, Any]) -> str:
    parts = [
        job.get('title') or '',
        job.get('company') or '',
        job.get('description') or '',
        ' '.join(job.get('extractedSkills') or []),
        ' '.join(job.get('requiredSkills') or []),
        ' '.join(job.get('preferredSkills') or []),
        ' '.join(job.get('extractedTechnologies') or []),
    ]
    return ' '.join(part for part in parts if part).lower()


def _score_text(text: str, corpus: str, priority_tokens: Set[str]) -> int:
    if not text:
        return 0
    lowered = text.lower()
    score = 0
    for token in priority_tokens:
        if token and token in lowered:
            score += 3
    for token in _tokenize(text):
        if token in corpus:
            score += 2
    return score


def _reorder_strings(items: Iterable[str], corpus: str, priority_tokens: Set[str]) -> List[str]:
    ranked = sorted(
        list(items),
        key=lambda item: _score_text(item, corpus, priority_tokens),
        reverse=True,
    )
    return ranked


def _reorder_bullets(bullets: List[Dict[str, Any]], corpus: str, priority_tokens: Set[str]) -> List[Dict[str, Any]]:
    ranked = sorted(
        bullets,
        key=lambda bullet: _score_text(
            f"{bullet.get('title', '')} {bullet.get('body', '')}",
            corpus,
            priority_tokens,
        ),
        reverse=True,
    )
    return ranked


def _limit_bullets(experience: List[Dict[str, Any]], *, first_role_max: int = 6, other_max: int = 3) -> List[Dict[str, Any]]:
    trimmed: List[Dict[str, Any]] = []
    for index, role in enumerate(experience):
        cap = first_role_max if index == 0 else other_max
        bullets = role.get('bullets') or []
        if isinstance(bullets, list):
            role = {**role, 'bullets': bullets[:cap]}
        trimmed.append(role)
    return trimmed


def _reorder_skill_groups(
    groups: List[Dict[str, Any]],
    corpus: str,
    priority_tokens: Set[str],
) -> List[Dict[str, Any]]:
    reordered: List[Dict[str, Any]] = []
    for group in groups:
        items = group.get('items') or []
        reordered.append(
            {
                **group,
                'items': _reorder_strings(items, corpus, priority_tokens),
            }
        )
    return reordered


def tailor_resume_json(master: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a job-specific resume JSON copy from the master resume.

    The master dict is never modified; a new tailored dict is returned.
    """
    tailored = copy.deepcopy(master)
    corpus = _build_job_corpus(job)
    priority_tokens = _tokenize(corpus)

    job_title = (job.get('title') or '').strip()
    if job_title:
        tailored['targetRole'] = job_title

    if job_title and tailored.get('summary'):
        tailored['summary'] = (
            f"{tailored['summary']} Targeting the {job_title} role at "
            f"{job.get('company') or 'the hiring company'} with emphasis on "
            f"matching platform, backend, and cloud engineering requirements."
        )

    tailored['skills'] = _reorder_strings(tailored.get('skills') or [], corpus, priority_tokens)

    if tailored.get('skillGroups'):
        tailored['skillGroups'] = _reorder_skill_groups(
            tailored['skillGroups'],
            corpus,
            priority_tokens,
        )

    experience = tailored.get('experience') or []
    reordered_experience: List[Dict[str, Any]] = []
    for role in experience:
        bullets = role.get('bullets') or []
        if bullets and isinstance(bullets[0], str):
            normalized = [{'title': 'Achievement', 'body': text} for text in bullets]
        else:
            normalized = list(bullets)
        reordered_experience.append(
            {
                **role,
                'bullets': _reorder_bullets(normalized, corpus, priority_tokens),
            }
        )
    tailored['experience'] = _limit_bullets(reordered_experience)

    projects = tailored.get('projects') or []
    ranked_projects = sorted(
        projects,
        key=lambda project: _score_text(
            ' '.join(
                [
                    project.get('title') or '',
                    project.get('techStack') or '',
                    ' '.join(
                        f"{bullet.get('title', '')} {bullet.get('body', '')}"
                        for bullet in (project.get('bullets') or [])
                        if isinstance(bullet, dict)
                    ),
                ]
            ),
            corpus,
            priority_tokens,
        ),
        reverse=True,
    )
    tailored['projects'] = ranked_projects

    tailored['tailoringMeta'] = {
        'jobTitle': job_title,
        'company': job.get('company'),
        'matchedSkillCount': sum(
            1 for skill in tailored.get('skills') or [] if _normalize_token(skill) in corpus
        ),
    }

    return tailored
