"""Central registry of active scanner plugins."""

from __future__ import annotations

from typing import List

from packages.scanner_sdk.python.base import BaseScanner


def get_registered_scanners() -> List[BaseScanner]:
    """Return all scanner plugins available to the pipeline."""
    from scanners.arbeitnow.scanner import ArbeitnowScanner
    from scanners.ashby.scanner import AshbyScanner
    from scanners.company_pages.scanner import CompanyPagesScanner
    from scanners.greenhouse.scanner import GreenhouseScanner
    from scanners.lever.scanner import LeverScanner
    from scanners.remoteok.scanner import RemoteOkScanner
    from scanners.smartrecruiters.scanner import SmartRecruitersScanner
    from scanners.teamtailor.scanner import TeamtailorScanner
    from scanners.wellfound.scanner import WellfoundScanner
    from scanners.weworkremotely.scanner import WeWorkRemotelyScanner
    from scanners.workable.scanner import WorkableScanner
    from scanners.workday.scanner import WorkdayScanner

    return [
        GreenhouseScanner(),
        LeverScanner(),
        SmartRecruitersScanner(),
        TeamtailorScanner(),
        WorkableScanner(),
        RemoteOkScanner(),
        WeWorkRemotelyScanner(),
        CompanyPagesScanner(),
        ArbeitnowScanner(),
        AshbyScanner(),
        WorkdayScanner(),
        WellfoundScanner(),
    ]
