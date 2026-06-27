"""Unit tests for deterministic salary extraction."""

import unittest

from packages.ai_engine.python.salary_extractor import NOT_SPECIFIED, extract_salary


class TestSalaryExtractor(unittest.TestCase):
    def test_extracts_usd_range_with_label(self):
        job = {
            'description': 'Salary: $120k – $180k per year plus equity.',
        }
        self.assertEqual(extract_salary(job), '$120k – $180k per year')

    def test_extracts_dollar_range(self):
        job = {'description': 'We offer $90,000 - $110,000 annually.'}
        result = extract_salary(job)
        self.assertIn('$90,000', result)

    def test_extracts_lpa(self):
        job = {'description': 'Compensation up to 35 LPA for the right candidate.'}
        self.assertIn('LPA', extract_salary(job))

    def test_extracts_euro_amount(self):
        job = {'description': 'Package: €80,000 per annum.'}
        result = extract_salary(job)
        self.assertIn('€80,000', result)

    def test_returns_not_specified_when_missing(self):
        job = {'description': 'Great team, flexible hours, no pay details.'}
        self.assertEqual(extract_salary(job), NOT_SPECIFIED)

    def test_prefers_existing_valid_salary_field(self):
        job = {
            'salaryEstimate': 'USD 150k - 180k',
            'description': 'No numbers here.',
        }
        self.assertIn('150k', extract_salary(job))


if __name__ == '__main__':
    unittest.main()
