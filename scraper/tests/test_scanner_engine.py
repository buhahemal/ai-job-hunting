import json
import os
import tempfile
import unittest
from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from scraper.scanner_engine import JsonJobStore, ScannerEngine


class FakeScanner(BaseScanner):
    """Test scanner returning predetermined raw jobs."""

    def __init__(self, name: str, jobs: List[Dict]):
        self._name = name
        self._jobs = jobs

    @property
    def name(self) -> str:
        return self._name

    def discover_jobs(self, limit: int = 10) -> List[Dict]:
        return self._jobs[:limit]

    def normalize(self, raw_job: Dict) -> Dict:
        return {
            "id": raw_job["id"],
            "title": raw_job["title"],
            "company": raw_job["company"],
            "location": raw_job.get("location", "Remote"),
            "remoteType": raw_job.get("remoteType", "Remote"),
            "source": self.name,
            "url": raw_job["url"],
            "description": raw_job.get("description", ""),
            "status": "New",
        }

    def health_check(self) -> bool:
        return True


class TestScannerEngineMatchPolicy(unittest.TestCase):
    def setUp(self):
        os.environ["USE_JSON_STORE"] = "true"
        self.profile = {
            "skills": ["Python", "Kubernetes", "Terraform"],
            "preferences": {"remotePreference": "Remote", "targetCompanies": []},
        }
        self._temp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        self._temp_path = self._temp.name
        json.dump(
            {"profile": self.profile, "jobs": [], "interviews": [], "scannedJobKeys": []},
            self._temp,
        )
        self._temp.close()
        self.store = JsonJobStore(path=self._temp_path)

    def tearDown(self):
        if os.path.exists(self._temp_path):
            os.remove(self._temp_path)

    def _engine(self, scanners: List[FakeScanner]) -> ScannerEngine:
        engine = ScannerEngine(store=self.store)
        engine.scrapers = scanners
        return engine

    def _bind_enrich(self, engine: ScannerEngine, scorer_fn):
        def enrich(job, profile, existing_jobs=None):
            analysis = scorer_fn(job, profile)
            score = int(analysis.get("score", 0))
            return {
                **job,
                "score": score,
                "isDuplicate": False,
                "canonicalRole": "Platform Engineer" if score > 75 else "Software Engineer",
                "priority": "High" if score > 85 else "Medium" if score > 70 else "Low",
                "fitExplanation": analysis.get("fitExplanation", ""),
                "extractedSkills": analysis.get("extractedSkills", []),
                "matchInsights": {
                    "overallScore": score,
                    "skillMatchScore": score,
                    "experienceMatchScore": score,
                    "atsScore": score,
                    "salaryMatchScore": 50,
                    "companyMatchScore": 50,
                    "locationMatchScore": 50,
                    "remoteMatchScore": 50,
                    "confidenceScore": 70,
                    "matchedSkills": analysis.get("extractedSkills", []),
                    "missingSkills": [],
                    "missingKeywords": [],
                    "resumeSuggestions": [],
                    "matchExplanation": analysis.get("fitExplanation", ""),
                    "scorer": "test",
                },
            }

        engine.ai_matcher.enrich_job = enrich  # type: ignore[method-assign]

    def test_ignores_jobs_at_or_below_threshold(self):
        scanners = [
            FakeScanner(
                "SourceA",
                [
                    {
                        "id": "low-1",
                        "title": "Junior Engineer",
                        "company": "Acme",
                        "url": "https://example.com/low-1",
                    },
                    {
                        "id": "high-1",
                        "title": "Senior Platform Engineer",
                        "company": "Acme",
                        "url": "https://example.com/high-1",
                    },
                ],
            )
        ]
        engine = self._engine(scanners)

        def fake_score(job, profile):
            score = 70 if job["id"] == "low-1" else 88
            return {"score": score, "extractedSkills": [], "seniority": "Senior", "fitExplanation": "test"}

        self._bind_enrich(engine, fake_score)
        added = engine.run(min_match_score=75, min_jobs=1, limit_per_source=5)

        self.assertEqual(len(added), 1)
        self.assertEqual(added[0]["id"], "high-1")
        self.assertGreater(added[0]["score"], 75)
        self.assertIn("https://example.com/low-1", self.store.get_scanned_keys())
        self.assertIn("https://example.com/high-1", self.store.get_scanned_keys())

    def test_scans_next_portal_until_minimum_met(self):
        scanners = [
            FakeScanner(
                "SourceA",
                [{"id": "a-low", "title": "Role A", "company": "A", "url": "https://example.com/a-low"}],
            ),
            FakeScanner(
                "SourceB",
                [
                    {"id": "b-1", "title": "Role B1", "company": "B", "url": "https://example.com/b-1"},
                    {"id": "b-2", "title": "Role B2", "company": "B", "url": "https://example.com/b-2"},
                    {"id": "b-3", "title": "Role B3", "company": "B", "url": "https://example.com/b-3"},
                ],
            ),
            FakeScanner(
                "SourceC",
                [{"id": "c-1", "title": "Role C1", "company": "C", "url": "https://example.com/c-1"}],
            ),
        ]
        engine = self._engine(scanners)

        def fake_score(job, profile):
            score = 90 if job["id"].startswith("b-") else 60
            return {"score": score, "extractedSkills": [], "seniority": "Senior", "fitExplanation": "test"}

        self._bind_enrich(engine, fake_score)
        added = engine.run(min_match_score=75, min_jobs=3, limit_per_source=5)

        self.assertEqual(len(added), 3)
        self.assertTrue(all(job["score"] > 75 for job in added))

    def test_persists_nothing_when_all_scores_too_low(self):
        scanners = [
            FakeScanner(
                "SourceA",
                [{"id": "low-1", "title": "Role", "company": "A", "url": "https://example.com/low-1"}],
            )
        ]
        engine = self._engine(scanners)
        self._bind_enrich(
            engine,
            lambda job, profile: {
                "score": 50,
                "extractedSkills": [],
                "seniority": "Mid-level",
                "fitExplanation": "weak fit",
            },
        )

        added = engine.run(min_match_score=75, min_jobs=3, limit_per_source=5)

        self.assertEqual(added, [])
        db = self.store.read_db()
        self.assertEqual(db.get("jobs", []), [])
        scanned_jobs = db.get("scannedJobs", [])
        self.assertEqual(len(scanned_jobs), 1)
        self.assertEqual(scanned_jobs[0]["dedupe_key"], "https://example.com/low-1")
        self.assertEqual(scanned_jobs[0]["overall_score"], 50)
        self.assertEqual(scanned_jobs[0]["title"], "Role")
        self.assertFalse(scanned_jobs[0]["promoted_to_jobs"])

    def test_persists_scan_insights_in_batches_of_ten(self):
        """Scan insights flush every 10 rows, with a final flush for the remainder."""
        write_counts: List[int] = []
        original_record = self.store.record_scanned_jobs

        def tracking_record(records):
            write_counts.append(len(records))
            return original_record(records)

        self.store.record_scanned_jobs = tracking_record  # type: ignore[method-assign]

        jobs = [
            {
                "id": f"job-{index}",
                "title": f"Role {index}",
                "company": "Acme",
                "url": f"https://example.com/job-{index}",
            }
            for index in range(13)
        ]
        engine = self._engine([FakeScanner("SourceA", jobs)])
        self._bind_enrich(
            engine,
            lambda job, profile: {
                "score": 50,
                "extractedSkills": [],
                "seniority": "Mid-level",
                "fitExplanation": "weak fit",
            },
        )

        engine.run(min_match_score=75, min_jobs=3, limit_per_source=20)

        self.assertEqual(write_counts, [10, 3])
        self.assertEqual(len(self.store.get_scanned_keys()), 13)

    def test_multi_pass_increases_fetch_limit_until_target_met(self):
        jobs = [
            {
                "id": f"low-{index}",
                "title": f"Junior Role {index}",
                "company": "Acme",
                "url": f"https://example.com/low-{index}",
            }
            for index in range(3)
        ] + [
            {
                "id": f"high-{index}",
                "title": f"Senior Platform Engineer {index}",
                "company": "Acme",
                "url": f"https://example.com/high-{index}",
            }
            for index in range(3)
        ]
        engine = self._engine([FakeScanner("SourceA", jobs)])

        def fake_score(job, profile):
            score = 90 if job["id"].startswith("high-") else 50
            return {"score": score, "extractedSkills": [], "seniority": "Senior", "fitExplanation": "test"}

        self._bind_enrich(engine, fake_score)
        added = engine.run(min_match_score=75, min_jobs=3, limit_per_source=2)

        self.assertEqual(len(added), 3)
        self.assertTrue(all(job["score"] > 75 for job in added))

    def test_evaluates_all_source_jobs_before_stopping(self):
        os.environ["SCANNER_MAX_PASSES"] = "0"
        os.environ["SCANNER_MAX_LIMIT_PER_SOURCE"] = "10"
        os.environ["SCANNER_LIMIT_STEP"] = "5"
        os.environ["SCANNER_MAX_EVALUATIONS"] = "100"
        jobs = [
            {
                "id": f"job-{index}",
                "title": f"Role {index}",
                "company": "Acme",
                "url": f"https://example.com/job-{index}",
            }
            for index in range(10)
        ]
        engine = self._engine([FakeScanner("SourceA", jobs)])
        evaluated_ids: List[str] = []

        def fake_score(job, profile):
            evaluated_ids.append(job["id"])
            return {
                "score": 50,
                "extractedSkills": [],
                "seniority": "Mid-level",
                "fitExplanation": "weak fit",
            }

        self._bind_enrich(engine, fake_score)
        added = engine.run(min_match_score=75, min_jobs=3, limit_per_source=3)

        self.assertEqual(added, [])
        self.assertEqual(len(evaluated_ids), 10)

    def test_second_run_skips_previously_scanned_jobs(self):
        jobs = [
            {
                "id": "seen-1",
                "title": "Backend Engineer",
                "company": "Acme",
                "url": "https://example.com/seen-1",
            },
            {
                "id": "new-1",
                "title": "Platform Engineer",
                "company": "Beta",
                "url": "https://example.com/new-1",
            },
        ]
        scanners = [FakeScanner("SourceA", jobs)]

        def fake_score(job, profile):
            return {
                "score": 50,
                "extractedSkills": [],
                "seniority": "Mid-level",
                "fitExplanation": "weak fit",
            }

        db = self.store.read_db()
        db["scannedJobKeys"] = ["https://example.com/seen-1"]
        with open(self._temp_path, "w", encoding="utf-8") as handle:
            json.dump(db, handle)

        enrich_calls: List[str] = []

        def tracking_score(job, profile):
            enrich_calls.append(job["id"])
            return fake_score(job, profile)

        engine = self._engine(scanners)
        self._bind_enrich(engine, tracking_score)
        engine.run(min_match_score=75, min_jobs=3, limit_per_source=5)

        self.assertEqual(enrich_calls, ["new-1"])
        self.assertIn("https://example.com/seen-1", self.store.get_scanned_keys())
        self.assertIn("https://example.com/new-1", self.store.get_scanned_keys())

    def test_follow_up_scan_after_full_run_skips_every_known_job(self):
        jobs = [
            {
                "id": "seen-1",
                "title": "Backend Engineer",
                "company": "Acme",
                "url": "https://example.com/seen-1",
            },
            {
                "id": "new-1",
                "title": "Platform Engineer",
                "company": "Beta",
                "url": "https://example.com/new-1",
            },
        ]
        scanners = [FakeScanner("SourceA", jobs)]

        def fake_score(job, profile):
            return {
                "score": 50,
                "extractedSkills": [],
                "seniority": "Mid-level",
                "fitExplanation": "weak fit",
            }

        first_engine = self._engine(scanners)
        self._bind_enrich(first_engine, fake_score)
        first_engine.run(min_match_score=75, min_jobs=3, limit_per_source=5)

        enrich_calls: List[str] = []

        def tracking_score(job, profile):
            enrich_calls.append(job["id"])
            return fake_score(job, profile)

        second_engine = self._engine(scanners)
        self._bind_enrich(second_engine, tracking_score)
        second_engine.run(min_match_score=75, min_jobs=3, limit_per_source=5)

        self.assertEqual(enrich_calls, [])


if __name__ == "__main__":
    unittest.main()
