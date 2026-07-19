// @vitest-environment jsdom
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { describe, expect, it, vi, afterEach } from 'vitest';
import InterviewTracker from './InterviewTracker';
import type { Interview, Job } from '../types';

const MOCK_JOBS: Job[] = [
  {
    id: 'job-1',
    source: 'RemoteOK',
    title: 'Lead Architect 🚀',
    company: 'Nexus Systems',
    location: 'Remote',
    remoteType: 'Remote',
    status: 'Interviewing',
    url: 'https://example.com/job-1',
    description: 'Architecture role',
    postedAt: '2026-07-19T00:00:00Z',
  },
];

const MOCK_INTERVIEWS: Interview[] = [
  {
    id: 'int-1',
    jobId: 'job-1',
    company: 'Nexus Systems',
    role: 'Lead Architect 🚀',
    date: '2026-07-25T14:00',
    type: 'Technical System Design',
    status: 'Scheduled',
    notes: 'Focus on distributed caching and Kafka architecture',
  },
];

describe('InterviewTracker Component & Actions', () => {
  afterEach(cleanup);

  it('renders interviews list with company, role, date, and status', () => {
    render(
      <InterviewTracker
        interviews={MOCK_INTERVIEWS}
        jobs={MOCK_JOBS}
        onAddInterview={vi.fn()}
        onUpdateStatus={vi.fn()}
      />,
    );

    expect(screen.getByText(/Nexus Systems/i)).toBeDefined();
    expect(screen.getByText(/Lead Architect 🚀/i)).toBeDefined();
    expect(screen.getByText('Technical System Design')).toBeDefined();
    expect(screen.getByText('Scheduled')).toBeDefined();
  });

  it('opens schedule modal and submits new interview', () => {
    const handleAdd = vi.fn();

    render(
      <InterviewTracker
        interviews={[]}
        jobs={MOCK_JOBS}
        onAddInterview={handleAdd}
        onUpdateStatus={vi.fn()}
      />,
    );

    const scheduleBtn = screen.getByRole('button', { name: /Schedule Interview/i });
    fireEvent.click(scheduleBtn);

    // Select job from modal dropdown
    const select = screen.getAllByRole('combobox')[0];
    fireEvent.change(select, { target: { value: 'job-1' } });

    // Fill date
    const dateInput = document.querySelector('input[type="datetime-local"]')!;
    fireEvent.change(dateInput, { target: { value: '2026-07-25T14:00' } });

    const submitBtn = screen.getByRole('button', { name: /Add Scheduled Round/i });
    fireEvent.click(submitBtn);

    expect(handleAdd).toHaveBeenCalled();
  });

  it('triggers onUpdateStatus when Pass button is clicked', () => {
    const handleUpdateStatus = vi.fn();

    render(
      <InterviewTracker
        interviews={MOCK_INTERVIEWS}
        jobs={MOCK_JOBS}
        onAddInterview={vi.fn()}
        onUpdateStatus={handleUpdateStatus}
      />,
    );

    const passBtn = screen.getByRole('button', { name: /Pass/i });
    fireEvent.click(passBtn);

    expect(handleUpdateStatus).toHaveBeenCalledWith('int-1', 'Passed');
  });
});
