// @vitest-environment jsdom
import { render, screen, cleanup } from '@testing-library/react';
import { describe, expect, it, afterEach } from 'vitest';
import AnalyticsView from './AnalyticsView';
import type { Job } from '../types';

const MOCK_JOBS: Job[] = [
  {
    id: 'job-1',
    source: 'RemoteOK',
    title: 'Senior Frontend Engineer',
    company: 'Acme',
    location: 'Remote',
    remoteType: 'Remote',
    status: 'Applied',
    score: 92,
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
    company: 'Beta',
    location: 'Remote',
    remoteType: 'Remote',
    status: 'Shortlisted',
    score: 80,
    primaryStack: 'Backend',
    seniority: 'Mid-level',
    url: 'https://example.com/2',
    description: 'Backend role',
    postedAt: '2026-07-19T00:00:00Z',
  },
];

describe('AnalyticsView Component & Calculations', () => {
  afterEach(cleanup);

  it('renders overall metrics summary cards', () => {
    render(<AnalyticsView jobs={MOCK_JOBS} interviews={[]} />);

    expect(screen.getByText(/Discovered Jobs/i)).toBeDefined();
    expect(screen.getByText(/Avg AI Fit Score/i)).toBeDefined();
  });

  it('renders match score distribution breakdown', () => {
    render(<AnalyticsView jobs={MOCK_JOBS} interviews={[]} />);

    expect(screen.getByText(/Application Funnel & Conversion/i)).toBeDefined();
  });
});
