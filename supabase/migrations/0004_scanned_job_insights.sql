-- Expand scanned_jobs into a full Scan Insights layer (summary + match outcome per evaluated job).

ALTER TABLE scanned_jobs
  ADD COLUMN IF NOT EXISTS title TEXT,
  ADD COLUMN IF NOT EXISTS company TEXT,
  ADD COLUMN IF NOT EXISTS location TEXT,
  ADD COLUMN IF NOT EXISTS remote_type TEXT,
  ADD COLUMN IF NOT EXISTS canonical_role TEXT,
  ADD COLUMN IF NOT EXISTS primary_stack TEXT,
  ADD COLUMN IF NOT EXISTS seniority TEXT,
  ADD COLUMN IF NOT EXISTS employment_type TEXT,
  ADD COLUMN IF NOT EXISTS application_url TEXT,
  ADD COLUMN IF NOT EXISTS required_skills JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS preferred_skills JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS extracted_technologies JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS overall_score INTEGER,
  ADD COLUMN IF NOT EXISTS skill_match_score INTEGER,
  ADD COLUMN IF NOT EXISTS experience_match_score INTEGER,
  ADD COLUMN IF NOT EXISTS ats_score INTEGER,
  ADD COLUMN IF NOT EXISTS matched_skills JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS missing_skills JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS missing_keywords JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS match_explanation TEXT,
  ADD COLUMN IF NOT EXISTS scorer TEXT,
  ADD COLUMN IF NOT EXISTS promoted_to_jobs BOOLEAN NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS scan_run_id TEXT;

-- Backfill overall_score from legacy score column when present.
UPDATE scanned_jobs
SET overall_score = score
WHERE overall_score IS NULL AND score IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_scanned_jobs_overall_score ON scanned_jobs (overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_scanned_jobs_canonical_role ON scanned_jobs (canonical_role);
CREATE INDEX IF NOT EXISTS idx_scanned_jobs_source ON scanned_jobs (source);
CREATE INDEX IF NOT EXISTS idx_scanned_jobs_promoted ON scanned_jobs (promoted_to_jobs);
CREATE INDEX IF NOT EXISTS idx_scanned_jobs_scan_run_id ON scanned_jobs (scan_run_id);
