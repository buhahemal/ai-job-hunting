# AI Job Hunter

Monorepo for a GitHub-hosted job hunting dashboard: React on GitHub Pages, Python scraper on GitHub Actions, and Supabase for live data (JSON fallback when secrets are not configured).

## Repository layout

```text
.ai/             AI operating system — start here for agents
apps/
  dashboard/     React + Vite → GitHub Pages
  api/           Local Flask API + data/data.json (dev / fallback)
packages/
  config/        Shared path configuration (TS + Python)
  database/      Supabase clients (TS + Python)
  scanner_sdk/   Scanner plugin SDK (Python)
scanners/        Per-source plugins (greenhouse, lever, remoteok, …)
scraper/         Scan pipeline orchestration (GitHub Actions)
supabase/        SQL migrations + RLS
docs/            Architecture and phase planning
```

AI agents: read [`.ai/AGENTS.md`](.ai/AGENTS.md) first. Quality pipeline: `npm run quality && npm test`.

## Development phases

Roadmap and completion tracking: [`docs/phases/README.md`](docs/phases/README.md)

|                            Phase | Status  |
| -------------------------------: | ------- |
|        1 Research & Architecture | done    |
| 2 Repository + CI/CD + Standards | done    |
|            3 Database + Supabase | done    |
|          4 Scanner SDK + sources | done    |
|                             5–11 | pending |

## GitHub hosting model

| Component       | Host               | How it runs                                                      |
| --------------- | ------------------ | ---------------------------------------------------------------- |
| Dashboard       | GitHub Pages       | `deploy-pages.yml` builds `apps/dashboard/` on push to `main`    |
| Data            | Supabase (primary) | `scanner-cron.yml` upserts jobs; dashboard reads via anon key    |
| Data (fallback) | GitHub repo        | `data.json` when Supabase secrets are not set                    |
| Scraper         | GitHub Actions     | `scanner-cron.yml` runs daily                                    |
| API             | Local only         | Optional Flask server for full AI scan/tailor during development |

On GitHub Pages with Supabase secrets, the app loads live data from Supabase. Without secrets, it uses bundled `data.json` and `localStorage`.

See [docs/phases/phase-03-database-supabase/SETUP.md](docs/phases/phase-03-database-supabase/SETUP.md) to connect Supabase.

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

Open <http://localhost:5173>

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
