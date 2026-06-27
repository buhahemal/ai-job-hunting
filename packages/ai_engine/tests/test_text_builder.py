import unittest

from packages.ai_engine.python.text_builder import (
    build_candidate_text,
    build_job_text,
    extract_matched_skills,
    infer_seniority,
)


class TestTextBuilder(unittest.TestCase):
    PROFILE = {
        'fullName': 'Hemal Buha',
        'targetRoles': ['Senior Platform Engineer'],
        'skills': ['Python', 'Kubernetes', 'AWS'],
        'experience': [
            {
                'role': 'Senior Platform Engineer',
                'company': 'Edmingle',
                'bullets': ['Built CI/CD pipelines with GitHub Actions'],
            }
        ],
        'preferences': {'remotePreference': 'Remote', 'targetCompanies': ['Stripe']},
    }

    JOB = {
        'title': 'Senior Platform Engineer',
        'company': 'Stripe',
        'location': 'Remote',
        'remoteType': 'Remote',
        'description': 'Python, Kubernetes, AWS platform role.',
    }

    def test_build_candidate_text_includes_core_sections(self):
        text = build_candidate_text(self.PROFILE)
        self.assertIn('Hemal Buha', text)
        self.assertIn('Senior Platform Engineer', text)
        self.assertIn('Python', text)
        self.assertIn('Remote preference: Remote', text)

    def test_build_job_text_includes_description(self):
        text = build_job_text(self.JOB)
        self.assertIn('Senior Platform Engineer', text)
        self.assertIn('Stripe', text)
        self.assertIn('Python, Kubernetes, AWS', text)

    def test_extract_matched_skills(self):
        matched = extract_matched_skills(self.JOB, self.PROFILE)
        self.assertEqual(matched, ['Python', 'Kubernetes', 'AWS'])

    def test_infer_seniority(self):
        self.assertEqual(infer_seniority('Senior Backend Engineer'), 'Senior')
        self.assertEqual(infer_seniority('Junior Developer'), 'Junior')


if __name__ == '__main__':
    unittest.main()
