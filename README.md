# 🎯 AI Job Hunter

> **Automated Job Discovery, AI Match Scoring, LaTeX Resume Tailoring, and Application Tracking — Operating at ₹0 Budget.**

[![CI Pipeline](https://github.com/buhahemal/ai-job-hunting/actions/workflows/ci.yml/badge.svg)](https://github.com/buhahemal/ai-job-hunting/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Zero Cost](https://img.shields.io/badge/Operational%20Cost-%E2%82%B90%20/ %240-brightgreen.svg)](#-zero-cost-architecture)
[![Stack](https://img.shields.io/badge/Stack-React%20%7C%20Python%20%7C%20Supabase%20%7C%20GitHub%20Actions-indigo.svg)](#-technology-stack)

---

## 🌟 Overview

**AI Job Hunter** is an open-source, self-hosted, zero-cost job hunting platform designed for engineers, developers, and job seekers. It automates the tedious parts of job hunting—discovering relevant listings across direct company ATS boards, scoring job fit using local Hugging Face embedding models, generating tailored ATS-compliant LaTeX resumes, and tracking applications—all hosted for free using GitHub Pages, GitHub Actions, and Supabase.

---

## 🔥 Key Features

- 🕵️ **Multi-ATS Job Scrapers**: Built-in scraper SDK support for **Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Teamtailor, Workday**, and remote job aggregators (**RemoteOK, We Work Remotely, Arbeitnow**).
- 🧠 **Zero-Cost AI Scoring**: Uses open-source Hugging Face embedding models (`sentence-transformers/all-MiniLM-L6-v2`) to compute semantic match scores, skill overlap, and missing keywords without paying for OpenAI or proprietary APIs.
- 📄 **LaTeX Resume Tailoring**: Maintains a single source-of-truth profile and master LaTeX resume, automatically customizing bullets and keywords for target job descriptions and compiling ATS-friendly PDFs.
- 📊 **Analytics & Job Tracking Dashboard**: High-performance React dashboard featuring Kanban application boards, detailed job fit breakdowns, scan insights, and interview status trackers.
- 💰 **₹0 Operational Cost**: 100% free operation using GitHub Pages (frontend hosting), GitHub Actions (daily scheduled scraper & AI pipeline), and Supabase (free PostgreSQL data layer).

---

## 🏗️ Zero-Cost Architecture

```text
+-----------------------------------------------------------------------+
|                             GITHUB REPO                               |
|                                                                       |
|  +---------------------------+       +-----------------------------+  |
|  |    React + Vite App       |       |  GitHub Actions Cron Jobs   |  |
|  |  Deployed to GitHub Pages |       |  (Python Scrapers + AI SDK) |  |
|  +-------------+-------------+       +--------------+--------------+  |
+----------------|------------------------------------|-----------------+
                 |                                    |
                 v                                    v
+-----------------------------------------------------------------------+
|                          SUPABASE CLOUD (FREE)                        |
|                                                                       |
|   +-------------------+  +--------------------+  +-----------------+  |
|   |  Candidate Profile|  |  Scanned Job Leads |  |  Interviews DB  |  |
|   +-------------------+  +--------------------+  +-----------------+  |
+-----------------------------------------------------------------------+
```

---

## 📁 Repository Layout

```text
.ai/             AI operating system and agent rules
apps/
  dashboard/     React + Vite dashboard (GitHub Pages)
  api/           Local Flask API server (local AI scoring & pdflatex compiling)
packages/
  config/        Shared environment and path configurations (TS + Python)
  database/      Supabase database client, SQL repositories & schemas
  scanner_sdk/   Python SDK for custom job board scrapers
scanners/        ATS plugin scrapers (Greenhouse, Lever, Ashby, Workable, etc.)
scraper/         Automated scan pipeline orchestration & deduplication
supabase/        SQL migrations, table definitions & RLS security policies
scripts/         Database setup, profile syncing, and utility scripts
docs/            Detailed architecture guides and user documentation
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js**: `v20.0.0` or later
- **Python**: `v3.11` or later
- **LaTeX** (Optional, for local PDF compilation): `pdflatex` (TeX Live or MacTeX)

### 1. Installation

Clone the repository and install all Node.js and Python dependencies:

```bash
git clone https://github.com/buhahemal/ai-job-hunting.git
cd ai-job-hunting

# Install Node modules
npm install

# Install Python packages
pip install -r apps/api/requirements.txt -r scraper/requirements.txt
```

### 2. Configure Your Candidate Profile

Copy the starter profile template to create your personal profile:

```bash
cp apps/api/data/profile.example.json apps/api/data/profile.json
```

Open `apps/api/data/profile.json` and customize your target job titles, skills, experience, education, locations, and match settings. Alternatively, you can edit your profile directly from the Dashboard UI (**Profile & Settings** tab).

> 📘 **Detailed Guide:** See [docs/USER_GUIDE.md](docs/USER_GUIDE.md) for full instructions on configuring ATS scrapers, Supabase credentials, and GitHub Actions secrets.

---

## 💻 Running Locally

### Dashboard Only (Static / GitHub Pages Mode)

Runs the frontend dashboard connected to local JSON mock data or Supabase:

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Full Local Stack (Flask API + AI Engine + Resume Tailoring)

To generate tailored resumes, run local embedding AI models, and compile PDFs:

```bash
# Terminal 1: Launch Flask API Backend
npm run dev:api

# Terminal 2: Launch Dashboard connected to Local API Backend
npm run dev:full
```

### Run Job Scrapers Locally

Trigger job discovery scrapers on demand:

```bash
npm run scan
```

---

## ⚙️ Configuration & Secrets

Copy `.env.example` to `.env` for local configuration:

```bash
cp .env.example .env
```

### Key Environment Variables

| Variable                  | Description                                 | Default / Example                  |
| :------------------------ | :------------------------------------------ | :--------------------------------- |
| `SUPABASE_URL`            | Supabase project URL                        | `https://your-project.supabase.co` |
| `SUPABASE_ANON_KEY`       | Supabase public anon key                    | `your-anon-key`                    |
| `SUPABASE_SERVICE_KEY`    | Supabase service role key (CI/scraper)      | `your-service-key`                 |
| `GREENHOUSE_BOARD_TOKENS` | Comma-separated Greenhouse company tokens   | `gitlab,stripe,cloudflare`         |
| `LEVER_COMPANY_SITES`     | Comma-separated Lever company slugs         | `netflix,spotify`                  |
| `ASHBY_JOB_BOARD_SLUGS`   | Comma-separated Ashby company slugs         | `linear,vercel`                    |
| `WORKABLE_ACCOUNT_SLUGS`  | Comma-separated Workable account slugs      | `workable,datadog`                 |
| `SCANNER_MIN_MATCH_SCORE` | Minimum match score (0-100) to promote lead | `75`                               |

---

## 🧪 Testing & Quality Assurance

Maintain high code quality with automated linting, typing, duplicate checks, and unit tests:

```bash
# Run entire quality and test suite
npm run quality && npm test

# Individual commands
npm run lint          # ESLint & Python Ruff check
npm run typecheck     # TypeScript strict verification
npm run format:check  # Prettier formatting check
npm test              # Vitest & Python Pytest suites
```

---

## 📖 Documentation

- 📄 [User Setup & Onboarding Guide](docs/USER_GUIDE.md) — Comprehensive guide to setting up profiles, scrapers, and automation.
- 📐 [Architecture Documentation](docs/architecture/) — Deep dive into system design and security.
- 📋 [Development Phases & Roadmap](docs/PROJECT-TRACKER.md) — Project status and execution phases.
- 🤖 [AI Coding Guidelines](.ai/AGENTS.md) — Guidelines and rules for AI paired coding.

---

## 🤝 Contributing

Contributions are welcome! Whether adding new ATS scraper plugins, improving UI components, or enhancing AI scoring algorithms:

1. Fork the project repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'feat(scanner): add new company plugin'`).
4. Ensure all quality checks pass (`npm run quality && npm test`).
5. Push to the branch and open a Pull Request.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
