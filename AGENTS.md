# AI Job Hunter — Agent Guidelines

**Canonical AI instructions live in [`.ai/AGENTS.md`](.ai/AGENTS.md).**

Read `.ai/` before any implementation:

| File                                                 | Purpose                            |
| ---------------------------------------------------- | ---------------------------------- |
| [`.ai/PROJECT.md`](.ai/PROJECT.md)                   | Product vision                     |
| [`.ai/EXECUTION_PLAN.md`](.ai/EXECUTION_PLAN.md)     | Phase roadmap                      |
| [`.ai/CODING_RULES.md`](.ai/CODING_RULES.md)         | Search → Reuse → Refactor → Create |
| [`.ai/REVIEW_CHECKLIST.md`](.ai/REVIEW_CHECKLIST.md) | PR quality gates                   |
| [`.ai/ARCHITECTURE.md`](.ai/ARCHITECTURE.md)         | System layout                      |
| [`.ai/PROMPT_LIBRARY.md`](.ai/PROMPT_LIBRARY.md)     | Reusable AI prompts                |

## Quick rules

- Never skip phases · Never duplicate code · ₹0 cost only
- Duplicate code must stay **< 3%** (`npm run quality:duplicates`)
- Full pipeline: `npm run quality && npm test`

Human phase specs: [`docs/phases/README.md`](docs/phases/README.md) · [Project tracker](docs/PROJECT-TRACKER.md) · [Wiki](https://github.com/buhahemal/ai-job-hunting/wiki)
