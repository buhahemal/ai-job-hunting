"""Cross-run job deduplication helpers for the scanner pipeline."""

from __future__ import annotations

from typing import Dict, Iterable, List, Set


def job_dedupe_key(job: Dict) -> str:
    """
    Stable unique key for a canonical job.

    Prefers URL; falls back to lowercase title-company signature.
    """
    url = (job.get("url") or "").strip()
    if url:
        return url
    title = (job.get("title") or "").strip()
    company = (job.get("company") or "").strip()
    return f"{title}-{company}".lower()


def merge_scanned_keys(scanned_keys: Set[str], jobs: Iterable[Dict]) -> Set[str]:
    """Combine persisted scan registry with keys derived from saved jobs."""
    merged = set(scanned_keys)
    for job in jobs:
        merged.add(job_dedupe_key(job))
    return merged


def scanned_job_record(job: Dict, *, score: int) -> Dict:
    """Build a minimal scanned-job record for persistence."""
    return {
        "dedupe_key": job_dedupe_key(job),
        "job_id": job.get("id"),
        "source": job.get("source"),
        "score": score,
    }


def dedupe_key_list(keys: Iterable[str]) -> List[str]:
    """Return sorted unique keys for stable JSON storage."""
    return sorted({key for key in keys if key})
