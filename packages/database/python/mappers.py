"""Map between application job/profile dicts and Supabase row shapes."""

from __future__ import annotations

from typing import Any, Dict, List


def job_to_row(job: Dict[str, Any]) -> Dict[str, Any]:
    """Convert canonical job dict (camelCase) to database row (snake_case)."""
    external_id = job.get('external_id') or job.get('id', '')
    return {
        'id': job['id'],
        'source': job.get('source', 'Unknown'),
        'external_id': external_id,
        'title': job.get('title', 'Unknown Role'),
        'company': job.get('company', 'Unknown Company'),
        'location': job.get('location'),
        'remote_type': job.get('remoteType', 'Remote'),
        'url': job.get('url'),
        'description': job.get('description'),
        'posted_at': job.get('postedAt'),
        'status': job.get('status', 'New'),
        'score': job.get('score'),
        'fit_explanation': job.get('fitExplanation'),
        'extracted_skills': job.get('extractedSkills') or [],
        'salary_estimate': job.get('salaryEstimate'),
        'seniority': job.get('seniority'),
        'notes': job.get('notes'),
        'tailored_resume_latex': job.get('tailoredResumeLaTeX'),
        'tailored_cover_letter': job.get('tailoredCoverLetter'),
        'ats_score': job.get('atsScore'),
    }


def row_to_job(row: Dict[str, Any]) -> Dict[str, Any]:
    """Convert database row to canonical job dict."""
    return {
        'id': row['id'],
        'title': row.get('title', ''),
        'company': row.get('company', ''),
        'location': row.get('location') or '',
        'remoteType': row.get('remote_type') or 'Remote',
        'source': row.get('source') or '',
        'url': row.get('url') or '',
        'description': row.get('description') or '',
        'postedAt': row.get('posted_at') or '',
        'status': row.get('status') or 'New',
        'score': row.get('score'),
        'fitExplanation': row.get('fit_explanation'),
        'extractedSkills': row.get('extracted_skills') or [],
        'salaryEstimate': row.get('salary_estimate'),
        'seniority': row.get('seniority'),
        'notes': row.get('notes'),
        'tailoredResumeLaTeX': row.get('tailored_resume_latex'),
        'tailoredCoverLetter': row.get('tailored_cover_letter'),
        'atsScore': row.get('ats_score'),
    }


def row_to_interview(row: Dict[str, Any]) -> Dict[str, Any]:
    """Convert database row to canonical interview dict."""
    return {
        'id': row['id'],
        'jobId': row['job_id'],
        'role': row.get('role', ''),
        'company': row.get('company', ''),
        'date': row.get('interview_date') or '',
        'type': row.get('interview_type') or '',
        'notes': row.get('notes') or '',
        'status': row.get('status') or 'Scheduled',
    }


def profile_data_from_row(row: Dict[str, Any] | None) -> Dict[str, Any]:
    """Extract profile JSON from profiles table row."""
    if not row:
        return {}
    data = row.get('data')
    return data if isinstance(data, dict) else {}


def dedupe_indexes(jobs: List[Dict[str, Any]]) -> tuple[set[str], set[str]]:
    """Build URL and title-company deduplication indexes from job list."""
    urls = {j.get('url') for j in jobs if j.get('url')}
    signatures = {f"{j.get('title')}-{j.get('company')}".lower() for j in jobs}
    return urls, signatures
