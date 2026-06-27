"""Load immutable master resume JSON."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict

from packages.config.python.paths import MASTER_RESUME_JSON


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
