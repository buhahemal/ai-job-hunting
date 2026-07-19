import { describe, expect, it } from 'vitest';
import { filterJobs, DEFAULT_JOB_FILTERS } from './JobFilters';
import type { Job } from '../types';

const MOCK_JOBS: Job[] = [
  {
    id: 'job-1',
    source: 'RemoteOK',
    title: 'Senior Frontend Engineer',
    company: 'Acme Corp',
    location: 'Remote',
    remoteType: 'Remote',
    status: 'New',
    score: 90,
    primaryStack: 'Frontend',
    seniority: 'Senior',
    url: 'https://example.com/1',
    description: 'Frontend role',
    postedAt: '2026-07-19T00:00:00Z',
  },
  {
    id: 'job-2',
    source: 'Greenhouse',
    title: 'Backend Systems Engineer',
    company: 'Beta Systems',
    location: 'New York, NY',
    remoteType: 'Hybrid',
    status: 'Applied',
    score: 80,
    primaryStack: 'Backend',
    seniority: 'Mid-level',
    url: 'https://example.com/2',
    description: 'Backend role',
    postedAt: '2026-07-19T00:00:00Z',
  },
  {
    id: 'job-3',
    source: 'Lever',
    title: 'Full Stack Developer',
    company: 'Gamma Tech',
    location: 'Remote',
    remoteType: 'Remote',
    status: 'Ignored',
    score: 70,
    primaryStack: 'Fullstack',
    seniority: 'Mid-level',
    url: 'https://example.com/3',
    description: 'Fullstack role',
    postedAt: '2026-07-19T00:00:00Z',
  },
  {
    id: 'job-4',
    source: 'Ashby',
    title: 'DevOps Lead',
    company: 'Delta Cloud',
    location: 'San Francisco, CA',
    remoteType: 'On-site',
    status: 'Rejected',
    score: 88,
    primaryStack: 'DevOps',
    seniority: 'Lead',
    url: 'https://example.com/4',
    description: 'DevOps role',
    postedAt: '2026-07-19T00:00:00Z',
  },
  {
    id: 'job-5',
    source: 'Workable',
    title: 'AI Research Engineer 🚀',
    company: 'Epsilon AI',
    location: 'Remote',
    remoteType: 'Remote',
    status: 'Shortlisted',
    score: 95,
    primaryStack: 'AI / ML',
    seniority: 'Senior',
    url: 'https://example.com/5',
    description: 'AI role',
    postedAt: '2026-07-19T00:00:00Z',
  },
];

describe('JobFilters - Business Rules & Exhaustive Filtering', () => {
  it('hides Ignored and Rejected jobs when status filter is set to "All" (All Active Leads)', () => {
    const result = filterJobs(MOCK_JOBS, { ...DEFAULT_JOB_FILTERS, statusFilter: 'All' });
    const ids = result.map((j) => j.id);

    expect(ids).toContain('job-1');
    expect(ids).toContain('job-2');
    expect(ids).toContain('job-5');
    expect(ids).not.toContain('job-3'); // Ignored
    expect(ids).not.toContain('job-4'); // Rejected
  });

  it('includes Ignored jobs when status filter is explicitly set to "Ignored"', () => {
    const result = filterJobs(MOCK_JOBS, { ...DEFAULT_JOB_FILTERS, statusFilter: 'Ignored' });
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe('job-3');
    expect(result[0].status).toBe('Ignored');
  });

  it('includes Rejected jobs when status filter is explicitly set to "Rejected"', () => {
    const result = filterJobs(MOCK_JOBS, { ...DEFAULT_JOB_FILTERS, statusFilter: 'Rejected' });
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe('job-4');
    expect(result[0].status).toBe('Rejected');
  });

  it('filters by search query case-insensitively across title and company', () => {
    const titleMatch = filterJobs(MOCK_JOBS, { ...DEFAULT_JOB_FILTERS, searchQuery: 'frontend' });
    expect(titleMatch).toHaveLength(1);
    expect(titleMatch[0].id).toBe('job-1');

    const companyMatch = filterJobs(MOCK_JOBS, { ...DEFAULT_JOB_FILTERS, searchQuery: 'beta' });
    expect(companyMatch).toHaveLength(1);
    expect(companyMatch[0].id).toBe('job-2');
  });

  it('filters by match score threshold (Excellent >= 85%)', () => {
    const result = filterJobs(MOCK_JOBS, { ...DEFAULT_JOB_FILTERS, scoreFilter: 'Excellent' });
    const ids = result.map((j) => j.id);

    expect(ids).toContain('job-1'); // 90
    expect(ids).toContain('job-5'); // 95
    expect(ids).not.toContain('job-2'); // 80
  });

  it('filters by primary stack in search query (Backend, AI / ML)', () => {
    const backendResult = filterJobs(MOCK_JOBS, { ...DEFAULT_JOB_FILTERS, searchQuery: 'Backend' });
    expect(backendResult).toHaveLength(1);
    expect(backendResult[0].id).toBe('job-2');

    const aiResult = filterJobs(MOCK_JOBS, { ...DEFAULT_JOB_FILTERS, searchQuery: 'AI / ML' });
    expect(aiResult).toHaveLength(1);
    expect(aiResult[0].id).toBe('job-5');
  });

  it('handles Unicode, emojis, and special characters in search query', () => {
    const emojiMatch = filterJobs(MOCK_JOBS, { ...DEFAULT_JOB_FILTERS, searchQuery: '🚀' });
    expect(emojiMatch).toHaveLength(1);
    expect(emojiMatch[0].id).toBe('job-5');
  });

  it('handles boundary conditions: empty job list and null/undefined fields', () => {
    expect(filterJobs([], DEFAULT_JOB_FILTERS)).toEqual([]);

    const incompleteJobs: Job[] = [
      {
        id: 'job-null',
        source: 'Unknown',
        title: '',
        company: '',
        location: '',
        remoteType: 'Remote',
        status: 'New',
        url: '',
        description: '',
        postedAt: '',
      },
    ];
    const result = filterJobs(incompleteJobs, DEFAULT_JOB_FILTERS);
    expect(result).toHaveLength(1);
  });
});
