from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScanner(ABC):
    """
    Abstract Base Class representing a Modular Job Scanner plugin.
    Every custom parser or board integrator must inherit from this
    and implement all required interfaces.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The logical name of the job source."""
        pass

    @abstractmethod
    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        """
        Polls or crawls the target source to retrieve active listings.
        Should return raw or semi-normalized data records.
        """
        pass

    @abstractmethod
    def normalize(self, raw_job: Dict) -> Dict:
        """
        Transforms a raw listing record into the canonical Job schema.
        Canonical format:
        {
            "id": str,
            "title": str,
            "company": str,
            "location": str,
            "remoteType": "Remote" | "Hybrid" | "On-site",
            "source": str,
            "url": str,
            "description": str,
            "status": "New"
        }
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Checks connectivity to the target source feed or API.
        Returns True if reachable, False otherwise.
        """
        pass
