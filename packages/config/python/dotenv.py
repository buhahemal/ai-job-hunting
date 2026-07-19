"""Load repo-root `.env` into process environment (no external dependency)."""

from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: str | os.PathLike[str] | None = None, *, override: bool = False) -> Path | None:
    """
    Parse KEY=VALUE lines from a .env file into os.environ.

    Existing variables are kept unless ``override`` is True.
    Returns the path loaded, or None if the file is missing.
    """
    env_path = Path(path) if path else Path(__file__).resolve().parents[3] / '.env'
    if not env_path.is_file():
        return None

    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if override or key not in os.environ:
            os.environ[key] = value
    return env_path
