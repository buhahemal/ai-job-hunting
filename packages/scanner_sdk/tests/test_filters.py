import unittest

from packages.scanner_sdk.python.filters import evaluate_job_preferences


class TestJobPreferenceFilters(unittest.TestCase):
    def test_blacklisted_company_is_rejected_case_insensitively(self):
        decision = evaluate_job_preferences(
            {'company': 'Crossover Inc', 'title': 'Engineer', 'location': 'Remote'},
            {'preferences': {'companyBlacklist': ['crossover']}},
            [],
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, 'company_blacklist')

    def test_apply_once_rejects_company_already_in_jobs(self):
        decision = evaluate_job_preferences(
            {'company': 'Acme', 'title': 'Engineer', 'location': 'Remote'},
            {'preferences': {'applyOncePerCompany': True}},
            [{'company': 'Acme', 'title': 'Other Role'}],
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, 'already_seen_company')

    def test_remote_clearance_role_is_rejected(self):
        decision = evaluate_job_preferences(
            {
                'company': 'Defense Co',
                'title': 'Engineer',
                'location': 'Remote',
                'description': 'US citizenship and security clearance required',
            },
            {'preferences': {'remotePreference': 'Remote'}},
            [],
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, 'remote_restriction')

    def test_unselected_experience_level_is_rejected_after_enrichment(self):
        decision = evaluate_job_preferences(
            {'company': 'Acme', 'title': 'Engineer', 'location': 'Remote', 'seniority': 'Junior'},
            {'preferences': {'experienceLevels': ['Senior', 'Lead']}},
            [],
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, 'experience_level')


if __name__ == '__main__':
    unittest.main()
