# Built vs Pending

Detailed tracker synced from [docs/PROJECT-TRACKER.md](https://github.com/buhahemal/ai-job-hunting/blob/main/docs/PROJECT-TRACKER.md).

**Last updated:** 2026-06-27

---

## Done (Phases 1–7)

### Phase 1 — Research

- Deep research report, executive summary, architecture diagrams, Supabase schema draft, ₹0 cost analysis

### Phase 2 — Foundation

- Monorepo (`apps/`, `packages/`, `scanners/`, `scraper/`)
- CI umbrella (`ci.yml`), CodeQL, gitleaks, commitlint, husky
- `deploy-pages.yml`, `pipeline-cron.yml`, Docker

### Phase 3 — Database

- Migrations `0001`–`0007` (jobs, profiles, scanned_jobs, enrichment, resume storage, RLS fixes)
- `@ai-job-hunter/database` TS + Python clients
- RLS for anon dashboard pattern

### Phase 4–5 — Scanners

- Plugin SDK + registry
- Greenhouse, Lever, SmartRecruiters, Teamtailor, Workable, RemoteOK, WWR, career pages, Ashby, Workday, Wellfound, Arbeitnow

### Phase 6 — AI

- Embedding + heuristic scoring, skill matcher, salary regex, duplicate detection
- Scanner promotion gate (score > threshold)
- Rescan engine with `profile_hash`

### Phase 7 — Resume

- `packages/resume_engine/` — tailor, LaTeX, PDF, publisher, ATS
- Supabase Storage + versioned `resumes` rows
- T5 deferred; deterministic tailor adopted

---

## In progress (Phases 8–9)

### Built

| Area               | Items                                                                               |
| ------------------ | ----------------------------------------------------------------------------------- |
| **Profile**        | Unified schema, ProfileView UI, JSON import, match preferences, min score slider    |
| **API**            | Profile save/import, tailor, list resumes, scan, rescan, promote, custom job import |
| **Dashboard tabs** | Job Leads, Scan Insights, Tailor, Interviews, Analytics, Profile                    |
| **Data**           | Supabase live mode on GitHub Pages (`VITE_USE_SUPABASE`)                            |
| **Resume UX**      | Tailor from profile, PDF download link, completeness gating                         |
| **Ops**            | Branch ruleset reference, seed-if-empty profile sync                                |

### Pending

| Area         | Items                                                                       |
| ------------ | --------------------------------------------------------------------------- |
| **Backend**  | Auth, OpenAPI, rate limits, pagination, applications API, integration tests |
| **Frontend** | WCAG audit, E2E tests, resume versions UI, PDF resume import                |
| **Docs**     | Published OpenAPI, Lighthouse report                                        |

---

## Not started (Phases 10–11)

### Phase 10 — Learning

- Feedback from Applied/Rejected/Interview/Offer
- Automated auditable weight updates
- Funnel and source-quality analytics beyond current charts

### Phase 11 — Production

- Actions minutes budget audit
- OWASP + RLS full sign-off
- Incident runbooks and monitoring
- Final release tag when all phases done

---

## Quick commands

```bash
npm run quality          # Full quality pipeline
npm test                 # All tests
bash scripts/sync_docs_to_wiki.sh   # Push wiki pages manually
```
