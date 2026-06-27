import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Protocol, Tuple

from apps.api.defaults import DEFAULT_PROFILE, normalize_profile
from scraper.ai_matcher import AIMatcher
from scraper.paths import DATA_FILE
from scanners.arbeitnow import ArbeitnowScanner
from scanners.base import BaseScanner
from scanners.career_portal import CareerPortalScanner

DB_FILE = DATA_FILE


class JobStore(Protocol):
    """Persistence backend for scanner pipeline."""

    def get_profile(self) -> Dict: ...

    def get_dedupe_indexes(self) -> Tuple[set, set]: ...

    def persist_new_jobs(self, jobs: List[Dict]) -> None: ...


class JsonJobStore:
    """Legacy JSON file store (USE_JSON_STORE=true or missing Supabase config)."""

    def __init__(self, path: str = DB_FILE):
        self._path = path

    def read_db(self) -> Dict:
        if not os.path.exists(self._path):
            print("[JsonJobStore] Warning: Database file not found. Initializing.")
            return {"profile": DEFAULT_PROFILE, "jobs": [], "interviews": []}
        try:
            with open(self._path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
                data["profile"] = normalize_profile(data.get("profile"))
                return data
        except Exception as exc:
            print(f"[JsonJobStore] Error reading data.json: {exc}")
            return {"profile": DEFAULT_PROFILE, "jobs": [], "interviews": []}

    def get_profile(self) -> Dict:
        return self.read_db().get("profile", DEFAULT_PROFILE)

    def get_dedupe_indexes(self) -> Tuple[set, set]:
        jobs = self.read_db().get("jobs", [])
        urls = {j.get("url") for j in jobs if j.get("url")}
        signatures = {f"{j.get('title')}-{j.get('company')}".lower() for j in jobs}
        return urls, signatures

    def persist_new_jobs(self, jobs: List[Dict]) -> None:
        db = self.read_db()
        db["jobs"] = jobs + db.get("jobs", [])
        with open(self._path, "w", encoding="utf-8") as handle:
            json.dump(db, handle, indent=2)


class SupabaseJobStore:
    """Supabase-backed store for GitHub Actions pipeline."""

    def __init__(self, repository):
        self._repo = repository

    def get_profile(self) -> Dict:
        profile = self._repo.get_profile()
        return normalize_profile(profile)

    def get_dedupe_indexes(self) -> Tuple[set, set]:
        return self._repo.get_dedupe_indexes()

    def persist_new_jobs(self, jobs: List[Dict]) -> None:
        count = self._repo.upsert_jobs(jobs)
        print(f"[SupabaseJobStore] Upserted {count} job(s) to Supabase.")


def create_job_store() -> JobStore:
    """Select JSON or Supabase store from environment."""
    from packages.database.python.client import is_supabase_configured, use_json_store
    from packages.database.python.repositories.jobs import JobRepository
    from packages.database.python.client import create_service_client

    if use_json_store() or not is_supabase_configured():
        if not use_json_store() and not is_supabase_configured():
            print("[ScannerEngine] Supabase not configured — falling back to JSON store.")
        return JsonJobStore()

    client = create_service_client()
    return SupabaseJobStore(JobRepository(client))


class ScannerEngine:
    """
    Coordinator engine running scheduled scans across active scanner plugins.
    """

    def __init__(self, store: Optional[JobStore] = None):
        self.scrapers: List[BaseScanner] = [
            ArbeitnowScanner(),
            CareerPortalScanner(),
        ]
        self.ai_matcher = AIMatcher()
        self.store = store or create_job_store()

    def read_db(self) -> Dict:
        """Compatibility helper for tests using JSON layout."""
        if isinstance(self.store, JsonJobStore):
            return self.store.read_db()
        profile = self.store.get_profile()
        jobs = self.store._repo.list_jobs() if isinstance(self.store, SupabaseJobStore) else []
        interviews = (
            self.store._repo.list_interviews() if isinstance(self.store, SupabaseJobStore) else []
        )
        return {"profile": profile, "jobs": jobs, "interviews": interviews}

    def write_db(self, data: Dict):
        """Compatibility helper for tests."""
        if isinstance(self.store, JsonJobStore):
            with open(DB_FILE, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2)

    def run(self, limit_per_source: int = 5) -> List[Dict]:
        """Run complete synchronized pipeline across all registered scanners."""
        print("=== AI Job Hunter: Starting Automated Scraper Pipeline ===")
        profile = self.store.get_profile()
        existing_urls, existing_signatures = self.store.get_dedupe_indexes()

        discovered_count = 0
        added_jobs = []

        for scraper in self.scrapers:
            print(f"[ScannerEngine] Invoking: {scraper.name} scraper...")

            if not scraper.health_check():
                print(f"[ScannerEngine] Health Check failed for {scraper.name}. Skipping.")
                continue

            raw_jobs = scraper.discover_jobs(limit=limit_per_source)
            for raw_job in raw_jobs:
                canonical = scraper.normalize(raw_job)

                signature = f"{canonical.get('title')}-{canonical.get('company')}".lower()
                if canonical.get("url") in existing_urls or signature in existing_signatures:
                    continue

                print(
                    f"[ScannerEngine] Discovered New Lead: {canonical.get('title')} at {canonical.get('company')}"
                )

                analysis = self.ai_matcher.score_job(canonical, profile)
                canonical.update(
                    {
                        "score": analysis.get("score", 70),
                        "extractedSkills": analysis.get("extractedSkills", []),
                        "seniority": analysis.get("seniority", "Unknown"),
                        "remoteType": analysis.get("remoteType", canonical.get("remoteType")),
                        "salaryEstimate": analysis.get("salaryEstimate", "Not Specified"),
                        "fitExplanation": analysis.get("fitExplanation", ""),
                        "postedAt": datetime.utcnow().isoformat() + "Z",
                    }
                )

                added_jobs.append(canonical)
                existing_urls.add(canonical.get("url"))
                existing_signatures.add(signature)
                discovered_count += 1

        if added_jobs:
            self.store.persist_new_jobs(added_jobs)
            target = "Supabase" if isinstance(self.store, SupabaseJobStore) else "data.json"
            print(
                f"[ScannerEngine] Sync complete! Registered {discovered_count} new scored opportunities in {target}."
            )
        else:
            print("[ScannerEngine] Sync complete! No new unique job opportunities identified in this cycle.")

        return added_jobs


if __name__ == "__main__":
    ScannerEngine().run()
