-- Optional seed for local `supabase db reset`
-- Default profile JSON is merged at runtime from apps/api/defaults.py

INSERT INTO profiles (id, data)
VALUES ('default', '{}'::jsonb)
ON CONFLICT (id) DO NOTHING;
