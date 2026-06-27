import os
import json
from typing import Dict, List, Optional, Protocol, Tuple

from apps.api.defaults import DEFAULT_PROFILE, normalize_profile
from scraper.ai_matcher import AIMatcher
from scraper.paths import DATA_FILE
from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.dedupe import job_dedupe_key, merge_scanned_keys, scan_run_id, scanned_job_record
from packages.scanner_sdk.python.registry import get_registered_scanners

from packages.database.python.constants import (
    MATCH_SCORE_THRESHOLD,
    SCANNER_LIMIT_PER_SOURCE,
    SCANNER_LIMIT_STEP,
    SCANNER_MAX_EVALUATIONS,
    SCANNER_MAX_LIMIT_PER_SOURCE,
    SCANNER_MAX_PASSES,
    SCANNER_MIN_JOBS_PER_RUN,
    SCANNER_SCAN_INSIGHT_BATCH_SIZE,
)

DB_FILE = DATA_FILE


class JobStore(Protocol):
    """Persistence backend for scanner pipeline."""

    def get_profile(self) -> Dict: ...

    def get_dedupe_indexes(self) -> Tuple[set, set]: ...

    def get_scanned_keys(self) -> set: ...

    def record_scanned_jobs(self, records: List[Dict]) -> None: ...

    def persist_new_jobs(self, jobs: List[Dict]) -> None: ...


class ScanInsightBuffer:
    """Buffer scanned job insight rows and flush to the store in fixed-size batches."""

    def __init__(self, store: JobStore, batch_size: int = SCANNER_SCAN_INSIGHT_BATCH_SIZE):
        self._store = store
        self._batch_size = max(1, batch_size)
        self._pending: List[Dict] = []

    def append(self, record: Dict) -> None:
        """Queue one insight row; flush automatically when the batch is full."""
        self._pending.append(record)
        if len(self._pending) >= self._batch_size:
            self.flush()

    def flush(self) -> None:
        """Persist any queued insight rows."""
        if not self._pending:
            return
        self._store.record_scanned_jobs(self._pending)
        self._pending.clear()

    @property
    def pending_count(self) -> int:
        return len(self._pending)


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

    def get_scanned_keys(self) -> set:
        db = self.read_db()
        keys: set = set()
        scanned_jobs = db.get("scannedJobs", [])
        if isinstance(scanned_jobs, list):
            for entry in scanned_jobs:
                key = entry.get("dedupe_key") or entry.get("dedupeKey")
                if key:
                    keys.add(key)
        legacy_keys = db.get("scannedJobKeys", [])
        if isinstance(legacy_keys, list):
            keys.update(legacy_keys)
        return keys

    def record_scanned_jobs(self, records: List[Dict]) -> None:
        if not records:
            return
        db = self.read_db()
        existing_jobs = db.get("scannedJobs", [])
        if not isinstance(existing_jobs, list):
            existing_jobs = []

        by_key = {
            (entry.get("dedupe_key") or entry.get("dedupeKey")): entry
            for entry in existing_jobs
            if entry.get("dedupe_key") or entry.get("dedupeKey")
        }
        legacy_keys = db.get("scannedJobKeys", [])
        if isinstance(legacy_keys, list):
            for key in legacy_keys:
                if key and key not in by_key:
                    by_key[key] = {"dedupe_key": key}

        for record in records:
            key = record.get("dedupe_key")
            if key:
                by_key[key] = record

        db["scannedJobs"] = sorted(by_key.values(), key=lambda row: row.get("dedupe_key", ""))
        db["scannedJobKeys"] = sorted(by_key.keys())
        with open(self._path, "w", encoding="utf-8") as handle:
            json.dump(db, handle, indent=2)

    def list_scanned_job_rows(self, *, limit: Optional[int] = None) -> List[Dict]:
        """Return raw scanned job rows for rescan engine."""
        rows = self.read_db().get("scannedJobs", [])
        if not isinstance(rows, list):
            return []
        if limit is not None:
            return rows[: max(1, limit)]
        return rows

    def promote_scanned_job_to_lead(self, dedupe_key: str) -> Dict:
        """Promote a scanned job into Job Leads (JSON store)."""
        from packages.database.python.mappers import scanned_job_row_to_job

        db = self.read_db()
        scanned_jobs = db.get("scannedJobs", [])
        if not isinstance(scanned_jobs, list):
            raise ValueError(f"Scanned job not found: {dedupe_key}")

        row = next(
            (
                entry
                for entry in scanned_jobs
                if (entry.get("dedupe_key") or entry.get("dedupeKey")) == dedupe_key
            ),
            None,
        )
        if not row:
            raise ValueError(f"Scanned job not found: {dedupe_key}")

        job = scanned_job_row_to_job(row)
        jobs = db.get("jobs", [])
        if not isinstance(jobs, list):
            jobs = []
        jobs = [existing for existing in jobs if existing.get("id") != job.get("id")]
        jobs.insert(0, job)
        db["jobs"] = jobs

        for entry in scanned_jobs:
            key = entry.get("dedupe_key") or entry.get("dedupeKey")
            if key == dedupe_key:
                entry["promoted_to_jobs"] = True
                entry["promotion_type"] = "manual"

        db["scannedJobs"] = scanned_jobs
        with open(self._path, "w", encoding="utf-8") as handle:
            json.dump(db, handle, indent=2)
        return job

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
        """Load profile from Supabase without local file skill defaults."""
        return self._repo.get_profile()

    def get_dedupe_indexes(self) -> Tuple[set, set]:
        return self._repo.get_dedupe_indexes()

    def get_scanned_keys(self) -> set:
        return self._repo.get_scanned_keys()

    def record_scanned_jobs(self, records: List[Dict]) -> None:
        count = self._repo.record_scanned_jobs(records)
        if count:
            print(f"[SupabaseJobStore] Recorded {count} scanned job insight(s).")

    def list_scanned_job_rows(self, *, limit: Optional[int] = None) -> List[Dict]:
        return self._repo.list_scanned_job_rows(limit=limit)

    def promote_scanned_job_to_lead(self, dedupe_key: str) -> Dict:
        return self._repo.promote_scanned_job_to_lead(dedupe_key)

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
        raw = os.environ.get("SCANNER_MIN_MATCH_SCORE", str(MATCH_SCORE_THRESHOLD))
        try:
            return int(raw)
        except ValueError:
            return MATCH_SCORE_THRESHOLD

    @staticmethod
    def min_jobs_per_run() -> int:
        """Minimum qualifying jobs to collect before stopping a scan cycle."""
        raw = os.environ.get("SCANNER_MIN_JOBS_PER_RUN", str(SCANNER_MIN_JOBS_PER_RUN))
        try:
            return max(1, int(raw))
        except ValueError:
            return SCANNER_MIN_JOBS_PER_RUN

    @staticmethod
    def max_passes() -> int:
        """Maximum discovery passes (0 = unlimited until sources are exhausted)."""
        raw = os.environ.get("SCANNER_MAX_PASSES", str(SCANNER_MAX_PASSES))
        try:
            return max(0, int(raw))
        except ValueError:
            return SCANNER_MAX_PASSES

    @staticmethod
    def limit_step() -> int:
        """Increase per-source fetch limit by this amount each pass."""
        raw = os.environ.get("SCANNER_LIMIT_STEP", str(SCANNER_LIMIT_STEP))
        try:
            return max(1, int(raw))
        except ValueError:
            return SCANNER_LIMIT_STEP

    @staticmethod
    def max_limit_per_source() -> int:
        """Cap per-source job fetch size during aggressive discovery."""
        raw = os.environ.get("SCANNER_MAX_LIMIT_PER_SOURCE", str(SCANNER_MAX_LIMIT_PER_SOURCE))
        try:
            return max(1, int(raw))
        except ValueError:
            return SCANNER_MAX_LIMIT_PER_SOURCE

    @staticmethod
    def max_evaluations() -> int:
        """Maximum number of unique jobs to score in one run."""
        raw = os.environ.get("SCANNER_MAX_EVALUATIONS", str(SCANNER_MAX_EVALUATIONS))
        try:
            return max(1, int(raw))
        except ValueError:
            return SCANNER_MAX_EVALUATIONS

    @staticmethod
    def scan_insight_batch_size() -> int:
        """Number of scanned job rows to buffer before upserting."""
        raw = os.environ.get(
            "SCANNER_SCAN_INSIGHT_BATCH_SIZE",
            str(SCANNER_SCAN_INSIGHT_BATCH_SIZE),
        )
        try:
            return max(1, int(raw))
        except ValueError:
            return SCANNER_SCAN_INSIGHT_BATCH_SIZE

    @staticmethod
    def _evaluate_scraper_batch(
        scraper: BaseScanner,
        *,
        scan_insights: ScanInsightBuffer,
        profile: Dict,
        threshold: int,
        target_jobs: int,
        limit: int,
        scanned_at_start: set,
        evaluated_keys: set,
        existing_jobs: List[Dict],
        added_jobs: List[Dict],
        stats: Dict[str, int],
        matcher: Optional[AIMatcher] = None,
    ) -> Tuple[int, int]:
        """Score jobs from one scanner batch. Returns (accepted, newly_evaluated)."""
        if not scraper.health_check():
            print(f"[ScannerEngine] Health Check failed for {scraper.name}. Skipping.")
            return 0, 0

        print(f"[ScannerEngine] Invoking: {scraper.name} (fetch up to {limit} jobs)...")
        raw_jobs = scraper.discover_jobs(limit=limit)
        accepted = 0
        newly_evaluated = 0

        for raw_job in raw_jobs:
            if len(added_jobs) >= target_jobs:
                break
            if stats["evaluated"] >= ScannerEngine.max_evaluations():
                print("[ScannerEngine] Evaluation budget reached for this run.")
                break

            canonical = scraper.normalize(raw_job)
            dedupe_key = job_dedupe_key(canonical)

            if dedupe_key in evaluated_keys:
                if dedupe_key in scanned_at_start:
                    stats["skipped_previously_scanned"] += 1
                else:
                    stats["skipped_repeat"] += 1
                continue

            evaluated_keys.add(dedupe_key)
            stats["evaluated"] += 1
            newly_evaluated += 1
            enriched = ScannerEngine._enrich_job_static(
                canonical, profile, matcher, existing_jobs + added_jobs
            )
            score = ScannerEngine._coerce_score({"score": enriched.get("score", 0)})
            promoted = not enriched.get("isDuplicate") and score > threshold
            scan_insights.append(
                scanned_job_record(
                    enriched,
                    score=score,
                    promoted_to_jobs=promoted,
                    scan_run_id_value=scan_run_id(),
                )
            )

            if enriched.get("isDuplicate"):
                stats["skipped_duplicate"] += 1
                print(
                    f"[ScannerEngine] Skipped duplicate: "
                    f"{enriched.get('title')} at {enriched.get('company')}"
                )
                continue

            if score <= threshold:
                stats["ignored_low_score"] += 1
                print(
                    f"[ScannerEngine] Ignored (match {score}% <= {threshold}%): "
                    f"{enriched.get('title')} at {enriched.get('company')}"
                )
                continue

            print(
                f"[ScannerEngine] Accepted (match {score}%): "
                f"{enriched.get('title')} at {enriched.get('company')} "
                f"[{enriched.get('canonicalRole')} / {enriched.get('priority')}]"
            )
            added_jobs.append(enriched)
            accepted += 1

        return accepted, newly_evaluated

    def _apply_match_analysis(self, canonical: Dict, profile: Dict) -> int:
        """Score a job and attach match metadata. Returns numeric match score."""
        enriched = self._enrich_job_static(canonical, profile, self.ai_matcher, [])
        return int(enriched.get("score", 0))

    @staticmethod
    def _enrich_job_static(
        canonical: Dict,
        profile: Dict,
        matcher: Optional[AIMatcher] = None,
        existing_jobs: Optional[List[Dict]] = None,
    ) -> Dict:
        """Enrich a job using the provided matcher (or a fresh one for tests)."""
        ai = matcher or AIMatcher()
        return ai.enrich_job(canonical, profile, existing_jobs=existing_jobs or [])

    @staticmethod
    def _apply_match_analysis_static(
        canonical: Dict, profile: Dict, matcher: Optional[AIMatcher] = None
    ) -> int:
        """Score a job using the provided matcher (or a fresh one for tests)."""
        enriched = ScannerEngine._enrich_job_static(canonical, profile, matcher, [])
        return ScannerEngine._coerce_score({"score": enriched.get("score", 0)})

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

    def run(
        self,
        limit_per_source: int = SCANNER_LIMIT_PER_SOURCE,
        min_match_score: Optional[int] = None,
        min_jobs: Optional[int] = None,
    ) -> List[Dict]:
        """Run pipeline across scanners until target met or all sources exhausted."""
        threshold = self.min_match_score() if min_match_score is None else min_match_score
        target_jobs = self.min_jobs_per_run() if min_jobs is None else max(1, min_jobs)
        max_passes = self.max_passes()
        max_limit = self.max_limit_per_source()
        step = self.limit_step()
        pass_cap = f"{max_passes}" if max_passes > 0 else "unlimited"

        print("=== AI Job Hunter: Starting Automated Scraper Pipeline ===")
        print(
            f"[ScannerEngine] Match policy: score must exceed {threshold}% "
            f"(target {target_jobs} job(s) per scan)."
        )
        print(
            f"[ScannerEngine] Discovery: {pass_cap} pass(es) or until exhausted, "
            f"limit {limit_per_source}→{max_limit} (+{step}/pass), "
            f"max {self.max_evaluations()} evaluations."
        )

        profile = self.store.get_profile()
        scanned_registry = self.store.get_scanned_keys()
        saved_jobs = (
            self.read_db().get("jobs", [])
            if isinstance(self.store, JsonJobStore)
            else self.store._repo.list_jobs()
            if isinstance(self.store, SupabaseJobStore)
            else []
        )
        scanned_at_start = merge_scanned_keys(scanned_registry, saved_jobs)
        evaluated_keys: set = set(scanned_at_start)

        added_jobs: List[Dict] = []
        scan_insights = ScanInsightBuffer(
            self.store,
            batch_size=self.scan_insight_batch_size(),
        )
        stats = {
            "evaluated": 0,
            "ignored_low_score": 0,
            "skipped_repeat": 0,
            "skipped_previously_scanned": 0,
            "skipped_duplicate": 0,
        }

        if scanned_at_start:
            print(
                f"[ScannerEngine] Skipping {len(scanned_at_start)} job(s) "
                "already scanned in prior runs."
            )

        current_limit = min(limit_per_source, max_limit)
        pass_num = 0

        while len(added_jobs) < target_jobs:
            if max_passes > 0 and pass_num >= max_passes:
                print(f"[ScannerEngine] Reached pass safety cap ({max_passes}).")
                break
            if stats["evaluated"] >= self.max_evaluations():
                print("[ScannerEngine] Evaluation budget exhausted; stopping discovery.")
                break

            pass_num += 1
            pass_new_evaluations = 0
            pass_label = f"{pass_num}/{pass_cap}" if max_passes > 0 else str(pass_num)
            print(
                f"[ScannerEngine] --- Discovery pass {pass_label} "
                f"(fetch up to {current_limit} jobs per source) ---"
            )

            for scraper in self.scrapers:
                if len(added_jobs) >= target_jobs:
                    break
                if stats["evaluated"] >= self.max_evaluations():
                    break

                _accepted, batch_newly_evaluated = self._evaluate_scraper_batch(
                    scraper,
                    scan_insights=scan_insights,
                    profile=profile,
                    threshold=threshold,
                    target_jobs=target_jobs,
                    limit=current_limit,
                    scanned_at_start=scanned_at_start,
                    evaluated_keys=evaluated_keys,
                    existing_jobs=saved_jobs + added_jobs,
                    added_jobs=added_jobs,
                    stats=stats,
                    matcher=self.ai_matcher,
                )
                pass_new_evaluations += batch_newly_evaluated

            if len(added_jobs) >= target_jobs:
                print(
                    f"[ScannerEngine] Reached target of {target_jobs} qualifying job(s). "
                    "Stopping scan."
                )
                break

            if stats["evaluated"] >= self.max_evaluations():
                break

            if pass_new_evaluations == 0:
                print(
                    "[ScannerEngine] All sources exhausted — no new jobs to evaluate this pass."
                )
                break

            if current_limit < max_limit:
                current_limit = min(current_limit + step, max_limit)

        scan_insights.flush()

        if added_jobs:
            self.store.persist_new_jobs(added_jobs)
            target = "Supabase" if isinstance(self.store, SupabaseJobStore) else "data.json"
            print(
                f"[ScannerEngine] Sync complete! Registered {len(added_jobs)} job(s) "
                f"with match score above {threshold}% in {target} "
                f"({pass_num} pass(es), {stats['evaluated']} evaluated)."
            )
        else:
            print(
                f"[ScannerEngine] Sync complete! No jobs exceeded the {threshold}% match threshold "
                f"after {pass_num} pass(es) "
                f"(evaluated {stats['evaluated']}, ignored {stats['ignored_low_score']}, "
                f"skipped previously scanned {stats['skipped_previously_scanned']}, "
                f"skipped duplicate {stats['skipped_duplicate']}, "
                f"skipped repeat {stats['skipped_repeat']})."
            )

        if len(added_jobs) < target_jobs:
            print(
                f"[ScannerEngine] Warning: only {len(added_jobs)} qualifying job(s) found "
                f"(target {target_jobs}). Consider broadening sources or profile skills."
            )

        return added_jobs


if __name__ == "__main__":
    ScannerEngine().run()
