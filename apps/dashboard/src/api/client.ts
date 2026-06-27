import type { Interview, Job, Profile } from '../types';
import {
  buildScanSummary,
  createBrowserClient,
  DashboardRepository,
  MATCH_SCORE_THRESHOLD,
  SCAN_INSIGHTS_LIST_MAX,
  SCAN_INSIGHTS_PAGE_SIZE,
  rowToScannedJob,
  type InterviewRecord,
  type JobRecord,
  type ListScannedJobsParams,
  type ScanSummary,
  type ScannedJobRecord,
  type ScannedJobsPage,
  type ScanSummaryRow,
} from '@ai-job-hunter/database';
import { normalizeProfile } from './defaultProfile';
import { SUPABASE_ANON_KEY, SUPABASE_URL, USE_BACKEND, USE_SUPABASE } from './config';
import { heuristicScore, loadDatabase, saveDatabase, tailorFallback } from './staticStore';

let repository: DashboardRepository | null = null;

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

function mapJsonScannedJob(raw: Record<string, unknown>): ScannedJobRecord {
  if (raw.dedupeKey) {
    return raw as unknown as ScannedJobRecord;
  }
  return rowToScannedJob({
    dedupe_key: String(raw.dedupe_key ?? ''),
    job_id: (raw.job_id as string | null) ?? null,
    source: (raw.source as string | null) ?? null,
    score: (raw.score as number | null) ?? null,
    scanned_at: String(raw.scanned_at ?? ''),
    title: (raw.title as string | null) ?? null,
    company: (raw.company as string | null) ?? null,
    location: (raw.location as string | null) ?? null,
    remote_type: (raw.remote_type as ScannedJobRecord['remoteType'] | null) ?? null,
    canonical_role: (raw.canonical_role as string | null) ?? null,
    primary_stack: (raw.primary_stack as string | null) ?? null,
    seniority: (raw.seniority as string | null) ?? null,
    employment_type: (raw.employment_type as string | null) ?? null,
    application_url: (raw.application_url as string | null) ?? null,
    required_skills: (raw.required_skills as string[] | null) ?? null,
    preferred_skills: (raw.preferred_skills as string[] | null) ?? null,
    extracted_technologies: (raw.extracted_technologies as string[] | null) ?? null,
    overall_score: (raw.overall_score as number | null) ?? (raw.score as number | null),
    skill_match_score: (raw.skill_match_score as number | null) ?? null,
    experience_match_score: (raw.experience_match_score as number | null) ?? null,
    ats_score: (raw.ats_score as number | null) ?? null,
    matched_skills: (raw.matched_skills as string[] | null) ?? null,
    missing_skills: (raw.missing_skills as string[] | null) ?? null,
    missing_keywords: (raw.missing_keywords as string[] | null) ?? null,
    match_explanation: (raw.match_explanation as string | null) ?? null,
    scorer: (raw.scorer as string | null) ?? null,
    promoted_to_jobs: Boolean(raw.promoted_to_jobs),
    scan_run_id: (raw.scan_run_id as string | null) ?? null,
  });
}

function filterScannedJobs(
  items: ScannedJobRecord[],
  params: ListScannedJobsParams,
): ScannedJobRecord[] {
  const threshold = params.threshold ?? MATCH_SCORE_THRESHOLD;
  return items.filter((item) => {
    if (params.minScore !== undefined && item.overallScore < params.minScore) return false;
    if (params.maxScore !== undefined && item.overallScore > params.maxScore) return false;
    if (params.source && item.source !== params.source) return false;
    if (params.role && item.canonicalRole !== params.role) return false;
    if (params.missingSkill && !item.missingSkills.includes(params.missingSkill)) return false;
    if (params.belowThresholdOnly && item.overallScore > threshold) return false;
    return true;
  });
}

export async function listScannedJobs(
  params: ListScannedJobsParams = {},
): Promise<ScannedJobsPage> {
  if (USE_SUPABASE) {
    return getRepository().listScannedJobs(params);
  }

  const db = await loadDatabase();
  const rawItems = (db as { scannedJobs?: Record<string, unknown>[] }).scannedJobs ?? [];
  const allItems = rawItems.map(mapJsonScannedJob);
  const filtered = filterScannedJobs(allItems, params);
  const page = Math.max(1, params.page ?? 1);
  const limit = Math.max(
    1,
    Math.min(params.limit ?? SCAN_INSIGHTS_PAGE_SIZE, SCAN_INSIGHTS_LIST_MAX),
  );
  const offset = (page - 1) * limit;

  return {
    items: filtered.slice(offset, offset + limit),
    page,
    limit,
    total: filtered.length,
  };
}

export async function getScanSummary(threshold = MATCH_SCORE_THRESHOLD): Promise<ScanSummary> {
  if (USE_SUPABASE) {
    return getRepository().getScanSummary(threshold);
  }

  const db = await loadDatabase();
  const rawItems = (db as { scannedJobs?: Record<string, unknown>[] }).scannedJobs ?? [];
  const rows: ScanSummaryRow[] = rawItems.map((raw) => ({
    overall_score: (raw.overall_score as number | null) ?? (raw.score as number | null),
    score: (raw.score as number | null) ?? null,
    source: (raw.source as string | null) ?? null,
    scanned_at: String(raw.scanned_at ?? ''),
    promoted_to_jobs: Boolean(raw.promoted_to_jobs),
    missing_skills: (raw.missing_skills as string[] | null) ?? [],
    scan_run_id: (raw.scan_run_id as string | null) ?? null,
  }));
  return buildScanSummary(rows, threshold, normalizeProfile(db.profile));
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

  const data = await backendFetch<{ success: boolean; rescoredCount: number }>(
    '/api/scan-insights/rescan',
    { method: 'POST' },
  );
  return { rescoredCount: data.rescoredCount };
}

export async function promoteScannedJob(dedupeKey: string): Promise<JobRecord> {
  if (USE_SUPABASE) {
    return getRepository().promoteScannedJobToLead(dedupeKey);
  }

  const encodedKey = encodeURIComponent(dedupeKey);
  const data = await backendFetch<{ success: boolean; job: JobRecord }>(
    `/api/scan-insights/${encodedKey}/promote`,
    { method: 'POST' },
  );
  return data.job;
}
