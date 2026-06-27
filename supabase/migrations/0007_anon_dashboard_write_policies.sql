-- Allow GitHub Pages dashboard (anon key) to promote scanned jobs into Job Leads.
-- Service role (GitHub Actions / API) bypasses RLS; anon needs explicit write policies.

DROP POLICY IF EXISTS job_match_scores_insert_anon ON job_match_scores;
CREATE POLICY job_match_scores_insert_anon
  ON job_match_scores FOR INSERT TO anon
  WITH CHECK (true);

DROP POLICY IF EXISTS job_match_scores_update_anon ON job_match_scores;
CREATE POLICY job_match_scores_update_anon
  ON job_match_scores FOR UPDATE TO anon
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS scanned_jobs_update_anon ON scanned_jobs;
CREATE POLICY scanned_jobs_update_anon
  ON scanned_jobs FOR UPDATE TO anon
  USING (true)
  WITH CHECK (true);
