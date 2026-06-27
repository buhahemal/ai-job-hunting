"""Unit tests for scanner deduplication helpers."""

import unittest

from packages.scanner_sdk.python.dedupe import job_dedupe_key, merge_scanned_keys, scanned_job_record


class TestScannerDedupe(unittest.TestCase):
    def test_job_dedupe_key_prefers_url(self):
        key = job_dedupe_key(
            {"url": "https://example.com/jobs/1", "title": "Dev", "company": "Acme"}
        )
        self.assertEqual(key, "https://example.com/jobs/1")

    def test_job_dedupe_key_falls_back_to_title_company(self):
        key = job_dedupe_key({"title": "Dev", "company": "Acme"})
        self.assertEqual(key, "dev-acme")

    def test_merge_scanned_keys_includes_saved_jobs(self):
        merged = merge_scanned_keys(
            {"https://example.com/old"},
            [{"url": "https://example.com/saved", "title": "Dev", "company": "A"}],
        )
        self.assertIn("https://example.com/old", merged)
        self.assertIn("https://example.com/saved", merged)

    def test_scanned_job_record(self):
        record = scanned_job_record(
            {
                "id": "gh-1",
                "source": "Greenhouse",
                "url": "https://example.com/1",
                "title": "Platform Engineer",
                "company": "Acme",
                "location": "Remote",
                "remoteType": "Remote",
                "canonicalRole": "Platform Engineer",
                "primaryStack": "Kubernetes",
                "seniority": "Senior",
                "employmentType": "Full-time",
                "applicationUrl": "https://example.com/1",
                "requiredSkills": ["Kubernetes"],
                "preferredSkills": ["Terraform"],
                "extractedTechnologies": ["Kubernetes", "AWS"],
                "matchInsights": {
                    "overallScore": 42,
                    "skillMatchScore": 40,
                    "experienceMatchScore": 55,
                    "atsScore": 35,
                    "matchedSkills": ["Python"],
                    "missingSkills": ["Kubernetes"],
                    "missingKeywords": ["SRE"],
                    "matchExplanation": "Weak fit",
                    "scorer": "test",
                },
            },
            score=42,
            promoted_to_jobs=False,
        )
        self.assertEqual(record["dedupe_key"], "https://example.com/1")
        self.assertEqual(record["job_id"], "gh-1")
        self.assertEqual(record["score"], 42)
        self.assertEqual(record["overall_score"], 42)
        self.assertEqual(record["title"], "Platform Engineer")
        self.assertEqual(record["missing_skills"], ["Kubernetes"])
        self.assertFalse(record["promoted_to_jobs"])


if __name__ == "__main__":
    unittest.main()
