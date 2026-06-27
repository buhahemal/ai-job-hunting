-- Track jobs already evaluated by the scanner (including sub-threshold rejects).

CREATE TABLE IF NOT EXISTS scanned_jobs (
  dedupe_key TEXT PRIMARY KEY,
  job_id TEXT,
  source TEXT,
  score INTEGER,
  scanned_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_scanned_jobs_scanned_at ON scanned_jobs (scanned_at DESC);

ALTER TABLE scanned_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY scanned_jobs_select_anon ON scanned_jobs FOR SELECT TO anon USING (true);
