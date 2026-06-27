"""Embedding-based job match scoring using local MiniLM vectors."""

from __future__ import annotations

from typing import Dict

from packages.ai_engine.python.cosine import cosine_similarity, similarity_to_percentage
from packages.ai_engine.python.embedder import encode_texts
from packages.ai_engine.python.salary_extractor import extract_salary
from packages.ai_engine.python.text_builder import (
    build_candidate_text,
    build_job_text,
    extract_matched_skills,
    infer_seniority,
)


def score(job: Dict, profile: Dict) -> Dict:
    """
    Score a job against a candidate profile using cosine similarity of embeddings.

    Returns the standard matcher payload consumed by the scanner pipeline.
    """
    candidate_text = build_candidate_text(profile)
    job_text = build_job_text(job)

    if not candidate_text.strip() or not job_text.strip():
        raise ValueError('Candidate and job text are required for embedding scoring')

    candidate_vector, job_vector = encode_texts([candidate_text, job_text])
    similarity = cosine_similarity(candidate_vector, job_vector)
    match_score = similarity_to_percentage(similarity)
    matched_skills = extract_matched_skills(job, profile)

    explanation = (
        f'Embedding match score of {match_score}% '
        f'(cosine similarity {similarity:.3f}) using sentence-transformers/all-MiniLM-L6-v2.'
    )
    if matched_skills:
        explanation += f' Matched skills: {", ".join(matched_skills[:5])}.'

    return {
        'score': match_score,
        'extractedSkills': matched_skills,
        'fitExplanation': explanation,
        'salaryEstimate': extract_salary(job),
        'seniority': infer_seniority(job.get('title', '')),
        'remoteType': job.get('remoteType', 'Hybrid'),
        'scorer': 'embedding',
    }
