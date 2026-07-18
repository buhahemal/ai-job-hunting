"""Optional, reviewed ATS board seeds for zero-config discovery."""

import json
import os
from pathlib import Path
from typing import Dict, List

DEFAULT_SEED_PATH = Path(__file__).resolve().parents[3] / 'scanners' / 'ats-seeds.json'
ENV_BY_PLATFORM = {
    'greenhouse': 'GREENHOUSE_BOARD_TOKENS',
    'lever': 'LEVER_COMPANY_SITES',
    'workable': 'WORKABLE_ACCOUNT_SLUGS',
    'ashby': 'ASHBY_JOB_BOARD_SLUGS',
}


def _enabled() -> bool:
    return os.environ.get('ATS_DISCOVERY_ENABLED', '').strip().lower() in {'1', 'true', 'yes'}


def _merge_env(name: str, values: List[str]) -> None:
    existing = [value.strip() for value in os.environ.get(name, '').split(',') if value.strip()]
    merged = existing + [value for value in values if value and value not in existing]
    if merged:
        os.environ[name] = ','.join(merged)


def apply_ats_seed_environment(path: str | Path = DEFAULT_SEED_PATH) -> None:
    """Merge reviewed board identifiers into scanner env configuration."""
    if not _enabled():
        return
    seed_path = Path(path)
    if not seed_path.is_file():
        return
    payload: Dict[str, List[str]] = json.loads(seed_path.read_text(encoding='utf-8'))
    for platform, env_name in ENV_BY_PLATFORM.items():
        _merge_env(env_name, payload.get(platform, []))
