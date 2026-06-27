import { MATCH_SCORE_THRESHOLD } from './constants.js';
import type {
  ExperienceBullet,
  ProfileEducationEntry,
  ProfileExperienceEntry,
  ProfileMatchSettings,
  ProfileProjectEntry,
  ProfileRecord,
  ProfileSkillGroup,
} from './types.js';

const STORED_PROFILE_DEFAULTS: ProfileRecord = {
  fullName: '',
  email: '',
  phone: '',
  website: '',
  github: '',
  linkedin: '',
  location: '',
  summary: '',
  targetRoles: [],
  skills: [],
  skillGroups: [],
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
  matchSettings: {
    minMatchScore: MATCH_SCORE_THRESHOLD,
  },
  masterResumeLaTeX: '',
};

function normalizeExperience(
  entries: Partial<ProfileExperienceEntry>[] | undefined,
): ProfileExperienceEntry[] {
  return (entries ?? []).map((entry) => ({
    role: entry.role ?? '',
    company: entry.company ?? '',
    period: entry.period ?? '',
    location: entry.location ?? '',
    techStack: entry.techStack ?? '',
    bullets: [...(entry.bullets ?? [])],
  }));
}

function normalizeEducation(
  entries: Partial<ProfileEducationEntry>[] | undefined,
): ProfileEducationEntry[] {
  return (entries ?? []).map((entry) => ({
    degree: entry.degree ?? '',
    school: entry.school ?? '',
    period: entry.period ?? '',
    location: entry.location ?? '',
  }));
}

function normalizeProjects(
  entries: Partial<ProfileProjectEntry>[] | undefined,
): ProfileProjectEntry[] {
  return (entries ?? []).map((entry) => ({
    title: entry.title ?? '',
    description: entry.description ?? '',
    tech: [...(entry.tech ?? [])],
    subtitle: entry.subtitle,
    techStack: entry.techStack,
  }));
}

function normalizeSkillGroups(
  groups: Partial<ProfileSkillGroup>[] | undefined,
): ProfileSkillGroup[] {
  return (groups ?? [])
    .filter((group) => group.label || group.items?.length)
    .map((group) => ({
      label: group.label ?? 'Skills',
      items: [...(group.items ?? [])],
    }));
}

function normalizeMatchSettings(
  settings: Partial<ProfileMatchSettings> | undefined,
): ProfileMatchSettings {
  const raw = settings?.minMatchScore ?? MATCH_SCORE_THRESHOLD;
  const minMatchScore = Number.isFinite(raw)
    ? Math.min(100, Math.max(50, Math.round(raw)))
    : MATCH_SCORE_THRESHOLD;
  return { minMatchScore };
}

/** Normalize Supabase profiles.data without injecting bundled demo skills. */
export function normalizeStoredProfile(profile?: Partial<ProfileRecord> | null): ProfileRecord {
  const source = profile ?? {};
  return {
    ...STORED_PROFILE_DEFAULTS,
    ...source,
    skills: [...(source.skills ?? [])],
    targetRoles: [...(source.targetRoles ?? [])],
    summary: source.summary ?? '',
    skillGroups: normalizeSkillGroups(source.skillGroups),
    experience: normalizeExperience(source.experience),
    education: normalizeEducation(source.education),
    projects: normalizeProjects(source.projects),
    preferences: {
      ...STORED_PROFILE_DEFAULTS.preferences,
      ...source.preferences,
      remotePreference:
        source.preferences?.remotePreference ??
        STORED_PROFILE_DEFAULTS.preferences.remotePreference,
      locations: [...(source.preferences?.locations ?? [])],
      companySizes: [...(source.preferences?.companySizes ?? [])],
      targetCompanies: [...(source.preferences?.targetCompanies ?? [])],
      skillsKeywords: [...(source.preferences?.skillsKeywords ?? [])],
    },
    matchSettings: normalizeMatchSettings(source.matchSettings),
    masterResumeLaTeX: source.masterResumeLaTeX ?? '',
  };
}

/** Flatten structured or plain bullets into searchable text. */
export function flattenExperienceBullet(bullet: ExperienceBullet): string {
  if (typeof bullet === 'string') {
    return bullet.trim();
  }
  const title = bullet.title?.trim() ?? '';
  const body = bullet.body?.trim() ?? '';
  if (title && body) {
    return `${title}: ${body}`;
  }
  return title || body;
}

export function flattenExperienceBullets(bullets: ExperienceBullet[] | undefined): string[] {
  return (bullets ?? []).map(flattenExperienceBullet).filter(Boolean);
}

export interface ProfileCompletenessIssue {
  field: string;
  message: string;
}

/** Report missing fields that reduce match quality or resume generation. */
export function getProfileCompletenessIssues(profile: ProfileRecord): ProfileCompletenessIssue[] {
  const issues: ProfileCompletenessIssue[] = [];
  if (!profile.fullName.trim())
    issues.push({ field: 'fullName', message: 'Full name is required' });
  if (!profile.email.trim()) issues.push({ field: 'email', message: 'Email is required' });
  if (!profile.skills.length) issues.push({ field: 'skills', message: 'Add at least one skill' });
  if (!profile.targetRoles.length) {
    issues.push({ field: 'targetRoles', message: 'Add target roles for experience matching' });
  }
  if (!profile.preferences.skillsKeywords.length) {
    issues.push({ field: 'skillsKeywords', message: 'Add skill keywords used for gap analysis' });
  }
  if (!profile.experience.length) {
    issues.push({ field: 'experience', message: 'Add at least one work experience entry' });
  }
  if (!profile.summary.trim()) {
    issues.push({ field: 'summary', message: 'Add a professional summary for resume generation' });
  }
  return issues;
}

export function isProfileCompleteForMatching(profile: ProfileRecord): boolean {
  return getProfileCompletenessIssues(profile).length === 0;
}

export function resolveMinMatchScore(profile: ProfileRecord): number {
  return profile.matchSettings.minMatchScore;
}
