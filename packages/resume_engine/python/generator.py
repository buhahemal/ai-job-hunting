"""Orchestrate master JSON → tailored JSON → LaTeX → optional artifacts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from packages.config.python.paths import MASTER_RESUME_JSON, RESUME_GENERATED_DIR, RESUME_TEMPLATE_TEX
from packages.resume_engine.python.ats import estimate_ats_score
from packages.resume_engine.python.cover_letter import generate_cover_letter
from packages.resume_engine.python.master import load_master_resume, load_master_resume_from_profile
from packages.resume_engine.python.renderer import render_resume_latex
from packages.resume_engine.python.tailor import tailor_resume_json


@dataclass(frozen=True)
class TailoredResumeResult:
    """Output of the resume generation pipeline."""

    resume_json: Dict[str, Any]
    latex: str
    cover_letter: str
    ats_score: int


def render_master_latex(
    *,
    profile: Dict[str, Any] | None = None,
    master_path: str | Path | None = None,
    template_path: str | Path | None = None,
) -> str:
    """Render the unmodified master resume JSON to LaTeX."""
    if profile:
        master = load_master_resume_from_profile(profile)
    else:
        master = load_master_resume(master_path)
    return render_resume_latex(master, template_path=template_path or RESUME_TEMPLATE_TEX)


def generate_tailored_resume(
    job: Dict[str, Any],
    *,
    profile: Dict[str, Any] | None = None,
    master_path: str | Path | None = None,
    template_path: str | Path | None = None,
) -> TailoredResumeResult:
    """
    Generate a tailored resume for a job without modifying master.json.

    Pipeline:
        master JSON → tailor copy → render LaTeX → cover letter + ATS score
    """
    if profile:
        master = load_master_resume_from_profile(profile)
    else:
        master = load_master_resume(master_path)
    tailored = tailor_resume_json(master, job)
    latex = render_resume_latex(tailored, template_path=template_path or RESUME_TEMPLATE_TEX)
    cover_letter = generate_cover_letter(tailored, job)
    ats_score = estimate_ats_score(tailored, job)

    return TailoredResumeResult(
        resume_json=tailored,
        latex=latex,
        cover_letter=cover_letter,
        ats_score=ats_score,
    )


def _slugify(value: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    return slug or 'job'


def save_generated_artifacts(
    result: TailoredResumeResult,
    job: Dict[str, Any],
    *,
    output_root: str | Path | None = None,
) -> Path:
    """
    Persist tailored JSON and LaTeX under resume/generated/{company}/.

    Returns:
        Directory containing saved artifacts.
    """
    company = _slugify(str(job.get('company') or 'company'))
    root = Path(output_root or RESUME_GENERATED_DIR) / company
    root.mkdir(parents=True, exist_ok=True)

    json_path = root / 'resume.json'
    tex_path = root / 'resume.tex'
    cover_path = root / 'cover-letter.txt'

    with json_path.open('w', encoding='utf-8') as handle:
        json.dump(result.resume_json, handle, indent=2)
        handle.write('\n')

    tex_path.write_text(result.latex, encoding='utf-8')
    cover_path.write_text(result.cover_letter, encoding='utf-8')

    return root
