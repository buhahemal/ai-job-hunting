# Phase 7 — Resume Engine

```yaml
status: pending
started:
completed:
```

## Deliverables

- [ ] `packages/resume-engine/`
- [ ] Master LaTeX template(s) in `templates/` — **read-only** master source
- [ ] T5-generated JSON → Jinja2 LaTeX merge
- [ ] `pdflatex` in GitHub Actions (or pre-built latex docker image)
- [ ] PDF upload to Supabase Storage
- [ ] Version tracking in `resumes` table (`master`, `tailored_v1`, …)
- [ ] ATS compatibility check (open-source heuristic)
- [ ] Cover letter generation (template-based + optional small HF model)
- [ ] Never overwrite master resume

## Rules

- AI may **reword and reorder** bullets — not invent employers, degrees, or dates
- Store PDF URL in Supabase; link from dashboard

## Quality gate

- [ ] End-to-end: shortlisted job → PDF in Storage → URL in DB
- [ ] LaTeX compiles in CI
- [ ] Master resume unchanged after tailoring run

## Next phase

→ [Phase 8: Dashboard Backend](../phase-08-dashboard-backend/)
