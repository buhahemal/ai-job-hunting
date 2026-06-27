# Phase 7 — Resume Engine

**Status:** done

Track deliverables in [STATUS.md](./STATUS.md).

## Pipeline

```text
master.json → tailor.py → renderer.py → resume.tex
                              ↓
                         pdf.py (pdflatex)
                              ↓
                    Supabase Storage (resumes bucket)
                              ↓
                    resumes table (master, tailored_v1, …)
```

Tailoring is triggered from the dashboard via `POST /api/jobs/:id/tailor`.
