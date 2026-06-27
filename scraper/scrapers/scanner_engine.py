import os
import json
from datetime import datetime
from typing import Dict, List

from scraper.ai_matcher import AIMatcher
from scraper.paths import DATA_FILE
from scraper.scrapers.arbeitnow import ArbeitnowScanner
from scraper.scrapers.base import BaseScanner
from scraper.scrapers.career_portal import CareerPortalScanner

DB_FILE = DATA_FILE

class ScannerEngine:
    """
    Coordinator engine running scheduled scans across active scanner plugins.
    """

    def __init__(self):
        self.scrapers: List[BaseScanner] = [
            ArbeitnowScanner(),
            CareerPortalScanner()
        ]
        self.ai_matcher = AIMatcher()

    def read_db(self) -> Dict:
        """Reads flat data store with dynamic default profile fallback."""
        if not os.path.exists(DB_FILE):
            print("[ScannerEngine] Warning: Database file not found. Initializing.")
            return {"profile": {}, "jobs": [], "interviews": []}
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ScannerEngine] Error reading data.json: {e}")
            return {"profile": {}, "jobs": [], "interviews": []}

    def write_db(self, data: Dict):
        """Saves current database state."""
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[ScannerEngine] Error writing database state: {e}")

    def run(self, limit_per_source: int = 5) -> List[Dict]:
        """
        Runs complete synchronized pipeline across all registered scanners.
        """
        print("=== AI Job Hunter: Starting Automated Scraper Pipeline ===")
        db = self.read_db()
        profile = db.get("profile", {})
        existing_jobs = db.get("jobs", [])
        
        # Build deduplication indexes
        existing_urls = {j.get("url") for j in existing_jobs if j.get("url")}
        existing_signatures = {f"{j.get('title')}-{j.get('company')}".lower() for j in existing_jobs}

        discovered_count = 0
        added_jobs = []

        for scraper in self.scrapers:
            print(f"[ScannerEngine] Invoking: {scraper.name} scraper...")
            
            # Health check source first
            if not scraper.health_check():
                print(f"[ScannerEngine] Health Check failed for {scraper.name}. Skipping.")
                continue

            raw_jobs = scraper.discover_jobs(limit=limit_per_source)
            for raw_job in raw_jobs:
                canonical = scraper.normalize(raw_job)
                
                # Check for duplication (URL matching and title-company matching)
                signature = f"{canonical.get('title')}-{canonical.get('company')}".lower()
                if canonical.get("url") in existing_urls or signature in existing_signatures:
                    continue

                print(f"[ScannerEngine] Discovered New Lead: {canonical.get('title')} at {canonical.get('company')}")
                
                # Dynamic scoring
                analysis = self.ai_matcher.score_job(canonical, profile)
                canonical.update({
                    "score": analysis.get("score", 70),
                    "extractedSkills": analysis.get("extractedSkills", []),
                    "seniority": analysis.get("seniority", "Unknown"),
                    "remoteType": analysis.get("remoteType", canonical.get("remoteType")),
                    "salaryEstimate": analysis.get("salaryEstimate", "Not Specified"),
                    "fitExplanation": analysis.get("fitExplanation", ""),
                    "postedAt": datetime.utcnow().isoformat() + "Z"
                })

                added_jobs.append(canonical)
                existing_urls.add(canonical.get("url"))
                existing_signatures.add(signature)
                discovered_count += 1

        if added_jobs:
            # Inject new items at top of list
            db["jobs"] = added_jobs + existing_jobs
            self.write_db(db)
            print(f"[ScannerEngine] Sync complete! Registered {discovered_count} new scored opportunities in data.json.")
        else:
            print("[ScannerEngine] Sync complete! No new unique job opportunities identified in this cycle.")

        return added_jobs
if __name__ == "__main__":
    ScannerEngine().run()
