#!/usr/bin/env python3
"""Run health checks for all registered scanner plugins."""

import sys

from packages.scanner_sdk.python.registry import get_registered_scanners


def main() -> int:
    failed = []

    for scanner in get_registered_scanners():
        healthy = scanner.health_check()
        status = 'OK' if healthy else 'FAIL'
        print(f'[{status}] {scanner.name}')
        if not healthy:
            failed.append(scanner.name)

    if failed:
        print(f'Health check failed for: {", ".join(failed)}', file=sys.stderr)
        return 1

    print('All scanner health checks passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
