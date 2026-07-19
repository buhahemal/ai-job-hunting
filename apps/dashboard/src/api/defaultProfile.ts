import type { Profile } from '../types';
import profileBase from '../../../api/data/profile.json';

/** Offline/demo fallback only — not used when VITE_USE_SUPABASE=true. */
export const DEFAULT_PROFILE: Profile = {
  ...(profileBase as Profile),
  summary: (profileBase as Partial<Profile>).summary ?? '',
  skillGroups: (profileBase as Partial<Profile>).skillGroups ?? [],
  preferences: {
    locations: [],
    remotePreference: 'Any',
    companySizes: [],
    targetCompanies: [],
    skillsKeywords: [],
    companyBlacklist: [],
    titleBlacklist: [],
    locationBlacklist: [],
    experienceLevels: [],
    applyOncePerCompany: false,
    ...((profileBase as Partial<Profile>).preferences ?? {}),
  },
  matchSettings: { minMatchScore: 75 },
  masterResumeLaTeX: '',
};

export function normalizeProfile(profile?: Partial<Profile> | null): Profile {
  if (!profile?.fullName) {
    return {
      ...DEFAULT_PROFILE,
      ...profile,
      skills: profile?.skills?.length ? profile.skills : DEFAULT_PROFILE.skills,
      targetRoles: profile?.targetRoles?.length ? profile.targetRoles : DEFAULT_PROFILE.targetRoles,
      experience: profile?.experience?.length ? profile.experience : DEFAULT_PROFILE.experience,
      education: profile?.education?.length ? profile.education : DEFAULT_PROFILE.education,
      projects: profile?.projects?.length ? profile.projects : DEFAULT_PROFILE.projects,
      summary: profile?.summary || DEFAULT_PROFILE.summary,
      skillGroups: profile?.skillGroups?.length ? profile.skillGroups : DEFAULT_PROFILE.skillGroups,
      preferences: {
        ...DEFAULT_PROFILE.preferences,
        ...profile?.preferences,
      },
      matchSettings: {
        ...DEFAULT_PROFILE.matchSettings,
        ...profile?.matchSettings,
      },
      masterResumeLaTeX: '',
    };
  }

  return {
    ...DEFAULT_PROFILE,
    ...profile,
    skills: profile.skills ?? DEFAULT_PROFILE.skills,
    targetRoles: profile.targetRoles ?? DEFAULT_PROFILE.targetRoles,
    experience: profile.experience ?? DEFAULT_PROFILE.experience,
    education: profile.education ?? DEFAULT_PROFILE.education,
    projects: profile.projects ?? DEFAULT_PROFILE.projects,
    summary: profile.summary ?? DEFAULT_PROFILE.summary,
    skillGroups: profile.skillGroups ?? DEFAULT_PROFILE.skillGroups,
    preferences: {
      ...DEFAULT_PROFILE.preferences,
      ...profile.preferences,
    },
    matchSettings: {
      ...DEFAULT_PROFILE.matchSettings,
      ...profile.matchSettings,
    },
    masterResumeLaTeX: '',
  };
}

export function getProfileInitials(fullName?: string): string {
  if (!fullName?.trim()) return '?';
  return fullName
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}
