"""Explainable worldwide-remote eligibility policy shared by pipeline packages."""

from dataclasses import dataclass
import re
from typing import Tuple

RESTRICTED_PATTERNS: Tuple[str, ...] = (
    r'\bus\b only',
    r'\bunited states\b only',
    r'must reside in (?:the )?us',
    r'\buk\b only',
    r'\beurope\b only',
    r'must live in (?:the )?(?:us|uk|eu)',
    r'no visa sponsorship',
    r'\bw-?2\b only',
)
HARD_RESTRICTION_PATTERNS: Tuple[str, ...] = (
    r'us citizen(?:ship)?',
    r'citizenship required',
    r'security clearance',
    r'cleared candidates',
)
WORLDWIDE_PATTERNS: Tuple[str, ...] = (
    r'work from anywhere',
    r'anywhere in the world',
    r'\bworldwide\b',
    r'\bglobal team\b',
    r'remote\s*[-–]?\s*india',
    r'distributed team',
    r'digital nomad',
)


@dataclass(frozen=True)
class RemoteEligibility:
    status: str
    score_adjustment: int
    hard_restriction: bool


def analyze_remote_eligibility(text: str) -> RemoteEligibility:
    """Classify remote eligibility using auditable red/green phrases."""
    normalized = (text or '').lower()
    hard = any(re.search(pattern, normalized) for pattern in HARD_RESTRICTION_PATTERNS)
    restricted = hard or any(re.search(pattern, normalized) for pattern in RESTRICTED_PATTERNS)
    worldwide = any(re.search(pattern, normalized) for pattern in WORLDWIDE_PATTERNS)
    if restricted:
        return RemoteEligibility('Likely Restricted', -30 if hard else -20, hard)
    if worldwide:
        return RemoteEligibility('Verified Worldwide', 15, False)
    return RemoteEligibility('Remote Unverified', 0, False)
