# 🎯 AI Job Hunter

> **Automated Job Discovery, AI Match Scoring, Scan Insights, and Application Tracking — Operating at ₹0 Operational Budget.**

[![CI Pipeline](https://github.com/buhahemal/ai-job-hunting/actions/workflows/ci.yml/badge.svg)](https://github.com/buhahemal/ai-job-hunting/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Zero Cost](https://img.shields.io/badge/Operational%20Cost-%E2%82%B90%20/%20%240-brightgreen.svg)](#zero-cost-architecture)
[![Stack](https://img.shields.io/badge/Stack-React%20%7C%20Python%20%7C%20Supabase%20%7C%20GitHub%20Actions-indigo.svg)](#overview)

---

## 🌟 Overview

**AI Job Hunter** is an open-source, self-hosted, zero-cost job discovery and scoring engine designed for software engineers and job seekers. It automates job search discovery across direct company ATS boards (Greenhouse, Lever, Ashby, Workable, Workday, SmartRecruiters, Teamtailor), computes multi-dimensional match fit using local open-source AI embedding models against your candidate profile, and manages your application pipeline—all operating for free via GitHub Pages, GitHub Actions, and Supabase.

---

## 🔥 Key Features

- 🕵️ **Multi-ATS Job Scrapers**: Built-in plugin SDK support for **Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Teamtailor, Workday**, and remote job aggregators (**RemoteOK, We Work Remotely**).
- 🧠 **Zero-Cost AI Matching**: Uses open-source Hugging Face embedding models (`sentence-transformers/all-MiniLM-L6-v2`) to compute semantic match scores, skill overlap, and missing keywords without paying for OpenAI or proprietary APIs.
- 🎯 **Automated Job Lead Promotion**: Automatically filters scan insights and promotes jobs meeting your candidate match threshold (default $\ge 75\%$) into **Job Leads**.
- 📊 **Analytics & Application Tracking**: High-performance React dashboard featuring application stage tracking (New, Shortlisted, Applied, Interviewing, Offer, Rejected), interview scheduling, and skill frequency analytics.
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
apps/
  dashboard/     React + Vite dashboard (GitHub Pages)
  api/           Flask local API server (profile import & rescan API)
packages/
  config/        Shared environment and path configurations (TS + Python)
  database/      Supabase database client, SQL repositories & schemas
  scanner_sdk/   Python SDK for custom job board scrapers
  ai_engine/     Hugging Face embedding scoring & skill matchers
scanners/        ATS plugin scrapers (Greenhouse, Lever, Ashby, Workable, etc.)
scraper/         Automated scan pipeline orchestration & deduplication
supabase/        SQL migrations, table definitions & RLS security policies
scripts/         Database setup, profile syncing, and utility scripts
docs/            Architecture, setup, and development guides
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js**: `v20.0.0` or later
- **Python**: `v3.11` or later

### 1. Installation

```bash
git clone https://github.com/buhahemal/ai-job-hunting.git
cd ai-job-hunting

# Install Node modules and Python packages
npm install
pip install -r apps/api/requirements.txt -r scraper/requirements.txt
```

### 2. Configure Candidate Profile

```bash
cp apps/api/data/profile.example.json apps/api/data/profile.json
```

Edit `apps/api/data/profile.json` with your target job titles, technical skills, preferred locations, and match settings. Alternatively, manage your profile JSON directly from the Dashboard UI (**Profile & Settings** tab).

---

## 📖 Documentation Structure

Documentation is organized into three dedicated sections under `docs/`:

- 🏗️ **[Architecture Overview](docs/architecture/overview.md)** — System architecture, ₹0 cost model, data flow, and match engine design.
- ⚙️ **[Quick Start & Setup Guide](docs/setup/quickstart.md)** — Comprehensive setup guide covering profile setup, Supabase database, ATS tokens, and GitHub deployment.
- 💻 **[Development & Contribution Guide](docs/development/guide.md)** — Monorepo guide, adding custom ATS scanner plugins, and quality assurance workflows.

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
npm test              # Pytest & Vitest test suites
```

---

## 🤝 Contributing

Contributions are welcome! See [docs/development/guide.md](docs/development/guide.md) for guidelines on creating new ATS scanner plugins and submitting PRs.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
