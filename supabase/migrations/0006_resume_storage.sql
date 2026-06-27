-- Phase 7: Supabase Storage bucket for versioned resume PDFs

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES ('resumes', 'resumes', true, 5242880, ARRAY['application/pdf']::text[])
ON CONFLICT (id) DO NOTHING;

DROP POLICY IF EXISTS resumes_storage_select_anon ON storage.objects;
CREATE POLICY resumes_storage_select_anon
  ON storage.objects FOR SELECT TO anon
  USING (bucket_id = 'resumes');

DROP POLICY IF EXISTS resumes_storage_select_authenticated ON storage.objects;
CREATE POLICY resumes_storage_select_authenticated
  ON storage.objects FOR SELECT TO authenticated
  USING (bucket_id = 'resumes');
