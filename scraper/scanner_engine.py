import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Protocol, Tuple

from apps.api.defaults import DEFAULT_PROFILE, normalize_profile
from scraper.ai_matcher import AIMatcher
from scraper.paths import DATA_FILE
from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.registry import get_registered_scanners

DB_FILE = DATA_FILE
DEFAULT_MIN_MATCH_SCORE = 75
DEFAULT_MIN_JOBS_PER_RUN = 3
DEFAULT_LIMIT_PER_SOURCE = 10


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
        self.scrapers: List[BaseScanner] = get_registered_scanners()
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

    @staticmethod
    def min_match_score() -> int:
        """Minimum match score (exclusive) required to persist a discovered job."""
        raw = os.environ.get("SCANNER_MIN_MATCH_SCORE", str(DEFAULT_MIN_MATCH_SCORE))
        try:
            return int(raw)
        except ValueError:
            return DEFAULT_MIN_MATCH_SCORE

    @staticmethod
    def min_jobs_per_run() -> int:
        """Minimum qualifying jobs to collect before stopping a scan cycle."""
        raw = os.environ.get("SCANNER_MIN_JOBS_PER_RUN", str(DEFAULT_MIN_JOBS_PER_RUN))
        try:
            return max(1, int(raw))
        except ValueError:
            return DEFAULT_MIN_JOBS_PER_RUN

    @staticmethod
    def _coerce_score(analysis: Dict) -> int:
        score = analysis.get("score")
        if isinstance(score, (int, float)):
            return int(score)
        if isinstance(score, str):
            try:
                return int(float(score.strip().rstrip("%")))
            except ValueError:
                return 0
        return 0

    def _apply_match_analysis(self, canonical: Dict, profile: Dict) -> int:
        """Score a job and attach match metadata. Returns numeric match score."""
        analysis = self.ai_matcher.score_job(canonical, profile)
        score = self._coerce_score(analysis)
        canonical.update(
            {
                "score": score,
                "extractedSkills": analysis.get("extractedSkills", []),
                "seniority": analysis.get("seniority", "Unknown"),
                "remoteType": analysis.get("remoteType", canonical.get("remoteType")),
                "salaryEstimate": analysis.get("salaryEstimate", "Not Specified"),
                "fitExplanation": analysis.get("fitExplanation", ""),
                "postedAt": datetime.utcnow().isoformat() + "Z",
            }
        )
        return score

    def run(
        self,
        limit_per_source: int = DEFAULT_LIMIT_PER_SOURCE,
        min_match_score: Optional[int] = None,
        min_jobs: Optional[int] = None,
    ) -> List[Dict]:
        """Run pipeline across scanners until enough high-match jobs are found."""
        threshold = self.min_match_score() if min_match_score is None else min_match_score
        target_jobs = self.min_jobs_per_run() if min_jobs is None else max(1, min_jobs)

        print("=== AI Job Hunter: Starting Automated Scraper Pipeline ===")
        print(
            f"[ScannerEngine] Match policy: score must exceed {threshold}% "
            f"(target {target_jobs} job(s) per scan)."
        )

        profile = self.store.get_profile()
        existing_urls, existing_signatures = self.store.get_dedupe_indexes()

        added_jobs: List[Dict] = []
        evaluated_count = 0
        ignored_low_score = 0

        for scraper in self.scrapers:
            if len(added_jobs) >= target_jobs:
                print(
                    f"[ScannerEngine] Reached target of {target_jobs} qualifying job(s). "
                    "Stopping scan."
                )
                break

            print(f"[ScannerEngine] Invoking: {scraper.name} scraper...")

            if not scraper.health_check():
                print(f"[ScannerEngine] Health Check failed for {scraper.name}. Skipping.")
                continue

            raw_jobs = scraper.discover_jobs(limit=limit_per_source)
            for raw_job in raw_jobs:
                if len(added_jobs) >= target_jobs:
                    break

                canonical = scraper.normalize(raw_job)
                signature = f"{canonical.get('title')}-{canonical.get('company')}".lower()
                if canonical.get("url") in existing_urls or signature in existing_signatures:
                    continue

                evaluated_count += 1
                score = self._apply_match_analysis(canonical, profile)

                if score <= threshold:
                    ignored_low_score += 1
                    print(
                        f"[ScannerEngine] Ignored (match {score}% <= {threshold}%): "
                        f"{canonical.get('title')} at {canonical.get('company')}"
                    )
                    continue

                print(
                    f"[ScannerEngine] Accepted (match {score}%): "
                    f"{canonical.get('title')} at {canonical.get('company')}"
                )
                added_jobs.append(canonical)
                existing_urls.add(canonical.get("url"))
                existing_signatures.add(signature)

        if added_jobs:
            self.store.persist_new_jobs(added_jobs)
            target = "Supabase" if isinstance(self.store, SupabaseJobStore) else "data.json"
            print(
                f"[ScannerEngine] Sync complete! Registered {len(added_jobs)} job(s) "
                f"with match score above {threshold}% in {target}."
            )
        else:
            print(
                f"[ScannerEngine] Sync complete! No jobs exceeded the {threshold}% match threshold "
                f"in this cycle (evaluated {evaluated_count}, ignored {ignored_low_score})."
            )

        if len(added_jobs) < target_jobs:
            print(
                f"[ScannerEngine] Warning: only {len(added_jobs)} qualifying job(s) found "
                f"(target {target_jobs}). Consider broadening sources or profile skills."
            )

        return added_jobs


if __name__ == "__main__":
    ScannerEngine().run()
