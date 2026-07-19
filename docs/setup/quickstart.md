# Quick Start & Setup Guide — AI Job Hunter

Follow this step-by-step guide to configure **AI Job Hunter** for your job search.

---

## 1. Local Prerequisites

- **Node.js**: `v20.0.0` or higher
- **Python**: `v3.11` or higher

```bash
# Clone the repository
git clone https://github.com/buhahemal/ai-job-hunting.git
cd ai-job-hunting

# Install dependencies
npm install
pip install -r apps/api/requirements.txt -r scraper/requirements.txt
```

---

## 2. Configure Your Candidate Profile

Copy the starter profile template:

```bash
cp apps/api/data/profile.example.json apps/api/data/profile.json
```

Edit `apps/api/data/profile.json` with your candidate details:

- `targetRoles`: Desired job titles (e.g. `["Backend Engineer", "Platform Engineer"]`)
- `skills`: Technical skills (e.g. `["Node.js", "TypeScript", "AWS", "PostgreSQL"]`)
- `preferences`: Preferred locations, remote preferences, target companies, keyword priorities
- `matchSettings.minMatchScore`: Minimum score threshold to promote scan insights to Job Leads (default: `75`)

_Note: You can also update and import/export your profile JSON anytime directly in the Dashboard UI (**Profile & Settings**)._

---

## 3. Supabase Cloud Database Setup

1. Create a free project at [supabase.com](https://supabase.com).
2. Get your Project URL, Anon Key, and Service Role Key from **Settings → API**.
3. Create a `.env` file from the template:

```bash
cp .env.example .env
```

Set `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_KEY` in `.env`.

1. Apply database schema migrations:

```bash
bash scripts/apply_migrations.sh
```

1. Seed your candidate profile to Supabase:

```bash
python3 scripts/sync_profile_to_supabase.py
```

---

## 4. ATS Board Tokens Configuration

Configure your target companies in `.env` (for local runs) or in GitHub Secrets (for GitHub Actions):

```env
GREENHOUSE_BOARD_TOKENS=gitlab,stripe,cloudflare
LEVER_COMPANY_SITES=netflix,spotify,figma
ASHBY_JOB_BOARD_SLUGS=linear,notion,vercel
WORKABLE_ACCOUNT_SLUGS=workable,datadog
SMARTRECRUITERS_COMPANIES=square,visa
```

---

## 5. GitHub Actions & GitHub Pages Deployment

1. Go to repository **Settings → Pages** and set **Source** to **GitHub Actions**.
2. Go to **Settings → Secrets and variables → Actions** and add your Supabase credentials and ATS tokens.
3. Trigger the **Daily Scanner Pipeline** manually from the **Actions** tab.

Your dashboard will be published automatically at `https://<your-username>.github.io/ai-job-hunting/`.

---

## 6. Running Locally

### Development Dashboard

```bash
npm run dev
```

### Run Job Scrapers & AI Match Engine Locally

```bash
npm run scan
```
