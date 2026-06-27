# AI Agent Entry Point

**Start here.** This repository is an AI-first engineering platform.

## Read order

1. [PROJECT.md](./PROJECT.md) — vision and constraints
2. [EXECUTION_PLAN.md](./EXECUTION_PLAN.md) — current phase (never skip)
3. [CODING_RULES.md](./CODING_RULES.md) — Search → Reuse → Refactor → Create
4. [ARCHITECTURE.md](./ARCHITECTURE.md) — system layout
5. Phase file: [phases/phase-XX.md](./phases/)

## Principles

SOLID · DRY · KISS · YAGNI · Clean Architecture · Strict TypeScript · Conventional Commits · ₹0 cost

## Implementation workflow

```text
Search → Reuse → Refactor → Create
         ↓
Implement with tests + docs
         ↓
Architecture → Security → Performance → Quality → Cost review
         ↓
npm run quality && npm test
         ↓
Done
```

## Definition of done

✓ TypeScript strict · ESLint · Tests · Build  
✓ Duplicate code < 3% · Knip clean · Architecture rules pass  
✓ Documentation updated · No secrets · No TODOs · No console.log  
✓ GitHub Actions pass · ₹0 cost verified

Full checklist: [REVIEW_CHECKLIST.md](./REVIEW_CHECKLIST.md)

## Quality commands

```bash
npm run quality          # Full local quality pipeline
npm run quality:duplicates
npm run quality:dead-code
npm run arch:depcruise
npm run arch:madge
npm test
```

## Phase status

See [EXECUTION_PLAN.md](./EXECUTION_PLAN.md). Human specs: [`docs/phases/`](../docs/phases/README.md) · [Tracker](../docs/PROJECT-TRACKER.md) · [Wiki](https://github.com/buhahemal/ai-job-hunting/wiki)

## Constraints for AI

- Never skip phases
- Never generate placeholder implementations
- Never duplicate existing utilities, types, or SQL
- Never commit secrets
- Never use paid LLM APIs in CI/production
- Never overwrite master resume (Phase 7+)

Human-facing rules also in root [`AGENTS.md`](../AGENTS.md) (summary pointer).
