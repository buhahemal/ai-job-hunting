# Phase Build Rules (All Phases)

These rules apply to **every phase** of AI Job Hunter. They are derived from [AGENTS.md](../../AGENTS.md), [deep-research-report.md](../deep-research-report.md), and [Executive Summary.pdf](../Executive%20Summary.pdf).

## Non‑negotiable constraints

| Rule | Requirement |
|------|-------------|
| **Cost** | ₹0 / $0 — free tiers only (GitHub, Supabase, Hugging Face OSS models) |
| **Hosting** | Public GitHub repo; frontend on **GitHub Pages**; automation on **GitHub Actions** |
| **AI inference** | Run on **GitHub Actions runners** using **Hugging Face** models locally (`transformers`, `sentence-transformers`) — **no paid LLM APIs** (OpenAI, Gemini paid, Claude) |
| **Data sources** | Official APIs, RSS, and public ATS feeds only — **no LinkedIn scraping**, no TOS violations |
| **Master resume** | Read-only source; tailoring creates **new versions**, never overwrites master |
| **Secrets** | GitHub Secrets only — never commit `.env`, keys, or tokens |

## Recommended AI stack (zero cost)

| Use case | Model / library | Runs on |
|----------|-----------------|---------|
| Job–profile similarity | `sentence-transformers/all-MiniLM-L6-v2` | GH Actions runner |
| Resume JSON draft | `nakamoto-yama/t5-resume-generation` | GH Actions runner |
| Summarization (optional) | `facebook/bart-large-cnn` or `t5-small` | GH Actions runner |
| Scoring fallback | Heuristic + embedding cosine similarity | GH Actions runner |

Use `HF_HOME` cache in Actions; prefer **small** models to fit runner RAM (~7GB usable).

## Target repository structure

```text
apps/
  dashboard/              # React/Vite → GitHub Pages
  api/                    # Optional local/edge API (Phase 8)

packages/
  scanner-sdk/            # Plugin interface (Phase 4)
  ai-engine/              # HF scoring + tailoring (Phase 6)
  resume-engine/            # LaTeX → PDF (Phase 7)
  common/                   # Shared types, utils
  database/                 # Supabase client + migrations (Phase 3)
  config/                   # Centralized configuration

scanners/
  arbeitnow/                # Existing
  greenhouse/               # Phase 4 first ATS scanner
  remoteok/
  weworkremotely/
  ...

supabase/
  migrations/
  seed/

.github/workflows/
  ci.yml                    # Parallel PR gates
  pipeline-cron.yml         # Scan → score → AI → Supabase
  deploy-pages.yml

docs/
  phases/                   # Phase tracking (this folder)
  architecture/
  research/
```

Current transitional layout (`frontend/`, `backend/`, `scraper/`) migrates into the above without breaking GitHub Pages.

## Phase completion rules

A phase is **done** only when:

1. All deliverables in `STATUS.md` are checked
2. `status: done` and `completed:` date set in `STATUS.md`
3. Index updated in [README.md](./README.md)
4. CI passes (typecheck, lint, tests, build)
5. Documentation updated (README + architecture if impacted)
6. No TODO placeholders in production code paths
7. Security & cost review: still ₹0, no secrets in repo

**Never skip phases.** Never merge experimental code to `main`.

## GitHub Actions layout

| Group | Workflows | Purpose |
|-------|-----------|---------|
| **CI** | `ci.yml` | Parallel jobs: frontend, python, docker, docs, markdown, secrets |
| **Security** | `codeql.yml`, `dependency-review.yml` | PR security |
| **Pipeline** | `scanner-cron.yml` (rename to `pipeline-cron.yml` in Phase 6) | Scheduled ingest + HF AI on runner |
| **Deploy** | `deploy-pages.yml` | GitHub Pages |
| **Ops** | `nightly-tests.yml`, `scanner-health.yml`, `stale.yml`, `release.yml` | Scheduled maintenance |

## Compliance

- Respect robots.txt and API rate limits
- Attribute RemoteOK per their guidelines
- Store minimal PII; protect dashboard if resume data is sensitive
- RLS on all Supabase tables

## References

- [Deep Research Report](../deep-research-report.md) — full R&D specification
- [Executive Summary](../Executive%20Summary.pdf) — condensed vision
- [Architecture Overview](../architecture/overview.md) — system context
