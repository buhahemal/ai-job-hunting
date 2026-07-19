# System Architecture — AI Job Hunter

**AI Job Hunter** is designed as a self-hosted, zero-operational-cost platform for discovering, scoring, and tracking job opportunities.

---

## 1. Zero-Cost Operating Model

The system operates 100% free using public open-source infrastructure:

| Component                 | Provider / Host           | Function                                                             |
| :------------------------ | :------------------------ | :------------------------------------------------------------------- |
| **Frontend Dashboard**    | GitHub Pages              | React + Vite static single-page application                          |
| **Data Layer (Primary)**  | Supabase Free Tier        | PostgreSQL database with Row Level Security (RLS)                    |
| **Data Layer (Fallback)** | Local / GitHub Repository | `data.json` local storage when Supabase is unconfigured              |
| **Job Scrapers & AI**     | GitHub Actions            | Daily scheduled workflows running ATS scrapers & AI embedding models |

---

## 2. Core Subsystems

```text
+-------------------------------------------------------------------------+
|                              JOB DISCOVERY                              |
|   ATS Scrapers: Greenhouse, Lever, Ashby, Workable, Workday, etc.       |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                             AI MATCH ENGINE                             |
|   Local Hugging Face Embeddings + Skill Overlap + Role Match Scoring    |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                             SUPABASE DATA STORE                         |
|   Candidate Profile, Scanned Jobs, Job Leads, Interview Tracking        |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                             REACT DASHBOARD                             |
|   Scan Insights, High-Match Job Promotion, Filterable Pipeline          |
+-------------------------------------------------------------------------+
```

### A. Job Scrapers (`scanners/`, `scraper/`)

- Plugin-based SDK for direct ATS company career pages.
- Standardized job extraction (title, company, location, remote type, requirements, canonical role).
- Deduplication by source URL and external job ID.

### B. AI Match & Scoring Engine (`scraper/ai_matcher.py`, `packages/ai_engine/`)

- Uses open-source Hugging Face embedding models (`sentence-transformers/all-MiniLM-L6-v2`).
- Evaluates candidate profile against scanned job listings.
- Produces multi-dimensional scores:
  - **Overall Score** (0–100%)
  - **Skill Match Score** & Missing Skills
  - **Experience & Role Score**
  - **Location & Remote Preference Score**
- Automatically promotes jobs with overall score $\ge$ `minMatchScore` (default 75%) to **Job Leads**.

### C. Candidate Profile & Application Tracking (`apps/dashboard/`)

- Candidate profile imported via JSON or managed directly in Supabase.
- Kanban and table management for application stages: **New**, **Shortlisted**, **Applied**, **Interviewing**, **Offer**, **Rejected**.
- Scheduled interview tracking and scan insight analytics.
