import type { Interview, Job, Profile } from '../types';
import {
  createBrowserClient,
  DashboardRepository,
  MATCH_SCORE_THRESHOLD,
  type InterviewRecord,
  type JobRecord,
  type ListScannedJobsParams,
  type ScanSummary,
  type ScannedJobsPage,
} from '@ai-job-hunter/database';
import {
  DATA_NOT_CONFIGURED,
  SUPABASE_ANON_KEY,
  SUPABASE_URL,
  USE_BACKEND,
  USE_SUPABASE,
} from './config';
import { heuristicScore, tailorFallback } from './staticStore';

let repository: DashboardRepository | null = null;

function throwDataNotFound(): never {
  throw new Error(DATA_NOT_CONFIGURED);
}

function getRepository(): DashboardRepository {
  if (!repository) {
    if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
      throw new Error(
        'Supabase is not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.',
      );
    }
    repository = new DashboardRepository(
      createBrowserClient({ url: SUPABASE_URL, anonKey: SUPABASE_ANON_KEY }),
    );
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
    return getRepository().getProfile();
  }
  throwDataNotFound();
}

export async function saveProfile(
  profile: Profile,
  options?: { rescan?: boolean },
): Promise<Profile> {
  if (USE_BACKEND) {
    const data = await backendFetch<{ profile: Profile; rescoredCount?: number }>('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile, rescan: options?.rescan ?? false }),
    });
    return data.profile;
  }
  if (USE_SUPABASE) {
    await getRepository().saveProfile(profile);
    return profile;
  }
  throwDataNotFound();
}

export async function importProfile(payload: Partial<Profile>): Promise<Profile> {
  if (USE_BACKEND) {
    const data = await backendFetch<{ profile: Profile }>('/api/profile/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile: payload }),
    });
    return data.profile;
  }
  throw new Error('Profile import requires the Python API server (set VITE_USE_BACKEND=true).');
}

export interface TailorJobResult {
  job: Job;
  resume?: {
    version: string;
    pdfUrl?: string | null;
    pdfCompiled?: boolean;
  };
}

export interface JobResumeVersion {
  version: string;
  pdfUrl?: string | null;
  atsScore?: number | null;
  createdAt?: string | null;
}

export async function listJobResumes(jobId: string): Promise<JobResumeVersion[]> {
  if (USE_BACKEND) {
    const data = await backendFetch<{ items: JobResumeVersion[] }>(`/api/jobs/${jobId}/resumes`);
    return data.items;
  }
  return [];
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
  throwDataNotFound();
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
  throwDataNotFound();
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
  throwDataNotFound();
}

export async function tailorJob(jobId: string): Promise<TailorJobResult> {
  if (USE_BACKEND) {
    const data = await backendFetch<TailorJobResult>(`/api/jobs/${jobId}/tailor`, {
      method: 'POST',
    });
    return data;
  }

  const profile = await getProfile();

  if (USE_SUPABASE) {
    const repo = getRepository();
    const jobs = await repo.listJobs();
    const job = jobs.find((entry) => entry.id === jobId);
    if (!job) throw new Error('Job not found');
    const tailored = { ...job, ...tailorFallback(job as Job, profile) };
    return { job: asJob(await repo.upsertJob(tailored)) };
  }
  throwDataNotFound();
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
  throwDataNotFound();
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
  throwDataNotFound();
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
  throwDataNotFound();
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
  throwDataNotFound();
}

export async function listScannedJobs(
  params: ListScannedJobsParams = {},
): Promise<ScannedJobsPage> {
  if (USE_SUPABASE) {
    return getRepository().listScannedJobs(params);
  }
  throwDataNotFound();
}

export async function getScanSummary(threshold = MATCH_SCORE_THRESHOLD): Promise<ScanSummary> {
  if (USE_SUPABASE) {
    return getRepository().getScanSummary(threshold);
  }
  throwDataNotFound();
}

export async function rescanScanInsights(): Promise<{ rescoredCount: number }> {
  if (USE_SUPABASE) {
    try {
      return await backendFetch<{ success: boolean; rescoredCount: number }>(
        '/api/scan-insights/rescan',
        { method: 'POST' },
      ).then((data) => ({ rescoredCount: data.rescoredCount }));
    } catch {
      throw new Error(
        'Rescan requires the Python API server (set VITE_USE_BACKEND=true) or the rescan-insights GitHub Action.',
      );
    }
  }

  if (USE_BACKEND) {
    const data = await backendFetch<{ success: boolean; rescoredCount: number }>(
      '/api/scan-insights/rescan',
      { method: 'POST' },
    );
    return { rescoredCount: data.rescoredCount };
  }
  throwDataNotFound();
}

export async function promoteScannedJob(dedupeKey: string): Promise<JobRecord> {
  if (USE_SUPABASE) {
    return getRepository().promoteScannedJobToLead(dedupeKey);
  }

  if (USE_BACKEND) {
    const encodedKey = encodeURIComponent(dedupeKey);
    const data = await backendFetch<{ success: boolean; job: JobRecord }>(
      `/api/scan-insights/${encodedKey}/promote`,
      { method: 'POST' },
    );
    return data.job;
  }
  throwDataNotFound();
}
