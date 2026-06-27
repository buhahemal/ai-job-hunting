"""Compile LaTeX resume sources to PDF via pdflatex."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Union


class LatexCompileError(RuntimeError):
    """Raised when pdflatex fails to produce a PDF."""


def pdflatex_available() -> bool:
    """Return True when pdflatex is on PATH."""
    return shutil.which('pdflatex') is not None


def compile_latex_to_pdf(
    latex: str,
    *,
    work_dir: Union[str, Path],
    stem: str = 'resume',
) -> Path:
    """
    Write LaTeX to disk and compile to PDF using pdflatex.

    Args:
        latex: Full LaTeX document source.
        work_dir: Directory for .tex aux log and PDF output.
        stem: Basename for the TeX file (default ``resume`` → ``resume.pdf``).

    Returns:
        Path to the generated PDF file.

    Raises:
        LatexCompileError: When pdflatex is missing or compilation fails.
    """
    if not pdflatex_available():
        raise LatexCompileError('pdflatex is not installed or not on PATH')

    directory = Path(work_dir)
    directory.mkdir(parents=True, exist_ok=True)
    tex_path = directory / f'{stem}.tex'
    tex_path.write_text(latex, encoding='utf-8')

    command = [
        'pdflatex',
        '-interaction=nonstopmode',
        '-halt-on-error',
        f'-output-directory={directory}',
        str(tex_path),
    ]

    for _ in range(2):
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            log_tail = (completed.stdout or '')[-2000:] + (completed.stderr or '')[-2000:]
            raise LatexCompileError(f'pdflatex failed:\n{log_tail}')

    pdf_path = directory / f'{stem}.pdf'
    if not pdf_path.is_file():
        raise LatexCompileError(f'pdflatex did not produce {pdf_path}')

    return pdf_path
