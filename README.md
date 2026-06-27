# AI Job Hunter

Monorepo for a GitHub-hosted job hunting dashboard: React frontend on GitHub Pages, Python scraper via GitHub Actions, and a static JSON data store.

## Repository layout

```
frontend/   React + Vite dashboard (GitHub Pages)
backend/    Local Flask API + data/data.json (source of truth for scraped jobs)
scraper/    Scheduled job scan pipeline (GitHub Actions)
docs/       Architecture and phase planning
```

## Development phases

Roadmap and completion tracking: [`docs/phases/README.md`](docs/phases/README.md)

| Phase | Status |
|------:|--------|
| 0 Research & Architecture | done |
| 1 Foundation | in_progress |
| 2–9 | pending |

Mark a phase complete in its folder `STATUS.md` and update the index.

## GitHub hosting model

| Component | Host | How it runs |
|-----------|------|-------------|
| Frontend | GitHub Pages | `deploy-pages.yml` builds `frontend/` on every push to `main` |
| Data | GitHub repo | `backend/data/data.json` updated by the scraper workflow |
| Scraper | GitHub Actions | `scanner-cron.yml` runs daily (and on manual dispatch) |
| Backend API | Local only | Optional Flask server for full AI scan/tailor during development |

On GitHub Pages, the app loads `data/data.json` and stores your edits (profile, statuses, notes) in browser `localStorage`. New jobs arrive when the scraper workflow commits updates.

## Setup

### Frontend (static / GitHub Pages mode)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### Full local stack (Flask backend + AI features)

Terminal 1:

```bash
pip install -r backend/requirements.txt
PYTHONPATH=. python3 backend/server.py
```

Terminal 2:

```bash
cd frontend
VITE_USE_BACKEND=true npm run dev
```

### Run scraper locally

```bash
pip install -r scraper/requirements.txt
PYTHONPATH=. python3 -m scraper
```

### Tests

```bash
PYTHONPATH=. python3 -m unittest discover -s scraper/tests
```

## GitHub configuration

1. **Pages**: Settings → Pages → Source = **GitHub Actions**
2. **Secrets** (optional): Add `GEMINI_API_KEY` for AI scoring in the scraper workflow
3. **Workflows**:
   - `Deploy Frontend to GitHub Pages` — publishes the dashboard
   - `Scanner Cron` — fetches and scores new jobs

## Live URL

After the first successful Pages deploy:

`https://<your-username>.github.io/ai-job-hunting/`
