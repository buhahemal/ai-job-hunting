# AI Job Hunter

Monorepo for a GitHub-hosted job hunting dashboard: React dashboard on GitHub Pages, Python scraper via GitHub Actions, and a static JSON data store (migrating to Supabase in Phase 3).

## Repository layout

```text
apps/
  dashboard/     React + Vite → GitHub Pages
  api/           Local Flask API + data/data.json
packages/
  config/        Shared path configuration (TS + Python)
scanners/        Per-source job discovery plugins
scraper/         Scan pipeline orchestration (GitHub Actions)
docs/            Architecture and phase planning
```

## Development phases

Roadmap and completion tracking: [`docs/phases/README.md`](docs/phases/README.md)

|                            Phase | Status  |
| -------------------------------: | ------- |
|        1 Research & Architecture | done    |
| 2 Repository + CI/CD + Standards | done    |
|                             3–11 | pending |

## GitHub hosting model

| Component | Host           | How it runs                                                      |
| --------- | -------------- | ---------------------------------------------------------------- |
| Dashboard | GitHub Pages   | `deploy-pages.yml` builds `apps/dashboard/` on push to `main`    |
| Data      | GitHub repo    | `apps/api/data/data.json` updated by scanner workflow            |
| Scraper   | GitHub Actions | `scanner-cron.yml` runs daily                                    |
| API       | Local only     | Optional Flask server for full AI scan/tailor during development |

On GitHub Pages, the app loads `data/data.json` and stores edits in browser `localStorage`.

## Setup

### Install (root workspace)

```bash
npm install
pip install -r apps/api/requirements.txt -r scraper/requirements.txt
```

### Dashboard (static / GitHub Pages mode)

```bash
npm run dev
```

Open http://localhost:5173

### Full local stack (Flask API + AI features)

Terminal 1:

```bash
npm run dev:api
```

Terminal 2:

```bash
npm run dev:full
```

### Run scraper locally

```bash
npm run scan
```

### Tests & quality

```bash
npm test
npm run lint
npm run format:check
PYTHONPATH=. python3 scripts/scanner_health.py
```

### Git hooks

Husky runs Prettier via lint-staged on commit and validates commit messages with Commitlint.

## GitHub configuration

1. **Pages**: Settings → Pages → Source = **GitHub Actions**
2. **Secrets** (optional): `GEMINI_API_KEY` for AI scoring until Phase 6 (Hugging Face migration)
3. **Workflows**: Deploy Pages, Scanner Cron, CI

## Live URL

`https://<your-username>.github.io/ai-job-hunting/`
