import type { Interview, Job, Profile } from '../types';
import { normalizeProfile } from './defaultProfile';
import { USE_BACKEND } from './config';
import {
  heuristicScore,
  loadDatabase,
  saveDatabase,
  tailorFallback,
} from './staticStore';

async function backendFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error(String((error as { error?: string }).error ?? 'Request failed'));
  }
  return response.json() as Promise<T>;
}

export async function getProfile(): Promise<Profile> {
  if (USE_BACKEND) {
    return backendFetch<Profile>('/api/profile');
  }
  const db = await loadDatabase();
  return normalizeProfile(db.profile);
}

export async function saveProfile(profile: Profile): Promise<Profile> {
  if (USE_BACKEND) {
    const data = await backendFetch<{ profile: Profile }>('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    });
    return data.profile;
  }

  const db = await loadDatabase();
  db.profile = profile;
  saveDatabase(db);
  return profile;
}

export async function getJobs(): Promise<{ jobs: Job[]; interviews: Interview[] }> {
  if (USE_BACKEND) {
    return backendFetch<{ jobs: Job[]; interviews: Interview[] }>('/api/jobs');
  }

  const db = await loadDatabase();
  return {
    jobs: db.jobs,
    interviews: db.interviews,
  };
}

export async function scanJobs(): Promise<{ addedCount: number; addedJobs: Job[] }> {
  if (USE_BACKEND) {
    return backendFetch<{ addedCount: number; addedJobs: Job[] }>('/api/jobs/scan', {
      method: 'POST',
    });
  }

  throw new Error(
    'Live scans run on GitHub Actions. Trigger the "Scheduled Job Scan & Score" workflow, then refresh this page.',
  );
}

export async function updateJobStatus(jobId: string, status: Job['status']): Promise<Job> {
  if (USE_BACKEND) {
    const data = await backendFetch<{ job: Job }>(`/api/jobs/${jobId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    return data.job;
  }

  const db = await loadDatabase();
  const job = db.jobs.find((entry) => entry.id === jobId);
  if (!job) throw new Error('Job not found');
  job.status = status;
  saveDatabase(db);
  return job;
}

export async function updateJobNotes(jobId: string, notes: string): Promise<Job> {
  if (USE_BACKEND) {
    const data = await backendFetch<{ job: Job }>(`/api/jobs/${jobId}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes }),
    });
    return data.job;
  }

  const db = await loadDatabase();
  const job = db.jobs.find((entry) => entry.id === jobId);
  if (!job) throw new Error('Job not found');
  job.notes = notes;
  saveDatabase(db);
  return job;
}

export async function tailorJob(jobId: string): Promise<Job> {
  if (USE_BACKEND) {
    const data = await backendFetch<{ job: Job }>(`/api/jobs/${jobId}/tailor`, { method: 'POST' });
    return data.job;
  }

  const db = await loadDatabase();
  const job = db.jobs.find((entry) => entry.id === jobId);
  if (!job) throw new Error('Job not found');

  Object.assign(job, tailorFallback(job, db.profile));
  saveDatabase(db);
  return job;
}

export async function saveTailoredJob(
  jobId: string,
  payload: { tailoredResumeLaTeX: string; tailoredCoverLetter: string; atsScore?: number },
): Promise<Job> {
  if (USE_BACKEND) {
    const data = await backendFetch<{ job: Job }>(`/api/jobs/${jobId}/save-tailored`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return data.job;
  }

  const db = await loadDatabase();
  const job = db.jobs.find((entry) => entry.id === jobId);
  if (!job) throw new Error('Job not found');

  job.tailoredResumeLaTeX = payload.tailoredResumeLaTeX;
  job.tailoredCoverLetter = payload.tailoredCoverLetter;
  if (payload.atsScore !== undefined) job.atsScore = payload.atsScore;
  saveDatabase(db);
  return job;
}

export async function addCustomJob(payload: {
  title: string;
  company: string;
  location: string;
  remoteType: Job['remoteType'];
  url: string;
  description: string;
}): Promise<Job> {
  if (USE_BACKEND) {
    const data = await backendFetch<{ job: Job }>('/api/jobs/add-custom', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return data.job;
  }

  const db = await loadDatabase();
  const newJob: Job = {
    id: `custom-${Date.now()}`,
    title: payload.title,
    company: payload.company,
    location: payload.location,
    remoteType: payload.remoteType,
    source: 'Manual Import',
    url: payload.url,
    description: payload.description,
    postedAt: new Date().toISOString(),
    status: 'New',
    ...heuristicScore(payload, db.profile),
  };

  db.jobs.unshift(newJob);
  saveDatabase(db);
  return newJob;
}

export async function addInterview(
  interviewData: Omit<Interview, 'id' | 'status'>,
): Promise<void> {
  if (USE_BACKEND) {
    await backendFetch('/api/interviews', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(interviewData),
    });
    return;
  }

  const db = await loadDatabase();
  const interview: Interview = {
    ...interviewData,
    id: `int-${Date.now()}`,
    status: 'Scheduled',
  };

  db.interviews.push(interview);
  const job = db.jobs.find((entry) => entry.id === interview.jobId);
  if (job) job.status = 'Interviewing';
  saveDatabase(db);
}

export async function updateInterviewStatus(
  id: string,
  status: Interview['status'],
): Promise<void> {
  if (USE_BACKEND) {
    await backendFetch(`/api/interviews/${id}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    return;
  }

  const db = await loadDatabase();
  const interview = db.interviews.find((entry) => entry.id === id);
  if (!interview) throw new Error('Interview not found');

  interview.status = status;
  const job = db.jobs.find((entry) => entry.id === interview.jobId);
  if (job) {
    if (status === 'Passed') job.status = 'Offer';
    if (status === 'Failed') job.status = 'Rejected';
  }
  saveDatabase(db);
}
