import type { Interview, Job, Profile } from '../types';

export interface Database {
  profile: Profile;
  jobs: Job[];
  interviews: Interview[];
}

export const USE_BACKEND = import.meta.env.VITE_USE_BACKEND === 'true';
export const USE_SUPABASE = import.meta.env.VITE_USE_SUPABASE === 'true';
export const DATA_URL = `${import.meta.env.BASE_URL}data/data.json`;
export const STORAGE_KEY = 'ai-job-hunter-state';
