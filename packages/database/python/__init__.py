"""Supabase database access layer for AI Job Hunter."""

from packages.database.python.client import create_service_client, is_supabase_configured
from packages.database.python.mappers import dedupe_indexes, job_to_row, row_to_interview, row_to_job


def __getattr__(name: str):
    if name == 'JobRepository':
        from packages.database.python.repositories.jobs import JobRepository

        return JobRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    'JobRepository',
    'create_service_client',
    'dedupe_indexes',
    'is_supabase_configured',
    'job_to_row',
    'row_to_interview',
    'row_to_job',
]
