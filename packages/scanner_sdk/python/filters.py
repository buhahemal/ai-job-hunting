"""Profile-driven filters applied before expensive AI enrichment."""

from dataclasses import dataclass
from typing import Dict, List

from packages.config.python.remote_policy import analyze_remote_eligibility


@dataclass(frozen=True)
class PreferenceDecision:
    allowed: bool
    reason: str = ''


def _matches_any(value: str, patterns: List[str]) -> bool:
    normalized = value.lower()
    return any(str(pattern).strip().lower() in normalized for pattern in patterns if str(pattern).strip())


def evaluate_job_preferences(
    job: Dict,
    profile: Dict,
    existing_jobs: List[Dict],
) -> PreferenceDecision:
    """Reject jobs excluded by explicit profile preferences."""
    preferences = profile.get('preferences') or {}
    checks = (
        ('company', 'companyBlacklist', 'company_blacklist'),
        ('title', 'titleBlacklist', 'title_blacklist'),
        ('location', 'locationBlacklist', 'location_blacklist'),
    )
    for field, preference, reason in checks:
        if _matches_any(str(job.get(field) or ''), preferences.get(preference) or []):
            return PreferenceDecision(False, reason)

    if preferences.get('applyOncePerCompany'):
        company = str(job.get('company') or '').strip().lower()
        if company and any(str(item.get('company') or '').strip().lower() == company for item in existing_jobs):
            return PreferenceDecision(False, 'already_seen_company')

    levels = [str(level).strip().lower() for level in preferences.get('experienceLevels') or []]
    seniority = str(job.get('seniority') or '').strip().lower()
    if levels and seniority and not any(level in seniority or seniority in level for level in levels):
        return PreferenceDecision(False, 'experience_level')

    if preferences.get('remotePreference') == 'Remote':
        text = f"{job.get('location', '')} {job.get('description', '')}"
        if analyze_remote_eligibility(text).hard_restriction:
            return PreferenceDecision(False, 'remote_restriction')

    return PreferenceDecision(True)
