from abc import ABC, abstractmethod
from typing import Dict, List


class BaseScanner(ABC):
    """Abstract job scanner plugin. All sources must implement this contract."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Logical name of the job source."""

    @abstractmethod
    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        """Poll or crawl the source and return raw listing records."""

    @abstractmethod
    def normalize(self, raw_job: Dict) -> Dict:
        """Transform a raw record into the canonical job schema."""

    @abstractmethod
    def health_check(self) -> bool:
        """Return True when the source is reachable."""
