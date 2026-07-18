# AI Job Hunter — Project Tracker

Last updated: **2026-06-27**

Single view of what is **built**, **in progress**, and **pending** across all 11 phases.

**Quick links:** [Phase index](./phases/README.md) · [Profile guide](./guides/profile-and-resume.md) · [Architecture](./architecture/overview.md)

---

## Phase summary

| Phase | Name                    | Status          | Built (high level)                                                  | Pending (high level)                       |
| ----: | ----------------------- | --------------- | ------------------------------------------------------------------- | ------------------------------------------ |
|     1 | Research & Architecture | **done**        | R&D docs, architecture, schema draft, cost/risk analysis            | —                                          |
|     2 | Foundation + CI/CD      | **done**        | Monorepo, ESLint/Prettier/Husky, CI umbrella, Pages deploy workflow | —                                          |
|     3 | Database + Supabase     | **done**        | Migrations, RLS, `@ai-job-hunter/database`, scanner → Supabase      | —                                          |
|     4 | Scanner SDK + sources   | **done**        | `scanner_sdk`, 8 core scanners, health checks                       | —                                          |
|     5 | Scanner expansion       | **done**        | Ashby, Workday, Wellfound, Arbeitnow + attribution notes            | Wellfound 403 workaround (optional)        |
|     6 | AI pipeline             | **done**        | MiniLM embeddings, skill/salary extractors, dedupe, 90% gate        | BART JD summarize (optional)               |
|     7 | Resume engine           | **done**        | LaTeX tailor, PDF compile, Storage, versioning, ATS benchmark       | T5 generation (deferred)                   |
|     8 | Dashboard backend       | **in_progress** | Flask API, profile CRUD/import, tailor/rescan/scan                  | Auth, OpenAPI, rate limits, pagination API |
|     9 | Dashboard frontend      | **in_progress** | Supabase UI, jobs/scan/tailor/profile/interviews/analytics tabs     | A11y audit, E2E tests, polish              |
|    10 | Learning + analytics    | **pending**     | Basic analytics view (read-only)                                    | Feedback loop, auto re-weighting           |
|    11 | Production hardening    | **pending**     | CodeQL, gitleaks, branch ruleset reference                          | Runbooks, full OWASP sign-off              |

**Progress:** 7 phases done · 2 in progress · 2 pending

---

## Built — by capability

### Job discovery & scanning

| Capability            | Location                                         | Notes                                                    |
| --------------------- | ------------------------------------------------ | -------------------------------------------------------- |
| Scanner plugin SDK    | `packages/scanner_sdk/`                          | `discover_jobs`, `normalize`, `health_check`             |
| 14+ source plugins    | `scanners/*`                                     | Adds Remotive + HN Who is Hiring to ATS and remote feeds |
| Scanner cron pipeline | `.github/workflows/pipeline-cron.yml`            | HF embeddings on GitHub runner                           |
| Scan Insights store   | `scanned_jobs` table + dashboard tab             | Below-threshold jobs retained for review                 |
| Manual rescan         | `POST /api/scan-insights/rescan`, `RescanEngine` | Re-scores when profile changes                           |
| Promotion threshold   | `profile.matchSettings.minMatchScore`            | Inclusive default 80%; env override still supported      |
| Remote eligibility    | `remote_policy.py`                               | Worldwide boost; geo/clearance restrictions explained    |
| Preference prefilter  | `scanner_sdk/python/filters.py`                  | Blacklists, experience levels, one lead per company      |

### AI matching & enrichment

| Capability           | Location                             | Notes                                                    |
| -------------------- | ------------------------------------ | -------------------------------------------------------- |
| Embedding scorer     | `packages/ai_engine/`                | `all-MiniLM-L6-v2`                                       |
| Heuristic fallback   | `heuristic_scorer.py`                | ₹0 path when embeddings fail                             |
| Skill matcher + gaps | `skill_matcher.py`, Scan Insights UI | Missing skills vs profile corpus                         |
| Job enrichment       | `job_enricher.py`                    | Sub-scores: skill, experience, remote, company, location |
| Duplicate detection  | `duplicate_detector.py`              | Embedding similarity threshold                           |

### Profile & match criteria

| Capability             | Location                                            | Notes                                              |
| ---------------------- | --------------------------------------------------- | -------------------------------------------------- |
| Unified profile schema | `ProfileRecord` in `packages/database/`             | summary, skillGroups, matchSettings, preferences   |
| Full profile UI        | `apps/dashboard/src/components/profile/`            | Import JSON, all fields editable                   |
| Profile API            | `GET/POST /api/profile`, `POST /api/profile/import` | Validates + regenerates LaTeX on save              |
| Seed-if-empty sync     | `scripts/sync_profile_to_supabase.py`               | Does not overwrite dashboard edits                 |
| Match preferences UI   | ProfileView → Match Preferences                     | locations, skills, blacklists, levels, one/company |
| Min match score UI     | ProfileView → Advanced                              | Slider 70–95%; scanner reads from profile          |

### Resume generation

| Capability            | Location                                  | Notes                                            |
| --------------------- | ----------------------------------------- | ------------------------------------------------ |
| Master JSON SOT       | `apps/api/data/resume/master.json`        | Read-only on disk; runtime uses Supabase profile |
| Deterministic tailor  | `packages/resume_engine/python/tailor.py` | Reorders skills/bullets; no LLM                  |
| LaTeX render + PDF    | `renderer.py`, `pdf.py`, `publisher.py`   | TeX Live in CI + Docker API image                |
| Supabase Storage PDFs | `0006_resume_storage.sql`, `storage.py`   | `{job_id}/{version}.pdf`                         |
| Version tracking      | `resumes` table                           | `master`, `tailored_v1`, …                       |
| Tailor API + UI       | `POST /api/jobs/:id/tailor`, Tailor tab   | PDF download when compile succeeds               |

### Dashboard & hosting

| Capability                | Location                                       | Notes                                                            |
| ------------------------- | ---------------------------------------------- | ---------------------------------------------------------------- |
| React/Vite dashboard      | `apps/dashboard/`                              | Job Leads, Scan Insights, Tailor, Interviews, Analytics, Profile |
| Supabase browser client   | `packages/database/`, `VITE_USE_SUPABASE`      | Primary production data path                                     |
| Flask API (optional)      | `apps/api/server.py`                           | Tailor, import, rescan, scan                                     |
| GitHub Pages deploy       | `.github/workflows/deploy-pages.yml`           | Requires Supabase secrets                                        |
| CI quality gates          | `.github/workflows/ci.yml`                     | lint, tests, semgrep, spellcheck, architecture, …                |
| Branch protection ruleset | `.github/rulesets/main-branch-protection.json` | Reference JSON for `main`                                        |

---

## Pending — prioritized backlog

### Phase 8 (Dashboard backend)

- [ ] Supabase Auth for personal dashboard (replace anon-wide RLS pattern)
- [ ] OpenAPI spec in `docs/api/`
- [ ] Rate limiting on mutation endpoints
- [ ] Server-side search, filter, pagination APIs
- [ ] Applications CRUD (schema exists; API incomplete)
- [ ] API integration tests against Supabase test project

### Phase 9 (Dashboard frontend)

- [ ] WCAG 2.1 AA accessibility audit + fixes
- [ ] E2E tests for profile save, tailor, promote flows
- [ ] Lighthouse score documented
- [ ] Resume version list in Tailor tab (`GET /api/jobs/:id/resumes` wired in UI)
- [ ] PDF upload import (Phase B — PyMuPDF heuristic parser)

### Phase 10 (Learning engine)

- [ ] Outcome feedback: Applied / Rejected / Interview / Offer → learning store
- [ ] Auditable weight tuning from outcomes
- [ ] Source quality analytics (beyond current read-only charts)
- [ ] A/B heuristic vs embedding effectiveness report

### Phase 11 (Production)

- [ ] GitHub Actions minutes audit (stay within free tier)
- [ ] Full OWASP + RLS audit sign-off
- [ ] Runbooks (failed cron, Supabase outage, model cache miss)
- [ ] Mark phases 8–10 done; tag release via `release.yml`

---

## Recent milestones

| Date       | Milestone                                                      |
| ---------- | -------------------------------------------------------------- |
| 2026-06-27 | Phase 7 resume engine complete (PDF, Storage, CI LaTeX)        |
| 2026-06-27 | Unified profile UI + match settings + scanner threshold wiring |
| 2026-06-27 | GitHub ruleset reference for `main` branch protection          |
| 2026-06-27 | Phases 1–6 production scanners + AI pipeline complete          |

---

## How to update this tracker

1. When a deliverable ships, check it off in `docs/phases/phase-XX-*/STATUS.md`
2. Update this file and [docs/phases/README.md](./phases/README.md)
3. Sync to GitHub Wiki: `bash scripts/sync_docs_to_wiki.sh` (or push to `main` — workflow runs automatically)
