# AI Job Hunter - Engineering Standards & Repository Guidelines

## Repository Principles

This repository follows strict engineering standards.

Every change must be:

- Production Ready
- Fully Tested
- Fully Typed
- Fully Documented
- Secure
- Modular
- Cost Optimized (₹0)
- Open Source Friendly

Never merge experimental or incomplete implementations.

---

## Development Phases

Development is incremental. Every phase must be production-ready before moving to the next. **Never skip phases.**

| Phase | Focus                                   | Status      |
| ----- | --------------------------------------- | ----------- |
| 1     | Research & Architecture                 | done        |
| 2     | Repository Setup + CI/CD + Standards    | done        |
| 3     | Database + Supabase Schema              | done        |
| 4     | Scanner SDK + Greenhouse                | in_progress |
| 5     | Remaining Scanners (one by one)         | pending     |
| 6     | AI Pipeline (Hugging Face on GH runner) | pending     |
| 7     | Resume Engine (LaTeX → PDF)             | pending     |
| 8     | Dashboard Backend                       | pending     |
| 9     | Dashboard Frontend (GitHub Pages)       | pending     |
| 10    | Learning Engine + Analytics             | pending     |
| 11    | Performance, Security, Production       | pending     |

Phase specs, deliverables, and global build rules live in [`docs/phases/`](docs/phases/README.md) and [`docs/phases/RULES.md`](docs/phases/RULES.md). Mark a phase done by updating its `STATUS.md` and the index table in `docs/phases/README.md`.

---

## Current Repository Layout

```text
apps/
  dashboard/         React + Vite → GitHub Pages
  api/               Local Flask API + data/data.json
packages/
  config/            Shared path configuration
scanners/            Per-source job discovery plugins
scraper/             Scan pipeline orchestration → GitHub Actions
docs/                Architecture, API, research
.github/workflows/   CI, security, deployment, scanner cron
```

### Target Folder Structure

```text
apps/
    dashboard/
    api/

packages/
    scanner-sdk/
    ai-engine/
    resume-engine/
    common/
    database/
    logger/
    queue/
    config/

scanners/
    greenhouse/
    lever/
    workday/
    ashby/
    company-pages/

.github/
    workflows/
    ISSUE_TEMPLATE/
    PULL_REQUEST_TEMPLATE.md

docs/
    architecture/
    phases/
    api/
    research/

scripts/
tests/
docker/
supabase/
.ai/
```

---

## General Coding Rules

### Code Quality

- TypeScript Strict Mode only
- Never use `any`
- Prefer interfaces over types when appropriate
- Prefer composition over inheritance
- Prefer dependency injection
- Avoid global mutable state
- Keep functions small (<50 lines where practical)
- One responsibility per function
- One responsibility per class

### Naming

| Kind       | Good                              | Bad                 |
| ---------- | --------------------------------- | ------------------- |
| Variables  | `userId`, `jobScanner`            | `x`, `obj`, `temp2` |
| Classes    | `ResumeService`, `JobScanner`     | —                   |
| Interfaces | `IResumeGenerator`, `IJobScanner` | —                   |
| Constants  | `MAX_RETRY`, `DEFAULT_TIMEOUT`    | —                   |

---

## Module Rules

Every module must contain:

```text
README.md
src/ or package root
tests/
CHANGELOG.md
```

---

## Function Rules

Every public function must have:

- Description
- Parameters
- Return Type
- Example (where helpful)
- Tests

---

## Error Handling

Never:

```ts
catch (e) {}
```

Always:

- Log
- Retry if recoverable
- Wrap meaningful errors
- Preserve stack traces

---

## Logging

Every important action should log: Request ID, Job ID, Scanner, Duration, Status.

Never log: Secrets, Tokens, Passwords.

---

## Configuration

Never hardcode URLs, API keys, timeouts, or retry counts. Everything must come from configuration.

---

## Security Rules

Never commit: `.env`, secrets, private keys, tokens.

Always: validate inputs, escape outputs, rate limit, sanitize HTML, use parameterized queries.

---

## Database Rules

Every migration must be reversible, idempotent, and documented. Indexes and foreign keys required. Use transactions where needed.

---

## AI Rules

- Run inference on **GitHub Actions runners** using **Hugging Face** OSS models (`transformers`, `sentence-transformers`)
- **No paid LLM APIs** (OpenAI, Gemini, Claude) in CI or production
- Never hallucinate resume content
- Never invent experience or fabricate projects
- Only optimize wording

---

## Resume Rules

Master Resume → Read Only → Generate → Store Version → PDF. Never overwrite master.

---

## Scanner Rules

Every scanner implements:

```text
discoverJobs()
normalize()
healthCheck()
validate()
deduplicate()
```

Every scanner must be: independent, retryable, observable, testable.

---

## Testing Rules

Required: Unit, Integration, Contract, Snapshot tests where applicable.

Coverage target: **minimum 90%** (enforced incrementally in CI).

---

## Pull Request Rules

Every PR must include: Purpose, Architecture Impact, Performance Impact, Security Impact, Testing, Screenshots (UI), Documentation.

Use `.github/PULL_REQUEST_TEMPLATE.md`.

---

## Git Commit Rules

Format: `type(scope): summary`

Examples:

```text
feat(scanner): add greenhouse scanner
fix(ai): improve resume scoring
docs(api): update endpoints
refactor(database): optimize indexes
```

---

## Documentation Rules

Every module requires: README, Architecture notes, Configuration, Example Usage, Known Limitations.

---

## GitHub Actions

### PR / push to main (parallel jobs in one workflow)

| Workflow                             | Jobs                                                                         |
| ------------------------------------ | ---------------------------------------------------------------------------- |
| [`ci.yml`](.github/workflows/ci.yml) | `frontend`, `python`, `docker`, `docs`, `markdown`, `secrets` (all parallel) |

### Separate workflows (different triggers, permissions, or side effects)

| Workflow                                                           | Purpose                             |
| ------------------------------------------------------------------ | ----------------------------------- |
| [`codeql.yml`](.github/workflows/codeql.yml)                       | GitHub CodeQL analysis              |
| [`dependency-review.yml`](.github/workflows/dependency-review.yml) | Dependency changes in PRs           |
| [`scanner-health.yml`](.github/workflows/scanner-health.yml)       | Scheduled scanner health (every 6h) |
| [`nightly-tests.yml`](.github/workflows/nightly-tests.yml)         | Full integration tests              |
| [`release.yml`](.github/workflows/release.yml)                     | Release automation                  |
| [`stale.yml`](.github/workflows/stale.yml)                         | Close stale issues                  |
| [`scanner-cron.yml`](.github/workflows/scanner-cron.yml)           | Scheduled job discovery             |
| [`deploy-pages.yml`](.github/workflows/deploy-pages.yml)           | GitHub Pages deployment             |

Every pull request runs **CI** (type check, lint, tests, build, docs, markdown, secrets, docker), plus **Dependency Review** and **CodeQL**.

See [docs/architecture/overview.md](docs/architecture/overview.md#github-actions) for the workflow layout.

---

## Code Review Checklist

Before merge verify: SOLID, DRY, KISS, Clean Architecture, no dead code, no duplication, no magic numbers, proper logging, proper error handling, performance reviewed, security reviewed, tests added, documentation updated.

---

## AI Self Review

Before finishing any task answer:

1. Is the implementation production ready?
2. Can it be simplified?
3. Is it modular?
4. Is it scalable?
5. Are there hidden edge cases?
6. Are failures handled?
7. Are retries implemented?
8. Is the code reusable?
9. Are tests sufficient?
10. Does it increase operational cost?

If any answer is **No**, revise before completion.

---

## AI Review Rules (Post-Feature)

- **Architecture**: SOLID, Clean Architecture, modular design
- **Security**: OWASP, injection, SSRF, XSS, CSRF, auth, rate limiting
- **Performance**: N+1, memory, CPU, caching, pagination
- **Database**: indexes, FKs, transactions, query plans
- **AI**: prompt quality, token usage, latency, hallucination risk
- **Cost**: verify ₹0 budget; prefer open-source alternatives

---

## Definition of Done

A task is complete only when:

✓ Builds successfully  
✓ TypeScript passes (strict)  
✓ ESLint passes  
✓ Tests pass  
✓ Coverage ≥ 90% (target; CI reports progress)  
✓ Documentation updated  
✓ Security review passed  
✓ Performance review passed  
✓ GitHub Actions pass  
✓ No TODO comments remain

Otherwise the task is considered incomplete.
