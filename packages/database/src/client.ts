import { createClient, type SupabaseClient } from '@supabase/supabase-js';

export interface SupabaseEnv {
  url: string;
  anonKey: string;
}

/** Create browser-safe Supabase client (anon key + RLS). */
export function createBrowserClient(env: SupabaseEnv): SupabaseClient {
  return createClient(env.url, env.anonKey);
}

export function readSupabaseEnvFromImportMeta(meta: ImportMeta): SupabaseEnv | null {
  const url = meta.env.VITE_SUPABASE_URL as string | undefined;
  const anonKey = meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;
  if (!url || !anonKey) return null;
  return { url, anonKey };
}
