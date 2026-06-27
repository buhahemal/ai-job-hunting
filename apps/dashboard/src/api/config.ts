export const USE_BACKEND = import.meta.env.VITE_USE_BACKEND === 'true';
export const USE_SUPABASE = import.meta.env.VITE_USE_SUPABASE === 'true';
/** Must be read here — Vite only inlines env vars referenced in app source. */
export const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL ?? '';
export const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY ?? '';

export const DATA_NOT_CONFIGURED =
  'Data not found. Configure Supabase (VITE_USE_SUPABASE=true with VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY) or the local API (VITE_USE_BACKEND=true).';
