"""Unit tests for job enrichment pipeline."""

import unittest
from unittest.mock import patch

from packages.ai_engine.python.job_enricher import (
    classify_canonical_role,
    detect_duplicate,
    enrich_job,
    estimate_priority,
    extract_technologies,
)


PROFILE = {
    "fullName": "Test User",
    "location": "Bangalore, India (Open to Remote / Global)",
    "targetRoles": ["Senior Platform Engineer", "Backend Engineer"],
    "skills": ["Node.js", "TypeScript", "Kubernetes", "Terraform", "AWS"],
    "preferences": {
        "remotePreference": "Remote",
        "targetCompanies": ["Google"],
        "locations": ["Bangalore"],
        "skillsKeywords": ["microservices", "platform"],
    },
}


class TestJobEnricher(unittest.TestCase):
    def test_classify_canonical_role(self):
        role = classify_canonical_role("Senior DevOps Engineer", "CI/CD pipelines and Kubernetes")
        self.assertEqual(role, "DevOps Engineer")

    def test_extract_technologies(self):
        tech = extract_technologies(
            {
                "title": "Backend Engineer",
                "description": "Node.js, TypeScript, AWS, Kubernetes required",
            }
        )
        self.assertIn("Node.js", tech)
        self.assertIn("Kubernetes", tech)

    def test_detect_duplicate_by_url(self):
        job = {"id": "new", "url": "https://example.com/job-1", "title": "Engineer", "company": "Acme"}
        existing = [{"id": "old", "url": "https://example.com/job-1", "title": "Engineer", "company": "Acme"}]
        is_dup, duplicate_of = detect_duplicate(job, existing)
        self.assertTrue(is_dup)
        self.assertEqual(duplicate_of, "old")

    def test_estimate_priority(self):
        self.assertEqual(estimate_priority(88, 90, False), "High")
        self.assertEqual(estimate_priority(50, 40, True), "Low")

    @patch("packages.ai_engine.python.job_enricher.matcher.score_job")
    def test_enrich_job_returns_match_insights(self, mock_score):
        mock_score.return_value = {
            "score": 82,
            "extractedSkills": ["Node.js", "Kubernetes"],
            "fitExplanation": "Strong platform fit",
            "salaryEstimate": "Not Specified",
            "seniority": "Senior",
            "remoteType": "Remote",
            "scorer": "heuristic",
        }
        job = {
            "id": "gh-1",
            "title": "Senior Platform Engineer",
            "company": "Acme",
            "location": "Remote",
            "remoteType": "Remote",
            "source": "Greenhouse",
            "url": "https://example.com/jobs/1",
            "description": "Node.js Kubernetes Terraform platform engineering role",
        }

        enriched = enrich_job(job, PROFILE)

        self.assertEqual(enriched["canonicalRole"], "Platform Engineer")
        self.assertIn("matchInsights", enriched)
        self.assertEqual(enriched["matchInsights"]["overallScore"], enriched["score"])
        self.assertTrue(enriched["matchInsights"]["matchedSkills"])
        self.assertIsInstance(enriched["matchInsights"]["missingSkills"], list)


if __name__ == "__main__":
    unittest.main()
