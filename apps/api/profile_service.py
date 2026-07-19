"""Profile validation and import merge."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Tuple

from packages.database.python.profile import normalize_stored_profile
from packages.database.python.profile_helpers import validate_profile_payload


def merge_import_payload(existing: Dict[str, Any], imported: Dict[str, Any]) -> Dict[str, Any]:
    """Merge imported JSON into the current profile, preferring imported values."""
    merged = deepcopy(existing)
    for key, value in imported.items():
        if key == 'preferences' and isinstance(value, dict):
            merged['preferences'] = {
                **(merged.get('preferences') or {}),
                **value,
            }
        elif key == 'matchSettings' and isinstance(value, dict):
            merged['matchSettings'] = {
                **(merged.get('matchSettings') or {}),
                **value,
            }
        elif value not in (None, '', [], {}):
            merged[key] = value
    return merged


def prepare_profile_for_save(raw: Dict[str, Any], *, regenerate_latex: bool = False) -> Dict[str, Any]:
    """Normalize and validate profile before persistence."""
    profile = normalize_stored_profile(raw)
    validate_profile_payload(profile)
    return profile


def import_profile_payload(
    existing: Dict[str, Any],
    imported: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Merge import payload and return profile plus a summary of applied keys."""
    merged_raw = merge_import_payload(existing, imported)
    profile = prepare_profile_for_save(merged_raw)
    applied_keys = sorted(key for key in imported.keys() if key in profile)
    return profile, {'appliedKeys': applied_keys, 'fieldCount': len(applied_keys)}

