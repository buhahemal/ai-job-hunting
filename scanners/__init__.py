"""Job source scanner plugins."""

from scanners.arbeitnow import ArbeitnowScanner
from scanners.base import BaseScanner
from scanners.career_portal import CareerPortalScanner

__all__ = ['ArbeitnowScanner', 'BaseScanner', 'CareerPortalScanner']
