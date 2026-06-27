"""Publish tailored resumes: compile PDF, upload to Storage, version in DB."""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from packages.database.python.repositories.resumes import ResumeRepository
from packages.database.python.storage import is_storage_configured, upload_resume_pdf
from packages.resume_engine.python.generator import TailoredResumeResult, save_generated_artifacts
from packages.resume_engine.python.pdf import LatexCompileError, compile_latex_to_pdf, pdflatex_available


@dataclass(frozen=True)
class PublishedResume:
    """Result of publishing a tailored resume."""

    version: str
    pdf_url: str
    pdf_path: Optional[Path]
    resume_row: Dict[str, Any]
    pdf_compiled: bool


def publish_tailored_resume(
    result: TailoredResumeResult,
    *,
    job_id: str,
    job: Dict[str, Any],
    client: Any,
) -> PublishedResume:
    """
    Compile LaTeX to PDF, upload to Supabase Storage, and insert a resumes row.

    Master JSON on disk is never modified. Also writes local artifacts under
    ``resume/generated/`` for debugging.
    """
    save_generated_artifacts(result, job)

    resume_repo = ResumeRepository(client)
    resume_repo.ensure_master_snapshot()
    version = resume_repo.next_tailored_version(job_id)

    pdf_path: Optional[Path] = None
    pdf_url = ''
    pdf_compiled = False

    if pdflatex_available():
        try:
            with tempfile.TemporaryDirectory(prefix='resume-pdf-') as tmp:
                pdf_path = compile_latex_to_pdf(result.latex, work_dir=tmp, stem='resume')
                pdf_bytes = pdf_path.read_bytes()
                pdf_compiled = True

                if is_storage_configured():
                    pdf_url = upload_resume_pdf(
                        client,
                        job_id=job_id,
                        version=version,
                        pdf_bytes=pdf_bytes,
                    )
                else:
                    pdf_url = f'file://{pdf_path}'
        except LatexCompileError as exc:
            print(f'[Publisher] PDF compile failed: {exc}')
    else:
        print('[Publisher] pdflatex not available — storing LaTeX version without PDF.')

    row = resume_repo.insert_tailored(
        job_id=job_id,
        version=version,
        content=result.resume_json,
        pdf_url=pdf_url,
        ats_score=result.ats_score,
    )

    return PublishedResume(
        version=version,
        pdf_url=pdf_url,
        pdf_path=pdf_path,
        resume_row=row,
        pdf_compiled=pdf_compiled,
    )
