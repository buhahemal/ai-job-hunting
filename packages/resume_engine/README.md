# Resume Engine

JSON master resume → job-aware tailoring → LaTeX → PDF → Supabase Storage.

## Architecture

```text
apps/api/data/resume/master.json   ← source of truth (never modified by pipeline)
apps/api/data/resume/template.tex  ← Jinja2 LaTeX template
          │
          ▼
packages/resume_engine/python/tailor.py     ← copy + reorder skills/bullets for job
          │
          ▼
packages/resume_engine/python/renderer.py   ← render LaTeX
          │
          ▼
packages/resume_engine/python/pdf.py        ← pdflatex compile (optional locally)
          │
          ▼
packages/resume_engine/python/publisher.py  ← Storage upload + resumes table row
          │
          ▼
apps/api/data/resume/generated/{company}/   ← local debug artifacts (gitignored)
```

## Usage

```python
from packages.resume_engine.python.generator import generate_tailored_resume
from packages.resume_engine.python.publisher import publish_tailored_resume

job = {
    "id": "gh-123",
    "title": "Senior Platform Engineer",
    "company": "Stripe",
    "description": "Kubernetes AWS Node.js ...",
    "extractedSkills": ["Kubernetes", "AWS", "Node.js"],
}

result = generate_tailored_resume(job)
# With Supabase client configured:
# published = publish_tailored_resume(result, job_id=job["id"], job=job, client=client)
```

Tailoring is invoked from `apps/api/server.py` (`POST /api/jobs/:id/tailor`) and `scraper/ai_matcher.py`.

## Files

| Path           | Purpose                                        |
| -------------- | ---------------------------------------------- |
| `master.json`  | Structured resume data (SOT)                   |
| `master.tex`   | Rendered baseline LaTeX (regenerate from JSON) |
| `template.tex` | LaTeX layout template                          |
| `generated/`   | Per-company tailored outputs (gitignored)      |

## Tests

```bash
PYTHONPATH=. python3 -m unittest discover -s packages/resume_engine/tests -v
```

PDF compile tests require `pdflatex` (installed in CI via TeX Live).
