"""Central registry of active scanner plugins."""

from __future__ import annotations

from typing import List

from packages.scanner_sdk.python.base import BaseScanner


def get_registered_scanners() -> List[BaseScanner]:
    """Return all scanner plugins available to the pipeline."""
    from scanners.arbeitnow.scanner import ArbeitnowScanner
    from scanners.company_pages.scanner import CompanyPagesScanner
    from scanners.greenhouse.scanner import GreenhouseScanner

    return [
        ArbeitnowScanner(),
        CompanyPagesScanner(),
        GreenhouseScanner(),
    ]
