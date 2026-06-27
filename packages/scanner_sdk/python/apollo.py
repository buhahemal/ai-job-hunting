"""Helpers for parsing Apollo GraphQL cache embedded in Next.js __NEXT_DATA__."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional


def _is_ref(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and not isinstance(value, list)
        and set(value.keys()) == {'__ref'}
    )


def resolve_apollo_value(value: Any, graph: Dict[str, Any]) -> Any:
    """Resolve Apollo __ref pointers inside a graph node."""
    if _is_ref(value):
        return resolve_apollo_value(graph.get(value['__ref'], {}), graph)
    if isinstance(value, list):
        return [resolve_apollo_value(item, graph) for item in value]
    if isinstance(value, dict):
        return {key: resolve_apollo_value(item, graph) for key, item in value.items()}
    return value


def extract_apollo_graph(next_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return the Apollo cache map from a parsed __NEXT_DATA__ object."""
    page_props = next_data.get('props', {}).get('pageProps', {})
    apollo_state = page_props.get('apolloState', {})
    data = apollo_state.get('data', {})
    return data if isinstance(data, dict) else {}


def parse_next_data_html(html: str) -> Optional[Dict[str, Any]]:
    """Extract and parse the __NEXT_DATA__ JSON payload from HTML."""
    match = re.search(
        r'<script[^>]+id="__NEXT_DATA__"[^>]*>(?P<payload>.*?)</script>',
        html,
        flags=re.DOTALL,
    )
    if not match:
        return None
    try:
        parsed = json.loads(match.group('payload'))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def extract_wellfound_jobs(next_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract job listing nodes from Wellfound Apollo state."""
    graph = extract_apollo_graph(next_data)
    jobs: List[Dict[str, Any]] = []

    for key, node in graph.items():
        if not key.startswith('JobListingSearchResult:'):
            continue
        if not isinstance(node, dict):
            continue

        resolved = resolve_apollo_value(node, graph)
        startup = resolved.get('startup') or resolved.get('company') or {}
        if isinstance(startup, dict):
            resolved['_company_name'] = startup.get('name', 'Unknown Company')
            resolved['_company_slug'] = startup.get('slug', '')
        else:
            resolved['_company_name'] = 'Unknown Company'
            resolved['_company_slug'] = ''

        location_names = resolved.get('locationNames')
        if isinstance(location_names, dict) and isinstance(location_names.get('json'), list):
            resolved['_location'] = ', '.join(location_names['json']) or 'Remote'
        else:
            resolved['_location'] = 'Remote'

        remote_flag = resolved.get('remote')
        if remote_flag is None:
            remote_flag = resolved.get('remtoe')
        resolved['_remote'] = bool(remote_flag)

        jobs.append(resolved)

    return jobs
