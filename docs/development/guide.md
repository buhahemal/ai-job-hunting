# Development & Contribution Guide — AI Job Hunter

This guide outlines code conventions, repository structure, and quality verification workflows.

---

## 1. Repository Structure

```text
apps/
  dashboard/     React + Vite dashboard (GitHub Pages)
  api/           Flask local API server & profile management
packages/
  config/        Shared environment and path utilities
  database/      Supabase SQL schemas, client & repository handlers
  scanner_sdk/   Python SDK contract for ATS scrapers
  ai_engine/     Hugging Face embedding scoring & skill matchers
scanners/        Per-source ATS scanner plugins (Greenhouse, Lever, Ashby, etc.)
scraper/         Scan pipeline orchestrator, deduplication & rescan engine
supabase/        SQL migrations and RLS security policies
scripts/         Database setup, profile syncing, and utility scripts
docs/            Architecture, setup, and development documentation
```

---

## 2. Quality Pipeline & Testing

Every commit and pull request must pass the automated quality check pipeline:

```bash
# Run full quality check & unit tests
npm run quality && npm test
```

### Individual Quality Commands

| Command                      | Tool             | Purpose                               |
| :--------------------------- | :--------------- | :------------------------------------ |
| `npm run lint`               | ESLint + Ruff    | Code style & naming enforcement       |
| `npm run typecheck`          | TypeScript `tsc` | Strict type validation                |
| `npm run format:check`       | Prettier         | Code formatting validation            |
| `npm run quality:duplicates` | `jscpd`          | Duplicate code check (< 3% threshold) |
| `npm run arch:madge`         | Madge            | Circular dependency validation        |
| `npm run spellcheck`         | CSpell           | Documentation & code spellcheck       |
| `npm test`                   | Pytest + Vitest  | Python & React test suites            |

---

## 3. Adding a New ATS Scanner Plugin

1. Create a new plugin folder under `scanners/<plugin_name>/`.
2. Implement the `BaseScanner` contract from `packages/scanner_sdk/python/base.py`.
3. Export the class in `scanners/__init__.py`.
4. Add unit tests under `scanners/<plugin_name>/tests/`.
5. Run `npm test` to verify integration.
