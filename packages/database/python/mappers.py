"""Map between application job/profile dicts and Supabase row shapes."""

from __future__ import annotations

from typing import Any, Dict, List


def match_insights_to_row(job_id: str, insights: Dict[str, Any]) -> Dict[str, Any]:
    """Convert nested matchInsights payload to job_match_scores row."""
    return {
        'job_id': job_id,
        'overall_score': insights.get('overallScore', 0),
        'skill_match_score': insights.get('skillMatchScore', 0),
        'experience_match_score': insights.get('experienceMatchScore', 0),
        'ats_score': insights.get('atsScore', 0),
        'salary_match_score': insights.get('salaryMatchScore', 0),
        'company_match_score': insights.get('companyMatchScore', 0),
        'location_match_score': insights.get('locationMatchScore', 0),
        'remote_match_score': insights.get('remoteMatchScore', 0),
        'confidence_score': insights.get('confidenceScore', 0),
        'matched_skills': insights.get('matchedSkills') or [],
        'missing_skills': insights.get('missingSkills') or [],
        'missing_keywords': insights.get('missingKeywords') or [],
        'resume_suggestions': insights.get('resumeSuggestions') or [],
        'match_explanation': insights.get('matchExplanation'),
        'scorer': insights.get('scorer'),
    }


def row_to_match_insights(row: Dict[str, Any] | None) -> Dict[str, Any] | None:
    """Convert job_match_scores row to camelCase insights dict."""
    if not row:
        return None
    return {
        'overallScore': row.get('overall_score', 0),
        'skillMatchScore': row.get('skill_match_score', 0),
        'experienceMatchScore': row.get('experience_match_score', 0),
        'atsScore': row.get('ats_score', 0),
        'salaryMatchScore': row.get('salary_match_score', 0),
        'companyMatchScore': row.get('company_match_score', 0),
        'locationMatchScore': row.get('location_match_score', 0),
        'remoteMatchScore': row.get('remote_match_score', 0),
        'confidenceScore': row.get('confidence_score', 0),
        'matchedSkills': row.get('matched_skills') or [],
        'missingSkills': row.get('missing_skills') or [],
        'missingKeywords': row.get('missing_keywords') or [],
        'resumeSuggestions': row.get('resume_suggestions') or [],
        'matchExplanation': row.get('match_explanation') or '',
        'scorer': row.get('scorer'),
    }


def job_to_row(job: Dict[str, Any]) -> Dict[str, Any]:
    """Convert canonical job dict (camelCase) to database row (snake_case)."""
    external_id = job.get('externalId') or job.get('external_id') or job.get('id', '')
    insights = job.get('matchInsights') or {}
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
        'score': job.get('score') or insights.get('overallScore'),
        'fit_explanation': job.get('fitExplanation') or insights.get('matchExplanation'),
        'extracted_skills': job.get('extractedSkills') or [],
        'salary_estimate': job.get('salaryEstimate'),
        'seniority': job.get('seniority'),
        'notes': job.get('notes'),
        'tailored_resume_latex': job.get('tailoredResumeLaTeX'),
        'tailored_cover_letter': job.get('tailoredCoverLetter'),
        'ats_score': job.get('atsScore') or insights.get('atsScore'),
        'employment_type': job.get('employmentType'),
        'required_skills': job.get('requiredSkills') or [],
        'preferred_skills': job.get('preferredSkills') or [],
        'extracted_technologies': job.get('extractedTechnologies') or [],
        'application_url': job.get('applicationUrl') or job.get('url'),
        'source_posted_at': job.get('sourcePostedAt') or None,
        'scanned_at': job.get('scannedAt'),
        'canonical_role': job.get('canonicalRole'),
        'primary_stack': job.get('primaryStack'),
        'priority': job.get('priority'),
        'is_duplicate': bool(job.get('isDuplicate')),
        'duplicate_of': job.get('duplicateOf'),
        'match_scorer': job.get('matchScorer') or insights.get('scorer'),
    }


def row_to_job(row: Dict[str, Any], match_row: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Convert database row to canonical job dict."""
    insights = row_to_match_insights(match_row)
    return {
        'id': row['id'],
        'externalId': row.get('external_id') or row['id'],
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
        'employmentType': row.get('employment_type'),
        'requiredSkills': row.get('required_skills') or [],
        'preferredSkills': row.get('preferred_skills') or [],
        'extractedTechnologies': row.get('extracted_technologies') or [],
        'applicationUrl': row.get('application_url') or row.get('url') or '',
        'sourcePostedAt': row.get('source_posted_at') or '',
        'scannedAt': row.get('scanned_at') or '',
        'canonicalRole': row.get('canonical_role'),
        'primaryStack': row.get('primary_stack'),
        'priority': row.get('priority'),
        'isDuplicate': row.get('is_duplicate', False),
        'duplicateOf': row.get('duplicate_of'),
        'matchScorer': row.get('match_scorer'),
        'matchInsights': insights,
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


def interview_to_row(interview: Dict[str, Any]) -> Dict[str, Any]:
    """Convert canonical interview dict to database row."""
    return {
        'id': interview['id'],
        'job_id': interview['jobId'],
        'role': interview.get('role', ''),
        'company': interview.get('company', ''),
        'interview_date': interview.get('date'),
        'interview_type': interview.get('type'),
        'notes': interview.get('notes'),
        'status': interview.get('status', 'Scheduled'),
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


def scanned_job_to_row(record: Dict[str, Any]) -> Dict[str, Any]:
    """Convert scanned job insight dict to database row (snake_case)."""
    overall = record.get('overall_score', record.get('score'))
    return {
        'dedupe_key': record['dedupe_key'],
        'job_id': record.get('job_id'),
        'source': record.get('source'),
        'score': overall,
        'title': record.get('title'),
        'company': record.get('company'),
        'location': record.get('location'),
        'remote_type': record.get('remote_type'),
        'canonical_role': record.get('canonical_role'),
        'primary_stack': record.get('primary_stack'),
        'seniority': record.get('seniority'),
        'employment_type': record.get('employment_type'),
        'application_url': record.get('application_url'),
        'required_skills': record.get('required_skills') or [],
        'preferred_skills': record.get('preferred_skills') or [],
        'extracted_technologies': record.get('extracted_technologies') or [],
        'overall_score': overall,
        'skill_match_score': record.get('skill_match_score'),
        'experience_match_score': record.get('experience_match_score'),
        'ats_score': record.get('ats_score'),
        'matched_skills': record.get('matched_skills') or [],
        'missing_skills': record.get('missing_skills') or [],
        'missing_keywords': record.get('missing_keywords') or [],
        'match_explanation': record.get('match_explanation'),
        'scorer': record.get('scorer'),
        'promoted_to_jobs': bool(record.get('promoted_to_jobs')),
        'scan_run_id': record.get('scan_run_id'),
        'promotion_type': record.get('promotion_type'),
        'profile_hash': record.get('profile_hash'),
        'skill_match_confidence': record.get('skill_match_confidence'),
        'rescored_at': record.get('rescored_at'),
    }


def row_to_scanned_job(row: Dict[str, Any]) -> Dict[str, Any]:
    """Convert scanned_jobs database row to camelCase insight dict."""
    overall = row.get('overall_score', row.get('score'))
    return {
        'dedupeKey': row['dedupe_key'],
        'jobId': row.get('job_id'),
        'source': row.get('source') or '',
        'title': row.get('title') or '',
        'company': row.get('company') or '',
        'location': row.get('location') or '',
        'remoteType': row.get('remote_type') or 'Remote',
        'canonicalRole': row.get('canonical_role'),
        'primaryStack': row.get('primary_stack'),
        'seniority': row.get('seniority'),
        'employmentType': row.get('employment_type'),
        'applicationUrl': row.get('application_url') or '',
        'requiredSkills': row.get('required_skills') or [],
        'preferredSkills': row.get('preferred_skills') or [],
        'extractedTechnologies': row.get('extracted_technologies') or [],
        'overallScore': overall or 0,
        'skillMatchScore': row.get('skill_match_score'),
        'experienceMatchScore': row.get('experience_match_score'),
        'atsScore': row.get('ats_score'),
        'matchedSkills': row.get('matched_skills') or [],
        'missingSkills': row.get('missing_skills') or [],
        'missingKeywords': row.get('missing_keywords') or [],
        'matchExplanation': row.get('match_explanation') or '',
        'scorer': row.get('scorer'),
        'promotedToJobs': bool(row.get('promoted_to_jobs')),
        'scanRunId': row.get('scan_run_id'),
        'promotionType': row.get('promotion_type'),
        'profileHash': row.get('profile_hash'),
        'skillMatchConfidence': row.get('skill_match_confidence'),
        'rescoredAt': row.get('rescored_at') or '',
        'scannedAt': row.get('scanned_at') or '',
    }


def scanned_job_row_to_job(row: Dict[str, Any]) -> Dict[str, Any]:
    """Map a scanned_jobs row to a canonical job dict for promotion to leads."""
    overall = row.get('overall_score', row.get('score')) or 0
    job_id = row.get('job_id') or row.get('dedupe_key')
    insights = {
        'overallScore': overall,
        'skillMatchScore': row.get('skill_match_score') or 0,
        'experienceMatchScore': row.get('experience_match_score') or 0,
        'atsScore': row.get('ats_score') or 0,
        'salaryMatchScore': 50,
        'companyMatchScore': 50,
        'locationMatchScore': 50,
        'remoteMatchScore': 50,
        'confidenceScore': row.get('skill_match_confidence') or 50,
        'skillMatchConfidence': row.get('skill_match_confidence') or 50,
        'matchedSkills': row.get('matched_skills') or [],
        'missingSkills': row.get('missing_skills') or [],
        'missingKeywords': row.get('missing_keywords') or [],
        'resumeSuggestions': [],
        'matchExplanation': row.get('match_explanation') or '',
        'scorer': row.get('scorer') or 'rescan',
    }
    return {
        'id': job_id,
        'externalId': job_id,
        'title': row.get('title') or 'Unknown Role',
        'company': row.get('company') or 'Unknown Company',
        'location': row.get('location') or '',
        'remoteType': row.get('remote_type') or 'Remote',
        'source': row.get('source') or 'Scan Insights',
        'url': row.get('application_url') or '',
        'applicationUrl': row.get('application_url') or '',
        'description': '',
        'postedAt': row.get('scanned_at') or '',
        'status': 'New',
        'score': overall,
        'fitExplanation': row.get('match_explanation') or '',
        'extractedSkills': row.get('matched_skills') or [],
        'requiredSkills': row.get('required_skills') or [],
        'preferredSkills': row.get('preferred_skills') or [],
        'extractedTechnologies': row.get('extracted_technologies') or [],
        'canonicalRole': row.get('canonical_role'),
        'primaryStack': row.get('primary_stack'),
        'seniority': row.get('seniority'),
        'employmentType': row.get('employment_type'),
        'scannedAt': row.get('scanned_at') or '',
        'matchScorer': row.get('scorer'),
        'matchInsights': insights,
    }
