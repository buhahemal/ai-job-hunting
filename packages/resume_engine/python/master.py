"""Load immutable master resume JSON."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict

from packages.config.python.paths import MASTER_RESUME_JSON
from packages.database.python.profile_helpers import profile_to_master_resume


def load_master_resume(path: str | Path | None = None) -> Dict[str, Any]:
    """
    Load the master resume JSON (read-only source of truth).

    Returns:
        Deep-copied dict so callers cannot mutate the canonical master on disk.
    """
    source = Path(path or MASTER_RESUME_JSON)
    if not source.is_file():
        raise FileNotFoundError(f'Master resume JSON not found: {source}')

    with source.open(encoding='utf-8') as handle:
        data = json.load(handle)

    return copy.deepcopy(data)


def load_master_resume_from_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a master resume payload from a unified profile document.

    Falls back to disk master.json when the profile lacks resume content.
    """
    has_content = bool(
        str(profile.get('fullName') or '').strip()
        and (
            profile.get('experience')
            or str(profile.get('summary') or '').strip()
            or profile.get('skills')
        )
    )
    if not has_content:
        return load_master_resume()

    return copy.deepcopy(profile_to_master_resume(profile))
