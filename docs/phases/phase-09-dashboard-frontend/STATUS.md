# Phase 9 — Dashboard Frontend (GitHub Pages)

```yaml
status: in_progress
started: 2026-06-27
completed:
last_updated: 2026-06-27
```

## Built

- [x] React/Vite dashboard in `apps/dashboard/`
- [x] Supabase client mode (`VITE_USE_SUPABASE` + `deploy-pages.yml` secrets)
- [x] **Job Leads** tab — list, filters, scores, job detail panel
- [x] **Scan Insights** tab — paginated scanned jobs, rescan, promote, RemoteOK attribution
- [x] **Tailor** tab — LaTeX preview, cover letter, PDF download when backend compiles
- [x] **Interviews** tab — schedule and status tracking
- [x] **Analytics** tab — job/interview charts (read-only baseline)
- [x] **Profile** tab — full ProfileView (import JSON, match preferences, threshold)
- [x] Profile completeness gating before tailor
- [x] GitHub Pages deploy workflow (`.github/workflows/deploy-pages.yml`)
- [x] Optional backend mode (`VITE_USE_BACKEND`) for tailor/import/rescan

## Pending

- [ ] Resume version list in Tailor tab (`listJobResumes` UI)
- [ ] PDF resume upload import (Phase B — deferred)
- [ ] WCAG 2.1 AA accessibility audit + remediation
- [ ] E2E or integration tests for critical flows
- [ ] Lighthouse accessibility score documented
- [ ] Responsive polish pass on all tabs
- [ ] Confirm production Pages URL documented in README

## Current baseline

Dashboard is feature-complete for solo use; remaining work is polish, testing, and accessibility.

## Rules

- Host on GitHub Pages (₹0)
- Static export compatible with `VITE_BASE_PATH`

## Quality gate

- [x] TypeScript strict + ESLint pass
- [ ] E2E tests for profile save, tailor, promote
- [ ] Lighthouse report archived

## Next phase

→ [Phase 10: Learning + Analytics](../phase-10-learning-analytics/)
