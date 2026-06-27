"""Deterministic salary extraction from job descriptions (no LLM)."""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional

NOT_SPECIFIED = 'Not Specified'

# Ordered patterns — first match wins. Groups capture the human-readable salary span.
_SALARY_PATTERNS: List[re.Pattern[str]] = [
    re.compile(
        r'(?:salary|compensation|pay(?:\s+range)?|package|remuneration)'
        r'[:\s-]*'
        r'((?:USD|INR|EUR|GBP|CAD|AUD|\$|€|£|₹)\s*[\d,]+(?:\.\d+)?\s*[kK]?'
        r'(?:\s*[-–—]\s*(?:USD|INR|EUR|GBP|CAD|AUD|\$|€|£|₹)?\s*[\d,]+(?:\.\d+)?\s*[kK]?)?'
        r'(?:\s*(?:per\s+(?:year|annum|annually)|/yr|/year|p\.?a\.?|LPA|lpa))?'
        r')',
        re.IGNORECASE,
    ),
    re.compile(
        r'((?:USD|INR|EUR|GBP|CAD|AUD|\$|€|£|₹)\s*[\d,]+(?:\.\d+)?\s*[kK]'
        r'\s*[-–—]\s*(?:USD|INR|EUR|GBP|CAD|AUD|\$|€|£|₹)?\s*[\d,]+(?:\.\d+)?\s*[kK]'
        r'(?:\s*(?:per\s+(?:year|annum)|/yr|/year|p\.?a\.?|LPA|lpa))?)',
        re.IGNORECASE,
    ),
    re.compile(
        r'([\d,]+(?:\.\d+)?\s*(?:LPA|lpa))',
        re.IGNORECASE,
    ),
    re.compile(
        r'((?:USD|INR|EUR|GBP|CAD|AUD|\$|€|£|₹)\s*[\d,]+(?:\.\d+)?\s*[kK]?'
        r'(?:\s*(?:per\s+(?:year|annum|annually)|/yr|/year|p\.?a\.?))?)',
        re.IGNORECASE,
    ),
    re.compile(
        r'(\$[\d,]+(?:\.\d+)?\s*(?:[-–—]\s*\$[\d,]+(?:\.\d+)?)?)',
    ),
]


def _normalize_match(raw: str) -> str:
    """Collapse whitespace and trim punctuation from a salary span."""
    cleaned = re.sub(r'\s+', ' ', raw).strip(' .,;:')
    return cleaned if cleaned else NOT_SPECIFIED


def _search_texts(job: Dict) -> Iterable[str]:
    """Yield searchable text fields from a job record."""
    for key in ('description', 'title', 'salaryEstimate', 'compensation'):
        value = job.get(key)
        if value and str(value).strip() and str(value).strip().lower() not in {
            'not specified',
            'unknown',
            'n/a',
        }:
            yield str(value)


def extract_salary(job: Dict) -> str:
    """
    Extract a salary string from job text using regex/heuristics only.

    Returns ``Not Specified`` when no confident match is found.
    """
    for text in _search_texts(job):
        for pattern in _SALARY_PATTERNS:
            match = pattern.search(text)
            if match:
                normalized = _normalize_match(match.group(1))
                if normalized != NOT_SPECIFIED and len(normalized) >= 3:
                    return normalized
    return NOT_SPECIFIED


def extract_salary_with_source(job: Dict) -> tuple[str, Optional[str]]:
    """Return salary text and the field it was extracted from."""
    for key in ('description', 'title', 'salaryEstimate', 'compensation'):
        value = job.get(key)
        if not value or str(value).strip().lower() in {'not specified', 'unknown', 'n/a'}:
            continue
        text = str(value)
        for pattern in _SALARY_PATTERNS:
            match = pattern.search(text)
            if match:
                normalized = _normalize_match(match.group(1))
                if normalized != NOT_SPECIFIED and len(normalized) >= 3:
                    return normalized, key
    return NOT_SPECIFIED, None
