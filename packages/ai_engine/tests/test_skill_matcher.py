"""Tests for accuracy-first skill matching."""

import unittest

from packages.ai_engine.python.skill_matcher import (
    compute_skill_match,
    filter_verified_gaps,
    normalize_skill,
    skill_in_corpus,
    build_candidate_skill_corpus,
)


PROFILE = {
    'fullName': 'Test User',
    'skills': [
        'Node.js',
        'TypeScript',
        'Express.js',
        'Golang',
        'Redis',
        'AWS',
        'Lambda',
        'Kubernetes',
    ],
    'experience': [
        {
            'role': 'Platform Engineer',
            'company': 'Acme',
            'bullets': ['Built APIs with Express.js and Redis caching on AWS Lambda'],
        }
    ],
    'projects': [],
    'preferences': {'skillsKeywords': ['microservices']},
    'masterResumeLaTeX': '',
}


class TestSkillMatcher(unittest.TestCase):
    def test_normalize_skill_aliases(self):
        self.assertEqual(normalize_skill('Golang'), normalize_skill('Go'))
        self.assertEqual(normalize_skill('Express.js'), normalize_skill('Express'))

    def test_profile_skill_never_missing(self):
        job = {
            'title': 'Backend Engineer',
            'description': 'Build scalable APIs with Node.js and Kubernetes on AWS.',
            'company': 'Acme',
        }
        result = compute_skill_match(job, PROFILE)
        for skill in ('Express.js', 'Redis', 'Golang', 'Lambda'):
            self.assertNotIn(skill, result.missing_skills, f'{skill} should not be a gap')

    def test_true_gap_when_job_requires_unknown_skill(self):
        job = {
            'title': 'Rust Systems Engineer',
            'description': 'Must have Rust and systems programming experience.',
            'company': 'Acme',
        }
        result = compute_skill_match(job, PROFILE)
        self.assertTrue(any('rust' in s.lower() for s in result.missing_skills))

    def test_alias_go_matches_golang_in_profile(self):
        job = {
            'title': 'Go Developer',
            'description': 'Strong Go programming required.',
            'company': 'Acme',
        }
        result = compute_skill_match(job, PROFILE)
        self.assertNotIn('Go', result.missing_skills)

    def test_filter_verified_gaps_excludes_profile_skills(self):
        gaps = ['Express.js', 'Rust', 'Redis']
        verified = filter_verified_gaps(gaps, PROFILE)
        self.assertIn('Rust', verified)
        self.assertNotIn('Express.js', verified)
        self.assertNotIn('Redis', verified)

    def test_corpus_includes_experience_bullets(self):
        tokens, text = build_candidate_skill_corpus(PROFILE)
        self.assertTrue(skill_in_corpus('Redis', tokens, text))
        self.assertTrue(skill_in_corpus('Lambda', tokens, text))


if __name__ == '__main__':
    unittest.main()
