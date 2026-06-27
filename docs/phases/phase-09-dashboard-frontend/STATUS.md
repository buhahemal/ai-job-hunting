# Phase 9 — Dashboard Frontend (GitHub Pages)

```yaml
status: pending
started:
completed:
```

## Deliverables

- [x] Migrated to `apps/dashboard/` (Phase 2)
- [ ] Supabase client — live data (replace static `data.json` + localStorage-only mode)
- [ ] Jobs list: score, filters, status, apply links
- [ ] Resume preview + download from Supabase Storage
- [ ] Profile & settings editor
- [ ] Interview tracker + analytics views
- [ ] Responsive + accessibility (WCAG 2.1 AA target)
- [ ] Deploy via `deploy-pages.yml` to GitHub Pages
- [ ] RemoteOK attribution link where required

## Current baseline

Existing React/Vite dashboard at `apps/dashboard/` — extend for Supabase in Phase 9.

## Rules

- Host **only** on GitHub Pages (no Vercel/Netlify unless still ₹0 — prefer GitHub)
- Static export compatible with `VITE_BASE_PATH`

## Quality gate

- [ ] E2E or integration tests for critical flows
- [ ] Lighthouse accessibility score documented
- [ ] Production URL live on GitHub Pages

## Next phase

→ [Phase 10: Learning + Analytics](../phase-10-learning-analytics/)
