import type { SupabaseClient } from '@supabase/supabase-js';

import {
  MATCH_SCORE_THRESHOLD,
  PROFILE_ID,
  SCAN_INSIGHTS_LIST_MAX,
  SCAN_INSIGHTS_PAGE_SIZE,
} from './constants.js';
import {
  buildScanSummary,
  interviewToRow,
  jobToRow,
  matchInsightsToRow,
  rowToInterview,
  rowToJob,
  rowToScannedJob,
  scannedJobRowToJob,
} from './mappers.js';
import { normalizeStoredProfile } from './profile.js';
import type {
  InterviewRecord,
  JobRecord,
  JobRow,
  ListScannedJobsParams,
  ProfileRecord,
  ScanSummary,
  ScanSummaryRow,
  ScannedJobRow,
  ScannedJobsPage,
} from './types.js';

export class DashboardRepository {
  constructor(private readonly client: SupabaseClient) {}

  async getProfile(): Promise<ProfileRecord> {
    const { data, error } = await this.client
      .from('profiles')
      .select('data')
      .eq('id', PROFILE_ID)
      .maybeSingle();
    if (error) throw error;
    return normalizeStoredProfile((data?.data as ProfileRecord | undefined) ?? null);
  }

  async saveProfile(profile: ProfileRecord): Promise<void> {
    const normalized = normalizeStoredProfile(profile);
    const { error } = await this.client
      .from('profiles')
      .upsert({ id: PROFILE_ID, data: normalized }, { onConflict: 'id' });
    if (error) throw error;
  }

  async listJobs(): Promise<JobRecord[]> {
    const { data, error } = await this.client
      .from('jobs')
      .select('*, job_match_scores(*)')
      .order('posted_at', { ascending: false });
    if (error) throw error;
    return ((data ?? []) as JobRow[]).map(rowToJob);
  }

  async getJob(jobId: string): Promise<JobRecord | null> {
    const { data, error } = await this.client
      .from('jobs')
      .select('*, job_match_scores(*)')
      .eq('id', jobId)
      .maybeSingle();
    if (error || !data) return null;
    return rowToJob(data as JobRow);
  }

  async listInterviews(): Promise<InterviewRecord[]> {
    const { data, error } = await this.client.from('interviews').select('*');
    if (error) throw error;
    return ((data ?? []) as Parameters<typeof rowToInterview>[0][]).map(rowToInterview);
  }

  async updateJobStatus(
    jobId: string,
    status: JobRecord['status'],
    note?: string,
  ): Promise<JobRecord> {
    const existing = await this.getJob(jobId);
    const now = new Date().toISOString();
    const history = [
      {
        timestamp: now,
        status,
        action: `Status changed to ${status}`,
        note: note || '',
      },
      ...(existing?.actionHistory ?? []),
    ];

    const patch: Record<string, unknown> = {
      status,
      updated_at: now,
      action_history: history,
    };
    if (note) patch.notes = note;

    const { data, error } = await this.client
      .from('jobs')
      .update(patch)
      .eq('id', jobId)
      .select('*')
      .single();
    if (error) throw error;
    return rowToJob(data as JobRow);
  }

  async updateJobNotes(jobId: string, notes: string): Promise<JobRecord> {
    const existing = await this.getJob(jobId);
    const now = new Date().toISOString();
    const history = [
      {
        timestamp: now,
        status: existing?.status ?? 'New',
        action: 'Notes updated',
        note: notes,
      },
      ...(existing?.actionHistory ?? []),
    ];

    const { data, error } = await this.client
      .from('jobs')
      .update({ notes, updated_at: now, action_history: history })
      .eq('id', jobId)
      .select('*')
      .single();
    if (error) throw error;
    return rowToJob(data as JobRow);
  }

  async upsertJob(job: JobRecord): Promise<JobRecord> {
    const { data, error } = await this.client
      .from('jobs')
      .upsert(jobToRow(job), { onConflict: 'id' })
      .select('*')
      .single();
    if (error) throw error;
    return rowToJob(data as JobRow);
  }

  async saveTailoredJob(
    jobId: string,
    payload: {
      tailoredResumeLaTeX: string;
      tailoredCoverLetter: string;
      atsScore?: number;
    },
  ): Promise<JobRecord> {
    const { data, error } = await this.client
      .from('jobs')
      .update({
        tailored_resume_latex: payload.tailoredResumeLaTeX,
        tailored_cover_letter: payload.tailoredCoverLetter,
        ats_score: payload.atsScore ?? null,
      })
      .eq('id', jobId)
      .select('*')
      .single();
    if (error) throw error;
    return rowToJob(data as JobRow);
  }

  async addInterview(
    interview: Omit<InterviewRecord, 'id' | 'status'> & {
      id: string;
      status: InterviewRecord['status'];
    },
  ): Promise<void> {
    const { error } = await this.client.from('interviews').insert(interviewToRow(interview));
    if (error) throw error;
  }

  async updateInterviewStatus(id: string, status: InterviewRecord['status']): Promise<void> {
    const { error } = await this.client.from('interviews').update({ status }).eq('id', id);
    if (error) throw error;
  }

  async listScannedJobs(params: ListScannedJobsParams = {}): Promise<ScannedJobsPage> {
    const page = Math.max(1, params.page ?? 1);
    const limit = Math.max(
      1,
      Math.min(params.limit ?? SCAN_INSIGHTS_PAGE_SIZE, SCAN_INSIGHTS_LIST_MAX),
    );
    const threshold = params.threshold ?? MATCH_SCORE_THRESHOLD;
    const from = (page - 1) * limit;
    const to = from + limit - 1;

    let query = this.client.from('scanned_jobs').select('*', { count: 'exact' });

    if (params.minScore !== undefined) {
      query = query.gte('overall_score', params.minScore);
    }
    if (params.maxScore !== undefined) {
      query = query.lte('overall_score', params.maxScore);
    }
    if (params.source) {
      query = query.eq('source', params.source);
    }
    if (params.role) {
      query = query.eq('canonical_role', params.role);
    }
    if (params.missingSkill) {
      query = query.contains('missing_skills', [params.missingSkill]);
    }
    if (params.belowThresholdOnly) {
      query = query.lte('overall_score', threshold);
    }

    const { data, error, count } = await query
      .order('scanned_at', { ascending: false })
      .range(from, to);
    if (error) throw error;

    return {
      items: ((data ?? []) as ScannedJobRow[]).map(rowToScannedJob),
      page,
      limit,
      total: count ?? data?.length ?? 0,
    };
  }

  async getScanSummary(threshold = MATCH_SCORE_THRESHOLD): Promise<ScanSummary> {
    const profile = await this.getProfile();
    const { data, error } = await this.client
      .from('scanned_jobs')
      .select(
        'overall_score, score, source, scanned_at, promoted_to_jobs, missing_skills, scan_run_id',
      );
    if (error) throw error;
    return buildScanSummary((data ?? []) as ScanSummaryRow[], threshold, profile);
  }

  async promoteScannedJobToLead(dedupeKey: string): Promise<JobRecord> {
    const { data, error } = await this.client
      .from('scanned_jobs')
      .select('*')
      .eq('dedupe_key', dedupeKey)
      .maybeSingle();
    if (error) throw error;
    if (!data) {
      throw new Error(`Scanned job not found: ${dedupeKey}`);
    }

    const job = scannedJobRowToJob(data as ScannedJobRow);
    const { error: upsertError } = await this.client
      .from('jobs')
      .upsert(jobToRow(job), { onConflict: 'id' });
    if (upsertError) throw upsertError;

    if (job.matchInsights) {
      const { error: scoreError } = await this.client
        .from('job_match_scores')
        .upsert(matchInsightsToRow(job.id, job.matchInsights), { onConflict: 'job_id' });
      if (scoreError) throw scoreError;
    }

    const { error: flagError } = await this.client
      .from('scanned_jobs')
      .update({ promoted_to_jobs: true, promotion_type: 'manual' })
      .eq('dedupe_key', dedupeKey);
    if (flagError) throw flagError;

    return job;
  }
}
