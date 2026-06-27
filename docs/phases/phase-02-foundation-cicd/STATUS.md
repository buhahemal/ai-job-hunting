# Phase 2 — Repository Setup + CI/CD + Coding Standards

```yaml
status: done
started: 2026-06-27
completed: 2026-06-27
```

## Deliverables

### Repository & structure

- [x] Public GitHub monorepo
- [x] `apps/dashboard/`, `apps/api/`, `scanners/`, `packages/config/`
- [x] Pipeline orchestration in `scraper/`
- [x] `.env.example` (no secrets committed)

### CI/CD (GitHub Actions)

- [x] Consolidated `ci.yml` (parallel: frontend, python, docker, docs, markdown, format, secrets)
- [x] `deploy-pages.yml` (GitHub Pages, Node 24)
- [x] `scanner-cron.yml` (daily job scan)
- [x] Security workflows: CodeQL, dependency-review, scanner-health, nightly, stale, release

### Coding standards

- [x] TypeScript strict mode (`apps/dashboard/`)
- [x] ESLint + Prettier + eslint-config-prettier
- [x] Husky + lint-staged + Commitlint (conventional commits)
- [x] Vitest unit tests (baseline)
- [x] Python scraper tests
- [x] `AGENTS.md` engineering standards
- [x] `docs/phases/RULES.md` phase build rules
- [x] Centralized `packages/config/` (Python + TypeScript paths)

### Documentation

- [x] Root README
- [x] Module READMEs (dashboard, api, scraper, scanners, config)
- [x] `docs/architecture/overview.md`
- [x] Phase tracking (`docs/phases/`)
- [x] PR and issue templates

## Quality gate

- [x] All deliverables checked
- [x] CI green on `main`
- [x] No paid services introduced

## Spec

[FOUNDATION.md](./FOUNDATION.md) — legacy foundation doc (reference)

## Next phase

→ [Phase 3: Supabase](../phase-03-database-supabase/)
