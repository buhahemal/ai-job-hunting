import type { SupabaseClient } from '@supabase/supabase-js';

import {
  buildScanSummary,
  interviewToRow,
  jobToRow,
  rowToInterview,
  rowToJob,
  rowToScannedJob,
} from './mappers.js';
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

const PROFILE_ID = 'default';

export class DashboardRepository {
  constructor(private readonly client: SupabaseClient) {}

  async getProfile(): Promise<ProfileRecord | null> {
    const { data, error } = await this.client
      .from('profiles')
      .select('data')
      .eq('id', PROFILE_ID)
      .maybeSingle();
    if (error) throw error;
    if (!data?.data) return null;
    return data.data as ProfileRecord;
  }

  async saveProfile(profile: ProfileRecord): Promise<void> {
    const { error } = await this.client
      .from('profiles')
      .upsert({ id: PROFILE_ID, data: profile }, { onConflict: 'id' });
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

  async listInterviews(): Promise<InterviewRecord[]> {
    const { data, error } = await this.client.from('interviews').select('*');
    if (error) throw error;
    return ((data ?? []) as Parameters<typeof rowToInterview>[0][]).map(rowToInterview);
  }

  async updateJobStatus(jobId: string, status: JobRecord['status']): Promise<JobRecord> {
    const { data, error } = await this.client
      .from('jobs')
      .update({ status })
      .eq('id', jobId)
      .select('*')
      .single();
    if (error) throw error;
    return rowToJob(data as JobRow);
  }

  async updateJobNotes(jobId: string, notes: string): Promise<JobRecord> {
    const { data, error } = await this.client
      .from('jobs')
      .update({ notes })
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
    const limit = Math.max(1, Math.min(params.limit ?? 25, 100));
    const threshold = params.threshold ?? 75;
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

  async getScanSummary(threshold = 75): Promise<ScanSummary> {
    const { data, error } = await this.client
      .from('scanned_jobs')
      .select(
        'overall_score, score, source, scanned_at, promoted_to_jobs, missing_skills, scan_run_id',
      );
    if (error) throw error;
    return buildScanSummary((data ?? []) as ScanSummaryRow[], threshold);
  }
}
