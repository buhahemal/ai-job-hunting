import type { Profile } from '../types';
import profileBase from '../../../api/data/profile.json';
import masterResumeLaTeX from '../../../api/data/resume/master.tex?raw';

/** Offline/demo fallback only — not used when VITE_USE_SUPABASE=true. */
export const DEFAULT_PROFILE: Profile = {
  ...(profileBase as Omit<Profile, 'masterResumeLaTeX'>),
  masterResumeLaTeX,
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
      preferences: {
        ...DEFAULT_PROFILE.preferences,
        ...profile?.preferences,
      },
      masterResumeLaTeX: profile?.masterResumeLaTeX || DEFAULT_PROFILE.masterResumeLaTeX,
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
    preferences: {
      ...DEFAULT_PROFILE.preferences,
      ...profile.preferences,
    },
    masterResumeLaTeX: profile.masterResumeLaTeX ?? DEFAULT_PROFILE.masterResumeLaTeX,
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
