"""Embedding-based near-duplicate detection for job postings."""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

from packages.ai_engine.python.cosine import cosine_similarity
from packages.ai_engine.python.embedder import encode_texts

DEFAULT_EMBEDDING_DUPLICATE_THRESHOLD = 0.92


def embedding_duplicate_threshold() -> float:
    """Return cosine similarity threshold for embedding duplicate detection."""
    raw = os.environ.get('AI_DUPLICATE_THRESHOLD', '').strip()
    if not raw:
        return DEFAULT_EMBEDDING_DUPLICATE_THRESHOLD
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_EMBEDDING_DUPLICATE_THRESHOLD
    return max(0.0, min(1.0, value))


def build_duplicate_text(job: Dict) -> str:
    """Build compact text used for embedding similarity comparisons."""
    description = (job.get('description') or '')[:800]
    parts = [
        job.get('title', ''),
        job.get('company', ''),
        job.get('location', ''),
        description,
    ]
    return ' '.join(str(part).strip() for part in parts if str(part).strip())


def embedding_similarity(left: Dict, right: Dict) -> float:
    """Compute cosine similarity between two job embedding vectors."""
    left_text = build_duplicate_text(left)
    right_text = build_duplicate_text(right)
    if not left_text.strip() or not right_text.strip():
        return 0.0
    left_vector, right_vector = encode_texts([left_text, right_text])
    return float(cosine_similarity(left_vector, right_vector))


def find_embedding_duplicate(
    job: Dict,
    existing_jobs: List[Dict],
    *,
    threshold: Optional[float] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Return whether ``job`` is an embedding near-duplicate of any existing posting.

    Skips comparisons when title and company differ completely unless similarity
    exceeds the threshold (guards against unrelated high-similarity false positives).
    """
    cutoff = embedding_duplicate_threshold() if threshold is None else threshold
    job_company = (job.get('company') or '').lower().strip()
    job_title = (job.get('title') or '').lower().strip()
    if not job_title:
        return False, None

    for existing in existing_jobs:
        existing_id = existing.get('id')
        if not existing_id:
            continue
        existing_company = (existing.get('company') or '').lower().strip()
        if job_company and existing_company and job_company != existing_company:
            continue

        similarity = embedding_similarity(job, existing)
        if similarity >= cutoff:
            return True, str(existing_id)

    return False, None
