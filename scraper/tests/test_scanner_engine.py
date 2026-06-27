import os
import unittest
from typing import Dict, List
from unittest.mock import patch

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
        self.store = JsonJobStore()
        self.profile = {
            "skills": ["Python", "Kubernetes", "Terraform"],
            "preferences": {"remotePreference": "Remote", "targetCompanies": []},
        }

    def _engine(self, scanners: List[FakeScanner]) -> ScannerEngine:
        engine = ScannerEngine(store=self.store)
        engine.scrapers = scanners
        return engine

    @patch.object(JsonJobStore, "get_profile")
    @patch.object(JsonJobStore, "get_dedupe_indexes", return_value=(set(), set()))
    @patch.object(JsonJobStore, "persist_new_jobs")
    def test_ignores_jobs_at_or_below_threshold(self, mock_persist, _mock_dedupe, mock_profile):
        mock_profile.return_value = self.profile
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

        engine.ai_matcher.score_job = fake_score  # type: ignore[method-assign]

        added = engine.run(min_match_score=75, min_jobs=1, limit_per_source=5)

        self.assertEqual(len(added), 1)
        self.assertEqual(added[0]["id"], "high-1")
        self.assertGreater(added[0]["score"], 75)
        mock_persist.assert_called_once()

    @patch.object(JsonJobStore, "get_profile")
    @patch.object(JsonJobStore, "get_dedupe_indexes", return_value=(set(), set()))
    @patch.object(JsonJobStore, "persist_new_jobs")
    def test_scans_next_portal_until_minimum_met(self, mock_persist, _mock_dedupe, mock_profile):
        mock_profile.return_value = self.profile
        scanners = [
            FakeScanner(
                "SourceA",
                [
                    {
                        "id": "a-low",
                        "title": "Role A",
                        "company": "A",
                        "url": "https://example.com/a-low",
                    }
                ],
            ),
            FakeScanner(
                "SourceB",
                [
                    {
                        "id": "b-1",
                        "title": "Role B1",
                        "company": "B",
                        "url": "https://example.com/b-1",
                    },
                    {
                        "id": "b-2",
                        "title": "Role B2",
                        "company": "B",
                        "url": "https://example.com/b-2",
                    },
                    {
                        "id": "b-3",
                        "title": "Role B3",
                        "company": "B",
                        "url": "https://example.com/b-3",
                    },
                ],
            ),
            FakeScanner(
                "SourceC",
                [
                    {
                        "id": "c-1",
                        "title": "Role C1",
                        "company": "C",
                        "url": "https://example.com/c-1",
                    }
                ],
            ),
        ]
        engine = self._engine(scanners)

        def fake_score(job, profile):
            score = 90 if job["id"].startswith("b-") else 60
            return {"score": score, "extractedSkills": [], "seniority": "Senior", "fitExplanation": "test"}

        engine.ai_matcher.score_job = fake_score  # type: ignore[method-assign]

        added = engine.run(min_match_score=75, min_jobs=3, limit_per_source=5)

        self.assertEqual(len(added), 3)
        self.assertTrue(all(job["score"] > 75 for job in added))
        mock_persist.assert_called_once()

    @patch.object(JsonJobStore, "get_profile")
    @patch.object(JsonJobStore, "get_dedupe_indexes", return_value=(set(), set()))
    @patch.object(JsonJobStore, "persist_new_jobs")
    def test_persists_nothing_when_all_scores_too_low(self, mock_persist, _mock_dedupe, mock_profile):
        mock_profile.return_value = self.profile
        scanners = [
            FakeScanner(
                "SourceA",
                [
                    {
                        "id": "low-1",
                        "title": "Role",
                        "company": "A",
                        "url": "https://example.com/low-1",
                    }
                ],
            )
        ]
        engine = self._engine(scanners)
        engine.ai_matcher.score_job = lambda job, profile: {  # type: ignore[method-assign]
            "score": 50,
            "extractedSkills": [],
            "seniority": "Mid-level",
            "fitExplanation": "weak fit",
        }

        added = engine.run(min_match_score=75, min_jobs=3, limit_per_source=5)

        self.assertEqual(added, [])
        mock_persist.assert_not_called()

    @patch.object(JsonJobStore, "get_profile")
    @patch.object(JsonJobStore, "get_dedupe_indexes", return_value=(set(), set()))
    @patch.object(JsonJobStore, "persist_new_jobs")
    def test_multi_pass_increases_fetch_limit_until_target_met(
        self, mock_persist, _mock_dedupe, mock_profile
    ):
        mock_profile.return_value = self.profile
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
        scanners = [FakeScanner("SourceA", jobs)]
        engine = self._engine(scanners)

        def fake_score(job, profile):
            score = 90 if job["id"].startswith("high-") else 50
            return {
                "score": score,
                "extractedSkills": [],
                "seniority": "Senior",
                "fitExplanation": "test",
            }

        engine.ai_matcher.score_job = fake_score  # type: ignore[method-assign]

        added = engine.run(min_match_score=75, min_jobs=3, limit_per_source=2)

        self.assertEqual(len(added), 3)
        self.assertTrue(all(job["score"] > 75 for job in added))
        mock_persist.assert_called_once()


if __name__ == "__main__":
    unittest.main()
