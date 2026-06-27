"""Job source scanner plugins."""

from packages.scanner_sdk.python.base import BaseScanner
from scanners.company_pages import CompanyPagesScanner
from scanners.greenhouse import GreenhouseScanner
from scanners.lever import LeverScanner
from scanners.remoteok import RemoteOkScanner
from scanners.smartrecruiters import SmartRecruitersScanner
from scanners.teamtailor import TeamtailorScanner
from scanners.weworkremotely import WeWorkRemotelyScanner
from scanners.workable import WorkableScanner

__all__ = [
    'BaseScanner',
    'CompanyPagesScanner',
    'GreenhouseScanner',
    'LeverScanner',
    'RemoteOkScanner',
    'SmartRecruitersScanner',
    'TeamtailorScanner',
    'WeWorkRemotelyScanner',
    'WorkableScanner',
]
