# User Setup & Configuration Guide — AI Job Hunter

This guide provides step-by-step instructions for configuring **AI Job Hunter** for your personal job search.

---

## Table of Contents

1. [Candidate Profile & Resume Setup](#1-candidate-profile--resume-setup)
2. [ATS Scrapers Configuration](#2-ats-scrapers-configuration)
3. [Supabase Database Setup](#3-supabase-database-setup)
4. [GitHub Actions & GitHub Pages Setup](#4-github-actions--github-pages-setup)
5. [Local AI & Resume Tailoring Engine](#5-local-ai--resume-tailoring-engine)
6. [Daily Workflow & Application Tracking](#6-daily-workflow--application-tracking)

---

## 1. Candidate Profile & Resume Setup

Your candidate profile is the single source of truth for job matching, embedding scoring, gap analysis, and resume tailoring.

### Option A: Using the Dashboard UI (Recommended)

1. Launch the dashboard (`npm run dev`).
2. Navigate to **Profile & Settings**.
3. Fill in your personal information, target roles, skills, experience, and match preferences.
4. Click **Save Profile** to update your database and auto-regenerate your master LaTeX resume.
5. Alternatively, click **Import Profile JSON** and select `apps/api/data/profile.example.json` (or your custom JSON file).

### Option B: Pre-configuring `profile.json`

Before seeding Supabase or running local scans, you can copy the starter template and edit your details:

```bash
cp apps/api/data/profile.example.json apps/api/data/profile.json
```

#### Profile Fields Explanation

| Field                          | Description                                                                           | Used By                            |
| :----------------------------- | :------------------------------------------------------------------------------------ | :--------------------------------- |
| `targetRoles`                  | Array of desired job titles (e.g. `["Senior Backend Engineer", "Platform Engineer"]`) | Experience & Role match scoring    |
| `skills`                       | Core technical skills (e.g. `["Node.js", "TypeScript", "AWS", "Docker"]`)             | Skill match scoring & gap analysis |
| `preferences.locations`        | Target job locations (e.g. `["Remote", "San Francisco, CA"]`)                         | Location filtering & match score   |
| `preferences.remotePreference` | `'Remote'`, `'Hybrid'`, `'On-site'`, or `'Any'`                                       | Remote match filter                |
| `preferences.targetCompanies`  | List of priority companies                                                            | Company match boost                |
| `preferences.skillsKeywords`   | High-priority skill keywords for matching                                             | Keywords sub-score                 |
| `matchSettings.minMatchScore`  | Minimum score (0–100) to promote a scan insight to Job Leads (default: `75`)          | Automated promotion filter         |
| `masterResumeLaTeX`            | Full LaTeX resume template code                                                       | Resume tailoring engine            |

---

## 2. ATS Scrapers Configuration

AI Job Hunter automatically scans direct company ATS job boards and remote boards without paid APIs.

### Configuring Target Companies

Environment variables (in `.env` for local runs, or GitHub Repo Secrets for GitHub Actions):

```env
# Greenhouse tokens (from boards.greenhouse.io/{board_token})
GREENHOUSE_BOARD_TOKENS=gitlab,stripe,cloudflare

# Lever company slugs (from jobs.lever.co/{slug})
LEVER_COMPANY_SITES=netflix,spotify,figma

# Ashby job board slugs (from jobs.ashbyhq.com/{slug})
ASHBY_JOB_BOARD_SLUGS=linear,notion,vercel

# Workable account slugs (from apply.workable.com/{account})
WORKABLE_ACCOUNT_SLUGS=workable,datadog

# SmartRecruiters company identifiers
SMARTRECRUITERS_COMPANIES=square,visa

# Teamtailor subdomain slugs ({slug}.teamtailor.com)
TEAMTAILOR_COMPANY_SLUGS=klarna,spotify

# Workday career sites (tenant:wd5:SiteName or full URL)
WORKDAY_CAREER_SITES=myworkdayjobs.com/company
```

_Note: Public remote job sources (RemoteOK, We Work Remotely, Arbeitnow) run automatically without any required credentials._

---

## 3. Supabase Database Setup

Supabase provides the free-tier PostgreSQL database backing the dashboard and scrapers.

### Step 1: Create a Free Supabase Project

1. Sign up at [supabase.com](https://supabase.com).
2. Create a new project named `ai-job-hunter`.
3. Obtain your Project URL, Anon Key, and Service Role Key from **Project Settings → API**.

### Step 2: Run Database Migrations

Apply the initial schema and Row Level Security (RLS) policies using the migration script:

```bash
# Set environment variables in .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# Apply migrations
bash scripts/apply_migrations.sh
```

### Step 3: Seed Profile to Supabase

Run the profile seed script to populate your profile in Supabase:

```bash
python3 scripts/sync_profile_to_supabase.py
```

---

## 4. GitHub Actions & GitHub Pages Setup

Run the scraper on a daily schedule for free on GitHub Actions, and host your personal job dashboard on GitHub Pages.

### Step 1: Enable GitHub Pages

1. Go to your GitHub Repository **Settings → Pages**.
2. Set **Source** to **GitHub Actions**.

### Step 2: Configure Repository Secrets

Navigate to **Settings → Secrets and variables → Actions** and add:

| Secret Name               | Description                                     |
| :------------------------ | :---------------------------------------------- |
| `SUPABASE_URL`            | Your Supabase Project URL                       |
| `SUPABASE_SERVICE_KEY`    | Your Supabase Service Role Key                  |
| `SUPABASE_ANON_KEY`       | Your Supabase Anon Key (for frontend live data) |
| `GREENHOUSE_BOARD_TOKENS` | Comma-separated Greenhouse board tokens         |
| `LEVER_COMPANY_SITES`     | Comma-separated Lever company slugs             |
| `ASHBY_JOB_BOARD_SLUGS`   | Comma-separated Ashby board slugs               |
| `WORKABLE_ACCOUNT_SLUGS`  | Comma-separated Workable account slugs          |

### Step 3: Trigger Initial Scanner Workflow

1. Go to the **Actions** tab in your repository.
2. Select **Daily Scanner Pipeline**.
3. Click **Run workflow**.

Once complete, your site will be live at `https://<your-username>.github.io/ai-job-hunting/`.

---

## 5. Local AI & Resume Tailoring Engine

While the frontend dashboard runs on GitHub Pages, full AI feature generation (Hugging Face embeddings, local rescoring, and LaTeX PDF compilation) can be run locally via the Flask API backend.

### Prerequisites for Resume PDF Generation

- Install `pdflatex` (TeX Live or MacTeX) if compiling PDFs locally:
  - macOS: `brew install --cask mactex-no-gui`
  - Linux: `sudo apt-get install texlive-latex-base texlive-latex-extra`

### Running the Full Local Stack

```bash
# Install dependencies
npm install
pip install -r apps/api/requirements.txt -r scraper/requirements.txt

# Terminal 1: Launch Flask API Server
npm run dev:api

# Terminal 2: Launch Vite Dashboard connected to Local API
npm run dev:full
```

Open `http://localhost:5173`. You can now:

- Run instant AI scoring against newly scanned jobs.
- Click **Tailor Resume** on any job lead to generate ATS-optimized LaTeX resumes.
- Download compiled PDF resumes directly from the browser.

---

## 6. Daily Workflow & Application Tracking

1. **Daily Scan**: GitHub Actions runs `pipeline-cron.yml` every 24 hours to scan configured ATS job boards.
2. **Review Scan Insights**: View high-scoring matches in the **Scan Insights** tab.
3. **Manage Job Leads**: Jobs with score $\ge$ `minMatchScore` (default 75) are automatically promoted to **Job Leads**.
4. **Tailor & Apply**: Open job lead details, view missing keywords, tailor your resume, click **Apply**, and mark status as **Applied**.
5. **Interview Tracking**: Track interview stages (Scheduled, Completed, Passed) in the **Interview Tracker** tab.
