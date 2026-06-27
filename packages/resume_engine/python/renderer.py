"""Render resume JSON into LaTeX using Jinja2 templates."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from packages.config.python.paths import RESUME_TEMPLATE_TEX
from packages.resume_engine.python.latex import escape_latex


def _build_environment(template_dir: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(default=False, default_for_string=False),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters['latex'] = escape_latex
    return env


def render_resume_latex(
    resume: Dict[str, Any],
    *,
    template_path: str | Path | None = None,
) -> str:
    """
    Render a resume dict (master or tailored) into LaTeX.

    Args:
        resume: Resume JSON payload matching template variables.
        template_path: Optional override for template.tex location.

    Returns:
        Complete LaTeX document string.
    """
    path = Path(template_path or RESUME_TEMPLATE_TEX)
    if not path.is_file():
        raise FileNotFoundError(f'Resume LaTeX template not found: {path}')

    env = _build_environment(path.parent)
    template = env.get_template(path.name)
    context = dict(resume)
    context.setdefault('targetRole', '')
    return template.render(**context)
