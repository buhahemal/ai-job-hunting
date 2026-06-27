import type { ProfileRecord, RemoteType } from './types.js';

const STORED_PROFILE_DEFAULTS: ProfileRecord = {
  fullName: '',
  email: '',
  phone: '',
  website: '',
  github: '',
  linkedin: '',
  location: '',
  targetRoles: [],
  skills: [],
  experience: [],
  education: [],
  projects: [],
  preferences: {
    locations: [],
    remotePreference: 'Any',
    companySizes: [],
    targetCompanies: [],
    skillsKeywords: [],
  },
  masterResumeLaTeX: '',
};

/** Normalize Supabase profiles.data without injecting bundled demo skills. */
export function normalizeStoredProfile(profile?: Partial<ProfileRecord> | null): ProfileRecord {
  const source = profile ?? {};
  return {
    ...STORED_PROFILE_DEFAULTS,
    ...source,
    skills: [...(source.skills ?? [])],
    targetRoles: [...(source.targetRoles ?? [])],
    experience: [...(source.experience ?? [])],
    education: [...(source.education ?? [])],
    projects: [...(source.projects ?? [])],
    preferences: {
      ...STORED_PROFILE_DEFAULTS.preferences,
      ...source.preferences,
      remotePreference:
        (source.preferences?.remotePreference as RemoteType | 'Any' | undefined) ??
        STORED_PROFILE_DEFAULTS.preferences.remotePreference,
    },
    masterResumeLaTeX: source.masterResumeLaTeX ?? '',
  };
}
