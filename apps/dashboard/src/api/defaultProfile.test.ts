import { describe, expect, it } from 'vitest';
import { DEFAULT_PROFILE, getProfileInitials, normalizeProfile } from './defaultProfile';

describe('normalizeProfile', () => {
  it('returns bundled defaults when profile is empty (offline mode)', () => {
    const profile = normalizeProfile({});
    expect(profile.fullName).toBe(DEFAULT_PROFILE.fullName);
    expect(profile.skills.length).toBeGreaterThan(0);
  });

  it('preserves user overrides without injecting bundled skills when provided', () => {
    const profile = normalizeProfile({
      fullName: 'Jane Doe',
      email: 'jane@example.com',
      skills: ['Rust'],
    });
    expect(profile.fullName).toBe('Jane Doe');
    expect(profile.email).toBe('jane@example.com');
    expect(profile.skills).toEqual(['Rust']);
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
