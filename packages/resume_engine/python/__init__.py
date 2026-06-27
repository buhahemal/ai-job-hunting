"""Resume generation: JSON master → tailored JSON → LaTeX."""

from packages.resume_engine.python.generator import (
    generate_tailored_resume,
    load_master_resume,
    render_master_latex,
    save_generated_artifacts,
)

__all__ = [
    'generate_tailored_resume',
    'load_master_resume',
    'render_master_latex',
    'save_generated_artifacts',
]
