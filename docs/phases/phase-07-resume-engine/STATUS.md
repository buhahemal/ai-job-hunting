# Phase 7 — Resume Engine

```yaml
status: done
started: 2026-06-01
completed: 2026-06-27
```

## Deliverables

- [x] `packages/resume_engine/` — tailor, renderer, generator, ATS, cover letter, PDF, publisher
- [x] Master resume JSON SOT in `apps/api/data/resume/master.json` — **read-only** master source
- [x] Jinja2 LaTeX template in `apps/api/data/resume/template.tex`
- [x] Deterministic JSON tailoring (`tailor.py`) — reorders skills/bullets; enriches summary with JD keywords
- [x] **T5 model deferred** — see [Design decision](#design-decision-t5-vs-deterministic-tailor)
- [x] `pdflatex` compile module (`pdf.py`) + CI LaTeX validation in `tests.yml` and `pipeline-cron.yml`
- [x] PDF upload to Supabase Storage (`storage.py`, migration `0006_resume_storage.sql`)
- [x] Version tracking in `resumes` table (`ResumeRepository`: `master`, `tailored_v1`, …)
- [x] ATS compatibility heuristic (`ats.py`) + benchmark test (≥25% improvement vs master)
- [x] Cover letter generation (template-based; optional HF model deferred)
- [x] Never overwrite master resume (unit test + copy-on-write tailor)

## Design decision: T5 vs deterministic tailor

| Option                                            | Decision                         |
| ------------------------------------------------- | -------------------------------- |
| `nakamoto-yama/t5-resume-generation` on HF runner | **Deferred** — optional R&D path |
| Deterministic `tailor.py` from master JSON        | **Adopted** for Phase 7          |

Rationale: master JSON is the source of truth; deterministic reordering and keyword enrichment satisfies ATS goals without inventing employers or dates. T5 draft generation may be revisited in a later phase if JSON-first tailoring proves insufficient.

## Quality gate

- [x] End-to-end: `POST /api/jobs/:id/tailor` → LaTeX → PDF (when `pdflatex` available) → Storage → `resumes` row
- [x] LaTeX compiles in CI (`TestPdfCompile` with TeX Live on GitHub Actions)
- [x] Master resume unchanged after tailoring run (`test_tailor_does_not_mutate_master`)

## API

| Endpoint                    | Purpose                              |
| --------------------------- | ------------------------------------ |
| `POST /api/jobs/:id/tailor` | Tailor, compile, upload, version     |
| `GET /api/jobs/:id/resumes` | List versioned resume rows for a job |

## Next phase

→ [Phase 8: Dashboard Backend](../phase-08-dashboard-backend/)
