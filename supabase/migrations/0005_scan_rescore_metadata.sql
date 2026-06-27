-- Rescore metadata, promotion type, and skill match confidence on scanned_jobs.

ALTER TABLE scanned_jobs
  ADD COLUMN IF NOT EXISTS rescored_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS profile_hash TEXT,
  ADD COLUMN IF NOT EXISTS promotion_type TEXT,
  ADD COLUMN IF NOT EXISTS skill_match_confidence INTEGER;

CREATE INDEX IF NOT EXISTS idx_scanned_jobs_rescored_at ON scanned_jobs (rescored_at DESC);
