# Phase 2 — Repository Setup + CI/CD + Coding Standards

```yaml
status: in_progress
started: 2026-06-27
completed:
```

## Deliverables

### Repository & structure
- [x] Public GitHub monorepo
- [x] Transitional modules: `frontend/`, `backend/`, `scraper/`
- [ ] Migrate toward target layout in [RULES.md](../RULES.md) (`apps/`, `packages/`, `scanners/`)
- [x] `.env.example` (no secrets committed)

### CI/CD (GitHub Actions)
- [x] Consolidated `ci.yml` (parallel: frontend, python, docker, docs, markdown, secrets)
- [x] `deploy-pages.yml` (GitHub Pages, Node 24)
- [x] `scanner-cron.yml` (daily job scan)
- [x] Security workflows: CodeQL, dependency-review, scanner-health, nightly, stale, release

### Coding standards
- [x] TypeScript strict mode (`frontend/`)
- [x] ESLint + no `any`
- [x] Vitest unit tests (baseline)
- [x] Python scraper tests
- [x] `AGENTS.md` engineering standards
- [x] `docs/phases/RULES.md` phase build rules
- [ ] Prettier + Husky + Commitlint
- [ ] Centralized `packages/config/`

### Documentation
- [x] Root README
- [x] Module READMEs (frontend, backend, scraper)
- [x] `docs/architecture/overview.md`
- [x] Phase tracking (`docs/phases/`)
- [x] PR and issue templates

## Quality gate

- [ ] All deliverables checked
- [ ] CI green on `main`
- [ ] No paid services introduced

## Spec

[FOUNDATION.md](./FOUNDATION.md) — legacy Phase 1 foundation doc (reference during migration)

## Next phase

→ [Phase 3: Supabase](../phase-03-database-supabase/)
