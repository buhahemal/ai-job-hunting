#!/usr/bin/env python3
"""Run health checks for all registered scanner plugins."""

import sys

from scraper.scrapers.arbeitnow import ArbeitnowScanner
from scraper.scrapers.career_portal import CareerPortalScanner


def main() -> int:
    scanners = [ArbeitnowScanner(), CareerPortalScanner()]
    failed = []

    for scanner in scanners:
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
