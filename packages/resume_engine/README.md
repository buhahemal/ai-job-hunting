# Resume Engine

JSON master resume → job-aware tailoring → LaTeX generation.

## Architecture

```
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
apps/api/data/resume/generated/{company}/   ← resume.json, resume.tex, cover-letter.txt
```

## Usage

```python
from packages.resume_engine.python.generator import generate_tailored_resume, save_generated_artifacts

job = {
    "title": "Senior Platform Engineer",
    "company": "Stripe",
    "description": "Kubernetes AWS Node.js ...",
    "extractedSkills": ["Kubernetes", "AWS", "Node.js"],
}

result = generate_tailored_resume(job)
save_generated_artifacts(result, job)

print(result.latex)
print(result.ats_score)
```

Tailoring is invoked from `scraper/ai_matcher.py` when a job is tailored in the dashboard/API.

## Files

| Path           | Purpose                                   |
| -------------- | ----------------------------------------- |
| `master.json`  | Structured resume data                    |
| `template.tex` | LaTeX layout template                     |
| `generated/`   | Per-company tailored outputs (gitignored) |

Master LaTeX for the profile tab is rendered from `master.json` via `render_master_latex()`.
