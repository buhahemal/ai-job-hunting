-- Enriched job metadata and separate match score components for analytics/recalculation.

ALTER TABLE jobs
  ADD COLUMN IF NOT EXISTS employment_type TEXT,
  ADD COLUMN IF NOT EXISTS required_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS preferred_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS extracted_technologies JSONB NOT NULL DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS application_url TEXT,
  ADD COLUMN IF NOT EXISTS source_posted_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS scanned_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS canonical_role TEXT,
  ADD COLUMN IF NOT EXISTS primary_stack TEXT,
  ADD COLUMN IF NOT EXISTS priority TEXT CHECK (priority IN ('High', 'Medium', 'Low')),
  ADD COLUMN IF NOT EXISTS is_duplicate BOOLEAN NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS duplicate_of TEXT REFERENCES jobs (id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS match_scorer TEXT;

CREATE INDEX IF NOT EXISTS idx_jobs_canonical_role ON jobs (canonical_role);
CREATE INDEX IF NOT EXISTS idx_jobs_priority ON jobs (priority);
CREATE INDEX IF NOT EXISTS idx_jobs_primary_stack ON jobs (primary_stack);
CREATE INDEX IF NOT EXISTS idx_jobs_scanned_at ON jobs (scanned_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_jobs_is_duplicate ON jobs (is_duplicate);

CREATE TABLE IF NOT EXISTS job_match_scores (
  job_id TEXT PRIMARY KEY REFERENCES jobs (id) ON DELETE CASCADE,
  overall_score INTEGER NOT NULL,
  skill_match_score INTEGER NOT NULL DEFAULT 0,
  experience_match_score INTEGER NOT NULL DEFAULT 0,
  ats_score INTEGER NOT NULL DEFAULT 0,
  salary_match_score INTEGER NOT NULL DEFAULT 0,
  company_match_score INTEGER NOT NULL DEFAULT 0,
  location_match_score INTEGER NOT NULL DEFAULT 0,
  remote_match_score INTEGER NOT NULL DEFAULT 0,
  confidence_score INTEGER NOT NULL DEFAULT 0,
  matched_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
  missing_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
  missing_keywords JSONB NOT NULL DEFAULT '[]'::jsonb,
  resume_suggestions JSONB NOT NULL DEFAULT '[]'::jsonb,
  match_explanation TEXT,
  scorer TEXT,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_job_match_scores_overall ON job_match_scores (overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_job_match_scores_skill ON job_match_scores (skill_match_score DESC);

ALTER TABLE job_match_scores ENABLE ROW LEVEL SECURITY;
CREATE POLICY job_match_scores_select_anon ON job_match_scores FOR SELECT TO anon USING (true);
