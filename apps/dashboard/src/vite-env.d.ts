/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_USE_BACKEND?: string;
  readonly VITE_USE_SUPABASE?: string;
  readonly VITE_SUPABASE_URL?: string;
  readonly VITE_SUPABASE_ANON_KEY?: string;
  readonly VITE_BASE_PATH?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
