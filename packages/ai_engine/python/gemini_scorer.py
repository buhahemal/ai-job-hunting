"""Deprecated optional Gemini scorer — removed from default pipeline in Phase 6.

The production path uses local Hugging Face embeddings and heuristic scoring only.
This module is retained for reference; it is not imported by matcher.py.
"""

from __future__ import annotations

import json
import os
import time
from typing import Dict, Optional

from google import genai
from google.genai import types

_client: Optional[genai.Client] = None
_init_checked = False


def is_available() -> bool:
    """Return True when a valid Gemini API key is configured."""
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    return bool(api_key) and api_key != 'MY_GEMINI_API_KEY'


def get_client() -> Optional[genai.Client]:
    """Lazy initialization of the Google GenAI client."""
    global _client, _init_checked
    if _client is not None:
        return _client

    if not _init_checked:
        if is_available():
            try:
                _client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
                print('[GeminiScorer] Loaded Gemini client for optional fallback scoring.')
            except Exception as exc:
                print(f'[GeminiScorer] Failed to initialize Gemini client: {exc}')
        else:
            print('[GeminiScorer] GEMINI_API_KEY not configured; skipping Gemini fallback.')
        _init_checked = True

    return _client


def reset_client_cache() -> None:
    """Clear cached Gemini client state (used in tests)."""
    global _client, _init_checked
    _client = None
    _init_checked = False


def score(job: Dict, profile: Dict) -> Dict:
    """Score a job using Gemini structured JSON output."""
    client = get_client()
    if not client:
        raise RuntimeError('Gemini scorer unavailable')

    prompt = f"""You are an expert AI Technical Recruiter. Analyze the following job description against the candidate's professional profile.

CANDIDATE PROFILE:
{json.dumps(profile, indent=2)}

JOB DETAILS:
Title: {job.get('title')}
Company: {job.get('company')}
Location: {job.get('location')}
Description: {job.get('description')}

Assess skills matching, salary parameters, remote preference alignment, and candidate fit.
"""

    schema = {
        'type': 'OBJECT',
        'properties': {
            'score': {'type': 'INTEGER'},
            'extractedSkills': {'type': 'ARRAY', 'items': {'type': 'STRING'}},
            'seniority': {'type': 'STRING'},
            'remoteType': {'type': 'STRING'},
            'salaryEstimate': {'type': 'STRING'},
            'fitExplanation': {'type': 'STRING'},
        },
        'required': [
            'score',
            'extractedSkills',
            'seniority',
            'remoteType',
            'salaryEstimate',
            'fitExplanation',
        ],
    }

    delay = 1.0
    last_error: Optional[Exception] = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=schema,
                ),
            )
            parsed = json.loads(response.text)
            parsed['scorer'] = 'gemini'
            return parsed
        except Exception as exc:
            last_error = exc
            print(f'[GeminiScorer] Gemini error (attempt {attempt + 1}): {exc}. Retrying in {delay}s...')
            time.sleep(delay)
            delay *= 2

    raise RuntimeError(f'Gemini scoring failed after retries: {last_error}')
