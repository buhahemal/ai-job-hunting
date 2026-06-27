-- Phase 3: AI Job Hunter schema
-- Apply via: supabase db push  OR  Supabase SQL Editor

-- ---------------------------------------------------------------------------
-- Tables
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS profiles (
  id TEXT PRIMARY KEY DEFAULT 'default',
  data JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  external_id TEXT NOT NULL,
  title TEXT NOT NULL,
  company TEXT NOT NULL,
  location TEXT,
  remote_type TEXT NOT NULL DEFAULT 'Remote',
  url TEXT,
  description TEXT,
  posted_at TIMESTAMPTZ,
  status TEXT NOT NULL DEFAULT 'New',
  score INTEGER,
  fit_explanation TEXT,
  extracted_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
  salary_estimate TEXT,
  seniority TEXT,
  notes TEXT,
  tailored_resume_latex TEXT,
  tailored_cover_letter TEXT,
  ats_score DOUBLE PRECISION,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT jobs_source_external_id_unique UNIQUE (source, external_id)
);

CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs (score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs (status);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_at ON jobs (posted_at DESC NULLS LAST);

CREATE TABLE IF NOT EXISTS interviews (
  id TEXT PRIMARY KEY,
  job_id TEXT NOT NULL REFERENCES jobs (id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  company TEXT NOT NULL,
  interview_date TIMESTAMPTZ NOT NULL,
  interview_type TEXT NOT NULL,
  notes TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'Scheduled',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_interviews_job_id ON interviews (job_id);

CREATE TABLE IF NOT EXISTS applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id TEXT NOT NULL REFERENCES jobs (id) ON DELETE CASCADE,
  applied_at TIMESTAMPTZ DEFAULT now(),
  result TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications (job_id);

CREATE TABLE IF NOT EXISTS companies (
  name TEXT PRIMARY KEY,
  career_url TEXT,
  last_scan TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS resumes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id TEXT REFERENCES jobs (id) ON DELETE CASCADE,
  version TEXT NOT NULL DEFAULT 'master',
  content JSONB,
  pdf_url TEXT,
  ats_score DOUBLE PRECISION,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_resumes_job_id ON resumes (job_id);

-- ---------------------------------------------------------------------------
-- Row Level Security (anon key = GitHub Pages dashboard)
-- Service role (GitHub Actions) bypasses RLS automatically.
-- ---------------------------------------------------------------------------

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;

-- Profiles
CREATE POLICY profiles_select_anon ON profiles FOR SELECT TO anon USING (true);
CREATE POLICY profiles_insert_anon ON profiles FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY profiles_update_anon ON profiles FOR UPDATE TO anon USING (true) WITH CHECK (true);

-- Jobs: anon can read/update/insert (personal dashboard; auth added Phase 8)
CREATE POLICY jobs_select_anon ON jobs FOR SELECT TO anon USING (true);
CREATE POLICY jobs_insert_anon ON jobs FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY jobs_update_anon ON jobs FOR UPDATE TO anon USING (true) WITH CHECK (true);

-- Interviews
CREATE POLICY interviews_select_anon ON interviews FOR SELECT TO anon USING (true);
CREATE POLICY interviews_insert_anon ON interviews FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY interviews_update_anon ON interviews FOR UPDATE TO anon USING (true) WITH CHECK (true);

-- Applications
CREATE POLICY applications_select_anon ON applications FOR SELECT TO anon USING (true);
CREATE POLICY applications_insert_anon ON applications FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY applications_update_anon ON applications FOR UPDATE TO anon USING (true) WITH CHECK (true);

-- Companies (read-only from dashboard)
CREATE POLICY companies_select_anon ON companies FOR SELECT TO anon USING (true);

-- Resumes (Phase 7)
CREATE POLICY resumes_select_anon ON resumes FOR SELECT TO anon USING (true);

-- ---------------------------------------------------------------------------
-- Seed default profile row
-- ---------------------------------------------------------------------------

INSERT INTO profiles (id, data)
VALUES ('default', '{}'::jsonb)
ON CONFLICT (id) DO NOTHING;
