// @vitest-environment jsdom
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { describe, expect, it, vi, afterEach } from 'vitest';
import JobDetailPanel from './JobDetailPanel';
import type { Job } from '../types';

const MOCK_JOB: Job = {
  id: 'job-101',
  source: 'RemoteOK',
  title: 'Staff Platform Architect 🚀',
  company: 'Quantum Dynamics',
  location: 'Remote - Worldwide',
  remoteType: 'Remote',
  status: 'New',
  score: 92,
  canonicalRole: 'Platform Engineer',
  primaryStack: 'DevOps / K8s',
  seniority: 'Staff',
  priority: 'High',
  url: 'https://example.com/apply/101',
  description: 'Building global Kubernetes infrastructure and high-throughput microservices.',
  postedAt: '2026-07-19T10:00:00.000Z',
  createdAt: '2026-07-19T10:00:00.000Z',
  updatedAt: '2026-07-19T12:00:00.000Z',
  scannedAt: '2026-07-19T10:00:00.000Z',
  notes: 'Referred by Sarah',
  applicationUrl: 'https://example.com/apply/101',
  matchInsights: {
    overallScore: 92,
    skillMatchScore: 95,
    experienceMatchScore: 90,
    atsScore: 88,
    salaryMatchScore: 85,
    companyMatchScore: 90,
    locationMatchScore: 95,
    remoteMatchScore: 100,
    confidenceScore: 95,
    matchedSkills: ['Kubernetes', 'Go', 'Terraform'],
    missingSkills: ['Rust'],
    missingKeywords: ['eBPF'],
    resumeSuggestions: ['Highlight eBPF knowledge'],
    matchExplanation: 'Exceptional fit for cloud-native infrastructure.',
  },
  actionHistory: [
    {
      timestamp: '2026-07-19T12:00:00.000Z',
      status: 'New',
      action: 'Status changed to New',
      note: 'Location requires remote fit',
    },
  ],
};

describe('JobDetailPanel Component & Action Handlers', () => {
  afterEach(cleanup);
  it('renders placeholder when no job is selected', () => {
    render(<JobDetailPanel job={null} onClose={vi.fn()} onSaveNotes={vi.fn()} />);

    expect(screen.getByText(/Select a job to view enriched metadata/i)).toBeDefined();
  });

  it('renders job title, company, stack, and match scores correctly', () => {
    render(<JobDetailPanel job={MOCK_JOB} onClose={vi.fn()} onSaveNotes={vi.fn()} />);

    expect(screen.getByText('Staff Platform Architect 🚀')).toBeDefined();
    expect(screen.getByText(/Quantum Dynamics/i)).toBeDefined();
    expect(screen.getByText('DevOps / K8s')).toBeDefined();
    expect(screen.getByText('92%')).toBeDefined(); // Match score
  });

  it('displays created and last modified timestamps', () => {
    render(<JobDetailPanel job={MOCK_JOB} onClose={vi.fn()} onSaveNotes={vi.fn()} />);

    expect(screen.getByText(/Created \/ Scanned/i)).toBeDefined();
    expect(screen.getByText(/Last Modified/i)).toBeDefined();
  });

  it('displays action history timeline entries with timestamps and user notes', () => {
    render(<JobDetailPanel job={MOCK_JOB} onClose={vi.fn()} onSaveNotes={vi.fn()} />);

    expect(screen.getByText(/Action History & Notes Timeline/i)).toBeDefined();
    expect(screen.getByText('Status changed to New')).toBeDefined();
    expect(screen.getByText('"Location requires remote fit"')).toBeDefined();
  });

  it('triggers onUpdateStatus with status and optional reason note when submitted', () => {
    const handleUpdateStatus = vi.fn();

    render(
      <JobDetailPanel
        job={MOCK_JOB}
        onClose={vi.fn()}
        onSaveNotes={vi.fn()}
        onUpdateStatus={handleUpdateStatus}
      />,
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'Shortlisted' } });

    const noteInput = screen.getByPlaceholderText(/Optional reason note/i);
    fireEvent.change(noteInput, {
      target: { value: 'Strong match on Kubernetes & Terraform' },
    });

    const submitBtn = screen.getByRole('button', { name: /Save Status & Note/i });
    fireEvent.click(submitBtn);

    expect(handleUpdateStatus).toHaveBeenCalledWith(
      'job-101',
      'Shortlisted',
      'Strong match on Kubernetes & Terraform',
    );
  });

  it('triggers onSaveNotes when general notes textarea is updated and blurred', () => {
    const handleSaveNotes = vi.fn();

    render(<JobDetailPanel job={MOCK_JOB} onClose={vi.fn()} onSaveNotes={handleSaveNotes} />);

    const notesTextarea = screen.getByPlaceholderText(/Track referrals, interviews, salary notes/i);

    fireEvent.blur(notesTextarea, {
      target: { value: 'Followed up with recruiter on LinkedIn 💬' },
    });

    expect(handleSaveNotes).toHaveBeenCalledWith(
      'job-101',
      'Followed up with recruiter on LinkedIn 💬',
    );
  });

  it('renders application URL link with target="_blank"', () => {
    render(<JobDetailPanel job={MOCK_JOB} onClose={vi.fn()} onSaveNotes={vi.fn()} />);

    const applyLink = screen.getByRole('link', { name: /Apply \/ View Posting/i });
    expect(applyLink.getAttribute('href')).toBe('https://example.com/apply/101');
    expect(applyLink.getAttribute('target')).toBe('_blank');
  });
});
