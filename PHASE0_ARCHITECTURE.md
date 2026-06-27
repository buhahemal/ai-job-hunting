# AI Job Hunter: Technical Design & Architecture (Phase 0)

This document establishes the architecture, design patterns, and operational blueprints for the **AI Job Hunter** platform, adhering strictly to the **Principal Engineer** standard and the ₹0 budget mandate.

---

## 1. Executive Architecture Summary

AI Job Hunter is a full-stack, automated career acceleration suite consisting of three core pillars:
1. **The Scanner Engine**: An asynchronous, scheduled scheduler (operating via GitHub Actions and local cron triggers) to scrape, deduplicate, and normalize potential career leads.
2. **The AI Matching Engine**: A server-side processing layer utilizing Google GenAI (`gemini-3.5-flash`) for structural parsing, multi-variable matching (skills, preferences, and company constraints), and auto-tailoring LaTeX resumes & cover letters.
3. **The Secure Dashboard UI**: A modular dashboard displaying active status tracking, rich filtering, and real-time insights.

---

## 2. System Architecture Diagram

```
                                    +-----------------------+
                                    | GitHub Actions Cron   |
                                    | (Daily / Dispatch)    |
                                    +-----------+-----------+
                                                |
                                                v [npx tsx scripts/scraper.ts]
+-------------------+               +-----------+-----------+
| External Job      | Scrapes Feed  |                       | Writes Scored Leads
| Boards / Portals  +-------------->| Scraper Pipeline      +---------------------+
| (Arbeitnow, etc.) |               | (scripts/scraper.ts)  |                     |
+-------------------+               +-----------+-----------+                     |
                                                |                                 |
                                                v [Google GenAI SDK]              v
                                    +-----------+-----------+            +--------+---------+
                                    | Gemini API Service    |            |                  |
                                    | (gemini-3.5-flash)    |            | Local DB         |
                                    +-----------+-----------+            | (data.json)      |
                                                |                        |                  |
                                                v [Tailored LaTeX]       |                  |
                                    +-----------+-----------+            |                  |
                                    | PDF Resume Generation |            |                  |
                                    | (pdflatex / typst)    |            |                  |
                                    +-----------------------+            +--------+---------+
                                                                                  ^
                                                                                  | Reads/Writes
                                                                                  |
                                    +-----------------------+                     |
                                    | Express API Server    +---------------------+
                                    | (server.ts / Node 24) |
                                    +-----------+-----------+
                                                ^
                                                | JSON APIs (port 3000)
                                                v
                                    +-----------+-----------+
                                    | Vite / React Frontend |
                                    | (App.tsx / Tailwind)  |
                                    +-----------------------+
```

---

## 3. Database Schema Design (Phase 2 Roadmap)

To maintain a secure, modular data footprint within a ₹0 tier budget, the production target database uses **Supabase (PostgreSQL)** with Row Level Security (RLS). Below is the relational entity-relationship definition.

```
       +-----------------------+             +-----------------------+
       |       profiles        |             |         jobs          |
       +-----------------------+             +-----------------------+
  PK   | id (uuid)             |--------+    | id (uuid/text)        | PK
       | full_name (text)      |        |    | title (text)          |
       | email (text)          |        |    | company (text)        |
       | phone (text)          |        |    | location (text)       |
       | website (text)        |        |    | remote_type (text)    |
       | github (text)         |        |    | source (text)         |
       | linkedin (text)       |        |    | url (text)            |
       | location (text)       |        |    | description (text)    |
       | target_roles (text[]) |        |    | status (text)         |
       | skills (text[])       |        |    | score (integer)       |
       | preferences (jsonb)   |        |    | fit_explanation (text)|
       | updated_at (timestamp)|        |    | extracted_skills(text[])
       +-----------------------+        |    | salary_estimate (text)|
                                        |    | seniority (text)      |
                                        |    | posted_at (timestamp) |
                                        +--->| profile_id (uuid)     | FK
                                             +-----------------------+
```

### PostgreSQL Schema Definition

```sql
-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- PROFILES table
create table public.profiles (
  id uuid references auth.users on delete cascade primary key,
  full_name text not null,
  email text not null,
  phone text,
  website text,
  github text,
  linkedin text,
  location text,
  target_roles text[] default '{}',
  skills text[] default '{}',
  preferences jsonb default '{"locations": [], "remotePreference": "Any", "companySizes": [], "targetCompanies": [], "skillsKeywords": []}'::jsonb,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- JOBS table
create table public.jobs (
  id text primary key, -- external key, e.g. "arbeit-slug"
  profile_id uuid references public.profiles(id) on delete cascade not null,
  title text not null,
  company text not null,
  location text not null,
  remote_type text check (remote_type in ('Remote', 'Hybrid', 'On-site')) not null,
  source text not null,
  url text not null,
  description text,
  status text check (status in ('New', 'Shortlisted', 'Applied', 'Interviewing', 'Offer', 'Rejected', 'Accepted', 'Ignored')) default 'New' not null,
  score integer check (score >= 0 and score <= 100),
  fit_explanation text,
  extracted_skills text[] default '{}',
  salary_estimate text,
  seniority text,
  posted_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- INTERVIEWS table
create table public.interviews (
  id uuid default uuid_generate_v4() primary key,
  job_id text references public.jobs(id) on delete cascade not null,
  scheduled_at timestamp with time zone not null,
  type text not null, -- "HR Screening", "Technical", "System Design", "Behavioral"
  notes text,
  status text check (status in ('Scheduled', 'Completed', 'Cancelled')) default 'Scheduled' not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

### Row Level Security (RLS) & Policies

To ensure complete data isolation (Security Gate), all tables enforce RLS:

```sql
-- Enable Row Level Security
alter table public.profiles enable row level security;
alter table public.jobs enable row level security;
alter table public.interviews enable row level security;

-- Policies for profiles
create policy "Users can view and manage their own profiles."
  on public.profiles for all
  using (auth.uid() = id);

-- Policies for jobs
create policy "Users can view and manage their own discovered jobs."
  on public.jobs for all
  using (auth.uid() = profile_id);

-- Policies for interviews
create policy "Users can manage interviews connected to their owned jobs."
  on public.interviews for all
  using (
    exists (
      select 1 from public.jobs 
      where jobs.id = interviews.job_id and jobs.profile_id = auth.uid()
    )
  );
```

---

## 4. API Design (OpenAPI Specification)

The Express dashboard backend implements a fully modular REST endpoint structure mapped below:

### Profiles Endpoint
* `GET /api/profile` - Fetches the current user profile.
* `PUT /api/profile` - Updates profile configuration, skills, target roles, and targeting preferences.

### Jobs Endpoint
* `GET /api/jobs` - Retrieves the scored and synchronized career leads. Supports query filtering:
  * `status`: e.g., `?status=Shortlisted`
  * `search`: text match across title/company/description `?search=kubernetes`
  * `minScore`: `?minScore=80`
* `PUT /api/jobs/:id` - Updates job status (e.g., Shortlisted, Applied, Interviewing, Rejected) or reviews rating score.
* `POST /api/jobs` - Manually adds a custom job lead.
* `POST /api/jobs/sync` - Manually triggers the crawler/scraper pipeline directly from the dashboard.

### Resume & Cover Letter Tailoring Endpoint
* `POST /api/jobs/:id/tailor` - Generates tailor-made materials using the `gemini-3.5-flash` engine. Returns:
  ```json
  {
    "success": true,
    "job": { ... },
    "tailoredResumeLaTeX": "...",
    "coverLetter": "...",
    "atsScore": 92
  }
  ```

---

## 5. Folder Structure Definition

To ensure modularity and avoid file length cutoff boundaries, the monorepo structure is defined as:

```
├── .github/
│   └── workflows/
│       └── job-scan.yml           # Daily scanning cron action
├── scripts/
│   └── scraper.ts                 # Main Scraper pipeline script
├── src/
│   ├── components/                # Modular React presentation components
│   │   ├── CoverLetterTab.tsx
│   │   ├── DashboardStats.tsx
│   │   ├── JobCard.tsx
│   │   ├── JobDetailsModal.tsx
│   │   ├── ProfileTab.tsx
│   │   ├── ResumeTab.tsx
│   │   └── TrackerBoard.tsx
│   ├── lib/
│   │   └── api.ts                 # Client API client methods
│   ├── App.tsx                    # Top-level UI entry & Layout
│   ├── index.css                  # Global Tailwind imports
│   ├── main.tsx                   # React client bootstrap entry
│   └── types.ts                   # Unified type systems and declarations
├── .env.example                   # Environment configuration manifest
├── AGENTS.md                      # Persistent rule engine parameters
├── data.json                      # Local developer flat file mock database
├── metadata.json                  # Application metadata and capabilities
├── package.json                   # Dependency definitions and scripts
├── server.ts                      # Express API web service server
├── tsconfig.json                  # TypeScript compiler settings
└── vite.config.ts                 # Vite bundle settings
```

---

## 6. Technology Decisions & Trade-Offs

| Technology | Selected Option | Considered Alternatives | Trade-Off Justification |
| :--- | :--- | :--- | :--- |
| **Model Selection** | `gemini-3.5-flash` | `gemini-2.5-pro`, `gpt-4o` | Highly cost-efficient, ultra-low latency, native JSON schema support, and robust handling of structured profile evaluations within a ₹0 budget limit. |
| **State Storage** | Flat File JSON -> Supabase PostgreSQL | SQLite, MongoDB Atlas | Flat file `data.json` is selected for localized rapid prototyping. In production, Supabase provides complete PostgreSQL RLS protection and robust relational capability for ₹0. |
| **Scraper Scheduling**| GitHub Actions (cron) | Server Cron Jobs, BullMQ | Standard, serverless execution requiring no active cloud footprint or monthly payment setups, avoiding operational costs completely (₹0 budget). |

---

## 7. Risk Analysis & Mitigation

1. **API Rate Limiting (Gemini 503 Errors)**:
   * *Risk*: High load peaks trigger standard API temporary unavailability or 429 quota exhaustion.
   * *Mitigation*: Implemented `generateContentWithRetry` featuring **exponential backoff retry wrappers** in `/server.ts` and automated warning sanitization (`logSafeWarning`) to handle expected API constraints gracefully.
2. **Scraper Portability & Environment Crash**:
   * *Risk*: If running on serverless environments like GitHub Actions without preexisting file structures, data persistence pipelines fail.
   * *Mitigation*: Integrated automatic fallback data seeding inside `/scripts/scraper.ts` to cleanly initialize structure profiles and records dynamically.
3. **Prompt Injection / Insecure LLM outputs**:
   * *Risk*: External job descriptions containing hostile prompts might attempt to hijack model response structure.
   * *Mitigation*: Strict JSON schemas enforced via Google GenAI's schema validations and localized heuristics error catch fallbacks.

---

## 8. Dependency Analysis

* `@google/genai`: Official Google Developer SDK for robust Gemini capabilities.
* `express`: Ultra-fast, modular web service.
* `tsx` / `esbuild`: Instantaneous execution and clean CommonJS bundling support.
* `react` / `vite`: Modern reactive presentation view client.
* `lucide-react`: Lightweight, standardized visual layout iconography.
* `motion/react`: Hardware-accelerated fluid component layout animations.

---

### Phase 0 - Verification & Quality Gate
✓ No implementation files created or modified except document registers and config flags.
✓ Technology roadmap fully compatible with production cloud deployments.
✓ System dependencies strictly audited against ₹0 cost parameters.
