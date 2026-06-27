"""Unit tests for resume engine."""

import json
import tempfile
import unittest
from pathlib import Path

from packages.resume_engine.python.ats import estimate_ats_score
from packages.resume_engine.python.generator import generate_tailored_resume, render_master_latex
from packages.resume_engine.python.latex import escape_latex
from packages.resume_engine.python.master import load_master_resume
from packages.resume_engine.python.tailor import tailor_resume_json


class TestLatexEscape(unittest.TestCase):
    def test_escapes_special_chars(self):
        self.assertEqual(escape_latex('100% & AWS'), r'100\% \& AWS')


class TestResumeEngine(unittest.TestCase):
    def test_master_load_returns_copy(self):
        master_a = load_master_resume()
        master_b = load_master_resume()
        master_a['fullName'] = 'Changed'
        self.assertNotEqual(master_a['fullName'], master_b['fullName'])

    def test_tailor_does_not_mutate_master(self):
        master = load_master_resume()
        original_name = master['fullName']
        job = {
            'title': 'Senior Platform Engineer',
            'company': 'Stripe',
            'description': 'Kubernetes AWS Node.js microservices Terraform',
            'extractedSkills': ['Kubernetes', 'AWS', 'Node.js'],
        }
        tailored = tailor_resume_json(master, job)
        self.assertEqual(master['fullName'], original_name)
        self.assertEqual(tailored['targetRole'], 'Senior Platform Engineer')
        original_index = master['skills'].index('Kubernetes')
        new_index = tailored['skills'].index('Kubernetes')
        self.assertLess(new_index, original_index)

    def test_render_master_latex_contains_document(self):
        latex = render_master_latex()
        self.assertIn('\\documentclass', latex)
        self.assertIn('Hemal Buha', latex)

    def test_generate_tailored_resume_pipeline(self):
        job = {
            'title': 'Backend Engineer',
            'company': 'Acme',
            'description': 'Node.js AWS Redis microservices REST APIs',
            'extractedSkills': ['Node.js', 'AWS', 'Redis'],
        }
        result = generate_tailored_resume(job)
        self.assertIn('\\documentclass', result.latex)
        self.assertIn('Backend Engineer', result.resume_json.get('targetRole', ''))
        self.assertIn('Acme', result.cover_letter)
        self.assertGreaterEqual(result.ats_score, 35)
        self.assertLessEqual(result.ats_score, 100)

    def test_custom_master_and_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            master_path = Path(tmp) / 'master.json'
            template_path = Path(tmp) / 'template.tex'
            master_path.write_text(
                json.dumps(
                    {
                        'fullName': 'Test User',
                        'email': 'test@example.com',
                        'phone': '000',
                        'github': 'https://github.com/test',
                        'linkedin': 'https://linkedin.com/in/test',
                        'location': 'Remote',
                        'summary': 'Engineer',
                        'education': [],
                        'experience': [],
                        'projects': [],
                        'skillGroups': [{'label': 'Core', 'items': ['Python']}],
                    }
                ),
                encoding='utf-8',
            )
            template_path.write_text(
                '\\documentclass{article}\\begin{document}{{ fullName | latex }}\\end{document}',
                encoding='utf-8',
            )
            latex = render_master_latex(master_path=master_path, template_path=template_path)
            self.assertIn('Test User', latex)


class TestAtsScore(unittest.TestCase):
    def test_higher_overlap_yields_higher_score(self):
        resume = {'skills': ['AWS', 'Kubernetes', 'Node.js'], 'skillGroups': [], 'experience': []}
        weak_job = {'description': 'sales marketing'}
        strong_job = {'description': 'AWS Kubernetes Node.js backend platform engineer'}
        self.assertGreater(
            estimate_ats_score(resume, strong_job),
            estimate_ats_score(resume, weak_job),
        )


if __name__ == '__main__':
    unittest.main()
