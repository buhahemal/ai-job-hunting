"""Scanner configuration helpers."""

from __future__ import annotations

import os
from typing import List


def parse_env_list(key: str) -> List[str]:
    """Parse comma-separated environment variable into a trimmed list."""
    raw = os.environ.get(key, '')
    return [item.strip() for item in raw.split(',') if item.strip()]
