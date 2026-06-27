"""LaTeX escaping helpers for Jinja2 templates."""

from __future__ import annotations

import re

_LATEX_SPECIAL = re.compile(r'([\\%&#_{}$~^])')


def escape_latex(text: str) -> str:
    """Escape characters that break LaTeX compilation."""
    if not text:
        return ''

    def _replace(match: re.Match[str]) -> str:
        char = match.group(1)
        mapping = {
            '\\': r'\textbackslash{}',
            '%': r'\%',
            '&': r'\&',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '$': r'\$',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        return mapping.get(char, char)

    return _LATEX_SPECIAL.sub(_replace, str(text))
