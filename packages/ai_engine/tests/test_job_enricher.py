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
            "description": "Node.js Kubernetes Terraform AWS platform engineering role",
        }

        enriched = enrich_job(job, PROFILE)

        self.assertEqual(enriched["canonicalRole"], "Platform Engineer")
        self.assertIn("matchInsights", enriched)
        self.assertEqual(enriched["matchInsights"]["overallScore"], enriched["score"])
        self.assertTrue(enriched["matchInsights"]["matchedSkills"])
        for skill in ("Node.js", "Kubernetes", "Terraform", "AWS"):
            self.assertNotIn(skill, enriched["matchInsights"]["missingSkills"], skill)
        self.assertGreaterEqual(enriched["matchInsights"]["overallScore"], 75)

    @patch("packages.ai_engine.python.job_enricher.matcher.score_job")
    def test_overall_score_reduced_for_true_gap(self, mock_score):
        mock_score.return_value = {
            "score": 70,
            "extractedSkills": ["Rust"],
            "fitExplanation": "Systems role",
            "salaryEstimate": "Not Specified",
            "seniority": "Senior",
            "remoteType": "Remote",
            "scorer": "heuristic",
        }
        job = {
            "id": "rust-1",
            "title": "Rust Systems Engineer",
            "company": "Acme",
            "location": "Remote",
            "remoteType": "Remote",
            "source": "Greenhouse",
            "url": "https://example.com/jobs/rust",
            "description": "Must have Rust and systems programming experience.",
        }

        enriched = enrich_job(job, PROFILE)
        missing = enriched["matchInsights"]["missingSkills"]
        self.assertTrue(any("rust" in skill.lower() for skill in missing))
        self.assertLess(enriched["matchInsights"]["overallScore"], 75)

    @patch("packages.ai_engine.python.job_enricher.matcher.score_job")
    def test_corpus_skill_absent_from_job_text_not_penalized(self, mock_score):
        mock_score.return_value = {
            "score": 80,
            "extractedSkills": ["Node.js", "Kubernetes"],
            "fitExplanation": "Backend fit",
            "salaryEstimate": "Not Specified",
            "seniority": "Senior",
            "remoteType": "Remote",
            "scorer": "heuristic",
        }
        profile = {
            **PROFILE,
            "skills": ["Node.js", "TypeScript", "Express.js", "Redis", "Kubernetes", "AWS"],
        }
        job = {
            "id": "node-1",
            "title": "Backend Engineer",
            "company": "Acme",
            "location": "Remote",
            "remoteType": "Remote",
            "source": "Greenhouse",
            "url": "https://example.com/jobs/node",
            "description": "Node.js and Kubernetes on AWS. No mention of Express or Redis in posting.",
        }

        enriched = enrich_job(job, profile)
        for skill in ("Express.js", "Redis"):
            self.assertNotIn(skill, enriched["matchInsights"]["missingSkills"], skill)


if __name__ == "__main__":
    unittest.main()
