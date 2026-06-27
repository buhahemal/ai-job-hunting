import requests
from typing import List, Dict
from scanners.base import BaseScanner

class ArbeitnowScanner(BaseScanner):
    """
    Job Scanner Plugin for the Arbeitnow Job Board API.
    """

    @property
    def name(self) -> str:
        return "Arbeitnow"

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        """
        Polls the public Arbeitnow feed.
        """
        url = "https://www.arbeitnow.com/api/job-board-api"
        try:
            response = requests.get(url, headers={"User-Agent": "AI-Job-Hunter-Agent"}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("data", [])
                return jobs[:limit]
            else:
                print(f"[ArbeitnowScanner] Warning: Received status code {response.status_code}")
                return []
        except Exception as e:
            print(f"[ArbeitnowScanner] Error during discovery: {e}")
            return []

    def normalize(self, raw_job: Dict) -> Dict:
        """
        Translates Arbeitnow raw records to canonical Job schema.
        """
        slug = raw_job.get("slug", "")
        external_id = f"arbeit-{slug}"
        
        # Clean HTML tags from description
        description = raw_job.get("description", "")
        import re
        clean_description = re.sub(r'<[^>]*>', '', description).strip()

        return {
            "id": external_id,
            "title": raw_job.get("title", "Unknown Role"),
            "company": raw_job.get("company_name", "Unknown Company"),
            "location": raw_job.get("location", "Remote"),
            "remoteType": "Remote" if raw_job.get("remote") else "Hybrid",
            "source": self.name,
            "url": raw_job.get("url", ""),
            "description": clean_description,
            "status": "New"
        }

    def health_check(self) -> bool:
        url = "https://www.arbeitnow.com/api/job-board-api"
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except:
            return False
