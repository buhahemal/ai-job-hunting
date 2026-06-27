"""Unit tests for LaTeX PDF compilation."""

import shutil
import tempfile
import unittest

from packages.resume_engine.python.generator import render_master_latex
from packages.resume_engine.python.pdf import (
    LatexCompileError,
    compile_latex_to_pdf,
    pdflatex_available,
)


@unittest.skipUnless(pdflatex_available(), 'pdflatex not installed')
class TestPdfCompile(unittest.TestCase):
    def test_compile_master_latex_to_pdf(self):
        latex = render_master_latex()
        with tempfile.TemporaryDirectory() as tmp:
            pdf_path = compile_latex_to_pdf(latex, work_dir=tmp)
            self.assertTrue(pdf_path.is_file())
            self.assertGreater(pdf_path.stat().st_size, 1000)

    def test_compile_invalid_latex_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(LatexCompileError):
                compile_latex_to_pdf(r'\documentclass{article}\begin{document}\broken', work_dir=tmp)


class TestPdfAvailability(unittest.TestCase):
    def test_pdflatex_availability_matches_path(self):
        self.assertEqual(pdflatex_available(), shutil.which('pdflatex') is not None)


if __name__ == '__main__':
    unittest.main()
