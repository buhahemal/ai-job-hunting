#!/usr/bin/env python3
"""Run import preflight and health checks for the scanner pipeline."""

from __future__ import annotations

import importlib
import sys
from typing import Iterable

from packages.scanner_sdk.python.registry import get_registered_scanners

PIPELINE_MODULES = (
    'scraper.scanner_engine',
    'scraper.rescan_engine',
    'scraper.ai_matcher',
)


def verify_pipeline_imports(modules: Iterable[str] = PIPELINE_MODULES) -> list[str]:
    """Import scanner modules to catch definition/order errors before a scan run."""
    failed: list[str] = []

    for module_name in modules:
        try:
            importlib.import_module(module_name)
            print(f'[OK] import {module_name}')
        except Exception as exc:
            print(f'[FAIL] import {module_name}: {exc}', file=sys.stderr)
            failed.append(module_name)

    return failed


def verify_scanner_plugins() -> list[str]:
    """Run health_check() on every registered scanner plugin."""
    failed: list[str] = []

    for scanner in get_registered_scanners():
        healthy = scanner.health_check()
        status = 'OK' if healthy else 'FAIL'
        print(f'[{status}] {scanner.name}')
        if not healthy:
            failed.append(scanner.name)

    return failed


def main() -> int:
    import_failures = verify_pipeline_imports()
    plugin_failures = verify_scanner_plugins()

    if import_failures:
        print(
            'Scanner import preflight failed for: '
            + ', '.join(import_failures),
            file=sys.stderr,
        )
        return 1

    if plugin_failures:
        print(
            'Scanner plugin health check failed for: '
            + ', '.join(plugin_failures),
            file=sys.stderr,
        )
        return 1

    print('Scanner preflight and health checks passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
