import type { Interview, Job, Profile } from '../types';
import {
  createBrowserClient,
  DashboardRepository,
  readSupabaseEnvFromImportMeta,
  type InterviewRecord,
  type JobRecord,
} from '@ai-job-hunter/database';
import { normalizeProfile } from './defaultProfile';
import { USE_BACKEND, USE_SUPABASE } from './config';
import { heuristicScore, loadDatabase, saveDatabase, tailorFallback } from './staticStore';

let repository: DashboardRepository | null = null;

function getRepository(): DashboardRepository {
  if (!repository) {
    const env = readSupabaseEnvFromImportMeta(import.meta);
    if (!env) {
      throw new Error(
        'Supabase is not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.',
      );
    }
    repository = new DashboardRepository(createBrowserClient(env));
  }
  return repository;
}

function asJob(record: JobRecord): Job {
  return record as Job;
}

function asInterview(record: InterviewRecord): Interview {
  return record as Interview;
}

async function backendFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    const errorBody: unknown = await response.json().catch(() => ({ error: response.statusText }));
    const message =
      typeof errorBody === 'object' &&
      errorBody !== null &&
      'error' in errorBody &&
      typeof (errorBody as { error: unknown }).error === 'string'
        ? (errorBody as { error: string }).error
        : 'Request failed';
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export async function getProfile(): Promise<Profile> {
  if (USE_BACKEND) {
    return backendFetch<Profile>('/api/profile');
  }
  if (USE_SUPABASE) {
    const profile = await getRepository().getProfile();
    return normalizeProfile(profile ?? {});
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
  if (USE_SUPABASE) {
    await getRepository().saveProfile(profile);
    return profile;
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
  if (USE_SUPABASE) {
    const repo = getRepository();
    const [jobs, interviews] = await Promise.all([repo.listJobs(), repo.listInterviews()]);
    return { jobs: jobs.map(asJob), interviews: interviews.map(asInterview) };
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
    'Live scans run on GitHub Actions. Trigger the "Scanner Cron" workflow, then refresh this page.',
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
  if (USE_SUPABASE) {
    return asJob(await getRepository().updateJobStatus(jobId, status));
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
  if (USE_SUPABASE) {
    return asJob(await getRepository().updateJobNotes(jobId, notes));
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

  const profile = await getProfile();

  if (USE_SUPABASE) {
    const repo = getRepository();
    const jobs = await repo.listJobs();
    const job = jobs.find((entry) => entry.id === jobId);
    if (!job) throw new Error('Job not found');
    const tailored = { ...job, ...tailorFallback(job as Job, profile) };
    return asJob(await repo.upsertJob(tailored));
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
  if (USE_SUPABASE) {
    return asJob(await getRepository().saveTailoredJob(jobId, payload));
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

  const profile = await getProfile();
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
    ...heuristicScore(payload, profile),
  };

  if (USE_SUPABASE) {
    return asJob(await getRepository().upsertJob(newJob));
  }

  const db = await loadDatabase();
  db.jobs.unshift(newJob);
  saveDatabase(db);
  return newJob;
}

export async function addInterview(interviewData: Omit<Interview, 'id' | 'status'>): Promise<void> {
  if (USE_BACKEND) {
    await backendFetch('/api/interviews', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(interviewData),
    });
    return;
  }

  const interview: Interview = {
    ...interviewData,
    id: `int-${Date.now()}`,
    status: 'Scheduled',
  };

  if (USE_SUPABASE) {
    await getRepository().addInterview(interview);
    if (interview.jobId) {
      await getRepository().updateJobStatus(interview.jobId, 'Interviewing');
    }
    return;
  }

  const db = await loadDatabase();
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

  if (USE_SUPABASE) {
    const repo = getRepository();
    await repo.updateInterviewStatus(id, status);
    const interviews = await repo.listInterviews();
    const interview = interviews.find((entry) => entry.id === id);
    if (interview) {
      const jobStatus = status === 'Passed' ? 'Offer' : status === 'Failed' ? 'Rejected' : null;
      if (jobStatus) {
        await repo.updateJobStatus(interview.jobId, jobStatus);
      }
    }
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
