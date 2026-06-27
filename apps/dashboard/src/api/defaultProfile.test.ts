import { describe, expect, it } from 'vitest';
import { DEFAULT_PROFILE, getProfileInitials, normalizeProfile } from './defaultProfile';

describe('normalizeProfile', () => {
  it('returns defaults when profile is empty', () => {
    const profile = normalizeProfile({});
    expect(profile.fullName).toBe(DEFAULT_PROFILE.fullName);
    expect(profile.skills.length).toBeGreaterThan(0);
  });

  it('preserves user overrides', () => {
    const profile = normalizeProfile({ fullName: 'Jane Doe', email: 'jane@example.com' });
    expect(profile.fullName).toBe('Jane Doe');
    expect(profile.email).toBe('jane@example.com');
  });
});

describe('getProfileInitials', () => {
  it('returns initials for a full name', () => {
    expect(getProfileInitials('Hemal Buha')).toBe('HB');
  });

  it('returns fallback when name is missing', () => {
    expect(getProfileInitials(undefined)).toBe('?');
    expect(getProfileInitials('')).toBe('?');
  });
});
