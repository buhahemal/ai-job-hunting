// @vitest-environment jsdom
import { render, screen, fireEvent, cleanup, waitFor } from '@testing-library/react';
import { describe, expect, it, vi, afterEach } from 'vitest';
import ScanInsightDetailPanel from './ScanInsightDetailPanel';
import type { ScanInsight } from '../types';

vi.mock('../api/client', () => ({
  promoteScannedJob: vi.fn().mockResolvedValue({ success: true }),
}));

const MOCK_INSIGHT: ScanInsight = {
  dedupeKey: 'key-101',
  source: 'RemoteOK',
  title: 'Lead Distributed Systems Engineer ⚡',
  company: 'HyperScale AI',
  location: 'Remote',
  remoteType: 'Remote',
  canonicalRole: 'Backend Engineer',
  overallScore: 88,
  skillMatchScore: 90,
  experienceMatchScore: 85,
  atsScore: 82,
  scannedAt: '2026-07-19T11:00:00.000Z',
  rescoredAt: '2026-07-19T12:00:00.000Z',
  createdAt: '2026-07-19T11:00:00.000Z',
  updatedAt: '2026-07-19T12:00:00.000Z',
  matchedSkills: ['Distributed Systems', 'Python', 'Kafka'],
  missingSkills: ['Cassandra'],
  missingKeywords: ['Raft'],
  applicationUrl: 'https://example.com/insight/101',
  requiredSkills: ['Distributed Systems'],
  preferredSkills: ['Kafka'],
  extractedTechnologies: ['Python'],
  matchExplanation: 'Solid distributed systems background.',
  promotedToJobs: false,
  actionHistory: [
    {
      timestamp: '2026-07-19T12:00:00.000Z',
      status: 'New',
      action: 'Rescored against updated profile',
      note: 'Skill match increased',
    },
  ],
};

describe('ScanInsightDetailPanel Component & Actions', () => {
  afterEach(cleanup);

  it('renders placeholder when no scan insight is selected', () => {
    render(<ScanInsightDetailPanel insight={null} onClose={vi.fn()} onPromoted={vi.fn()} />);

    expect(screen.getByText(/Select a scanned job to view match breakdown/i)).toBeDefined();
  });

  it('renders score breakdown, title, company, matched and missing skills', () => {
    render(
      <ScanInsightDetailPanel insight={MOCK_INSIGHT} onClose={vi.fn()} onPromoted={vi.fn()} />,
    );

    expect(screen.getByText('Lead Distributed Systems Engineer ⚡')).toBeDefined();
    expect(screen.getByText(/HyperScale AI/i)).toBeDefined();
    expect(screen.getByText('88%')).toBeDefined();
    expect(screen.getByText('Distributed Systems')).toBeDefined();
    expect(screen.getByText('Cassandra')).toBeDefined();
  });

  it('displays scanned and last modified timestamps correctly', () => {
    render(
      <ScanInsightDetailPanel insight={MOCK_INSIGHT} onClose={vi.fn()} onPromoted={vi.fn()} />,
    );

    expect(screen.getByText(/Scanned/i)).toBeDefined();
    expect(screen.getByText(/Modified/i)).toBeDefined();
  });

  it('renders action history entries and notes timeline', () => {
    render(
      <ScanInsightDetailPanel insight={MOCK_INSIGHT} onClose={vi.fn()} onPromoted={vi.fn()} />,
    );

    expect(screen.getByText(/Action History & Notes/i)).toBeDefined();
    expect(screen.getByText('Rescored against updated profile')).toBeDefined();
    expect(screen.getByText('"Skill match increased"')).toBeDefined();
  });

  it('triggers onPromoted action when "Promote to Job Leads" and "Confirm promote" are clicked', async () => {
    const handlePromote = vi.fn().mockResolvedValue(undefined);

    render(
      <ScanInsightDetailPanel
        insight={MOCK_INSIGHT}
        onClose={vi.fn()}
        onPromoted={handlePromote}
      />,
    );

    const promoteBtn = screen.getByRole('button', { name: /Promote to Job Leads/i });
    fireEvent.click(promoteBtn);

    const confirmBtn = screen.getByRole('button', { name: /Confirm promote/i });
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(handlePromote).toHaveBeenCalledWith('key-101');
    });
  });
});
